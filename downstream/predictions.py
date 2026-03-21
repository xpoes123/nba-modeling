"""Daily prediction script: compare our model's spreads/win probs to market lines.

Run after the nightly job, before the next game slate.

Usage:
    PYTHONPATH=. uv run python downstream/predictions.py [--date YYYY-MM-DD]

Default date: tomorrow (UTC).

Lineup/minutes source: our own DB (possession history — last 15 games per team).
Injury source: BDL (best-effort; skipped gracefully if unavailable or on free tier).
Odds source: Odds API.
"""
import argparse
import logging
import math
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, stdev

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    CALIBRATION_PATH,
    DB_PATH,
    INITIAL_SEASON,
    MONTE_CARLO_SIMULATIONS,
    NBA_TEAM_MAP,
    team_id_from_name,
)
from downstream.espn_client import get_nba_injuries, get_out_player_names
from downstream.calibration import load_calibration
from downstream.lineup_sampler import (
    MinutesProfile,
    apply_calibration,
    margin_to_win_prob,
    simulate_game,
)
from downstream.odds_client import GameOdds, get_nba_odds
from downstream.team_ratings import (
    PlayerRating,
    normalize_name,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Number of recent team games to use for possession-share estimation
_LINEUP_LOOKBACK_GAMES = 15


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

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
        raise ValueError(f"No league averages found for season {season}")
    return row["avg_ppp"], row["avg_pace"]


def _detect_b2b(team_id: str, game_date: date, conn: sqlite3.Connection) -> bool:
    """Return True if this team played yesterday."""
    prev = (game_date - timedelta(days=1)).isoformat()
    row = conn.execute(
        "SELECT 1 FROM games WHERE game_date = ? AND (home_team_id = ? OR away_team_id = ?) LIMIT 1",
        (prev, team_id, team_id),
    ).fetchone()
    return row is not None


def _upsert_prediction(conn: sqlite3.Connection, pred: dict) -> None:
    conn.execute(
        """
        INSERT INTO predictions (
            odds_event_id, game_date, home_team_id, away_team_id,
            home_team_name, away_team_name,
            predicted_spread, predicted_win_prob, sim_std,
            market_spread, market_win_prob, market_total,
            spread_edge, win_prob_edge,
            home_b2b, away_b2b, n_simulations
        ) VALUES (
            :odds_event_id, :game_date, :home_team_id, :away_team_id,
            :home_team_name, :away_team_name,
            :predicted_spread, :predicted_win_prob, :sim_std,
            :market_spread, :market_win_prob, :market_total,
            :spread_edge, :win_prob_edge,
            :home_b2b, :away_b2b, :n_simulations
        )
        ON CONFLICT(game_date, home_team_name, away_team_name) DO UPDATE SET
            predicted_spread   = excluded.predicted_spread,
            predicted_win_prob = excluded.predicted_win_prob,
            sim_std            = excluded.sim_std,
            market_spread      = excluded.market_spread,
            market_win_prob    = excluded.market_win_prob,
            market_total       = excluded.market_total,
            spread_edge        = excluded.spread_edge,
            win_prob_edge      = excluded.win_prob_edge,
            home_b2b           = excluded.home_b2b,
            away_b2b           = excluded.away_b2b,
            n_simulations      = excluded.n_simulations,
            created_at         = datetime('now')
        """,
        pred,
    )


# ---------------------------------------------------------------------------
# DB-based lineup / minutes estimation
# ---------------------------------------------------------------------------

def _get_team_possession_profiles(
    team_id: str,
    conn: sqlite3.Connection,
    n_games: int = _LINEUP_LOOKBACK_GAMES,
) -> dict[str, list[float]]:
    """Return player_id → [possession_share_game1, possession_share_game2, ...] for last n games.

    Possession share = fraction of the team's offensive possessions a player appeared in.
    """
    # Get the last n game IDs for this team (ordered newest first via games table)
    rows = conn.execute(
        """
        SELECT game_id
        FROM games
        WHERE home_team_id = ? OR away_team_id = ?
        ORDER BY game_date DESC
        LIMIT ?
        """,
        (team_id, team_id, n_games),
    ).fetchall()

    game_ids = [r["game_id"] for r in rows]
    if not game_ids:
        return {}

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
        return {}

    off_cols = ["off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5"]
    player_shares: dict[str, list[float]] = {}

    for game_id, game_df in poss_df.groupby("game_id"):
        n_poss = len(game_df)
        counts: dict[str, int] = {}
        for col in off_cols:
            for pid in game_df[col]:
                counts[pid] = counts.get(pid, 0) + 1
        for pid, cnt in counts.items():
            # Normalize: each player appears in 5 of every possession's player slots
            share = cnt / (n_poss * 5)
            player_shares.setdefault(pid, []).append(share)

    return player_shares


def _build_minutes_profile_from_db(
    team_id: str,
    conn: sqlite3.Connection,
    injured_names: set[str],
    player_id_to_name: dict[str, str],
    n_games: int = _LINEUP_LOOKBACK_GAMES,
    min_games: int = 3,
) -> MinutesProfile:
    """Build MinutesProfile from DB possession history.

    Converts possession shares → synthetic minutes (scaled to ~240 total team minutes
    per game = 5 players × 48 minutes).

    Args:
        team_id: nba.com team ID
        conn: DB connection
        injured_names: set of normalized player names to exclude
        player_id_to_name: player_id → player_name (for injury filtering)
        n_games: lookback window
        min_games: minimum appearances to include a player

    Returns:
        MinutesProfile: player_id → (mean_synthetic_minutes, std_synthetic_minutes)
    """
    profiles = _get_team_possession_profiles(team_id, conn, n_games)
    result: MinutesProfile = MinutesProfile()

    for pid, shares in profiles.items():
        if len(shares) < min_games:
            continue

        name = player_id_to_name.get(pid, "")
        if normalize_name(name) in injured_names:
            logger.debug("Skipping injured player: %s (%s)", name, pid)
            continue

        # Convert possession share → synthetic minutes
        # A player with 20% possession share plays ~20% of 240 team minutes = 48 min
        mean_share = mean(shares)
        std_share = stdev(shares) if len(shares) > 1 else 0.03

        # Scale to minutes (240 = 5 players × 48 min/game)
        mean_mins = mean_share * 240
        std_mins = std_share * 240

        result[pid] = (mean_mins, std_mins)

    logger.debug("Team %s: %d players in lineup profile", team_id, len(result))
    return result


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _abbrev(team_name: str) -> str:
    return next(
        (v["abbrev"] for v in NBA_TEAM_MAP.values() if v["name"] == team_name),
        team_name[:3].upper(),
    )


def _format_spread(spread: float, home_name: str, away_name: str) -> str:
    if spread >= 0:
        return f"{_abbrev(home_name)} -{spread:.1f}"
    return f"{_abbrev(away_name)} -{abs(spread):.1f}"


def _print_report(predictions: list[dict], target_date: date, injuries_available: bool) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\nNBA Predictions — {target_date}  (generated {now})")
    if not injuries_available:
        print("  [WARNING: injury data unavailable — predictions assume full rosters]")
    print("=" * 68)

    spread_edges: list[float] = []
    prob_edges: list[float] = []

    for p in predictions:
        home = p["home_team_name"]
        away = p["away_team_name"]
        our_spread = p["predicted_spread"]
        our_prob = p["predicted_win_prob"]
        mkt_spread = p["market_spread"]
        mkt_prob = p["market_win_prob"]
        mkt_total = p["market_total"]
        sim_std = p["sim_std"]

        notes = []
        if p["home_b2b"]:
            notes.append(f"{_abbrev(home)} B2B")
        if p["away_b2b"]:
            notes.append(f"{_abbrev(away)} B2B")

        our_spread_str = _format_spread(our_spread, home, away)
        mkt_spread_str = _format_spread(mkt_spread, home, away) if mkt_spread is not None else "N/A"
        spread_edge = p["spread_edge"]
        prob_edge = p["win_prob_edge"]
        edge_sign = "+" if spread_edge is not None and spread_edge > 0 else ""
        prob_sign = "+" if prob_edge is not None and prob_edge > 0 else ""

        print(f"\n{away} @ {home}")

        spread_line = f"  Spread   : Our {our_spread_str} ± {sim_std:.1f}"
        if mkt_spread is not None:
            spread_line += f"    Market: {mkt_spread_str}"
        if spread_edge is not None:
            spread_line += f"    Edge: {edge_sign}{spread_edge:.1f}"
        print(spread_line)

        home_ab = _abbrev(home)
        prob_line = f"  Win prob : Our {home_ab} {our_prob*100:.0f}%"
        if mkt_prob is not None:
            prob_line += f"          Market: {home_ab} {mkt_prob*100:.0f}%"
        if prob_edge is not None:
            prob_line += f"    Edge: {prob_sign}{prob_edge*100:.0f}pp"
        print(prob_line)

        if mkt_total is not None:
            print(f"  Total    : Market O/U {mkt_total:.1f}")
        print(f"  Notes    : {', '.join(notes) if notes else 'none'}")

        if spread_edge is not None:
            spread_edges.append(abs(spread_edge))
        if prob_edge is not None:
            prob_edges.append(abs(prob_edge))

    print("\n" + "=" * 68)
    parts = []
    if spread_edges:
        parts.append(f"Avg |spread edge|: {sum(spread_edges)/len(spread_edges):.1f} pts")
    if prob_edges:
        parts.append(f"Avg |win prob edge|: {sum(prob_edges)/len(prob_edges)*100:.1f}pp")
    if parts:
        print("  |  ".join(parts))
    print(f"{len(predictions)} predictions written to DB.\n")


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_predictions(
    target_date: date | None = None,
    db_path: str = DB_PATH,
    season: str = INITIAL_SEASON,
    n_simulations: int = MONTE_CARLO_SIMULATIONS,
) -> list[dict]:
    """Generate and store predictions for all NBA games on target_date."""
    if target_date is None:
        target_date = date.today() + timedelta(days=1)

    logger.info("Generating predictions for %s", target_date)

    # --- Load calibration coefficients ---
    try:
        coeffs = load_calibration(CALIBRATION_PATH)
    except FileNotFoundError:
        logger.error(
            "Calibration file not found. Run: PYTHONPATH=. uv run python downstream/calibration.py"
        )
        return []

    alpha = coeffs["alpha"]
    beta_hca = coeffs["beta_hca"]
    beta_b2b_home = coeffs["beta_b2b_home"]
    beta_b2b_away = coeffs["beta_b2b_away"]
    sigma_residual = coeffs["sigma_residual"]

    # --- Fetch market odds ---
    logger.info("Fetching Odds API lines for %s...", target_date)
    games_odds: list[GameOdds] = get_nba_odds(target_date=target_date)
    if not games_odds:
        logger.warning("No games found for %s in Odds API", target_date)
        return []
    logger.info("Found %d games in Odds API", len(games_odds))

    # --- Injury report from ESPN (public API, no auth required) ---
    injured_names: set[str] = set()
    injuries_available = False
    try:
        espn_injuries = get_nba_injuries()
        injured_names = get_out_player_names(espn_injuries)
        injuries_available = True
        logger.info("ESPN injury report: %d out/doubtful players excluded from lineups", len(injured_names))
    except Exception as exc:
        logger.warning("Injury report unavailable (%s) — proceeding with full rosters", exc)

    # --- Map team names from Odds API → nba.com IDs ---
    name_to_nba_id: dict[str, str] = {}
    for g in games_odds:
        for team_name in (g["home_team"], g["away_team"]):
            nba_id = team_id_from_name(team_name)
            if nba_id is None:
                logger.warning("Unknown Odds API team name: '%s'", team_name)
            else:
                name_to_nba_id[team_name] = nba_id

    # --- DB queries ---
    conn = _get_conn(db_path)
    try:
        player_ratings = _load_player_ratings(conn, season)
        league_avg_ppp, league_avg_pace = _load_league_avg(conn, season)

        # Build player_id → name for injury filtering
        player_id_to_name: dict[str, str] = {
            r["player_id"]: r["player_name"]
            for r in conn.execute("SELECT player_id, player_name FROM players").fetchall()
        }

        predictions: list[dict] = []

        for game in games_odds:
            home_name = game["home_team"]
            away_name = game["away_team"]

            home_nba_id = name_to_nba_id.get(home_name)
            away_nba_id = name_to_nba_id.get(away_name)

            if home_nba_id is None or away_nba_id is None:
                logger.warning("Skipping — unmapped team(s): %s @ %s", away_name, home_name)
                continue

            home_b2b = _detect_b2b(home_nba_id, target_date, conn)
            away_b2b = _detect_b2b(away_nba_id, target_date, conn)

            # Build lineup profiles from our DB possession history
            home_mins = _build_minutes_profile_from_db(
                home_nba_id, conn, injured_names, player_id_to_name
            )
            away_mins = _build_minutes_profile_from_db(
                away_nba_id, conn, injured_names, player_id_to_name
            )

            if not home_mins or not away_mins:
                logger.warning("Insufficient lineup data for %s @ %s", away_name, home_name)
                continue

            # Restrict to players with ratings in our model
            home_ratings = {pid: player_ratings[pid] for pid in home_mins if pid in player_ratings}
            away_ratings = {pid: player_ratings[pid] for pid in away_mins if pid in player_ratings}

            if not home_ratings or not away_ratings:
                logger.warning("No rated players found for %s @ %s", away_name, home_name)
                continue

            # Monte Carlo simulation
            sim = simulate_game(
                home_mins, away_mins,
                home_ratings, away_ratings,
                league_avg_ppp, league_avg_pace,
                n_simulations=n_simulations,
            )

            # Apply calibration to mean raw margin
            predicted_spread = apply_calibration(
                sim.mean_margin,
                alpha=alpha,
                beta_hca=beta_hca,
                beta_b2b_home=beta_b2b_home,
                beta_b2b_away=beta_b2b_away,
                home_b2b=home_b2b,
                away_b2b=away_b2b,
            )

            # Win probability: combine Monte Carlo σ with calibration residual σ
            total_sigma = math.sqrt(sim.std_margin ** 2 + sigma_residual ** 2)
            predicted_win_prob = margin_to_win_prob(predicted_spread, total_sigma)

            spread_edge = (
                predicted_spread - game["market_spread"]
                if game["market_spread"] is not None else None
            )
            win_prob_edge = (
                predicted_win_prob - game["market_win_prob"]
                if game["market_win_prob"] is not None else None
            )

            pred = {
                "odds_event_id": game["odds_event_id"],
                "game_date": game["game_date"],
                "home_team_id": home_nba_id,
                "away_team_id": away_nba_id,
                "home_team_name": home_name,
                "away_team_name": away_name,
                "predicted_spread": round(predicted_spread, 2),
                "predicted_win_prob": round(predicted_win_prob, 4),
                "sim_std": round(total_sigma, 2),  # total uncertainty (calibration + lineup)
                "market_spread": game["market_spread"],
                "market_win_prob": (
                    round(game["market_win_prob"], 4) if game["market_win_prob"] is not None else None
                ),
                "market_total": game["market_total"],
                "spread_edge": round(spread_edge, 2) if spread_edge is not None else None,
                "win_prob_edge": round(win_prob_edge, 4) if win_prob_edge is not None else None,
                "home_b2b": int(home_b2b),
                "away_b2b": int(away_b2b),
                "n_simulations": n_simulations,
            }
            predictions.append(pred)

        with conn:
            for pred in predictions:
                _upsert_prediction(conn, pred)

    finally:
        conn.close()

    _print_report(predictions, target_date, injuries_available)
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate NBA spread/win probability predictions")
    parser.add_argument("--date", type=date.fromisoformat, default=None,
                        help="Target date YYYY-MM-DD (default: tomorrow)")
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--season", default=INITIAL_SEASON)
    parser.add_argument("--sims", type=int, default=MONTE_CARLO_SIMULATIONS)
    args = parser.parse_args()
    run_predictions(target_date=args.date, db_path=args.db, season=args.season, n_simulations=args.sims)


if __name__ == "__main__":
    main()
