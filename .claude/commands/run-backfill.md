Start or resume the full-season backfill for the 2024-25 NBA Regular Season.

1. **Pre-flight checks** — verify prerequisites before running anything:
   - `ingestion/pbpstats_client.py` exists (P1 complete)
   - `ingestion/etl.py` exists (P2 complete)
   - `ingestion/backfill.py` exists (P3 complete)
   - Database exists at `config.DB_PATH`

2. **Check current backfill state**:
   ```sql
   SELECT COUNT(*) FROM games WHERE season = '2024-25';
   ```
   - **0 games**: starting fresh — full backfill will run (~1hr)
   - **1–1229 games**: resuming — backfill is idempotent, safe to re-run; it will skip already-ingested games
   - **1230+ games**: backfill is already complete — report this and stop; suggest running `/run-rapm` instead

3. **Run the backfill**:
   ```bash
   python ingestion/backfill.py
   ```
   Expected log format: `[423/1230] Game 0022400423 — LAL vs BOS — 198 possessions, 14 stints`

4. **Monitor for failures** — backfill.py should log any game IDs that failed. After completion, report:
   - Games successfully ingested
   - Games that failed (with error reason if available)
   - Whether a retry is needed for failed games

5. **Post-backfill validation** — after the run completes, execute `/check-db` to confirm:
   - Game count is 1200–1230
   - Possession count is 475K–525K
   - No stints/possessions mismatches
   - League averages were computed and inserted
