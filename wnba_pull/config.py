"""Configuration for the WNBA data pull (standalone from the NBA model).

Loads ODDS_API_KEY directly from .env so it does NOT import the root config.py
(which also requires BALLDONTLIE_API_KEY and would crash if that is unset).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

ODDS_API_KEY = os.environ["ODDS_API_KEY"]

# Output root. Each stream writes timestamped parquet files into a subdir;
# package_and_share.py consolidates them into one parquet + csv per dataset.
OUT = ROOT / "wnba_data"

# Last ~3 WNBA seasons. nba_api uses the END year as the season string.
SEASONS = ["2024", "2025", "2026"]

# ---- the-odds-api ----
ODDS_SPORT = "basketball_wnba"
ODDS_REGIONS = "us"
ODDS_GAME_MARKETS = ["h2h", "spreads", "totals"]
ODDS_PROP_MARKETS = [
    "player_points",
    "player_rebounds",
    "player_assists",
    "player_threes",
    "player_points_rebounds_assists",
]
ODDS_BOOKMAKER_FORMAT = "american"

# ---- Kalshi (public trade-api, no auth needed for market data) ----
KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
# Daily game-level series (the moneyline/spread/total equivalents + halves).
KALSHI_GAME_SERIES = [
    "KXWNBAGAME",      # game winner (moneyline)
    "KXWNBASPREAD",    # spread
    "KXWNBATOTAL",     # total
    "KXWNBA1HWINNER",  # 1st half winner
    "KXWNBA1HSPREAD",
    "KXWNBA1HTOTAL",
    "KXWNBA2HWINNER",
    "KXWNBA2HSPREAD",
    "KXWNBA2HTOTAL",
]
# Player prop series.
KALSHI_PROP_SERIES = ["KXWNBAPTS", "KXWNBAREB", "KXWNBAAST", "KXWNBA3PT"]

# ---- overnight polling ----
POLL_INTERVAL_SEC = 1200          # 20 min between live snapshots
PROPS_EVERY_N_CYCLES = 3          # pull sportsbook props only every 3rd cycle (~hourly) to save credits
RUN_HOURS = 11                    # how long the live polling loop runs

# ---- historical odds (credit-sensitive) ----
HIST_SEASON = "2026"              # current season closing lines only
HIST_ODDS_CREDIT_CAP = 3000      # hard stop; never spend more than this on historical odds
HIST_MARKETS = ["h2h", "spreads", "totals"]
HIST_OPEN_LEAD_HOURS = 24        # "opening" line = snapshot this many hours before tipoff

# ---- rate limiting for stats.wnba.com (be polite / avoid bans) ----
STATS_SLEEP_SEC = 1.0

# ---- publishing ----
VPS_HOST = "87.99.136.82"
VPS_USER = "root"
VPS_SHARE_DIR = "/opt/share/wnba"
PUBLIC_BASE_URL = "https://share.djiang.xyz/wnba"
