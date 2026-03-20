"""Fetch pre-game odds and spreads from The Odds API."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.the-odds-api.com/v4"
API_KEY = os.getenv("ODDS_API_KEY")

NBA_SPORT = "basketball_nba"


def get_odds(markets: str = "h2h,spreads,totals", regions: str = "us") -> list[dict]:
    """Fetch current NBA pre-game odds."""
    url = f"{BASE_URL}/sports/{NBA_SPORT}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": regions,
        "markets": markets,
        "oddsFormat": "american",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def get_scores(days_from: int = 1) -> list[dict]:
    """Fetch recent NBA scores."""
    url = f"{BASE_URL}/sports/{NBA_SPORT}/scores"
    params = {
        "apiKey": API_KEY,
        "daysFrom": days_from,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()
