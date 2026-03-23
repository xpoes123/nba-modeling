"""Calibration: fit OLS + James-Stein (Empirical Bayes) shrinkage on historical games.

Two-step process:
  1. OLS with 30 team dummies to get alpha, per-team HCA raw estimates, and B2B coefficients.
  2. James-Stein shrinkage: pull each team's raw HCA toward the grand mean by a data-driven
     factor. If sigma2_between <= 0 (no detectable real team variation), all teams pool to
     the grand mean.

Shrinkage formulas:
    sigma2_within_i = sigma_residual^2 / n_home_games_i
    sigma2_between  = max(0, var(raw_hca_estimates) - mean(sigma2_within_i))
    B_i             = sigma2_within_i / (sigma2_within_i + sigma2_between)
    hca_shrunk_i    = grand_mean + (1 - B_i) * (hca_raw_i - grand_mean)

Run once (or periodically) to generate calibration_coeffs.json.

Usage:
    PYTHONPATH=. uv run python downstream/calibration.py

Outputs: downstream/calibration_coeffs.json with keys:
    alpha, beta_hca, beta_hca_by_team, beta_b2b_home, beta_b2b_away, sigma_residual,
    train_rmse, val_rmse, train_corr, val_corr, n_train, n_val, sigma2_between, shrinkage_mean
"""
import json
import logging
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CALIBRATION_PATH, DB_PATH, INITIAL_SEASON, NBA_TEAM_MAP
from downstream.team_ratings import PlayerRating, compute_raw_margin, compute_team_ratings

# Canonical sorted team ID list — order must be stable across train/val/predict.
_TEAM_IDS: list[str] = sorted(NBA_TEAM_MAP.keys())

_LINEUP_LOOKBACK_GAMES = 15
_MIN_GAMES = 3
_RECENCY_DECAY = 0.85

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def _load_player_ratings(conn: sqlite3.Connection, season: str) -> dict[str, PlayerRating]:
    """Load current_ratings from DB into a dict keyed by player_id."""
    rows = conn.execute(
        "SELECT player_id, offense, defense, pace FROM current_ratings WHERE season = ?",
        (season,),
    ).fetchall()
    return {
        r["player_id"]: PlayerRating(
            player_id=r["player_id"],
            offense=r["offense"],
            defense=r["defense"],
            pace=r["pace"],
        )
        for r in rows
    }


def _load_games(conn: sqlite3.Connection, season: str) -> pd.DataFrame:
    """Load games with actual margins, ordered chronologically."""
    return pd.read_sql(
        """
        SELECT game_id, game_date, home_team_id, away_team_id,
               home_score, away_score,
               (home_score - away_score) AS actual_margin
        FROM games
        WHERE season = ? AND home_score IS NOT NULL AND away_score IS NOT NULL
        ORDER BY game_date ASC
        """,
        conn,
        params=(season,),
    )


def _load_league_avg(conn: sqlite3.Connection, season: str) -> tuple[float, float]:
    """Return (avg_ppp, avg_pace) for the season."""
    row = conn.execute(
        "SELECT avg_ppp, avg_pace FROM league_averages WHERE season = ?", (season,)
    ).fetchone()
    if row is None:
        raise ValueError(f"No league averages found for season {season}")
    return row["avg_ppp"], row["avg_pace"]


