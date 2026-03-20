Fit the RAPM model and update `current_ratings`.

1. **Pre-flight checks**:
   - Backfill is sufficiently complete:
     ```sql
     SELECT COUNT(*) FROM games WHERE season = '2024-25';
     ```
     Should be 1200+. Do not run RAPM on a partial backfill — sparse data inflates ratings for players whose teams have few games ingested.
   - League averages exist:
     ```sql
     SELECT avg_ppp, avg_pace, total_possessions FROM league_averages WHERE season = '2024-25';
     ```
     `avg_ppp` should be 1.10–1.15. If missing or out of range, stop and investigate before proceeding.
   - `models/rapm.py` exists (P4 complete).

2. **Determine which RAPM to run**:
   - `rapm_ratings` table is empty → **full-season RAPM** (P4):
     ```bash
     python pipeline/phase1_full_season.py
     ```
   - `rapm_ratings` has data and `pipeline/nightly_job.py` exists → **rolling RAPM** (P5+):
     ```bash
     python pipeline/nightly_job.py
     ```

3. **What to expect**:
   - Full-season RAPM: fits three ridge regressions (offense, defense, pace) on all ~475K–525K possessions aggregated into stints. Should complete in under a minute.
   - Rolling RAPM: fits on the last 30 games per player's window. Faster, but results will differ from full-season.

4. **After fitting**, automatically run `/validate-ratings` to check output quality:
   - Distribution should be roughly normal, centered near 0
   - Known stars (Jokic, SGA, Luka) should appear in the top 20
   - No |rating| > 10

5. **Report**: how many players were rated, phase stored in `current_ratings`, any players with suspicious values.
