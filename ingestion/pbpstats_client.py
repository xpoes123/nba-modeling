"""
P1: pbpstats client — parse a single game into structured possession data.

parse_game(game_id) -> dict with keys:
  game_id, season, game_date, home_team_id, away_team_id,
  home_score, away_score, game_pace, players, possessions

players: {player_id_str: player_name}
possessions: list of dicts matching the `possessions` DB schema
"""

import os
import logging
from typing import Optional

from pbpstats.client import Client
from pbpstats.resources.enhanced_pbp import (
    FieldGoal,
    FreeThrow,
    Turnover,
    Rebound,
)

from config import DATA_DIR, INITIAL_SEASON

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_dirs() -> None:
    """Create cache subdirectories pbpstats expects."""
    for sub in ("pbp", "game_details", "overrides"):
        os.makedirs(os.path.join(DATA_DIR, sub), exist_ok=True)


def _pbp_cache_path(game_id: str) -> str:
    # live provider caches to pbp/live_{game_id}.json
    return os.path.join(DATA_DIR, "pbp", f"live_{game_id}.json")


def _boxscore_cache_path(game_id: str) -> str:
    return os.path.join(DATA_DIR, "game_details", f"stats_boxscore_{game_id}.json")


def _clock_to_seconds(clock: str) -> float:
    """
    Convert clock string to total seconds remaining in the period.

    Handles two formats:
      - "MM:SS"         (older pbpstats format)
      - "PT{M}M{S}.{ms}S"  (live data ISO 8601 format, e.g. "PT12M00.00S")
    """
    try:
        clock = clock.strip()
        if clock.startswith("PT"):
            # ISO 8601 duration: PT{M}M{S}.{ms}S
            clock = clock[2:]  # strip "PT"
            minutes = 0.0
            seconds = 0.0
            if "M" in clock:
                m_idx = clock.index("M")
                minutes = float(clock[:m_idx])
                clock = clock[m_idx + 1:]
            if clock.endswith("S"):
                clock = clock[:-1]
            if clock:
                seconds = float(clock)
            return minutes * 60 + seconds
        else:
            # MM:SS
            parts = clock.split(":")
            return float(parts[0]) * 60 + float(parts[1])
    except Exception:
        return 0.0


def _make_pbpstats_client(game_id: str) -> Client:
    """
    Build pbpstats Client using the 'live' S3 provider (most reliable in 2025).

    Background: stats.nba.com PlayByPlayV2 was deprecated in 2024-25 season
    (returns empty JSON). data.nba.com is unreliable. The live S3 endpoint at
    nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com is stable and public.
    """
    _ensure_dirs()
    pbp_source = "file" if os.path.exists(_pbp_cache_path(game_id)) else "web"
    settings = {
        "dir": DATA_DIR,
        "Possessions": {"source": pbp_source, "data_provider": "live"},
    }
    return Client(settings)


# ---------------------------------------------------------------------------
# Player name fetching (BoxScoreTraditionalV3, per-game)
# ---------------------------------------------------------------------------

def _fetch_game_meta(game_id: str) -> dict:
    """
    Fetch game metadata (date, home/away teams, scores) via nba_api LeagueGameFinder.
    Used as fallback when game_meta is not supplied to parse_game().

    Note: LeagueGameFinder ignores game_id_nullable on the server side; we filter locally.
    """
    try:
        import time
        from nba_api.stats.endpoints import leaguegamefinder
        from ingestion.game_list import _normalise_date
        time.sleep(0.6)
        finder = leaguegamefinder.LeagueGameFinder(
            game_id_nullable=game_id,
            timeout=60,
        )
        df = finder.get_data_frames()[0]
        if df.empty:
            return {}

        # Filter to only the rows for this specific game_id
        df = df[df["GAME_ID"] == game_id]
        if df.empty:
            return {}

        meta: dict = {}
        for _, row in df.iterrows():
            matchup = str(row.get("MATCHUP", ""))
            team_id = str(int(row["TEAM_ID"]))
            pts = row.get("PTS")
            score = int(pts) if pts is not None and str(pts) != "nan" else None
            raw_date = str(row.get("GAME_DATE", ""))
            meta["game_date"] = _normalise_date(raw_date)
            if " vs. " in matchup:
                meta["home_team_id"] = team_id
                meta["home_score"] = score
            else:
                meta["away_team_id"] = team_id
                meta["away_score"] = score
        return meta
    except Exception as e:
        logger.warning("Could not fetch game meta for %s: %s", game_id, e)
        return {}