def _build_team_ratings_for_game(
    home_team_id: str,
    away_team_id: str,
    game_date: str,
    conn: sqlite3.Connection,
    player_ratings: dict[str, PlayerRating],
    league_avg_ppp: float,
    league_avg_pace: float,
) -> float | None:
    """Compute raw predicted home margin for a historical game.

    Uses the same 15-game lookback estimation with recency weighting that the
    backtest and live prediction pipeline use — NOT oracle lineup data from the
    game itself. This eliminates the train/test mismatch where calibration fits
    alpha on cleaner oracle data but applies it to noisier estimated data.
    """

    def _get_team_shares(team_id: str) -> dict[str, float] | None:
        """Return recency-weighted, availability-discounted possession shares."""
        rows = conn.execute(
            """
            SELECT game_id FROM games
            WHERE (home_team_id = ? OR away_team_id = ?) AND game_date < ?
            ORDER BY game_date DESC LIMIT ?
            """,
            (team_id, team_id, game_date, _LINEUP_LOOKBACK_GAMES),
        ).fetchall()
        game_ids = [r["game_id"] for r in rows]
        if not game_ids:
            return None

        n_window_games = len(game_ids)
        # slot 0 = most recent game (weight 1.0), slot 1 = 0.85, …
        game_weight = {gid: _RECENCY_DECAY ** i for i, gid in enumerate(game_ids)}
        total_window_weight = sum(_RECENCY_DECAY ** i for i in range(n_window_games))

        placeholders = ",".join("?" * len(game_ids))
        poss_df = pd.read_sql(
            f"""
            SELECT game_id, off_player_1, off_player_2, off_player_3, off_player_4, off_player_5
            FROM possessions
            WHERE offense_team_id = ? AND game_id IN ({placeholders})
            """,
            conn,
            params=[team_id] + game_ids,
        )
        if poss_df.empty:
            return None

        off_cols = ["off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5"]

        # Build per-player list of (raw_share, game_weight) entries
        player_share_list: dict[str, list[tuple[float, float]]] = {}
        for gid, gdf in poss_df.groupby("game_id"):
            n_poss = len(gdf)
            counts: dict[str, int] = {}
            for col in off_cols:
                for pid in gdf[col]:
                    counts[pid] = counts.get(pid, 0) + 1
            w = game_weight[gid]
            for pid, cnt in counts.items():
                player_share_list.setdefault(pid, []).append((cnt / (n_poss * 5), w))

        # Compute recency-weighted mean share with availability discounting
        shares: dict[str, float] = {}
        for pid, entries in player_share_list.items():
            if len(entries) < _MIN_GAMES:
                continue
            w_sum = sum(w for _, w in entries)
            mean_share = sum(w * s for s, w in entries) / w_sum
            # Availability: fraction of total window weight this player covered
            availability = w_sum / total_window_weight
            shares[pid] = mean_share * availability

        if not shares:
            return None
        return shares

    home_shares = _get_team_shares(home_team_id)
    away_shares = _get_team_shares(away_team_id)

    if not home_shares or not away_shares:
        return None

    home_team = compute_team_ratings(player_ratings, home_shares)
    away_team = compute_team_ratings(player_ratings, away_shares)

    return compute_raw_margin(home_team, away_team, league_avg_ppp, league_avg_pace)


def _detect_b2b(games_df: pd.DataFrame) -> pd.DataFrame:
    """Add home_b2b and away_b2b columns to games_df.

    A team is on a B2B if they played a game the calendar day before.
    """
    # Build set of (team_id, game_date) pairs
    team_dates: set[tuple[str, str]] = set()
    for _, row in games_df.iterrows():
        team_dates.add((row["home_team_id"], row["game_date"]))
        team_dates.add((row["away_team_id"], row["game_date"]))

    def _is_b2b(team_id: str, game_date: str) -> int:
        prev = (date.fromisoformat(game_date) - timedelta(days=1)).isoformat()
        return int((team_id, prev) in team_dates)

    games_df = games_df.copy()
    games_df["home_b2b"] = games_df.apply(
        lambda r: _is_b2b(r["home_team_id"], r["game_date"]), axis=1
    )
    games_df["away_b2b"] = games_df.apply(
        lambda r: _is_b2b(r["away_team_id"], r["game_date"]), axis=1
    )
    return games_df


