# Current Status

## Current Phase
**P1 — pbpstats Client (not started)**

## Completed
- **Repo scaffold**: all directories, `__init__.py` files, `.gitignore`, `pyproject.toml`, `requirements.txt`
- **CLAUDE.md**: full project instructions, skills, preventing-mistakes rules, memory continuity rules
- **`.claude/commands/`**: 5 skills created (fresh-eyes, check-db, validate-ratings, run-backfill, run-rapm)
- **P0 validated**: `config.py`, `db/schema.sql`, `db/init_db.py` — all 8 tables + 10 indexes confirmed created
- **Remote**: pushed to https://github.com/xpoes123/nba-modeling.git on `main`

## Key Design Decisions Locked In
- Dependency management: `uv` + `pyproject.toml` (requirements.txt kept as export)
- RAPM: two separate regressions (offense + defense), not net RAPM
- `stints` table stores `points_allowed` column (not derived at query time)
- Elo outcome: continuous PPP (not binary scored/not scored)
- `ingest_daily.py` built in P5 (not P3)
- `overall` in `current_ratings` = `offense - defense`

## What's Pending
- P1: `ingestion/pbpstats_client.py` + `ingestion/game_list.py`
- P2: `ingestion/etl.py`
- P3: `ingestion/backfill.py`
- P4: `models/rapm.py` + `pipeline/phase1_full_season.py`
- P5: rolling RAPM + `pipeline/nightly_job.py` + `ingestion/ingest_daily.py`
- P6: `models/elo.py` + `models/composite.py`

## Known Issues
None.

## Next Steps
Start P1: build `ingestion/pbpstats_client.py` with `parse_game(game_id)` and `ingestion/game_list.py` with `get_season_game_ids(season)`. Will need to install pbpstats and nba_api into the venv first.
