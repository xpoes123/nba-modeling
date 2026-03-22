
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

## Future Model Directions

Tracked here so Claude knows what to look for when starting new model work. Full analysis lives in `memory/model-analysis.md`.

- **Matchup-specific adjustments via play style clustering** — current RAPM treats all
  opponents as the average team. Cluster teams into style archetypes (pace, paint vs. 3-point
  tendency, etc.) using features already in the DB, then check whether calibration residuals
  correlate with cluster-pair matchups. If signal exists, add interaction terms to calibration.
  **Constraint:** needs 2+ seasons of H2H data for robust cluster-pair estimates; prototype with
  current season first and validate via backtest before touching `calibration_coeffs.json`.
  David's examples: OKC vs SAS/MIL, LAL vs ORL — track residuals for those style matchups.

## Skills

These are implemented as Claude Code slash commands in `.claude/commands/`. Use them to handle common operations without re-explaining context each time.

- **`/fresh-eyes`** — Re-orient at the start of a session. Reads `memory/current-status.md`, checks git log, inspects which project files exist, and queries DB health
- **`/check-db`** — Full database health check. Runs all validation queries, checks for data quality issues (missing lineups, games with 0 stints, stints/possessions mismatch)
- **`/validate-ratings`** — Sanity-check `current_ratings`. Prints top/bottom 20 players, checks distribution stats, flags known stars (Jokic, SGA, Luka) and outliers
- **`/run-backfill`** — Start or resume the full-season backfill with pre-flight checks. Reports progress and failures
- **`/run-rapm`** — Fit RAPM (full-season or rolling depending on phase) with prerequisite checks. Calls `/validate-ratings` on completion
- **`/analyze-game`** — Deep-dive on a specific game: why did our model miss? Spawns a subagent to trace lineup profiles, player ratings, raw margin math, and injury filter accuracy. Writes findings to `memory/game-analyses/YYYY-MM-DD-AWAY-HOME.md` and appends a summary to `memory/model-analysis.md`. Usage: `/analyze-game 2026-03-21 GSW ATL`

## Context Management — Protecting Main Context

Deep analysis (DB queries, multi-file reads, math traces) burns context fast. Follow these rules:

- **Use subagents for any analysis requiring more than ~5 DB queries or reading multiple files.**
  Delegate to `Task(subagent_type="general-purpose")` or `Task(subagent_type="Explore")`. Have
  the subagent write its findings to `memory/game-analyses/YYYY-MM-DD-AWAY-HOME.md`, then read
  that summary file in the main context. This keeps the main context clean for reasoning.
- **Use the `/analyze-game` skill** for post-game diagnostic work (why did we miss a game?).
  It spawns a subagent, does the full computation, and writes a persistent analysis file.
- **For one-off DB lookups** (a single `SELECT`, checking a count), use Bash directly — no need
  for a subagent.
- **Write findings to files, not just to the conversation.** If you do deep analysis inline,
  always end by writing a summary to `memory/model-analysis.md` or a new
  `memory/game-analyses/` file before the context grows too large to act on it.
- **If context is already large**, stop mid-analysis, write what you have, and instruct David
  to start a fresh session with `/fresh-eyes` before continuing.

## Memory & Session Continuity

- `memory/current-status.md` is the source of truth for session state: current phase (P0–P7), last validated milestone, known issues, and next steps
- `memory/model-analysis.md` is the source of truth for prediction model quality: calibration results, known gaps, improvement backlog, and per-game prediction logs. **Read this before doing any work on the downstream prediction engine.**
- `memory/game-analyses/` — per-game deep-dive files written by `/analyze-game`. Named
  `YYYY-MM-DD-AWAY-HOME.md` (e.g. `2026-03-21-GSW-ATL.md`). Reference these from
  `model-analysis.md` rather than re-running the analysis inline.
- **After every substantive response**, update memory files before the conversation continues:
  - `memory/current-status.md` — if anything changed about the project state, phase, or known issues
  - `memory/model-analysis.md` — if any prediction quality finding was made (backtest result,
    new edge identified, calibration change, game diagnosis)
  - `C:\Users\David\.claude\projects\...\memory\MEMORY.md` — if a stable pattern or gotcha was confirmed
  Do this proactively, not just at session end. Memory written mid-session survives context compression.
- **Before ending any session**, always update `memory/current-status.md` with:
  - Current phase and whether it's complete
  - Everything completed this session
  - Any key design decisions that were made
  - Known issues or blockers
  - Exact next steps
- **If working on model quality or predictions**, also update `memory/model-analysis.md` with new observations, edges, or improvement ideas.
- **Start every session with `/fresh-eyes`** to re-orient before writing any code
- If the DB has data, run `/check-db` before writing new code that queries it — the schema or contents may have changed since the last session
- **Do not rely on conversation history across sessions** — write everything important to `memory/current-status.md` so it survives a fresh context

