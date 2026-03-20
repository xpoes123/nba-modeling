# Current Status

## Current Phase
**P3 — Backfill RUNNING** (launched in background, ~60 min to complete)

## Completed
- **P0**: config.py, db/schema.sql, db/init_db.py — validated
- **P1**: ingestion/pbpstats_client.py + ingestion/game_list.py — validated
- **P2**: ingestion/etl.py — validated (single-game ETL, stints sum = possessions, idempotent)
- **P3**: ingestion/backfill.py — written, backfill running in background

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

## Backfill Status
- Command: `PYTHONPATH=<project_root> python ingestion/backfill.py > backfill.log 2>&1 &`
- Log: `backfill.log` in project root
- Rate: ~3.5s/game → ~1044 games → ~60 min
- Check progress: `tail -20 backfill.log` + `sqlite3 db/nba_ratings.db "SELECT COUNT(*) FROM games"`

## What's Pending After Backfill
- Validate backfill: ~1044 games, ~210K+ possessions, league avg PPP ~1.10-1.15
- P4: models/rapm.py + pipeline/phase1_full_season.py
- P5: rolling RAPM + pipeline/nightly_job.py
- P6: models/elo.py + models/composite.py

## Known Issues / Gotchas
- `nba_api.LeagueGameFinder` ignores `game_id_nullable` on server side — must filter client-side: `df[df["GAME_ID"] == game_id]`
- `BoxScoreSummaryV2` has missing data for games after 4/10/2025 — don't use it
- `stats.nba.com PlayByPlayV2` is dead (returns `{}`) — pbpstats stats_nba provider broken
- `data.nba.com` PBP endpoint times out in 2025 — pbpstats data_nba provider unreliable
- Live S3 provider: some possessions have 4 players (fouled out / substitution edge cases) — these are skipped, ~2-3 per game

## Next Steps
1. Wait for backfill to complete (check with `tail -20 backfill.log`)
2. Run `/check-db` to validate data quality
3. Start P4: RAPM model (models/rapm.py)
