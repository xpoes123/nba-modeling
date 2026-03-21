import os

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "db", "nba_ratings.db")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "db", "schema.sql")

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