## Committing & Pushing

**Commit early and often — every independently completable unit of work gets its own commit.**

Treat each of the following as a commit boundary:
- A new file is working and tested (e.g., `pbpstats_client.py` parses a game correctly)
- A validation query passes (schema init, backfill progress checkpoint, RAPM sanity check)
- A bug is fixed and verified
- A project phase (P0–P6) is fully validated

**Commit rules:**
- **Run `pytest tests/` before committing** any changes to `ingestion/` or `models/`
- Stage specific files by name — never `git add -A` or `git add .` blindly
- Write descriptive commit messages: what changed and why, not just "update"
- **Push after every commit** — do not let commits accumulate locally. `git push` immediately after `git commit`
- Never commit `db/nba_ratings.db` or anything under `data/` — these are local artifacts, not source
- **Always push memory file updates** (`memory/current-status.md`, `memory/model-analysis.md`) together with the code change that prompted them, in the same commit. Never leave memory updates un-pushed.

**When in doubt, commit.** A commit is cheap; lost work is not.

## Ask Don't Assume

When there is any ambiguity — about requirements, design choices, or intended behavior — **stop and ask David before writing code**. Do not make assumptions and proceed. Specifically:

- **If the spec is underspecified**, ask. Don't pick an arbitrary implementation and document it after the fact.
- **If two approaches are both reasonable**, present them and ask which to use. Don't silently choose one.
- **If a project's inputs or outputs are unclear**, clarify before starting. The projects are sequential — a wrong assumption in P1 propagates through P2–P6.
- **If something unexpected is found** (e.g., pbpstats attribute names differ from the README, a game has malformed data), surface it immediately rather than working around it silently.
- **If a design decision has downstream consequences** (schema changes, API contracts, model assumptions), flag it and confirm before locking it in.

The cost of a 30-second clarification question is far lower than the cost of building on a wrong assumption.

This applies especially to:
- pbpstats API surface (attribute names, object structure) — check the source/docs and ask if unclear
- RAPM matrix construction details (sign conventions, weighting, intercept handling)
- Elo update formulas (expected value definition, outcome normalization)
- Any change that would require modifying `db/schema.sql` after P0

## NBA Domain Knowledge Rules

Claude's internal NBA knowledge is unreliable for this project — player rosters, injuries, team
compositions, and recent performance are outside the training cutoff or simply wrong. Follow these
rules strictly:

- **Never rely on Claude's own NBA knowledge** to validate predictions, player ratings, or model
  outputs. Don't say "SGA should be top-5" or "the Lakers are a good home team" based on internal
  priors — these may be stale or wrong.
- **Always backtest before concluding anything about model quality.** If a prediction looks
  surprising or a rating looks off, run `downstream/backtest.py` against recent dates rather than
  judging by intuition. Do NOT say "this looks reasonable" without a backtest number to back it up.
  ```bash
  PYTHONPATH=. uv run python downstream/backtest.py --start YYYY-MM-DD --end YYYY-MM-DD
  ```
- **Backtest any model change before accepting it.** New calibration coefficient, formula fix,
  feature addition — always measure the before/after on the full season, not just a spot-check.
  Report: MAE, correlation, directional accuracy, bias. Compare explicitly to the previous version.
- **Ask David for sanity checks on NBA-specific questions — proactively, not as a last resort.**
  David has current-season NBA knowledge that Claude lacks. Ask early and often:
  - Any time a player's rating seems surprising ("Is X playing starter minutes this year?")
  - Any time a team spread looks wrong vs. the market ("Does it make sense MIL is -6 here?")
  - Any time an edge might be driven by an injury or trade ("Did SAC get worse after Fox left?")
  - Any time lineup estimates look stale ("Has this team's rotation changed recently?")
  Do not speculate using internal NBA knowledge — ask David instead.
- **The DB is ground truth for lineups and usage** — possession history in `possessions` table
  is more reliable than any internal knowledge about how teams use players.
- **When diagnosing a specific game miss, pull the actual box score via BallDontLie API** to see
  exactly who played and how many minutes. This is ground truth for the actual lineup vs. what
  our model assumed. Use `GET /v1/stats?game_ids[]=<game_id>` (requires paid BDL tier for stats
  endpoints — free tier only has /v1/teams). As an alternative, `nba_api.BoxScoreTraditionalV3`
  is already a project dependency and works for any historical game:
  ```python
  from nba_api.stats.endpoints import BoxScoreTraditionalV3
  bs = BoxScoreTraditionalV3(game_id='0022501026')
  print(bs.player_stats.get_data_frame()[['playerName','minutes','points']])
  ```
  Use this to compare: (a) who was actually in the lineup vs. who ESPN reported as Out/Doubtful,
  (b) actual minutes played vs. our possession-share estimates, and (c) confirm DNP reasons.
