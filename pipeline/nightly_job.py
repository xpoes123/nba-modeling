"""
P5: Nightly job — ingest new games, refit rolling RAPM, update current_ratings.

Usage:
    PYTHONPATH=<project_root> uv run python pipeline/nightly_job.py

Logs to stdout. When invoked via scripts/run_nightly.bat, stdout is redirected
to logs/nightly_YYYY-MM-DD.log automatically.

Rolling window design:
  - For each player, find their last ROLLING_WINDOW_GAMES game dates.
  - The "union window" spans from the earliest of those starts to today.
  - Stints in that date range are used to fit a fresh Ridge regression.
  - Results overwrite current_ratings with phase='rapm_rolling'.
"""

import logging
import sqlite3
import sys
from collections import defaultdict
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

import config
from ingestion.backfill import compute_and_insert_league_averages
from ingestion.ingest_daily import ingest_new_games
from models.composite import update_current_ratings
from models.elo import replay_game_elo
from models.rapm import build_design_matrix, build_player_index, fit_rapm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Connection helper (mirrors phase1_full_season.py)
# ---------------------------------------------------------------------------

def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Rolling window helpers (DB reads only)
# ---------------------------------------------------------------------------

def _compute_union_window(
    conn: sqlite3.Connection,
    season: str,
    as_of_date: str,
    window_size: int,
) -> str:
    """
    Determine the rolling window start date.

    Strategy (one pass, no per-player queries):
      1. Load all (game_date, offense_lineup_id, defense_lineup_id) from stints
         for this season, up to as_of_date.
      2. Build player_id -> sorted list[game_date] mapping in Python.
      3. For each player in current_ratings, find their Nth-to-last game date.
      4. union_start = min across all players.

    Returns:
        window_start_date (YYYY-MM-DD string).
    """
    # Lightweight load — 3 columns, ~55K rows
    stint_meta = pd.read_sql(
        """
        SELECT game_date, offense_lineup_id, defense_lineup_id
        FROM stints
        WHERE season = ? AND game_date <= ?
        ORDER BY game_date
        """,
        conn,
        params=(season, as_of_date),
    )

    if stint_meta.empty:
        raise ValueError(f"No stints for season '{season}' up to {as_of_date}.")

    # Build player -> sorted list of game dates they appeared in
    player_dates: dict[str, list[str]] = defaultdict(list)
    prev_date: dict[str, str] = {}  # deduplicate consecutive same dates

    for _, row in stint_meta.iterrows():
        game_date = row["game_date"]
        for pid in row["offense_lineup_id"].split("-"):
            if prev_date.get(pid) != game_date:
                player_dates[pid].append(game_date)
                prev_date[pid] = game_date
        for pid in row["defense_lineup_id"].split("-"):
            if prev_date.get(pid) != game_date:
                player_dates[pid].append(game_date)
                prev_date[pid] = game_date

    # Rated players define the population
    rated_ids = [
        r[0]
        for r in conn.execute(
            "SELECT player_id FROM current_ratings WHERE season = ?", (season,)
        ).fetchall()
    ]
    if not rated_ids:
        raise ValueError(f"No players in current_ratings for season '{season}'.")

    window_starts: list[str] = []
    for pid in rated_ids:
        dates = player_dates.get(pid, [])
        if len(dates) >= window_size:
            # Nth-to-last game date (0-indexed from end)
            window_starts.append(dates[-(window_size)])
        elif dates:
            window_starts.append(dates[0])
        else:
            # Player not in any stint — use as_of_date (will get no stints)
            window_starts.append(as_of_date)

    union_start = min(window_starts)
    logger.info(
        "Rolling window: %s → %s (union across %d players)",
        union_start, as_of_date, len(rated_ids),
    )
    return union_start


def _load_rolling_stints(
    conn: sqlite3.Connection,
    season: str,
    window_start: str,
    as_of_date: str,
) -> pd.DataFrame:
    """Load all stints in the rolling window date range."""
    stints = pd.read_sql(
        """
        SELECT *
        FROM stints
        WHERE season = ?
          AND game_date >= ?
          AND game_date <= ?
        """,
        conn,
        params=(season, window_start, as_of_date),
    )
    logger.info("Loaded %d stints in rolling window.", len(stints))
    return stints


# ---------------------------------------------------------------------------
# Rolling RAPM orchestrator
# ---------------------------------------------------------------------------

