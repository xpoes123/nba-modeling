Re-orient to the current state of the NBA Player Rating Engine project.

1. Read `memory/current-status.md` — if it exists, summarize the last recorded state (current phase, known issues, next steps). If it doesn't exist yet, note that.

2. Run `git log --oneline -10` to see recent commits and understand what has changed.

3. Determine which projects (P0–P6) have been completed by checking whether key files exist:
   - P0 complete: `config.py`, `db/schema.sql`, `db/init_db.py` exist
   - P1 complete: `ingestion/pbpstats_client.py`, `ingestion/game_list.py` exist
   - P2 complete: `ingestion/etl.py` exists
   - P3 complete: `ingestion/backfill.py` exists
   - P4 complete: `models/rapm.py` exists and `rapm_ratings` table has data
   - P5 complete: `pipeline/nightly_job.py` exists with rolling RAPM logic
   - P6 complete: `models/elo.py` and `models/composite.py` exist

4. If `db/nba_ratings.db` exists, run a quick DB health check:
   ```sql
   SELECT COUNT(*) FROM games WHERE season = '2024-25';
   SELECT COUNT(*) FROM possessions WHERE season = '2024-25';
   SELECT COUNT(*) FROM current_ratings;
   ```
   Compare against expected ranges: games ~1200–1230, possessions ~475K–525K.

5. Summarize clearly:
   - **Current phase:** which project we're on
   - **What's built and validated**
   - **What's in progress or broken**
   - **Recommended next action**