def _fetch_player_names(game_id: str) -> dict[str, str]:
    """Return {player_id_str: player_name} for all players in this game."""
    try:
        from nba_api.stats.endpoints import boxscoretraditionalv3
        bs = boxscoretraditionalv3.BoxScoreTraditionalV3(
            game_id=game_id,
            timeout=60,
        )
        df = bs.player_stats.get_data_frame()
        result: dict[str, str] = {}
        for _, row in df.iterrows():
            pid = str(int(row["personId"]))
            full_name = f"{row['firstName']} {row['familyName']}".strip()
            result[pid] = full_name
        return result
    except Exception as e:
        logger.warning("Could not fetch player names for %s: %s", game_id, e)
        return {}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_game(game_id: str, game_meta: Optional[dict] = None) -> dict:
    """
    Parse a single game into structured possession data.

    Args:
        game_id:   NBA Stats game ID (e.g. "0022400001")
        game_meta: Optional pre-fetched metadata dict with keys
                   game_date, home_team_id, away_team_id, home_score, away_score.
                   If None, metadata is fetched via LeagueGameFinder (one extra API call).

    Returns:
        dict with game-level metadata and possessions list.
    """
    _ensure_dirs()

    # ------------------------------------------------------------------
    # 1. Load possessions via pbpstats
    # ------------------------------------------------------------------
    client = _make_pbpstats_client(game_id)
    pbp_game = client.Game(game_id)
    raw_possessions = pbp_game.possessions.items

    # ------------------------------------------------------------------
    # 2. Player names (optional — gracefully degrades if unavailable)
    # ------------------------------------------------------------------
    players: dict[str, str] = _fetch_player_names(game_id)

    # ------------------------------------------------------------------
    # 3. Parse each possession
    # ------------------------------------------------------------------
    possessions = []
    for poss_num, poss in enumerate(raw_possessions, start=1):
        try:
            poss_dict = _parse_possession(poss, poss_num)
            if poss_dict is not None:
                possessions.append(poss_dict)
        except Exception as e:
            logger.warning(
                "Skipping possession %d in game %s: %s", poss_num, game_id, e
            )
            continue

    # ------------------------------------------------------------------
    # 4. Derive season string from game_id (data_nba convention)
    # ------------------------------------------------------------------
    # Characters 3-4 of game_id encode the year start of the season.
    # "0022400001" → "24" → 2024 → "2024-25"
    yr = game_id[3:5]
    prefix = "19" if yr.startswith("9") else "20"
    yr_int = int(prefix + yr)
    season = f"{yr_int}-{str(yr_int + 1)[-2:]}"

    # ------------------------------------------------------------------
    # 5. Compute game pace from possession data
    # ------------------------------------------------------------------
    if possessions:
        max_period = max(p["period"] for p in possessions)
        total_game_seconds = 2880.0  # 48 min regulation
        if max_period > 4:
            total_game_seconds += (max_period - 4) * 300.0  # 5-min OT periods
        total_possessions = len(possessions)
        # pace = per-team possessions per 48 min
        # = (total_possessions / 2) / (total_game_seconds / 2880)
        game_pace = round(total_possessions * 2880.0 / (total_game_seconds * 2), 2)
    else:
        game_pace = None

    # ------------------------------------------------------------------
    # 6. Resolve game metadata (fetch if not provided)
    # ------------------------------------------------------------------
    meta = dict(game_meta) if game_meta else _fetch_game_meta(game_id)
    if "home_score" not in meta and possessions and "home_team_id" in meta:
        home_tid = meta["home_team_id"]
        away_tid = meta["away_team_id"]
        meta["home_score"] = sum(
            p["points_scored"] for p in possessions if p["offense_team_id"] == home_tid
        )
        meta["away_score"] = sum(
            p["points_scored"] for p in possessions if p["offense_team_id"] == away_tid
        )

    return {
        "game_id": game_id,
        "season": season,
        "game_date": meta.get("game_date"),
        "home_team_id": meta.get("home_team_id"),
        "away_team_id": meta.get("away_team_id"),
        "home_score": meta.get("home_score"),
        "away_score": meta.get("away_score"),
        "game_pace": game_pace,
        "players": players,
        "possessions": possessions,
    }


