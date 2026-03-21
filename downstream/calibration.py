"""Calibration: fit OLS on historical games to map raw RAPM margins → actual margins.

Run once (or periodically) to generate calibration_coeffs.json.

Usage:
    PYTHONPATH=. uv run python downstream/calibration.py

Outputs: downstream/calibration_coeffs.json with keys:
    alpha, beta_hca, beta_b2b_home, beta_b2b_away, sigma_residual,
    train_rmse, val_rmse, train_corr, val_corr, n_train, n_val
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

from config import CALIBRATION_PATH, DB_PATH, INITIAL_SEASON
from downstream.team_ratings import PlayerRating, compute_raw_margin, compute_team_ratings

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
    game_id: str,
    home_team_id: str,
    away_team_id: str,
    conn: sqlite3.Connection,
    player_ratings: dict[str, PlayerRating],
    league_avg_ppp: float,
    league_avg_pace: float,
) -> float | None:
    """Compute raw predicted home margin for a historical game.

    Uses the players who actually appeared in the game (from possessions table)
    and their actual possession shares.
    """
    poss_df = pd.read_sql(
        """
        SELECT offense_team_id,
               off_player_1, off_player_2, off_player_3, off_player_4, off_player_5
        FROM possessions
        WHERE game_id = ?
        """,
        conn,
        params=(game_id,),
    )

    if poss_df.empty:
        return None

    # Count possessions per player per team (offensive possessions only — that's
    # when they're contributing their offensive rating)
    off_cols = ["off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5"]

    home_poss = poss_df[poss_df["offense_team_id"] == home_team_id]
    away_poss = poss_df[poss_df["offense_team_id"] == away_team_id]

    def _possession_shares(team_poss: pd.DataFrame) -> dict[str, float]:
        counts: dict[str, int] = {}
        n = len(team_poss)
        if n == 0:
            return {}
        for col in off_cols:
            for pid in team_poss[col]:
                counts[pid] = counts.get(pid, 0) + 1
        # Each player's share = appearances / (n_possessions * 5), then normalize
        return {pid: cnt / (n * 5) for pid, cnt in counts.items()}

    home_shares = _possession_shares(home_poss)
    away_shares = _possession_shares(away_poss)

    if not home_shares or not away_shares:
        return None

    # Use actual possession count as the pace (rather than estimated)
    actual_pace = (len(home_poss) + len(away_poss)) / 2

    home_team = compute_team_ratings(player_ratings, home_shares)
    away_team = compute_team_ratings(player_ratings, away_shares)

    home_ppp = league_avg_ppp + (home_team["offense"] - away_team["defense"]) / 100
    away_ppp = league_avg_ppp + (away_team["offense"] - home_team["defense"]) / 100
    return (home_ppp - away_ppp) * actual_pace


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
                row["game_id"], row["home_team_id"], row["away_team_id"],
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

    # Fit OLS: actual_margin ~ alpha*raw_margin + beta_hca + beta_b2b_home + beta_b2b_away
    def _features(df: pd.DataFrame) -> np.ndarray:
        return np.column_stack([
            df["raw_margin"].values,
            np.ones(len(df)),          # HCA intercept
            df["home_b2b"].values,
            df["away_b2b"].values,
        ])

    X_train = _features(train)
    y_train = train["actual_margin"].values
    X_val = _features(val)
    y_val = val["actual_margin"].values

    model = LinearRegression(fit_intercept=False)
    model.fit(X_train, y_train)

    alpha, beta_hca, beta_b2b_home, beta_b2b_away = model.coef_

    # Residual sigma on full training set (used for win probability)
    train_preds = model.predict(X_train)
    residuals = y_train - train_preds
    sigma_residual = float(np.std(residuals))

    train_rmse = float(root_mean_squared_error(y_train, train_preds))
    val_preds = model.predict(X_val)
    val_rmse = float(root_mean_squared_error(y_val, val_preds))
    train_corr = float(np.corrcoef(y_train, train_preds)[0, 1])
    val_corr = float(np.corrcoef(y_val, val_preds)[0, 1])

    coeffs = {
        "alpha": float(alpha),
        "beta_hca": float(beta_hca),
        "beta_b2b_home": float(beta_b2b_home),
        "beta_b2b_away": float(beta_b2b_away),
        "sigma_residual": sigma_residual,
        "train_rmse": train_rmse,
        "val_rmse": val_rmse,
        "train_corr": train_corr,
        "val_corr": val_corr,
        "n_train": len(train),
        "n_val": len(val),
        "season": season,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(coeffs, f, indent=2)

    logger.info("=== Calibration Results ===")
    logger.info("  alpha (raw margin scale): %.4f", alpha)
    logger.info("  beta_hca:                 %.4f pts", beta_hca)
    logger.info("  beta_b2b_home:            %.4f pts", beta_b2b_home)
    logger.info("  beta_b2b_away:            %.4f pts", beta_b2b_away)
    logger.info("  sigma_residual:           %.2f pts", sigma_residual)
    logger.info("  Train RMSE: %.2f  corr: %.3f", train_rmse, train_corr)
    logger.info("  Val   RMSE: %.2f  corr: %.3f", val_rmse, val_corr)
    logger.info("Saved to %s", output_path)

    return coeffs


def load_calibration(path: str = CALIBRATION_PATH) -> dict:
    """Load calibration coefficients from JSON. Raises FileNotFoundError if missing."""
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    run_calibration()
