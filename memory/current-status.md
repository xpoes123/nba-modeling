# Current Status

## Current Phase
**P5 — COMPLETE** → ready to start P6

## Completed
- **P0**: config.py, db/schema.sql, db/init_db.py — validated
- **P1**: ingestion/pbpstats_client.py + ingestion/game_list.py — validated
- **P2**: ingestion/etl.py — validated (single-game ETL, stints sum = possessions, idempotent)
- **P3**: ingestion/backfill.py — complete, 1041/1050 games, ~201K possessions, PPP=1.1441
- **P4**: models/rapm.py + pipeline/phase1_full_season.py + tests/test_rapm.py — validated
  - 567 players rated; SGA +6.1, Wemby +5.8, Holmgren +5.4, Jokic +4.7
  - Targets in per-100-possessions units (×100 multiplier); alpha=5000; pace filters seconds_played=0
- **P5**: ingestion/ingest_daily.py + pipeline/nightly_job.py + scripts/ — validated
  - First run: ingested 7 new games (Mar 20), 567 players re-rated with phase='rapm_rolling'
  - Rolling window union start = 2025-10-21 (season start — see gotcha below)
  - Task Scheduler: scripts/install_task.ps1 registers daily 4am job

## Key Design Decisions Locked In
- Dependency management: `uv` + `pyproject.toml`
- RAPM: two separate regressions (offense + defense)
- `stints` stores `points_allowed` column
- Elo outcome: continuous PPP
- `overall` = `offense - defense`
- **Season: 2025-26** (switched from 2024-25 — current season)
- **PBP Source: pbpstats 'live' S3 provider** (data.nba.com dead, stats.nba.com PlayByPlayV2 deprecated)
  - URL: `nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/liveData/playbyplay/playbyplay_{game_id}.json`
  - Cache: `data/pbp/live_{game_id}.json`
- Game metadata from: `nba_api.LeagueGameLog` (batch, season-level); `LeagueGameFinder` as fallback
- Player names from: `nba_api.BoxScoreTraditionalV3` per game
- Clock format from live provider: `PT{M}M{S}.{ms}S` (ISO 8601) not MM:SS
- **CLAUDE.md overrides README on rapm.py purity**: rolling RAPM orchestration lives in
  `pipeline/nightly_job.py` (not models/rapm.py), keeping models/rapm.py pure (no DB I/O)

## P5 Architecture
- `ingestion/ingest_daily.py` — `get_new_game_ids()` + `ingest_new_games()`: fetches full season
  schedule from nba_api, filters to IDs not in games table, parses + ETLs with rate limiting
- `pipeline/nightly_job.py` — `run_rolling_rapm()` + `main()`: union window logic, calls
  models/rapm.py pure functions, upserts rapm_ratings (phase='rapm_rolling') + current_ratings
- `scripts/run_nightly.bat` — sets PYTHONPATH, redirects stdout/stderr to logs/nightly_YYYY-MM-DD.log
- `scripts/install_task.ps1` — registers Windows Task Scheduler task (run once, elevated PS)
- nightly_job.py logs to stdout only; bat file handles file redirect

## What's Pending
- P6: models/elo.py + models/composite.py + integrate into nightly_job.py

## Known Issues / Gotchas
- **Rolling window = full season right now**: union window logic takes min(all players' window starts).
  Bench players and cut 10-day contract guys who only played in October drag it back to Oct 21.
  This is correct per spec. Rolling will differentiate more from full-season once we filter
  "active" players, or next season when the window genuinely covers only recent games.
- `ingest_daily.py` fetches the full season schedule on every run (one nba_api call). Fine for now.
- ~9/1050 games fail ingestion: 4 with NULL home_team_id (API returns incomplete metadata for some
  games), 5 with 4-player OT lineups. Pre-existing issue, handled gracefully (log + continue).
- `nba_api.LeagueGameFinder` ignores `game_id_nullable` on server side — must filter client-side
- `BoxScoreSummaryV2` has missing data for games after 4/10/2025 — don't use it
- `stats.nba.com PlayByPlayV2` is dead (returns `{}`) — pbpstats stats_nba provider broken
- `data.nba.com` PBP endpoint times out in 2025 — pbpstats data_nba provider unreliable
- Live S3 provider: some possessions have 4 players (fouled out / substitution edge cases) — skipped
- `datetime.utcnow()` deprecated in Python 3.14 — use `datetime.now(timezone.utc)`

## Key Commands
- `PYTHONPATH=. uv run python pipeline/nightly_job.py` — run nightly job manually
- `PYTHONPATH=. uv run python pipeline/phase1_full_season.py` — re-run full-season RAPM
- `uv run pytest tests/` — run all tests (10 tests, all passing as of P5)
- `powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1` — register Task Scheduler

## DB State (as of 2026-03-21)
- 1041 games, ~55,923 stints, ~201,361 possessions, 567 players rated
- current_ratings: phase='rapm_rolling' (P5 overwrote P4's rapm_full)
- rapm_ratings: has both rapm_full (historical) and rapm_rolling (latest) rows

## Next Steps
1. Start P6: Elo layer
   - models/elo.py — sigmoid, elo_update, replay_game_elo, reset_elo_to_rapm
   - models/composite.py — update_current_ratings combining RAPM base + Elo delta
   - Integrate into pipeline/nightly_job.py: after rolling RAPM, replay today's games via Elo
