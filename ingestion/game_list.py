"""
P1: game_list — fetch all game IDs and metadata for a season.

Public API:
    get_season_game_ids(season)  -> list[str]
    get_season_games(season)     -> list[dict]  (includes metadata)
"""

import logging
import time
from typing import Optional

from config import INITIAL_SEASON, SEASON_TYPE

logger = logging.getLogger(__name__)

# nba_api date format is "MMM DD, YYYY" but GAME_DATE column is "YYYY-MM-DD"
# in LeagueGameLog. We normalise to "YYYY-MM-DD" everywhere.


def get_season_game_ids(season: str = INITIAL_SEASON) -> list[str]:
    """Return sorted list of all regular-season game IDs for *season*."""
    return [g["game_id"] for g in get_season_games(season)]


def get_season_games(season: str = INITIAL_SEASON) -> list[dict]:
    """
    Return a list of dicts — one per game — sorted by game_date then game_id.

    Each dict has:
        game_id, game_date (YYYY-MM-DD), home_team_id, away_team_id,
        home_score (int|None), away_score (int|None)

    Uses LeagueGameLog at the team level to avoid per-game API calls.
    Each game appears twice in the log (once per team); we merge both rows.
    """
    from nba_api.stats.endpoints import leaguegamelog  # lazy import

    logger.info("Fetching game list for season %s ...", season)
    time.sleep(1)  # brief pause before hitting stats.nba.com

    try:
        log = leaguegamelog.LeagueGameLog(
            season=season,
            season_type_all_star=SEASON_TYPE,
            player_or_team_abbreviation="T",  # team-level rows
            timeout=60,
        )
        df = log.get_data_frames()[0]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch game list for {season}: {e}") from e

    # Build {game_id: dict} merging both team rows per game
    games: dict[str, dict] = {}
    for _, row in df.iterrows():
        gid = str(row["GAME_ID"])
        matchup: str = str(row.get("MATCHUP", ""))
        team_id = str(int(row["TEAM_ID"]))
        pts = row.get("PTS")
        score = int(pts) if pts is not None and str(pts) != "nan" else None

        # Normalise game_date to YYYY-MM-DD
        raw_date = str(row.get("GAME_DATE", ""))
        game_date = _normalise_date(raw_date)

        if gid not in games:
            games[gid] = {
                "game_id": gid,
                "game_date": game_date,
                "home_team_id": None,
                "away_team_id": None,
                "home_score": None,
                "away_score": None,
            }

        # "vs." in MATCHUP → this team is the home team
        if " vs. " in matchup:
            games[gid]["home_team_id"] = team_id
            games[gid]["home_score"] = score
        else:
            games[gid]["away_team_id"] = team_id
            games[gid]["away_score"] = score

    # Sort chronologically, then by game_id for stability
    result = sorted(games.values(), key=lambda g: (g["game_date"] or "", g["game_id"]))
    logger.info("Found %d games for season %s", len(result), season)
    return result


def _normalise_date(raw: str) -> Optional[str]:
    """
    Accept multiple date formats and return "YYYY-MM-DD".
    nba_api LeagueGameLog typically returns "YYYY-MM-DD" already.
    """
    raw = raw.strip()
    if not raw or raw.lower() == "nan":
        return None

    # Already YYYY-MM-DD
    if len(raw) == 10 and raw[4] == "-":
        return raw

    # "MMM DD, YYYY" e.g. "OCT 22, 2024"
    import datetime
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    logger.warning("Could not parse date: %r", raw)
    return raw
