"""
P3: Backfill script — ingest the full 2025-26 season into SQLite.

Usage:
    python ingestion/backfill.py

Features:
  - Fetches all game IDs + metadata from nba_api in one batch call
  - Skips games already in the `games` table (idempotent / resumable)
  - Rate-limits to BACKFILL_SLEEP_SECONDS between games
  - Logs one line per game: [N/Total] game_id date home vs away — N possessions
  - Gracefully handles per-game failures; continues to next game
  - Computes league averages after all games are ingested
"""

import logging
import sqlite3
import sys
import time
from datetime import datetime

from config import DB_PATH, INITIAL_SEASON, BACKFILL_SLEEP_SECONDS
from ingestion.game_list import get_season_games
from ingestion.pbpstats_client import parse_game
from ingestion.etl import insert_game

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# League averages
# ---------------------------------------------------------------------------

def compute_and_insert_league_averages(db_path: str, season: str) -> None:
    """
    Compute season-level PPP and pace from stints/games tables and upsert
    into league_averages.
    """
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            """
            SELECT
                CAST(SUM(points_scored) AS REAL) / NULLIF(SUM(possessions), 0) AS avg_ppp,
                SUM(possessions) AS total_possessions
            FROM stints
            WHERE season = ?
            """,
            (season,),
        ).fetchone()

        if not row or row[0] is None:
            logger.warning("No stint data found for season %s — skipping league averages.", season)
            return

        avg_ppp = row[0]
        total_possessions = row[1]

        # avg_pace = average per-team possessions per 48 min across all games
        pace_row = conn.execute(
            "SELECT AVG(game_pace) FROM games WHERE season = ? AND game_pace IS NOT NULL",
            (season,),
        ).fetchone()
        avg_pace = pace_row[0] if pace_row and pace_row[0] else 0.0

        with conn:
            conn.execute(
                """
                INSERT INTO league_averages (season, avg_ppp, avg_pace, total_possessions)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(season) DO UPDATE SET
                    avg_ppp           = excluded.avg_ppp,
                    avg_pace          = excluded.avg_pace,
                    total_possessions = excluded.total_possessions,
                    computed_at       = datetime('now')
                """,
                (season, avg_ppp, avg_pace, total_possessions),
            )

        logger.info(
            "League averages: avg_ppp=%.4f avg_pace=%.1f total_possessions=%d",
            avg_ppp, avg_pace, total_possessions,
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Already-ingested game set (for fast skip check)
# ---------------------------------------------------------------------------

def _get_ingested_games(db_path: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT game_id FROM games").fetchall()
        return {r[0] for r in rows}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Main backfill loop
# ---------------------------------------------------------------------------

def run_backfill(season: str = INITIAL_SEASON) -> None:
    start_time = datetime.now()
    logger.info("=== Starting backfill for %s ===", season)

    # 1. Fetch game list + metadata (one batch API call)
    logger.info("Fetching game list...")
    games = get_season_games(season)
    total = len(games)
    logger.info("Found %d games for %s", total, season)

    # 2. Filter already-ingested
    ingested = _get_ingested_games(DB_PATH)
    pending = [g for g in games if g["game_id"] not in ingested]
    logger.info(
        "Already ingested: %d | Remaining: %d", len(ingested), len(pending)
    )

    if not pending:
        logger.info("All games already ingested. Running league averages...")
        compute_and_insert_league_averages(DB_PATH, season)
        return

    # 3. Ingest loop
    success = 0
    failures: list[str] = []

    for idx, game_meta in enumerate(pending, start=1):
        game_id = game_meta["game_id"]
        global_pos = games.index(game_meta) + 1

        try:
            parsed = parse_game(game_id, game_meta=game_meta)
            insert_game(DB_PATH, parsed)

            n_poss = len(parsed["possessions"])
            conn = sqlite3.connect(DB_PATH)
            n_stints = conn.execute(
                "SELECT COUNT(*) FROM stints WHERE game_id=?", (game_id,)
            ).fetchone()[0]
            conn.close()

            logger.info(
                "[%d/%d] %s %s — %s vs %s — %d possessions, %d stints",
                global_pos, total, game_id,
                game_meta.get("game_date", ""),
                game_meta.get("home_team_id", "?"),
                game_meta.get("away_team_id", "?"),
                n_poss, n_stints,
            )
            success += 1

        except Exception as e:
            logger.error("[%d/%d] %s FAILED: %s", global_pos, total, game_id, e)
            failures.append(game_id)

        # Rate limiting — mandatory, do not remove
        if idx < len(pending):
            time.sleep(BACKFILL_SLEEP_SECONDS)

    # 4. League averages
    logger.info("Computing league averages...")
    compute_and_insert_league_averages(DB_PATH, season)

    # 5. Summary
    elapsed = datetime.now() - start_time
    logger.info(
        "=== Backfill complete: %d succeeded, %d failed, elapsed %s ===",
        success, len(failures), str(elapsed).split(".")[0],
    )
    if failures:
        logger.warning("Failed games: %s", failures)
        sys.exit(1)


if __name__ == "__main__":
    run_backfill()
