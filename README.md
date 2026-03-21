# NBA Player Rating Engine

A hybrid player rating system combining **Regularized Adjusted Plus-Minus (RAPM)** with **Elo-style incremental updates** to produce dynamic, three-dimensional player ratings (Offense, Defense, Pace) for every NBA player.

**The player ratings are the core product.** Downstream applications (spread prediction, live in-game trading on Kalshi/Polymarket, lineup optimization) consume ratings as inputs.

## Architecture Summary

```
stats.nba.com ──► pbpstats library ──► Local Cache ──► ETL ──► SQLite
                                                                  │
                                              ┌───────────────────┤
                                              ▼                   ▼
                                         Stint-Level         Possession-Level
                                         RAPM (Ridge)        Elo Updates
                                              │                   │
                                              └───────┬───────────┘
                                                      ▼
                                              current_ratings
                                              (3D per player)
                                                      │
                                              ┌───────┼───────────┐
                                              ▼       ▼           ▼
                                          Spreads   Live Model   Lineup Opt.
```

## Tech Stack

- **Python 3.11+**
- **pbpstats** — play-by-play parsing with lineup attribution (primary data source)
- **nba_api** — supplementary data (schedules, player metadata)
- **SQLite** — all processed data and ratings
- **scikit-learn** — ridge regression
- **numpy / pandas** — matrix construction, data manipulation

## Data Source

**Primary:** `pbpstats` Python library by dblackrun. Fetches raw play-by-play from stats.nba.com, parses into possessions with full lineup attribution, caches locally.

**Fallback:** REST API at `api.pbpstats.com` — pre-computed lineup/stint aggregates via `get-lineup-opponent-summary`. Sufficient for RAPM but not per-possession Elo.

**Scope:** 2024-25 season (complete). Add 2025-26 after validation.

---

## Project Breakdown

This project is built in discrete phases. **Complete each project fully before starting the next.** Each project has clear inputs, outputs, and validation criteria.

---

### Project 0: Repo Setup

**Goal:** Scaffold the repo, install dependencies, create the database.

**Tasks:**
1. Create the directory structure (see Repo Structure below)
2. Create `requirements.txt` with: `pbpstats`, `nba_api`, `scikit-learn`, `numpy`, `pandas`
3. Create `config.py` with all constants (see Config section)
4. Create `db/schema.sql` with the full schema (see Schema section)
5. Create `db/init_db.py` — reads `schema.sql` and creates the SQLite database at the configured path
6. Create `data/` directory for pbpstats cache with `.gitkeep`
7. Create `.gitignore` — ignore `*.db`, `data/`, `__pycache__/`, `.env`, `*.pyc`, `notebooks/.ipynb_checkpoints/`

**Validation:** `python db/init_db.py` runs without error and creates the database with all tables.

**Output:** Empty database with schema applied, all directories in place.

---

### Project 1: pbpstats Client

**Goal:** Build a wrapper around the pbpstats library that fetches and parses a single game into structured possession data with lineup attribution.

**Tasks:**
1. Create `ingestion/pbpstats_client.py` with a function `parse_game(game_id: str) -> dict` that:
   - Configures pbpstats with `data_directory` pointing to `config.DATA_DIR`
   - Fetches the game's play-by-play via pbpstats
   - Returns a dict with:
     - `game_id`, `season`, `game_date`, `home_team_id`, `away_team_id`
     - `possessions`: list of dicts, each containing:
       - `period`, `possession_number` (sequential)
       - `offense_team_id`, `defense_team_id`
       - `points_scored` (total points on this possession including FTs)
       - `fg2a`, `fg2m`, `fg3a`, `fg3m`, `turnovers`, `offensive_rebounds`, `free_throw_points`
       - `start_time`, `end_time`, `start_type`, `start_score_differential`
       - `offense_lineup_id` (dash-separated sorted player IDs)
       - `defense_lineup_id` (dash-separated sorted player IDs)
       - Individual player IDs: `off_player_1` through `off_player_5`, `def_player_1` through `def_player_5` (sorted)
2. Create `ingestion/game_list.py` with a function `get_season_game_ids(season: str) -> list[str]` that returns all game IDs for a season using nba_api or pbpstats.

**Important implementation notes:**
- pbpstats `Possession` objects have `.offense_team_id`, `.defense_team_id` attributes
- Lineup info is on the possession's `OffenseLineup` and `DefenseLineup` properties
- Player IDs should be stored as strings, sorted ascending, to create deterministic lineup keys
- The `offense_lineup_id` is the dash-separated sorted string of 5 player IDs (e.g., `"201566-203507-203954-1629029-1630567"`)
- Consult pbpstats docs/source for exact attribute names — they may vary between versions

