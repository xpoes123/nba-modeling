"""ESPN public API client (no auth required).

Injury endpoint: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries
Roster endpoint: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{id}/roster
"""
import logging
from typing import TypedDict

import requests

from downstream.team_ratings import normalize_name

logger = logging.getLogger(__name__)

_ESPN_INJURIES_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
_ESPN_ROSTER_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{}/roster"

# Statuses we consider a player definitively unavailable
OUT_STATUSES = {"out", "doubtful", "suspension", "suspended", "gtd-out"}

# Statuses we consider probable (reduce expected minutes but don't fully exclude)
QUESTIONABLE_STATUSES = {"questionable", "day-to-day", "probable"}


class EspnInjury(TypedDict):
    player_name: str
    normalized_name: str
    team_name: str
    status: str       # original ESPN status string
    is_out: bool      # True if definitively unavailable (Out / Doubtful / Suspension)
    is_questionable: bool  # True if uncertain (Day-To-Day / Questionable)
    short_comment: str


def get_nba_injuries() -> list[EspnInjury]:
    """Fetch current NBA injury report from ESPN public API.

    Returns all players with any injury status. Callers can filter by
    is_out or is_questionable as needed.
    """
    try:
        resp = requests.get(_ESPN_INJURIES_URL, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("ESPN injury API request failed: %s", exc)
        return []

    result: list[EspnInjury] = []
    for team_entry in resp.json().get("injuries", []):
        team_name = team_entry.get("displayName", "Unknown")
        for inj in team_entry.get("injuries", []):
            athlete = inj.get("athlete", {})
            first = athlete.get("firstName", "")
            last = athlete.get("lastName", "")
            full_name = f"{first} {last}".strip()
            if not full_name:
                continue

            raw_status = inj.get("status", "").strip()
            status_lower = raw_status.lower()

            is_out = any(s in status_lower for s in OUT_STATUSES)
            is_questionable = any(s in status_lower for s in QUESTIONABLE_STATUSES)

            result.append(
                EspnInjury(
                    player_name=full_name,
                    normalized_name=normalize_name(full_name),
                    team_name=team_name,
                    status=raw_status,
                    is_out=is_out,
                    is_questionable=is_questionable,
                    short_comment=inj.get("shortComment", ""),
                )
            )

    n_out = sum(1 for i in result if i["is_out"])
    n_q = sum(1 for i in result if i["is_questionable"])
    logger.info("ESPN injuries: %d out/doubtful, %d questionable/day-to-day", n_out, n_q)
    return result


def get_out_player_names(injuries: list[EspnInjury] | None = None) -> set[str]:
    """Return set of normalized names for players who are definitively out."""
    if injuries is None:
        injuries = get_nba_injuries()
    return {inj["normalized_name"] for inj in injuries if inj["is_out"]}


class EspnRosterPlayer(TypedDict):
    espn_id: str
    display_name: str
    normalized_name: str
    is_injured: bool  # True if player has any active injury designation in ESPN's roster data


def get_nba_roster(espn_team_id: int) -> list[EspnRosterPlayer]:
    """Fetch full roster for one NBA team from ESPN public API (no auth required).

    Returns all 20-26 players on the roster, including injured players.
    Use is_injured=False to filter to healthy/available players.

    Note: status.type is always "active" in ESPN's API regardless of injury —
    use the injuries[] array (is_injured flag) to detect unavailability.
    """
    url = _ESPN_ROSTER_URL.format(espn_team_id)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("ESPN roster API request failed for team %d: %s", espn_team_id, exc)
        return []

    result: list[EspnRosterPlayer] = []
    for athlete in resp.json().get("athletes", []):
        first = athlete.get("firstName", "")
        last = athlete.get("lastName", "")
        display_name = athlete.get("displayName", "") or f"{first} {last}".strip()
        if not display_name:
            continue

        is_injured = len(athlete.get("injuries", [])) > 0

        result.append(
            EspnRosterPlayer(
                espn_id=str(athlete.get("id", "")),
                display_name=display_name,
                normalized_name=normalize_name(display_name),
                is_injured=is_injured,
            )
        )

    n_healthy = sum(1 for p in result if not p["is_injured"])
    logger.debug(
        "ESPN roster team %d: %d total, %d healthy, %d injured",
        espn_team_id, len(result), n_healthy, len(result) - n_healthy,
    )
    return result