def run_calibration(
    db_path: str = DB_PATH,
    season: str = INITIAL_SEASON,
    train_fraction: float = 0.6,
    output_path: str = CALIBRATION_PATH,
) -> dict:
    """Fit OLS calibration and save coefficients to JSON.

    Returns the coefficient dict.
    """
    conn = _get_conn(db_path)
    try:
        player_ratings = _load_player_ratings(conn, season)
        logger.info("Loaded %d player ratings", len(player_ratings))

        games_df = _load_games(conn, season)
        logger.info("Loaded %d games with scores", len(games_df))

        league_avg_ppp, league_avg_pace = _load_league_avg(conn, season)
        logger.info("League avg PPP=%.4f  pace=%.1f", league_avg_ppp, league_avg_pace)

        games_df = _detect_b2b(games_df)

        # Compute raw predicted margin for each game
        logger.info("Computing raw predicted margins for %d games...", len(games_df))
        raw_margins = []
        valid_indices = []

        for i, row in games_df.iterrows():
            raw = _build_team_ratings_for_game(
                row["home_team_id"], row["away_team_id"], row["game_date"],
                conn, player_ratings, league_avg_ppp, league_avg_pace,
            )
            if raw is not None:
                raw_margins.append(raw)
                valid_indices.append(i)

        games_valid = games_df.loc[valid_indices].copy()
        games_valid["raw_margin"] = raw_margins
        logger.info("Valid games for calibration: %d", len(games_valid))

    finally:
        conn.close()

    # Train/val split (chronological)
    n_train = int(len(games_valid) * train_fraction)
    train = games_valid.iloc[:n_train]
    val = games_valid.iloc[n_train:]
    logger.info("Train: %d games | Val: %d games", len(train), len(val))

    # Fit OLS: actual_margin ~ alpha*raw_margin + hca[home_team] + beta_b2b_home + beta_b2b_away
    # Each of the 30 home-team dummies gets its own HCA coefficient instead of a single intercept.
    def _features(df: pd.DataFrame) -> np.ndarray:
        team_dummies = np.column_stack(
            [(df["home_team_id"] == tid).astype(float).values for tid in _TEAM_IDS]
        )
        return np.column_stack([
            df["raw_margin"].values,
            team_dummies,
            df["home_b2b"].values,
            df["away_b2b"].values,
        ])

    X_train = _features(train)
    y_train = train["actual_margin"].values
    y_val = val["actual_margin"].values

    model = LinearRegression(fit_intercept=False)
    model.fit(X_train, y_train)

    # --- Step 1: Extract raw OLS coefficients ---
    n_teams = len(_TEAM_IDS)
    alpha = float(model.coef_[0])
    raw_hca_by_team: dict[str, float] = {
        tid: float(model.coef_[i + 1]) for i, tid in enumerate(_TEAM_IDS)
    }
    beta_b2b_home = float(model.coef_[1 + n_teams])
    beta_b2b_away = float(model.coef_[1 + n_teams + 1])

    # Residual sigma from OLS training fit (used for win probability and shrinkage)
    train_preds_ols = model.predict(X_train)
    residuals = y_train - train_preds_ols
    sigma_residual = float(np.std(residuals))
    sigma2_residual = sigma_residual ** 2

    raw_hca_values = np.array(list(raw_hca_by_team.values()))
    grand_mean = float(np.mean(raw_hca_values))

    # --- Step 2: James-Stein shrinkage of team HCAs toward grand mean ---

    # Count actual home games per team in the training set
    n_home_games_per_team: dict[str, int] = {tid: 0 for tid in _TEAM_IDS}
    for _, row in train.iterrows():
        n_home_games_per_team[row["home_team_id"]] += 1

    # Sampling variance of each team's raw estimate
    sigma2_within = {
        tid: sigma2_residual / max(n_home_games_per_team[tid], 1)
        for tid in _TEAM_IDS
    }

    # True between-team variance (clamped to 0 if undetectable)
    var_raw = float(np.var(raw_hca_values, ddof=0))
    mean_sigma2_within = float(np.mean(list(sigma2_within.values())))
    sigma2_between = max(0.0, var_raw - mean_sigma2_within)

    logger.info("--- James-Stein Shrinkage Diagnostics ---")
    logger.info("  sigma_residual:       %.4f pts", sigma_residual)
    logger.info("  var(raw HCAs):        %.4f", var_raw)
    logger.info("  mean(sigma2_within):  %.4f", mean_sigma2_within)
    logger.info("  sigma2_between:       %.4f  (real team variation detected: %s)",
                sigma2_between, sigma2_between > 0)

    shrunk_hca_by_team: dict[str, float] = {}
    B_by_team: dict[str, float] = {}

    if sigma2_between <= 0:
        logger.info("  sigma2_between <= 0 — pooling all teams to grand mean")
        for tid in _TEAM_IDS:
            shrunk_hca_by_team[tid] = grand_mean
            B_by_team[tid] = 1.0
    else:
        for tid in _TEAM_IDS:
            B_i = sigma2_within[tid] / (sigma2_within[tid] + sigma2_between)
            shrunk_hca_by_team[tid] = grand_mean + (1.0 - B_i) * (raw_hca_by_team[tid] - grand_mean)
            B_by_team[tid] = B_i

    shrinkage_mean = float(np.mean(list(B_by_team.values())))

    # --- Evaluate using shrunk HCAs (not raw OLS predictions) ---
    def _predict_shrunk(df: pd.DataFrame) -> np.ndarray:
        preds = alpha * df["raw_margin"].values
        preds += np.array([shrunk_hca_by_team[tid] for tid in df["home_team_id"]])
        preds += beta_b2b_home * df["home_b2b"].values
        preds += beta_b2b_away * df["away_b2b"].values
        return preds

    train_preds = _predict_shrunk(train)
    val_preds = _predict_shrunk(val)

    train_rmse = float(root_mean_squared_error(y_train, train_preds))
    val_rmse = float(root_mean_squared_error(y_val, val_preds))
    train_corr = float(np.corrcoef(y_train, train_preds)[0, 1])
    val_corr = float(np.corrcoef(y_val, val_preds)[0, 1])

    coeffs = {
        "alpha": alpha,
        "beta_hca": grand_mean,
        "beta_hca_by_team": shrunk_hca_by_team,
        "beta_b2b_home": beta_b2b_home,
        "beta_b2b_away": beta_b2b_away,
        "sigma_residual": sigma_residual,
        "train_rmse": train_rmse,
        "val_rmse": val_rmse,
        "train_corr": train_corr,
        "val_corr": val_corr,
        "n_train": len(train),
        "n_val": len(val),
        "season": season,
        "sigma2_between": sigma2_between,
        "shrinkage_mean": shrinkage_mean,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(coeffs, f, indent=2)

    logger.info("=== Calibration Results (EB-shrunk) ===")
    logger.info("  alpha (raw margin scale): %.4f", alpha)
    logger.info("  beta_hca (grand mean):    %.4f pts", grand_mean)
    logger.info("  beta_b2b_home:            %.4f pts", beta_b2b_home)
    logger.info("  beta_b2b_away:            %.4f pts", beta_b2b_away)
    logger.info("  sigma_residual:           %.2f pts", sigma_residual)
    logger.info("  sigma2_between:           %.4f", sigma2_between)
    logger.info("  avg shrinkage B_i:        %.4f  (1.0 = full pool)", shrinkage_mean)
    logger.info("  Train RMSE: %.2f  corr: %.3f", train_rmse, train_corr)
    logger.info("  Val   RMSE: %.2f  corr: %.3f", val_rmse, val_corr)

    # Log raw vs shrunk HCAs sorted descending
    sorted_raw = sorted(raw_hca_by_team.items(), key=lambda x: x[1], reverse=True)
    logger.info("  Team HCAs — raw vs shrunk (sorted by raw):")
    for tid, raw_hca in sorted_raw:
        abbrev = NBA_TEAM_MAP[tid]["abbrev"]
        shrunk = shrunk_hca_by_team[tid]
        logger.info("    %s: raw %+.2f → shrunk %+.2f", abbrev, raw_hca, shrunk)

    logger.info("Saved to %s", output_path)

    return coeffs


def load_calibration(path: str = CALIBRATION_PATH) -> dict:
    """Load calibration coefficients from JSON. Raises FileNotFoundError if missing."""
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    run_calibration()