**Validation:** Run `parse_game("0022400001")` (or any known 2024-25 game ID) and verify:
- Returns possessions with valid lineup data
- Total points across possessions matches the actual game score
- Each possession has exactly 5 offensive and 5 defensive players
- Lineup IDs are deterministic (same game parsed twice → same IDs)

**Output:** Working single-game parser. No database writes yet.

---

### Project 2: ETL Pipeline

**Goal:** Transform parsed game data into database rows (possessions + stints) and insert into SQLite.

**Tasks:**
1. Create `ingestion/etl.py` with:
   - `insert_game(db_path: str, parsed_game: dict) -> None`
     - Inserts into `games` table
     - Inserts each possession into `possessions` table
     - Aggregates possessions into 10-man stints and inserts into `stints` table
     - Upserts player metadata into `players` table
     - Uses transactions — entire game is atomic (commit or rollback)
   - `aggregate_stints(possessions: list[dict]) -> list[dict]`
     - Groups possessions by `(offense_lineup_id, defense_lineup_id)`
     - For each group: sum possessions count, points_scored, compute seconds_played from time data
     - Compute `offensive_rating = points_scored / possessions * 100`
     - Returns list of stint dicts ready for DB insertion
2. Handle idempotency: if a game already exists in the DB, skip it (check `games` table)

**Validation:** Parse and ETL a single game. Then query:
```sql
-- Total points should match actual game score
SELECT offense_team_id, SUM(points_scored) FROM possessions WHERE game_id = ? GROUP BY offense_team_id;

-- Stints should cover all possessions
SELECT SUM(possessions) FROM stints WHERE game_id = ?;
-- Should equal total possessions in the game

-- Every stint should have exactly 10 unique players
-- (verify programmatically)
```

**Output:** Single-game ETL working end-to-end. Parse → transform → SQLite.

---

### Project 3: Backfill Script

**Goal:** Backfill the entire 2024-25 season into the database.

**Tasks:**
1. Create `ingestion/backfill.py` that:
   - Gets all game IDs for the 2024-25 season
   - For each game (in chronological order):
     - Skip if already in `games` table
     - Parse via `pbpstats_client.parse_game()`
     - ETL via `etl.insert_game()`
     - Sleep 2-3 seconds between games (rate limiting for stats.nba.com)
     - Log progress: `"[423/1230] Game 0022400423 — LAL vs BOS — 198 possessions, 14 stints"`
   - Handle errors gracefully: log failures, continue to next game, report summary at end
   - Support resume: since ETL is idempotent, re-running picks up where it left off
2. After backfill completes, compute and insert league averages:
   ```sql
   INSERT INTO league_averages (season, avg_ppp, avg_pace, total_possessions)
   SELECT
       season,
       CAST(SUM(points_scored) AS REAL) / SUM(possessions),
       AVG(game_pace),  -- need to compute from games table
       SUM(possessions)
   FROM stints
   GROUP BY season;
   ```

**Validation:**
- ~1,200-1,230 games ingested for 2024-25
- Total possessions across season is ~475K-525K (sanity check)
- League average PPP is ~1.10-1.15 (sanity check)
- No games with 0 possessions or 0 stints
- Run `SELECT COUNT(DISTINCT offense_lineup_id) FROM stints;` — should be several thousand unique lineups

**Output:** Full 2024-25 season in SQLite. Ready for RAPM.

---

### Project 4: RAPM Model (Full-Season)

**Goal:** Fit ridge regression on stint-level data to produce offense, defense, and pace ratings for every player.

**Tasks:**
1. Create `models/rapm.py` with:
   - `build_design_matrix(db_path: str, season: str) -> tuple[scipy.sparse.csr_matrix, np.array, np.array, list[str]]`
     - Query all stints for the season
     - Build player index: map each unique `player_id` to a column index
     - For each stint row:
       - Set `+1` at columns for the 5 offensive player indices
       - Set `-1` at columns for the 5 defensive player indices
     - Use `scipy.sparse` — the matrix is very sparse (~10 nonzeros per row out of ~500+ columns)
     - Weight each row by `sqrt(possessions)`
     - Target `y_offense`: `(points_scored / possessions - league_avg_ppp) * sqrt(possessions)`
     - Target `y_defense`: `(points_allowed / possessions - league_avg_ppp) * sqrt(possessions)`
     - Return: X matrix, y_offense, y_defense, player_id list (column order)
   - `build_pace_target(db_path: str, season: str) -> np.array`
     - Target: `(possessions / seconds_played * 2880 - league_avg_pace) * sqrt(possessions)`
     - Same design matrix X, different target
   - `fit_rapm(X, y, alpha=5000) -> np.array`
     - `sklearn.linear_model.Ridge(alpha=alpha, fit_intercept=False)`
     - Returns coefficient array
   - `run_full_season_rapm(db_path: str, season: str, alpha=5000) -> None`
     - Orchestrator: build matrix → fit offense → fit defense → fit pace
     - Insert results into `rapm_ratings` table
     - Update `current_ratings` table with `phase = 'rapm_full'`