def run_rolling_rapm(
    db_path: str,
    season: str,
    as_of_date: str,
    alpha: float = config.RIDGE_ALPHA,
    window_size: int = config.ROLLING_WINDOW_GAMES,
) -> dict:
    """
    Fit rolling-window RAPM and write results to rapm_ratings + current_ratings.

    Inserts a new rapm_ratings snapshot for today's window, then upserts
    current_ratings with phase='rapm_rolling'.

    Args:
        db_path:     Path to SQLite database.
        season:      Season string, e.g. '2025-26'.
        as_of_date:  Window end date (YYYY-MM-DD), typically today.
        alpha:       Ridge regularization strength.
        window_size: Number of games per player to look back.

    Returns:
        Summary dict with n_players, window dates, and distribution stats.
    """
    conn = _get_conn(db_path)
    try:
        # 1. League averages
        row = conn.execute(
            "SELECT avg_ppp, avg_pace FROM league_averages WHERE season = ?",
            (season,),
        ).fetchone()
        if row is None:
            raise ValueError(
                f"No league_averages for season '{season}'. Run backfill first."
            )
        avg_ppp, avg_pace = row
        logger.info("League averages: avg_ppp=%.4f, avg_pace=%.2f", avg_ppp, avg_pace)

        # 2. Determine union window, load stints
        window_start = _compute_union_window(conn, season, as_of_date, window_size)
        stints = _load_rolling_stints(conn, season, window_start, as_of_date)

        if stints.empty:
            raise ValueError(
                f"No stints in rolling window {window_start} → {as_of_date}."
            )

        # 3. Build player index + design matrix (reuse pure functions from models/rapm.py)
        player_index = build_player_index(stints)
        player_ids = sorted(player_index.keys(), key=lambda pid: player_index[pid])
        n_players = len(player_ids)
        X = build_design_matrix(stints, player_index)
        possessions = stints["possessions"].values.astype(float)
        logger.info("Rolling RAPM: %d players, %d stints", n_players, len(stints))

        # 4. Offense + defense targets (pts per 100 possessions above league avg)
        y_offense = (stints["points_scored"].values / possessions - avg_ppp) * 100.0
        y_defense = (stints["points_allowed"].values / possessions - avg_ppp) * 100.0

        # 5. Fit offense and defense regressions
        logger.info("Fitting rolling offense regression (alpha=%.0f)...", alpha)
        offense_coefs = fit_rapm(X, y_offense, possessions, alpha)

        logger.info("Fitting rolling defense regression (alpha=%.0f)...", alpha)
        defense_coefs = fit_rapm(X, y_defense, possessions, alpha)

        # 6. Pace regression — exclude stints with seconds_played = 0
        pace_mask = stints["seconds_played"] > 0
        n_excluded = int((~pace_mask).sum())
        if n_excluded:
            logger.warning("Excluding %d stints with seconds_played=0 from pace regression.", n_excluded)
        stints_pace = stints[pace_mask].reset_index(drop=True)
        X_pace = build_design_matrix(stints_pace, player_index)
        poss_pace = stints_pace["possessions"].values.astype(float)
        y_pace = (
            stints_pace["possessions"].values / stints_pace["seconds_played"].values * 2880
            - avg_pace
        )
        logger.info("Fitting rolling pace regression (%d stints)...", len(stints_pace))
        pace_coefs = fit_rapm(X_pace, y_pace, poss_pace, alpha)

        # 7. Write results atomically
        logger.info("Writing rolling RAPM results to database...")
        with conn:
            conn.executemany(
                """
                INSERT INTO rapm_ratings
                    (player_id, season, phase, window_start_date, window_end_date,
                     offense, defense, pace, computed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(player_id, season, phase, window_end_date) DO UPDATE SET
                    window_start_date = excluded.window_start_date,
                    offense           = excluded.offense,
                    defense           = excluded.defense,
                    pace              = excluded.pace,
                    computed_at       = datetime('now')
                """,
                [
                    (
                        player_ids[i], season, "rapm_rolling",
                        window_start, as_of_date,
                        float(offense_coefs[i]),
                        float(defense_coefs[i]),
                        float(pace_coefs[i]),
                    )
                    for i in range(n_players)
                ],
            )

            conn.executemany(
                """
                INSERT INTO current_ratings
                    (player_id, season, offense, defense, pace, overall, phase)
                VALUES (?, ?, ?, ?, ?, ?, 'rapm_rolling')
                ON CONFLICT(player_id) DO UPDATE SET
                    season     = excluded.season,
                    offense    = excluded.offense,
                    defense    = excluded.defense,
                    pace       = excluded.pace,
                    overall    = excluded.overall,
                    phase      = excluded.phase,
                    updated_at = datetime('now')
                """,
                [
                    (
                        player_ids[i], season,
                        float(offense_coefs[i]),
                        float(defense_coefs[i]),
                        float(pace_coefs[i]),
                        float(offense_coefs[i]) - float(defense_coefs[i]),
                    )
                    for i in range(n_players)
                ],
            )

        logger.info(
            "Rolling RAPM done: %d players, window %s → %s",
            n_players, window_start, as_of_date,
        )
        return {
            "n_players": n_players,
            "window_start_date": window_start,
            "window_end_date": as_of_date,
            "offense_mean": float(offense_coefs.mean()),
            "offense_std": float(offense_coefs.std()),
            "defense_mean": float(defense_coefs.mean()),
            "defense_std": float(defense_coefs.std()),
        }

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Elo state helpers (DB reads/writes; pure logic lives in models/elo.py)
# ---------------------------------------------------------------------------

