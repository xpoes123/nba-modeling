
# CLAUDE.md

## Project Overview

NBA Player Rating Engine — a hybrid RAPM + Elo system producing 3D player ratings (Offense, Defense, Pace). The ratings are the core product; downstream betting/trading models consume them.

## Critical Context

- **Owner:** David Jiang (FDE at Ramp, sports quant background)
- **Data source:** `pbpstats` Python library (dblackrun) — parses stats.nba.com play-by-play into possessions with lineup attribution, caches locally
- **Database:** SQLite (single file at `db/nba_ratings.db`)
- **Initial scope:** 2024-25 NBA Regular Season only

## How to Work on This Project

**READ THE README FIRST.** The project is broken into 7 discrete projects (P0–P6). Each project has explicit inputs, outputs, and validation criteria. **Complete one project fully and validate it before starting the next.** Do not attempt to build multiple projects in one pass.

**The project order matters:**
```
P0: Repo Setup → P1: pbpstats Client → P2: ETL → P3: Backfill → P4: RAPM → P5: Rolling RAPM → P6: Elo
```

Each project depends on the previous one's output.

## Architecture

```
stats.nba.com → pbpstats (parse+cache) → ETL → SQLite → RAPM (ridge) + Elo (per-possession) → current_ratings
```

Two data granularities in the DB:
- `stints` — aggregated 10-man matchup data (RAPM input)
- `possessions` — individual possessions with lineup tags (Elo input)

Both derived from the same pbpstats parsed output.

## Key Technical Decisions

- **pbpstats library** (not the REST API) is the primary data source — gives us possession-level lineup attribution locally
- **Lineup IDs** are dash-separated sorted player ID strings (e.g., `"201566-203507-203954-1629029-1630567"`)
- **Player IDs** are strings (nba.com/stats IDs), always sorted ascending within a lineup
- **Ridge regression** with `alpha=5000`, `fit_intercept=False` (target is already centered on league average)
- **Design matrix** uses `scipy.sparse` — +1 for offensive players, -1 for defensive players, weighted by `sqrt(possessions)`
- **Elo K-factor** = 2.0 (small — micro-adjustments on top of regression base), divided by 5 per player
- **Cold start** = 0 (league average) for all new players

## File Modification Rules

- **Do not modify files outside the project you are currently working on** — if you're on P1, don't touch `models/` or `pipeline/`
- **config.py** is the single source of truth for constants — do not hardcode paths, alphas, or season strings elsewhere
- **db/schema.sql** is the single source of truth for the schema — `init_db.py` reads it, don't duplicate DDL
- **All database writes use transactions** — entire game insert is atomic

## Common Commands

```bash
# Setup
pip install -r requirements.txt
python db/init_db.py

# Test single game parse (after P1)
python -c "from ingestion.pbpstats_client import parse_game; g = parse_game('0022400001'); print(len(g['possessions']), 'possessions')"

# Run backfill (after P3) — takes ~1hr with rate limiting
python ingestion/backfill.py

# Run full-season RAPM (after P4)
python pipeline/phase1_full_season.py

# Run nightly job (after P5)
python pipeline/nightly_job.py
```

## Validation Queries

