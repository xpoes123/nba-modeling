"""
P5: Incremental daily ingestion — fetch and ETL games played since last DB update.

Public API:
    get_new_game_ids(db_path, season)  -> list[str]
    ingest_new_games(db_path, season)  -> int

Difference from backfill.py: only fetches games not yet in the games table,
rather than the entire season. Safe to call daily (idempotent).
"""

import logging
import sqlite3
import time

from config import BACKFILL_SLEEP_SECONDS
from ingestion.game_list import get_season_games
from ingestion.pbpstats_client import parse_game
from ingestion.etl import insert_game

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_ingested_ids(db_path: str, season: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT game_id FROM games WHERE season = ?", (season,)
        ).fetchall()
        return {r[0] for r in rows}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_new_game_ids(db_path: str, season: str) -> list[str]:
    """
    Return game IDs from the season schedule that are not yet in the games table.

    Makes one nba_api call to fetch the full season schedule, then filters
    against the already-ingested set from the DB.
    """
    ingested = _get_ingested_ids(db_path, season)
    all_games = get_season_games(season)
    new_ids = [g["game_id"] for g in all_games if g["game_id"] not in ingested]
    logger.info(
        "Season schedule: %d games total, %d already ingested, %d new",
        len(all_games), len(ingested), len(new_ids),
    )
    return new_ids


def ingest_new_games(db_path: str, season: str) -> int:
    """
    Parse and ETL all games in the season schedule not yet in the DB.

    Rate-limited between games (BACKFILL_SLEEP_SECONDS). Gracefully handles
    per-game failures — logs and continues.

    Returns:
        Count of successfully ingested games.
    """
    ingested = _get_ingested_ids(db_path, season)
    all_games = get_season_games(season)
    pending = [g for g in all_games if g["game_id"] not in ingested]

    if not pending:
        logger.info("No new games to ingest.")
        return 0

    logger.info("Ingesting %d new game(s)...", len(pending))
    success = 0
    failures: list[str] = []

    for idx, game_meta in enumerate(pending, start=1):
        game_id = game_meta["game_id"]
        try:
            parsed = parse_game(game_id, game_meta=game_meta)
            insert_game(db_path, parsed)

            n_poss = len(parsed["possessions"])
            logger.info(
                "[%d/%d] %s %s — %s vs %s — %d possessions",
                idx, len(pending),
                game_id,
                game_meta.get("game_date", ""),
                game_meta.get("home_team_id", "?"),
                game_meta.get("away_team_id", "?"),
                n_poss,
            )
            success += 1

        except Exception as e:
            logger.error("[%d/%d] %s FAILED: %s", idx, len(pending), game_id, e)
            failures.append(game_id)

        # Rate limiting — mandatory, do not remove
        if idx < len(pending):
            time.sleep(BACKFILL_SLEEP_SECONDS)

    if failures:
        logger.warning(
            "Failed to ingest %d game(s): %s", len(failures), failures
        )

    logger.info("Ingested %d new game(s) successfully.", success)
    return success
