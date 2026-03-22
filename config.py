import os

from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "db", "nba_ratings.db")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "db", "schema.sql")
CALIBRATION_PATH = os.path.join(PROJECT_ROOT, "downstream", "calibration_coeffs.json")

# Seasons
INITIAL_SEASON = "2025-26"
SEASON_TYPE = "Regular Season"

# RAPM
RIDGE_ALPHA = 5000
ROLLING_WINDOW_GAMES = 30

# Elo
# K is calibrated for per-possession accumulation across a full season.
# With ~15K possessions per player per season and K/5 per-possession updates,
# σ(cumulative delta) = K/5 * σ(surprise) * sqrt(15000).
# K=0.02 gives σ ≈ 0.49 pts/100, keeping Elo deltas within ~10% of RAPM magnitude.
ELO_K_OFFENSE_DEFENSE = 0.02
ELO_K_PACE = 0.01

# Ingestion
BACKFILL_SLEEP_SECONDS = 2.5

# External API keys
ODDS_API_KEY = os.environ["ODDS_API_KEY"]
BALLDONTLIE_API_KEY = os.environ["BALLDONTLIE_API_KEY"]

# Predictions
MONTE_CARLO_SIMULATIONS = 1000
MINUTES_LOOKBACK_DAYS = 30        # days of BDL stats to pull for minutes distribution
MIN_GAMES_FOR_MINUTES = 5         # player needs at least this many games for minutes estimate
DEFAULT_MINUTES = 20.0            # fallback if insufficient history

# nba.com team ID → metadata mapping
# bdl_id: balldontlie team ID
NBA_TEAM_MAP: dict[str, dict] = {
    "1610612737": {"name": "Atlanta Hawks",          "abbrev": "ATL", "bdl_id": 1},
    "1610612738": {"name": "Boston Celtics",          "abbrev": "BOS", "bdl_id": 2},
    "1610612751": {"name": "Brooklyn Nets",           "abbrev": "BKN", "bdl_id": 3},
    "1610612766": {"name": "Charlotte Hornets",       "abbrev": "CHA", "bdl_id": 4},
    "1610612741": {"name": "Chicago Bulls",           "abbrev": "CHI", "bdl_id": 5},
    "1610612739": {"name": "Cleveland Cavaliers",     "abbrev": "CLE", "bdl_id": 6},
    "1610612742": {"name": "Dallas Mavericks",        "abbrev": "DAL", "bdl_id": 7},
    "1610612743": {"name": "Denver Nuggets",          "abbrev": "DEN", "bdl_id": 8},
    "1610612765": {"name": "Detroit Pistons",         "abbrev": "DET", "bdl_id": 9},
    "1610612744": {"name": "Golden State Warriors",   "abbrev": "GSW", "bdl_id": 10},
    "1610612745": {"name": "Houston Rockets",         "abbrev": "HOU", "bdl_id": 11},
    "1610612754": {"name": "Indiana Pacers",          "abbrev": "IND", "bdl_id": 12},
    "1610612746": {"name": "Los Angeles Clippers",    "abbrev": "LAC", "bdl_id": 13},
    "1610612747": {"name": "Los Angeles Lakers",      "abbrev": "LAL", "bdl_id": 14},
    "1610612763": {"name": "Memphis Grizzlies",       "abbrev": "MEM", "bdl_id": 15},
    "1610612748": {"name": "Miami Heat",              "abbrev": "MIA", "bdl_id": 16},
    "1610612749": {"name": "Milwaukee Bucks",         "abbrev": "MIL", "bdl_id": 17},
    "1610612750": {"name": "Minnesota Timberwolves",  "abbrev": "MIN", "bdl_id": 18},
    "1610612740": {"name": "New Orleans Pelicans",    "abbrev": "NOP", "bdl_id": 19},
    "1610612752": {"name": "New York Knicks",         "abbrev": "NYK", "bdl_id": 20},
    "1610612760": {"name": "Oklahoma City Thunder",   "abbrev": "OKC", "bdl_id": 21},
    "1610612753": {"name": "Orlando Magic",           "abbrev": "ORL", "bdl_id": 22},
    "1610612755": {"name": "Philadelphia 76ers",      "abbrev": "PHI", "bdl_id": 23},
    "1610612756": {"name": "Phoenix Suns",            "abbrev": "PHX", "bdl_id": 24},
    "1610612757": {"name": "Portland Trail Blazers",  "abbrev": "POR", "bdl_id": 25},
    "1610612758": {"name": "Sacramento Kings",        "abbrev": "SAC", "bdl_id": 26},
    "1610612759": {"name": "San Antonio Spurs",       "abbrev": "SAS", "bdl_id": 27},
    "1610612761": {"name": "Toronto Raptors",         "abbrev": "TOR", "bdl_id": 28},
    "1610612762": {"name": "Utah Jazz",               "abbrev": "UTA", "bdl_id": 29},
    "1610612764": {"name": "Washington Wizards",      "abbrev": "WAS", "bdl_id": 30},
}

# Reverse lookups derived from NBA_TEAM_MAP
_TEAM_NAME_TO_ID: dict[str, str] = {v["name"]: k for k, v in NBA_TEAM_MAP.items()}
_TEAM_ABBREV_TO_ID: dict[str, str] = {v["abbrev"]: k for k, v in NBA_TEAM_MAP.items()}
_BDL_ID_TO_TEAM_ID: dict[int, str] = {v["bdl_id"]: k for k, v in NBA_TEAM_MAP.items()}


def team_id_from_name(name: str) -> str | None:
    """Look up nba.com team ID from full team name (e.g. 'Los Angeles Lakers')."""
    return _TEAM_NAME_TO_ID.get(name)


def team_id_from_abbrev(abbrev: str) -> str | None:
    """Look up nba.com team ID from abbreviation (e.g. 'LAL')."""
    return _TEAM_ABBREV_TO_ID.get(abbrev)


def team_id_from_bdl(bdl_id: int) -> str | None:
    """Look up nba.com team ID from balldontlie team ID."""
    return _BDL_ID_TO_TEAM_ID.get(bdl_id)
