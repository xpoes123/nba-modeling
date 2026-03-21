"""ESPN public injury API client (no auth required).

Endpoint: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries
"""
import logging
from typing import TypedDict

import requests

from downstream.team_ratings import normalize_name

logger = logging.getLogger(__name__)

_ESPN_INJURIES_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"

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