def _parse_possession(poss, poss_num: int) -> Optional[dict]:
    """
    Extract a single possession's data from a pbpstats Possession object.
    Returns None if the possession lacks valid lineup data.
    """
    if not poss.events:
        return None

    # Lineup data comes from the first event of the possession.
    # current_players: {team_id_int: [player_id_int, ...]}
    # lineup_ids:       {team_id_int: "p1-p2-p3-p4-p5"}
    first_event = poss.events[0]

    try:
        current_players = first_event.current_players  # {int: [int]}
        lineup_ids = first_event.lineup_ids             # {int: str}
    except Exception:
        return None

    if len(current_players) != 2:
        return None

    offense_team_id = str(poss.offense_team_id)
    team_ids = list(current_players.keys())
    defense_team_id_int = team_ids[0] if str(team_ids[1]) == offense_team_id else team_ids[1]
    defense_team_id = str(defense_team_id_int)
    offense_team_id_int = int(offense_team_id)

    # Validate 5-player lineups
    off_players = [str(p) for p in current_players.get(offense_team_id_int, [])]
    def_players = [str(p) for p in current_players.get(defense_team_id_int, [])]
    if len(off_players) != 5 or len(def_players) != 5:
        return None

    off_players_sorted = sorted(off_players)
    def_players_sorted = sorted(def_players)

    offense_lineup_id = lineup_ids.get(offense_team_id_int, "-".join(off_players_sorted))
    defense_lineup_id = lineup_ids.get(defense_team_id_int, "-".join(def_players_sorted))

    # Count possession stats from events
    points_scored = 0
    fg2a = fg2m = fg3a = fg3m = 0
    turnovers = 0
    offensive_rebounds = 0
    free_throw_points = 0

    for event in poss.events:
        try:
            ev_team = str(getattr(event, "team_id", None))
            if isinstance(event, FieldGoal):
                if ev_team == offense_team_id:
                    if event.shot_value == 2:
                        fg2a += 1
                        if event.is_made:
                            fg2m += 1
                            points_scored += 2
                    elif event.shot_value == 3:
                        fg3a += 1
                        if event.is_made:
                            fg3m += 1
                            points_scored += 3
            elif isinstance(event, FreeThrow):
                if ev_team == offense_team_id and event.is_made:
                    free_throw_points += 1
                    points_scored += 1
            elif isinstance(event, Turnover):
                if not event.is_no_turnover:
                    turnovers += 1
            elif isinstance(event, Rebound):
                if event.is_real_rebound and event.oreb:
                    offensive_rebounds += 1
        except Exception:
            continue

    # Time info
    try:
        start_time = poss.start_time  # "MM:SS"
        end_time = poss.end_time
    except Exception:
        start_time = end_time = None

    # Start type and score differential
    try:
        start_type = poss.possession_start_type
    except Exception:
        start_type = None

    try:
        start_score_differential = poss.start_score_margin
    except Exception:
        start_score_differential = None

    period = poss.period

    return {
        "period": period,
        "possession_number": poss_num,
        "offense_team_id": offense_team_id,
        "defense_team_id": defense_team_id,
        "points_scored": points_scored,
        "fg2a": fg2a,
        "fg2m": fg2m,
        "fg3a": fg3a,
        "fg3m": fg3m,
        "turnovers": turnovers,
        "offensive_rebounds": offensive_rebounds,
        "free_throw_points": free_throw_points,
        "start_time": start_time,
        "end_time": end_time,
        "start_type": start_type,
        "start_score_differential": start_score_differential,
        "offense_lineup_id": offense_lineup_id,
        "defense_lineup_id": defense_lineup_id,
        "off_player_1": off_players_sorted[0],
        "off_player_2": off_players_sorted[1],
        "off_player_3": off_players_sorted[2],
        "off_player_4": off_players_sorted[3],
        "off_player_5": off_players_sorted[4],
        "def_player_1": def_players_sorted[0],
        "def_player_2": def_players_sorted[1],
        "def_player_3": def_players_sorted[2],
        "def_player_4": def_players_sorted[3],
        "def_player_5": def_players_sorted[4],
    }