**Important design notes:**
- `fit_intercept=False` because our target is already centered on league average
- The design matrix encodes offense as +1 and defense as -1, so a single regression produces ORAPM coefficients. For DRAPM, flip the sign convention or fit separately with defense as +1.
- Actually, the cleanest approach: fit ONE regression where each row's target is the offensive team's margin per possession. The coefficient for a player captures their net impact when on offense (+) or defense (-). Then:
  - `offense_rating` = coefficient when player is on offense = positive means good offense
  - `defense_rating` = coefficient when player is on defense = negative means good defense (allows fewer points)
  - To get both, fit two separate regressions: one for offensive possessions (target = points scored - avg), one for defensive possessions (target = points allowed - avg, sign-flipped so lower is better)
- Alternative (simpler): fit one regression, coefficient = net impact. Then use on/off splits from the data to decompose. **Start with net RAPM first, decompose later.**

**Validation:**
- Print top 20 and bottom 20 players by overall rating
- Sanity check: stars (Jokic, SGA, Luka) should be near the top; end-of-bench guys near zero (not bottom — ridge shrinks them)
- Coefficient distribution should be roughly normal, centered near 0
- Correlation with public RAPM sources > 0.7

**Output:** `rapm_ratings` and `current_ratings` populated for all players in 2024-25.

---

### Project 5: Rolling-Window RAPM

**Goal:** Replace full-season RAPM with a 30-game rolling window, re-fit nightly.

**Tasks:**

**P5.1 — Rolling RAPM + Nightly Job Script**
1. Create `ingestion/ingest_daily.py`:
   - `get_games_since(db_path: str, since_date: str) -> list[str]`
     - Query `games` table for the max `game_date` already ingested
     - Fetch all game IDs from `nba_api.LeagueGameLog` on or after that date
     - Return only game IDs not yet in the `games` table
   - `ingest_new_games(db_path: str) -> int`
     - Call `get_games_since`, parse + ETL each new game, return count of games ingested
2. Add to `models/rapm.py`:
   - `get_player_window(db_path: str, player_id: str, as_of_date: str, window_size=30) -> tuple[date, date]`
     - Find the last 30 games this player appeared in, on or before `as_of_date`
     - Return `(window_start_date, window_end_date)`
   - `build_rolling_design_matrix(db_path: str, season: str, as_of_date: str, window_size=30)`
     - Compute the union window: earliest `window_start_date` across all active players
     - Query stints where `game_date >= union_start AND game_date <= as_of_date`
     - Same matrix construction as full-season
   - `run_rolling_rapm(db_path: str, season: str, as_of_date: str, alpha=5000)`
     - Fit and store rolling RAPM ratings with window metadata
3. Create `pipeline/nightly_job.py`:
   - Ingest new games via `ingest_daily.ingest_new_games()`
   - Recalculate league averages
   - Run rolling RAPM as of today
   - Update `current_ratings` with `phase = 'rapm_rolling'`
   - Log a summary: games ingested, players updated, timestamp

**P5.2 — Scheduling Infrastructure**
4. Set up Windows Task Scheduler to run `nightly_job.py` automatically:
   - Create `scripts/run_nightly.bat` — a batch file that activates the `uv` environment and runs `nightly_job.py` with `PYTHONPATH` set correctly
   - Create `scripts/install_task.ps1` — a PowerShell script that registers the task in Windows Task Scheduler:
     - Trigger: daily at 4:00 AM (after games have finished and data is available)
     - Action: run `run_nightly.bat`
     - Working directory: project root
     - On failure: retry once after 30 minutes
   - Document the setup steps in a `SETUP.md` (or section in README) so it can be re-installed on a new machine
   - Log output to `logs/nightly_YYYY-MM-DD.log` — `nightly_job.py` should write structured log lines, and the batch file should redirect stdout/stderr to a dated log file