```sql
-- Check game count
SELECT COUNT(*) FROM games WHERE season = '2024-25';
-- Expected: ~1200-1230

-- Check possession volume
SELECT COUNT(*) FROM possessions WHERE season = '2024-25';
-- Expected: ~475K-525K

-- Check league average PPP
SELECT avg_ppp FROM league_averages WHERE season = '2024-25';
-- Expected: ~1.10-1.15

-- Top 10 players by overall rating
SELECT p.player_name, cr.offense, cr.defense, cr.pace, cr.overall
FROM current_ratings cr
JOIN players p ON cr.player_id = p.player_id
ORDER BY cr.overall DESC
LIMIT 10;

-- Verify stints cover all possessions for a game
SELECT
    (SELECT SUM(possessions) FROM stints WHERE game_id = '0022400001') AS stint_poss,
    (SELECT COUNT(*) FROM possessions WHERE game_id = '0022400001') AS total_poss;
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `pbpstats` | Play-by-play parsing with lineup attribution |
| `nba_api` | Game schedules, player metadata |
| `scikit-learn` | Ridge regression (`sklearn.linear_model.Ridge`) |
| `scipy` | Sparse matrix construction |
| `numpy` | Array operations |
| `pandas` | Data manipulation (ETL) |

## Testing

- Each project has a validation section in the README — run those checks before proceeding
- `tests/` directory has unit tests per module
- Key invariants to always verify:
  - Every possession has exactly 5 offense + 5 defense players
  - Stint possession counts sum to total possessions per game
  - RAPM coefficient distribution is roughly normal, centered near 0
  - Elo deltas are small relative to RAPM base (< 10% magnitude)

## Code Quality

- **Type hints on all functions** in `ingestion/`, `models/`, `pipeline/`
- **No raw `sqlite3` calls scattered around** — follow the connection/transaction pattern established in `etl.py`; all DB access is explicit and closeable
- **`models/rapm.py` and `models/elo.py` should be pure** — accept data as arguments, return results, no DB side effects. DB I/O belongs in the orchestrator functions (`run_full_season_rapm`, `replay_game_elo`)
- **Run `pytest tests/` before committing** any changes to `ingestion/` or `models/`
- **`config.py` is the single source of truth** for all constants — never hardcode a path, alpha, season string, or K-factor anywhere else

## Preventing Mistakes

- **Rate limiting is mandatory** — never remove or reduce the sleep in `backfill.py`. stats.nba.com will throttle or ban you, and the backfill takes ~1hr regardless; don't race it
- **Lineup ID sort order is load-bearing** — always sort player IDs ascending before joining with dashes. Wrong sort order creates phantom duplicate lineups that silently corrupt RAPM
- **Don't delete `data/`** — it's the pbpstats local cache. Deleting it forces a full re-download of all play-by-play
- **Validate `league_avg_ppp` before trusting any ratings** — if it's outside 1.10–1.15, all RAPM targets are shifted and the entire model output is wrong. Check this first when ratings look off
- **RAPM coefficient sanity check**: mean should be ≈ 0, std ≈ 1.5–3.0, no player should have |rating| > 10. If you see extremes, suspect a lineup ID mismatch or missing possessions, not a great player
- **Ridge alpha=5000 is calibrated** — don't tune it on the same data you're predicting on. If you want to experiment, use a holdout season
- **Stints must cover all possessions** — if `SUM(stints.possessions) != COUNT(possessions)` for any game, the ETL has a bug. Never proceed to RAPM with this mismatch
- **Never run RAPM on a partial backfill** — players whose teams haven't played yet will have biased (inflated) estimates due to sparse data
- **nba_api and stats.nba.com are unofficial** — handle failures and rate limits gracefully in all ingestion code; never let a single game failure abort the whole backfill

## Skills

These are implemented as Claude Code slash commands in `.claude/commands/`. Use them to handle common operations without re-explaining context each time.

- **`/fresh-eyes`** — Re-orient at the start of a session. Reads `memory/current-status.md`, checks git log, inspects which project files exist, and queries DB health
- **`/check-db`** — Full database health check. Runs all validation queries, checks for data quality issues (missing lineups, games with 0 stints, stints/possessions mismatch)
- **`/validate-ratings`** — Sanity-check `current_ratings`. Prints top/bottom 20 players, checks distribution stats, flags known stars (Jokic, SGA, Luka) and outliers
- **`/run-backfill`** — Start or resume the full-season backfill with pre-flight checks. Reports progress and failures
- **`/run-rapm`** — Fit RAPM (full-season or rolling depending on phase) with prerequisite checks. Calls `/validate-ratings` on completion

## Memory & Session Continuity

- `memory/current-status.md` is the source of truth for session state: current phase (P0–P6), last validated milestone, known issues, and next steps
- **Before ending any session**, update `memory/current-status.md` with what was completed, what's still in progress, and what to do next
- **Start every session with `/fresh-eyes`** to re-orient before writing any code
- If the DB has data, run `/check-db` before writing new code that queries it — the schema or contents may have changed since the last session
