"""Backtest the prediction model on historical games.

For each game with a known score, builds lineups from possession history BEFORE that game,
computes our predicted spread, and compares to the actual margin.

Note: No injury exclusions — we don't have historical injury data. This is a clean test
of the player-rating model using full observed rosters.

Usage:
    PYTHONPATH=. uv run python downstream/backtest.py [--start YYYY-MM-DD] [--end YYYY-MM-DD]

Default: all games in the current season that have scores.
"""
import argparse
import logging
import math
import sqlite3
import sys
from datetime import date
from pathlib import Path
from statistics import mean, stdev

import pandas as pd
from scipy.stats import pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DB_PATH, INITIAL_SEASON, NBA_TEAM_MAP
from downstream.calibration import load_calibration, CALIBRATION_PATH
from downstream.lineup_sampler import MinutesProfile, apply_calibration, simulate_game
from downstream.team_ratings import PlayerRating, normalize_name

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_LINEUP_LOOKBACK_GAMES = 15
_MIN_GAMES = 3
_N_SIMS = 500  # fewer sims for speed — Monte Carlo variance is negligible anyway


def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def _load_player_ratings(conn: sqlite3.Connection, season: str) -> dict[str, PlayerRating]:
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


def _load_league_avg(conn: sqlite3.Connection, season: str) -> tuple[float, float]:
    row = conn.execute(
        "SELECT avg_ppp, avg_pace FROM league_averages WHERE season = ?", (season,)
    ).fetchone()
    if row is None:
        raise ValueError(f"No league averages for season {season}")
    return row["avg_ppp"], row["avg_pace"]


def _get_team_profiles(
    team_id: str,
    conn: sqlite3.Connection,
    before_date: str,
    n_games: int = _LINEUP_LOOKBACK_GAMES,
) -> tuple[dict[str, list[float]], int]:
    """Possession shares from the n games before before_date.

    Returns (player_shares, n_window_games) where n_window_games is the actual
    number of games found (may be less than n_games early in the season).
    """
    rows = conn.execute(
        """
        SELECT game_id FROM games
        WHERE (home_team_id = ? OR away_team_id = ?) AND game_date < ?
        ORDER BY game_date DESC LIMIT ?
        """,
        (team_id, team_id, before_date, n_games),
    ).fetchall()
    game_ids = [r["game_id"] for r in rows]
    if not game_ids:
        return {}, 0

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
        return {}, len(game_ids)

    off_cols = ["off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5"]
    player_shares: dict[str, list[float]] = {}
    for gid, gdf in poss_df.groupby("game_id"):
        n_poss = len(gdf)
        counts: dict[str, int] = {}
        for col in off_cols:
            for pid in gdf[col]:
                counts[pid] = counts.get(pid, 0) + 1
        for pid, cnt in counts.items():
            player_shares.setdefault(pid, []).append(cnt / (n_poss * 5))
    return player_shares, len(game_ids)


def _build_minutes_profile(
    team_id: str,
    conn: sqlite3.Connection,
    before_date: str,
) -> tuple[MinutesProfile, float]:
    """Build lineup profile from possession history before before_date.

    Each player's weight is availability-discounted:
        effective_share = mean_share_when_played × (games_appeared / games_in_window)

    This means a player who appeared in 9 of 15 games gets 60% of their per-game
    share as their effective contribution — the remaining 40% is implicitly league
    average (someone else covered those possessions). Players with many DNPs are
    naturally downweighted without requiring explicit injury data.

    Returns (MinutesProfile, coverage_ratio).
    """
    profiles, n_window_games = _get_team_profiles(team_id, conn, before_date)
    if n_window_games == 0:
        return MinutesProfile(), 1.0

    result = MinutesProfile()
    total_weight = 0.0
    available_weight = 0.0

    for pid, shares in profiles.items():
        if len(shares) < _MIN_GAMES:
            continue
        # Availability discount: weight by fraction of games the player appeared in
        availability = len(shares) / n_window_games
        ms = mean(shares) * availability
        total_weight += ms
        available_weight += ms
        sd = stdev(shares) if len(shares) > 1 else 0.03
        result[pid] = (ms * 240, sd * 240)

    coverage = available_weight / total_weight if total_weight > 0 else 1.0
    return result, coverage