**Validation:**
- Rolling ratings should be correlated with but not identical to full-season ratings
- Players who had a strong recent stretch should rate higher in rolling vs full-season
- Window metadata in `rapm_ratings` should show correct date ranges
- Run `scripts/install_task.ps1` and verify the task appears in Task Scheduler; trigger it manually and confirm `logs/` gets a log file with expected output

**Output:** Nightly-updatable rolling RAPM pipeline that runs automatically each morning.

---

### Project 6: Elo Layer

**Goal:** Add per-possession Elo updates between RAPM re-fits.

**Tasks:**
1. Create `models/elo.py`:
   - `sigmoid(x: float) -> float` — standard logistic function
   - `elo_update(possession: dict, current_elos: dict, league_avg_ppp: float, K=2.0) -> dict`
     - Compute expected outcome from current Elo ratings of 10 players
     - Compute surprise (actual - expected)
     - Return updated Elo deltas for all 10 players
   - `replay_game_elo(db_path: str, game_id: str, current_elos: dict, league_avg_ppp: float, K=2.0) -> dict`
     - Fetch all possessions for game in chronological order
     - Apply Elo updates sequentially
     - Apply game-level pace Elo update after all possessions
     - Store Elo snapshots in `elo_ratings` table
     - Return updated elos
   - `reset_elo_to_rapm(db_path: str) -> dict`
     - Load latest RAPM ratings
     - Return elo dict with all deltas = 0, bases = RAPM values
2. Create `models/composite.py`:
   - `update_current_ratings(db_path: str) -> None`
     - For each player: `offense = rapm_base + elo_delta`, same for defense, pace
     - Update `current_ratings` with `phase = 'elo'`
3. Integrate into `nightly_job.py`:
   - After RAPM re-fit: reset Elo → replay today's games → update composite ratings

**Validation:**
- Elo deltas should be small relative to RAPM base (< 10% magnitude)
- After a blowout win, offensive players' Elo should tick up, defensive opponents' should tick down
- Calibration plot: bin possessions by predicted probability, plot actual scoring rate. Should be roughly diagonal.

**Output:** Full hybrid rating system: RAPM base + Elo adjustments, updated per-possession.

---

## Config

```python
# config.py
import os

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "db", "nba_ratings.db")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "db", "schema.sql")

# Seasons
INITIAL_SEASON = "2024-25"
SEASON_TYPE = "Regular Season"

# RAPM
RIDGE_ALPHA = 5000
ROLLING_WINDOW_GAMES = 30

# Elo
ELO_K_OFFENSE_DEFENSE = 2.0
ELO_K_PACE = 1.0

# Ingestion
BACKFILL_SLEEP_SECONDS = 2.5
```

---

## Schema

See `db/schema.sql` — full schema is in the spec document. Key tables:

| Table | Purpose | Phase |
|-------|---------|-------|
| `possessions` | Per-possession data with 10-man lineups | P1 (populated), P6 (consumed by Elo) |
| `stints` | Aggregated 10-man matchup data | P1 (populated), P4 (consumed by RAPM) |
| `games` | Game metadata, used for idempotency | P1 |
| `players` | Player metadata | P1 |
| `league_averages` | Season-level PPP and pace | P3 |
| `rapm_ratings` | RAPM coefficients with window metadata | P4-5 |
| `elo_ratings` | Per-possession Elo snapshots | P6 |
| `current_ratings` | Best current rating per player | P4+ |

---

## Repo Structure

```
nba-rating-engine/
├── README.md
├── CLAUDE.md
├── requirements.txt
├── config.py
├── .gitignore
├── db/
│   ├── schema.sql
│   ├── init_db.py
│   └── nba_ratings.db          (gitignored)
├── data/                        (gitignored — pbpstats cache)
│   └── .gitkeep
├── ingestion/
│   ├── __init__.py
│   ├── pbpstats_client.py
│   ├── game_list.py
│   ├── etl.py
│   ├── backfill.py
│   └── ingest_daily.py
├── models/
│   ├── __init__.py
│   ├── rapm.py
│   ├── elo.py
│   └── composite.py
├── pipeline/
│   ├── __init__.py
│   ├── nightly_job.py
│   └── phase1_full_season.py
├── analysis/
│   ├── validate_ratings.py
│   ├── calibration.py
│   └── notebooks/
│       ├── rapm_exploration.ipynb
│       └── elo_tuning.ipynb
├── downstream/
│   ├── __init__.py
│   ├── spread_model.py
│   ├── live_model.py
│   └── lineup_optimizer.py
└── tests/
    ├── __init__.py
    ├── test_etl.py
    ├── test_rapm.py
    ├── test_elo.py
    └── test_pipeline.py
```