def _load_elo_state(conn: sqlite3.Connection, season: str) -> dict:
    """
    Load current Elo state from DB.

    Combines:
      - Latest rapm_rolling ratings per player (as RAPM base)
      - Latest elo_ratings row per player (as cumulative deltas)

    Falls back to all deltas = 0 if no elo_ratings rows exist yet.

    Returns:
        current_elos dict: player_id -> {rapm_offense, rapm_defense, rapm_pace,
                                          offense_delta, defense_delta, pace_delta}
    """
    rapm_rows = conn.execute(
        """
        SELECT r.player_id, r.offense, r.defense, r.pace
        FROM rapm_ratings r
        INNER JOIN (
            SELECT player_id, MAX(window_end_date) AS latest
            FROM rapm_ratings
            WHERE season = ? AND phase = 'rapm_rolling'
            GROUP BY player_id
        ) sub ON r.player_id = sub.player_id
              AND r.window_end_date = sub.latest
        WHERE r.season = ? AND r.phase = 'rapm_rolling'
        """,
        (season, season),
    ).fetchall()

    current_elos: dict = {}
    for player_id, rapm_off, rapm_def, rapm_pace in rapm_rows:
        current_elos[player_id] = {
            "rapm_offense": rapm_off,
            "rapm_defense": rapm_def,
            "rapm_pace": rapm_pace,
            "offense_delta": 0.0,
            "defense_delta": 0.0,
            "pace_delta": 0.0,
        }

    # Overlay latest cumulative Elo deltas
    elo_rows = conn.execute(
        """
        SELECT e.player_id, e.offense_delta, e.defense_delta, e.pace_delta
        FROM elo_ratings e
        INNER JOIN (
            SELECT player_id, MAX(updated_at) AS latest
            FROM elo_ratings
            WHERE season = ?
            GROUP BY player_id
        ) sub ON e.player_id = sub.player_id
              AND e.updated_at = sub.latest
        WHERE e.season = ?
        """,
        (season, season),
    ).fetchall()

    for player_id, off_d, def_d, pace_d in elo_rows:
        if player_id in current_elos:
            current_elos[player_id]["offense_delta"] = off_d
            current_elos[player_id]["defense_delta"] = def_d
            current_elos[player_id]["pace_delta"] = pace_d
        else:
            # Has Elo data but no current RAPM (e.g. traded, cut): cold-start RAPM base
            current_elos[player_id] = {
                "rapm_offense": 0.0,
                "rapm_defense": 0.0,
                "rapm_pace": 0.0,
                "offense_delta": off_d,
                "defense_delta": def_d,
                "pace_delta": pace_d,
            }

    return current_elos


def _get_unreplayed_game_ids(conn: sqlite3.Connection, season: str) -> list[str]:
    """
    Return game IDs that have possessions in the DB but no elo_ratings entries yet.
    Ordered chronologically so cumulative deltas build up correctly.
    """
    rows = conn.execute(
        """
        SELECT DISTINCT g.game_id
        FROM games g
        WHERE g.season = ?
          AND EXISTS (
              SELECT 1 FROM possessions p WHERE p.game_id = g.game_id
          )
          AND NOT EXISTS (
              SELECT 1 FROM elo_ratings e WHERE e.game_id = g.game_id
          )
        ORDER BY g.game_date
        """,
        (season,),
    ).fetchall()
    return [r[0] for r in rows]


def _load_game_possessions(conn: sqlite3.Connection, game_id: str) -> list[dict]:
    """Load all possessions for a game in chronological order (by possession_number)."""
    rows = conn.execute(
        """
        SELECT off_player_1, off_player_2, off_player_3, off_player_4, off_player_5,
               def_player_1, def_player_2, def_player_3, def_player_4, def_player_5,
               points_scored
        FROM possessions
        WHERE game_id = ?
        ORDER BY possession_number
        """,
        (game_id,),
    ).fetchall()
    cols = [
        "off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5",
        "def_player_1", "def_player_2", "def_player_3", "def_player_4", "def_player_5",
        "points_scored",
    ]
    return [dict(zip(cols, row)) for row in rows]