def _detect_b2b(team_id: str, game_date: str, conn: sqlite3.Connection) -> bool:
    from datetime import date, timedelta
    prev = (date.fromisoformat(game_date) - timedelta(days=1)).isoformat()
    row = conn.execute(
        "SELECT 1 FROM games WHERE game_date = ? AND (home_team_id = ? OR away_team_id = ?) LIMIT 1",
        (prev, team_id, team_id),
    ).fetchone()
    return row is not None


def _team_abbrev(team_id: str) -> str:
    entry = NBA_TEAM_MAP.get(team_id)
    if entry:
        return entry.get("abbrev", team_id[:3])
    return team_id[:3].upper()


def run_backtest(
    db_path: str = DB_PATH,
    season: str = INITIAL_SEASON,
    start_date: str | None = None,
    end_date: str | None = None,
    n_simulations: int = _N_SIMS,
) -> list[dict]:
    """Run the prediction model on all scored games in the date range.

    Returns list of result dicts with keys:
        game_date, home_team_id, away_team_id,
        predicted_spread, actual_margin, error, abs_error
    """
    conn = _get_conn(db_path)
    try:
        from downstream.calibration import load_calibration
        try:
            coeffs = load_calibration(CALIBRATION_PATH)
        except FileNotFoundError:
            print("ERROR: Run downstream/calibration.py first to generate coefficients.")
            return []

        alpha = coeffs["alpha"]
        beta_hca_fallback = coeffs["beta_hca"]
        beta_hca_by_team: dict[str, float] = coeffs.get("beta_hca_by_team", {})
        beta_b2b_home = coeffs["beta_b2b_home"]
        beta_b2b_away = coeffs["beta_b2b_away"]

        player_ratings = _load_player_ratings(conn, season)
        league_avg_ppp, league_avg_pace = _load_league_avg(conn, season)

        # Load games with scores
        query = """
            SELECT game_id, game_date, home_team_id, away_team_id,
                   home_score, away_score, (home_score - away_score) AS actual_margin
            FROM games
            WHERE season = ? AND home_score IS NOT NULL AND away_score IS NOT NULL
        """
        params: list = [season]
        if start_date:
            query += " AND game_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND game_date <= ?"
            params.append(end_date)
        query += " ORDER BY game_date ASC"

        games = conn.execute(query, params).fetchall()
        print(f"Running backtest on {len(games)} games ({start_date or 'season start'} to {end_date or 'latest'})\n")

        results = []
        skipped = 0

        for g in games:
            gid = g["game_id"]
            gdate = g["game_date"]
            home_id = g["home_team_id"]
            away_id = g["away_team_id"]
            actual = g["actual_margin"]

            home_mins, home_cov = _build_minutes_profile(home_id, conn, before_date=gdate)
            away_mins, away_cov = _build_minutes_profile(away_id, conn, before_date=gdate)

            if not home_mins or not away_mins:
                skipped += 1
                continue

            home_ratings = {pid: player_ratings[pid] for pid in home_mins if pid in player_ratings}
            away_ratings = {pid: player_ratings[pid] for pid in away_mins if pid in player_ratings}

            if not home_ratings or not away_ratings:
                skipped += 1
                continue

            sim = simulate_game(
                home_mins, away_mins,
                home_ratings, away_ratings,
                league_avg_ppp, league_avg_pace,
                n_simulations=n_simulations,
            )

            home_b2b = _detect_b2b(home_id, gdate, conn)
            away_b2b = _detect_b2b(away_id, gdate, conn)

            team_hca = beta_hca_by_team.get(home_id, beta_hca_fallback)
            predicted = apply_calibration(
                sim.mean_margin,
                alpha=alpha,
                beta_hca=team_hca,
                beta_b2b_home=beta_b2b_home,
                beta_b2b_away=beta_b2b_away,
                home_b2b=home_b2b,
                away_b2b=away_b2b,
            )

            error = predicted - actual
            results.append({
                "game_date": gdate,
                "game_id": gid,
                "home_team_id": home_id,
                "away_team_id": away_id,
                "predicted_spread": round(predicted, 2),
                "actual_margin": actual,
                "error": round(error, 2),
                "abs_error": round(abs(error), 2),
                "home_coverage": round(home_cov, 3),
                "away_coverage": round(away_cov, 3),
                "home_b2b": int(home_b2b),
                "away_b2b": int(away_b2b),
            })

    finally:
        conn.close()

    if not results:
        print("No results — check that there are scored games in the date range.")
        return []

    # --- Summary stats ---
    errors = [r["error"] for r in results]
    abs_errors = [r["abs_error"] for r in results]
    preds = [r["predicted_spread"] for r in results]
    actuals = [r["actual_margin"] for r in results]

    mae = sum(abs_errors) / len(abs_errors)
    rmse = math.sqrt(sum(e**2 for e in errors) / len(errors))
    bias = sum(errors) / len(errors)
    corr, _ = pearsonr(preds, actuals)
    # Direction accuracy: did we call the right winner?
    dir_correct = sum(1 for p, a in zip(preds, actuals) if (p > 0) == (a > 0))
    dir_acc = dir_correct / len(results)

    print(f"{'Game':<30} {'Pred':>6} {'Actual':>7} {'Error':>7} {'AbsErr':>7}  {'Cov H/A'}")
    print("-" * 80)
    for r in results:
        home_ab = _team_abbrev(r["home_team_id"])
        away_ab = _team_abbrev(r["away_team_id"])
        matchup = f"{away_ab} @ {home_ab} ({r['game_date']})"
        b2b_tag = ""
        if r["home_b2b"]:
            b2b_tag += f" {home_ab}B2B"
        if r["away_b2b"]:
            b2b_tag += f" {away_ab}B2B"
        print(
            f"{matchup:<30} {r['predicted_spread']:>+6.1f} {r['actual_margin']:>+7.0f}"
            f" {r['error']:>+7.1f} {r['abs_error']:>7.1f}"
            f"  {r['home_coverage']:.0%}/{r['away_coverage']:.0%}{b2b_tag}"
        )

    print()
    print("=" * 80)
    print(f"Games:        {len(results)}  (skipped {skipped})")
    print(f"MAE:          {mae:.2f} pts")
    print(f"RMSE:         {rmse:.2f} pts")
    print(f"Bias:         {bias:+.2f} pts (+ = predict home too favorably)")
    print(f"Correlation:  {corr:.3f}")
    print(f"Dir accuracy: {dir_acc:.1%}  ({dir_correct}/{len(results)} correct winner)")

    # Coverage breakdown — do injury-heavy games have higher errors?
    low_cov = [r for r in results if min(r["home_coverage"], r["away_coverage"]) < 0.9]
    high_cov = [r for r in results if min(r["home_coverage"], r["away_coverage"]) >= 0.9]
    if low_cov and high_cov:
        mae_low = sum(r["abs_error"] for r in low_cov) / len(low_cov)
        mae_high = sum(r["abs_error"] for r in high_cov) / len(high_cov)
        print(f"\nCoverage breakdown (< 90% min coverage = injury games):")
        print(f"  Low coverage  ({len(low_cov):>3} games): MAE = {mae_low:.2f} pts")
        print(f"  High coverage ({len(high_cov):>3} games): MAE = {mae_high:.2f} pts")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest prediction model on historical games")
    parser.add_argument("--start", type=str, default=None, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, default=None, help="End date YYYY-MM-DD")
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--season", default=INITIAL_SEASON)
    parser.add_argument("--sims", type=int, default=_N_SIMS)
    args = parser.parse_args()
    run_backtest(
        db_path=args.db,
        season=args.season,
        start_date=args.start,
        end_date=args.end,
        n_simulations=args.sims,
    )


if __name__ == "__main__":
    main()
