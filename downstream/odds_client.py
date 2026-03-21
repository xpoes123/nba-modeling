"""Odds API client for fetching NBA game lines.

Docs: https://the-odds-api.com/liveapi/guides/v4/
Sport key: basketball_nba
"""
import logging
from datetime import date, datetime, timedelta
from typing import TypedDict

import requests

from config import ODDS_API_KEY

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.the-odds-api.com/v4"
_SPORT = "basketball_nba"


class GameOdds(TypedDict):
    odds_event_id: str
    game_date: str           # YYYY-MM-DD
    commence_time: str       # ISO 8601 UTC
    home_team: str
    away_team: str
    market_spread: float | None    # home spread (negative = home favored)
    market_win_prob: float | None  # vig-adjusted P(home wins) from best moneyline
    market_total: float | None     # over/under


def _implied_prob(american_odds: float) -> float:
    """Convert American odds to raw implied probability."""
    if american_odds < 0:
        return abs(american_odds) / (abs(american_odds) + 100)
    return 100 / (american_odds + 100)


def _vig_free_prob(home_odds: float, away_odds: float) -> float:
    """Return vig-free P(home wins) from American moneyline odds."""
    p_home = _implied_prob(home_odds)
    p_away = _implied_prob(away_odds)
    total = p_home + p_away
    return p_home / total


def _best_moneyline(bookmakers: list[dict]) -> tuple[float | None, float | None]:
    """Extract best (most favorable) home and away moneyline prices across books."""
    best_home: float | None = None
    best_away: float | None = None

    for book in bookmakers:
        for market in book.get("outcomes", []):
            pass
        for mkt in book.get("markets", []):
            if mkt["key"] != "h2h":
                continue
            for outcome in mkt.get("outcomes", []):
                price = outcome["price"]
                if outcome.get("name") == book.get("home_team"):
                    if best_home is None or price > best_home:
                        best_home = price
                else:
                    if best_away is None or price > best_away:
                        best_away = price

    return best_home, best_away


def _parse_game(event: dict) -> GameOdds:
    """Parse a single Odds API event into a GameOdds dict."""
    home_team = event["home_team"]
    away_team = event["away_team"]
    commence_time = event["commence_time"]
    # Convert UTC commence_time to US Eastern calendar date.
    # NBA late games tip at ~10pm ET = ~2am UTC next day, so UTC date would be wrong.
    from zoneinfo import ZoneInfo
    dt_utc = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
    dt_et = dt_utc.astimezone(ZoneInfo("America/New_York"))
    game_date = dt_et.date().isoformat()  # YYYY-MM-DD in US Eastern

    market_spread: float | None = None
    market_total: float | None = None
    best_home_ml: float | None = None
    best_away_ml: float | None = None

    for book in event.get("bookmakers", []):
        for mkt in book.get("markets", []):
            key = mkt["key"]
            outcomes = mkt.get("outcomes", [])

            if key == "spreads":
                for outcome in outcomes:
                    if outcome["name"] == home_team:
                        # Odds API point is from the home team's perspective:
                        #   -10 = home giving 10 (home favored by 10)
                        # Negate so market_spread uses our convention: positive = home favored.
                        if market_spread is None:
                            market_spread = -outcome["point"]

            elif key == "totals":
                for outcome in outcomes:
                    if outcome["name"] == "Over":
                        if market_total is None:
                            market_total = outcome["point"]

            elif key == "h2h":
                for outcome in outcomes:
                    price = outcome["price"]
                    if outcome["name"] == home_team:
                        if best_home_ml is None or price > best_home_ml:
                            best_home_ml = price
                    else:
                        if best_away_ml is None or price > best_away_ml:
                            best_away_ml = price

    market_win_prob: float | None = None
    if best_home_ml is not None and best_away_ml is not None:
        market_win_prob = _vig_free_prob(best_home_ml, best_away_ml)

    return GameOdds(
        odds_event_id=event["id"],
        game_date=game_date,
        commence_time=commence_time,
        home_team=home_team,
        away_team=away_team,
        market_spread=market_spread,
        market_win_prob=market_win_prob,
        market_total=market_total,
    )


def get_nba_odds(
    target_date: date | None = None,
    regions: str = "us",
    api_key: str | None = None,
) -> list[GameOdds]:
    """Fetch NBA odds from the Odds API for a given date (default: today + tomorrow).

    Args:
        target_date: filter to games commencing on this date (UTC). If None, returns
            all upcoming games (usually today + next couple of days).
        regions: bookmaker regions to query (e.g. "us", "us2", "eu")
        api_key: override the key from config (useful for testing)

    Returns:
        List of GameOdds dicts, one per game.
    """
    key = api_key or ODDS_API_KEY
    params = {
        "apiKey": key,
        "regions": regions,
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american",
        "dateFormat": "iso",
    }

    if target_date is not None:
        # NBA games tip off between ~noon ET and ~10:30pm ET.
        # In UTC (EDT = UTC-4 in March), that's 4pm–2:30am UTC — straddling midnight UTC.
        # Use 6am UTC as the day boundary (= 2am ET, between any two consecutive game days)
        # so Mar 21 and Mar 22 windows don't overlap.
        next_day = target_date + timedelta(days=1)
        params["commenceTimeFrom"] = f"{target_date.isoformat()}T06:00:00Z"
        params["commenceTimeTo"] = f"{next_day.isoformat()}T06:00:00Z"

    url = f"{_BASE_URL}/sports/{_SPORT}/odds"

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Odds API request failed: %s", exc)
        return []

    remaining = resp.headers.get("x-requests-remaining", "?")
    logger.info("Odds API: %s games returned, %s requests remaining", len(resp.json()), remaining)

    games = []
    for event in resp.json():
        try:
            games.append(_parse_game(event))
        except Exception as exc:
            logger.warning("Failed to parse event %s: %s", event.get("id"), exc)

    return games