def _upsert_elo_ratings(
    conn: sqlite3.Connection,
    game_id: str,
    season: str,
    appeared: set[str],
    current_elos: dict,
) -> None:
    """Write cumulative Elo deltas for all players who appeared in this game."""
    conn.executemany(
        """
        INSERT INTO elo_ratings
            (player_id, season, game_id, offense_delta, defense_delta, pace_delta)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(player_id, game_id) DO UPDATE SET
            offense_delta = excluded.offense_delta,
            defense_delta = excluded.defense_delta,
            pace_delta    = excluded.pace_delta,
            updated_at    = datetime('now')
        """,
        [
            (
                pid, season, game_id,
                current_elos[pid]["offense_delta"],
                current_elos[pid]["defense_delta"],
                current_elos[pid]["pace_delta"],
            )
            for pid in appeared
            if pid in current_elos
        ],
    )


# ---------------------------------------------------------------------------
# Elo replay orchestrator
# ---------------------------------------------------------------------------

def run_elo_replay(db_path: str, season: str) -> dict:
    """
    Load Elo state, replay all un-replayed games, persist cumulative deltas.

    Finds games that have possessions in the DB but no elo_ratings rows yet,
    replays them chronologically, and upserts cumulative deltas after each game.

    Args:
        db_path: Path to SQLite database.
        season:  Season string, e.g. '2025-26'.

    Returns:
        Summary dict with n_games replayed and n_players with Elo state.
    """
    conn = _get_conn(db_path)
    try:
        row = conn.execute(
            "SELECT avg_ppp, avg_pace FROM league_averages WHERE season = ?", (season,)
        ).fetchone()
        if row is None:
            raise ValueError(f"No league_averages for season '{season}'.")
        avg_ppp, avg_pace = row

        current_elos = _load_elo_state(conn, season)
        logger.info("Loaded Elo state for %d players.", len(current_elos))

        unreplayed = _get_unreplayed_game_ids(conn, season)
        logger.info("Found %d game(s) to replay via Elo.", len(unreplayed))

        if not unreplayed:
            logger.info("No new games to replay — Elo state is current.")
            return {"n_games": 0, "n_players": len(current_elos)}

        games_replayed = 0
        for game_id in unreplayed:
            game_row = conn.execute(
                "SELECT game_pace FROM games WHERE game_id = ?", (game_id,)
            ).fetchone()
            game_pace = game_row[0] if game_row else None

            possessions = _load_game_possessions(conn, game_id)
            if not possessions:
                logger.warning("Game %s has no possessions, skipping Elo replay.", game_id)
                continue

            appeared = replay_game_elo(
                possessions, current_elos,
                league_avg_ppp=avg_ppp,
                league_avg_pace=avg_pace,
                game_pace=game_pace,
                K=config.ELO_K_OFFENSE_DEFENSE,
                K_pace=config.ELO_K_PACE,
            )

            with conn:
                _upsert_elo_ratings(conn, game_id, season, appeared, current_elos)

            games_replayed += 1

        logger.info(
            "Elo replay done: %d game(s) replayed, %d players with Elo state.",
            games_replayed, len(current_elos),
        )
        return {"n_games": games_replayed, "n_players": len(current_elos)}

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    today = date.today().isoformat()
    logger.info("=== Nightly job start: %s ===", today)

    # 1. Ingest new games since last run
    n_ingested = ingest_new_games(config.DB_PATH, config.INITIAL_SEASON)
    logger.info("Ingested %d new game(s).", n_ingested)

    # 2. Recompute league averages (upserts — safe even if nothing changed)
    compute_and_insert_league_averages(config.DB_PATH, config.INITIAL_SEASON)

    # 3. Refit rolling RAPM as of today
    result = run_rolling_rapm(
        config.DB_PATH,
        config.INITIAL_SEASON,
        as_of_date=today,
    )

    # 4. Replay new games via Elo (cumulative deltas on top of RAPM base)
    result_elo = run_elo_replay(config.DB_PATH, config.INITIAL_SEASON)
    logger.info("Elo replay: %d game(s) replayed.", result_elo["n_games"])

    # 5. Update composite ratings (RAPM base + Elo delta → current_ratings phase='elo')
    update_current_ratings(config.DB_PATH, config.INITIAL_SEASON)
    logger.info("Composite ratings updated (phase='elo').")

    # 6. Summary
    conn = sqlite3.connect(config.DB_PATH)
    n_rated = conn.execute("SELECT COUNT(*) FROM current_ratings").fetchone()[0]
    conn.close()

    logger.info(
        "=== Done: %d players rated, window %s → %s ===",
        n_rated,
        result["window_start_date"],
        result["window_end_date"],
    )


if __name__ == "__main__":
    main()
