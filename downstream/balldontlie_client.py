"""Balldontlie API client for injury reports and player minute distributions.

Docs: https://docs.balldontlie.io/#nba-api
"""
import logging
import time
from datetime import date, timedelta
from statistics import mean, stdev
from typing import TypedDict

import requests

from config import BALLDONTLIE_API_KEY, MIN_GAMES_FOR_MINUTES, MINUTES_LOOKBACK_DAYS

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.balldontlie.io/v1"
_SLEEP_BETWEEN_PAGES = 0.3  # seconds — BDL rate limit is generous but be polite


def _headers(api_key: str) -> dict[str, str]:
    # BDL v1 accepts both bare key and Bearer prefix; try Bearer first.
    return {"Authorization": f"Bearer {api_key}"}


class InjuredPlayer(TypedDict):
    bdl_player_id: int
    player_name: str
    team_bdl_id: int
    status: str       # e.g. "Out", "Questionable", "Doubtful"
    return_date: str | None
    description: str | None


class MinutesData(TypedDict):
    bdl_player_id: int
    player_name: str
    team_bdl_id: int
    mean_minutes: float
    std_minutes: float
    n_games: int


def _paginate(url: str, params: dict, api_key: str) -> list[dict]:
    """Fetch all pages from a paginated BDL endpoint."""
    results = []
    cursor: int | None = None

    while True:
        if cursor is not None:
            params["cursor"] = cursor
        try:
            resp = requests.get(url, params=params, headers=_headers(api_key), timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("BDL request failed (%s): %s", url, exc)
            break

        body = resp.json()
        results.extend(body.get("data", []))

        meta = body.get("meta", {})
        next_cursor = meta.get("next_cursor")
        if next_cursor is None:
            break
        cursor = next_cursor
        time.sleep(_SLEEP_BETWEEN_PAGES)

    return results


def get_injury_report(api_key: str | None = None) -> list[InjuredPlayer]:
    """Fetch current NBA injury report from BDL.

    Returns all players currently listed as injured (any status).
    """
    key = api_key or BALLDONTLIE_API_KEY
    url = f"{_BASE_URL}/player_injuries"
    raw = _paginate(url, {"per_page": 100}, key)

    injuries: list[InjuredPlayer] = []
    for row in raw:
        player = row.get("player", {})
        team = row.get("team", {})
        injuries.append(
            InjuredPlayer(
                bdl_player_id=player.get("id", 0),
                player_name=f"{player.get('first_name', '')} {player.get('last_name', '')}".strip(),
                team_bdl_id=team.get("id", 0),
                status=row.get("status", ""),
                return_date=row.get("return_date"),
                description=row.get("description"),
            )
        )

    logger.info("BDL injury report: %d players listed", len(injuries))
    return injuries


def get_minutes_distribution(
    bdl_team_ids: list[int],
    lookback_days: int | None = None,
    api_key: str | None = None,
) -> dict[int, MinutesData]:
    """Fetch per-player minutes distribution for a list of BDL team IDs.

    Queries BDL /v1/stats for the last `lookback_days` days, computes
    mean and std of minutes played per player.

    Args:
        bdl_team_ids: list of BDL team IDs to query
        lookback_days: number of calendar days to look back (default: MINUTES_LOOKBACK_DAYS)
        api_key: override config key

    Returns:
        dict of bdl_player_id → MinutesData
    """
    key = api_key or BALLDONTLIE_API_KEY
    days = lookback_days or MINUTES_LOOKBACK_DAYS

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    url = f"{_BASE_URL}/stats"
    params: dict = {
        "per_page": 100,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    # Add team filters
    for bdl_id in bdl_team_ids:
        params.setdefault("team_ids[]", [])
        params["team_ids[]"] = bdl_team_ids  # BDL accepts repeated params

    raw = _paginate(url, params, key)

    # Group minutes by player
    player_minutes: dict[int, list[float]] = {}
    player_meta: dict[int, tuple[str, int]] = {}  # bdl_id → (name, team_bdl_id)

    for stat in raw:
        player = stat.get("player", {})
        team = stat.get("team", {})
        bdl_pid = player.get("id")
        if bdl_pid is None:
            continue

        mins_str = stat.get("min", "0:00") or "0:00"
        try:
            # BDL returns minutes as "MM:SS" string
            parts = mins_str.split(":")
            minutes_float = int(parts[0]) + int(parts[1]) / 60
        except (ValueError, IndexError):
            minutes_float = 0.0

        player_minutes.setdefault(bdl_pid, []).append(minutes_float)
        if bdl_pid not in player_meta:
            name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
            player_meta[bdl_pid] = (name, team.get("id", 0))

    result: dict[int, MinutesData] = {}
    for bdl_pid, mins_list in player_minutes.items():
        n = len(mins_list)
        if n < MIN_GAMES_FOR_MINUTES:
            continue
        name, team_bdl_id = player_meta[bdl_pid]
        std = stdev(mins_list) if n > 1 else 3.0
        result[bdl_pid] = MinutesData(
            bdl_player_id=bdl_pid,
            player_name=name,
            team_bdl_id=team_bdl_id,
            mean_minutes=mean(mins_list),
            std_minutes=std,
            n_games=n,
        )

    logger.info(
        "BDL minutes: %d players with >= %d games in last %d days",
        len(result), MIN_GAMES_FOR_MINUTES, days,
    )
    return result


def get_active_players_for_teams(
    bdl_team_ids: list[int],
    api_key: str | None = None,
) -> list[dict]:
    """Fetch active (rostered) players for a list of BDL team IDs.

    Returns raw BDL player dicts with keys: id, first_name, last_name, team.id, etc.
    """
    key = api_key or BALLDONTLIE_API_KEY
    url = f"{_BASE_URL}/players/active"
    params: dict = {"per_page": 100, "team_ids[]": bdl_team_ids}
    return _paginate(url, params, key)
