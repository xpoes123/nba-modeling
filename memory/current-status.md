# Current Status

## Current Phase
**P4 — RAPM COMPLETE** → ready to start P5

## Completed
- **P0**: config.py, db/schema.sql, db/init_db.py — validated
- **P1**: ingestion/pbpstats_client.py + ingestion/game_list.py — validated
- **P2**: ingestion/etl.py — validated (single-game ETL, stints sum = possessions, idempotent)
- **P3**: ingestion/backfill.py — complete, 1034/1044 games, 200K possessions, PPP=1.1446
- **P4**: models/rapm.py + pipeline/phase1_full_season.py + tests/test_rapm.py — validated
  - 567 players rated; overall std=1.67; SGA +6.1, Wemby +5.8, Holmgren +5.4, Jokic +4.7
  - Targets in per-100-possessions units (×100 multiplier); alpha=5000; pace filters seconds_played=0

## Key Design Decisions Locked In
- Dependency management: `uv` + `pyproject.toml`
- RAPM: two separate regressions (offense + defense)
- `stints` stores `points_allowed` column
- Elo outcome: continuous PPP
- `ingest_daily.py` built in P5
- `overall` = `offense - defense`
- **Season: 2025-26** (switched from 2024-25 — current season, 1044 games available as of Mar 2026)
- **PBP Source: pbpstats 'live' S3 provider** (data.nba.com dead, stats.nba.com PlayByPlayV2 deprecated)
  - URL: `nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/liveData/playbyplay/playbyplay_{game_id}.json`
  - Cache: `data/pbp/live_{game_id}.json`
- Game metadata from: `nba_api.LeagueGameLog` (batch, season-level) for backfill; `LeagueGameFinder` as fallback
- Player names from: `nba_api.BoxScoreTraditionalV3` per game
- Clock format from live provider: `PT{M}M{S}.{ms}S` (ISO 8601) not MM:SS

## What's Pending
- P5: rolling RAPM (30-game window) + pipeline/nightly_job.py
- P6: models/elo.py + models/composite.py

## Known Issues / Gotchas
- `nba_api.LeagueGameFinder` ignores `game_id_nullable` on server side — must filter client-side: `df[df["GAME_ID"] == game_id]`
- `BoxScoreSummaryV2` has missing data for games after 4/10/2025 — don't use it
- `stats.nba.com PlayByPlayV2` is dead (returns `{}`) — pbpstats stats_nba provider broken
- `data.nba.com` PBP endpoint times out in 2025 — pbpstats data_nba provider unreliable
- Live S3 provider: some possessions have 4 players (fouled out / substitution edge cases) — these are skipped, ~2-3 per game

## Key RAPM Implementation Notes
- Run with: `PYTHONPATH=<project_root> uv run python pipeline/phase1_full_season.py`
- `uv run pytest tests/` to run all tests (use `uv run` not bare `pytest` — system Python lacks deps)
- RAPM targets are in per-100-possessions (×100), not raw PPP — alpha=5000 calibrated for this scale
- Pace regression filters stints with seconds_played=0 (193 stints excluded)

## Next Steps
1. Start P5: rolling RAPM (30-game sliding window)
   - Build pipeline/nightly_job.py that computes rolling RAPM and updates current_ratings
   - Same models/rapm.py functions, different window query in orchestrator
2. Start P6: models/elo.py + models/composite.py
