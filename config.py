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
ELO_K_OFFENSE_DEFENSE = 2.0
ELO_K_PACE = 1.0

# Ingestion
BACKFILL_SLEEP_SECONDS = 2.5
