Run a full health check on the SQLite database at `db/nba_ratings.db`.

1. **Verify the database exists** at the path in `config.DB_PATH`. If it doesn't, report that P0 hasn't been run yet.

2. **Verify all tables are present**: `games`, `possessions`, `stints`, `players`, `league_averages`, `rapm_ratings`, `elo_ratings`, `current_ratings`. Report any missing tables.

3. **Run the core validation queries** and compare to expected ranges:

   ```sql
   -- Game count — expect 1200–1230 for a complete 2024-25 backfill
   SELECT COUNT(*) FROM games WHERE season = '2024-25';

   -- Possession count — expect 475K–525K
   SELECT COUNT(*) FROM possessions WHERE season = '2024-25';

   -- League average PPP — expect 1.10–1.15
   SELECT avg_ppp FROM league_averages WHERE season = '2024-25';

   -- Stints should cover all possessions
   SELECT
       (SELECT SUM(possessions) FROM stints WHERE season = '2024-25') AS stint_poss,
       (SELECT COUNT(*) FROM possessions WHERE season = '2024-25') AS total_poss;

   -- Current ratings count
   SELECT COUNT(*) FROM current_ratings;
   ```

4. **Check for data quality issues**:

   ```sql
   -- Games with no possessions (ETL bug or failed insert)
   SELECT game_id FROM games
   WHERE game_id NOT IN (SELECT DISTINCT game_id FROM possessions)
   AND season = '2024-25';

   -- Possessions missing lineup data
   SELECT COUNT(*) FROM possessions
   WHERE offense_lineup_id IS NULL OR defense_lineup_id IS NULL;

   -- Stints/possessions mismatch per game (sample 5 worst offenders)
   SELECT s.game_id,
          SUM(s.possessions) AS stint_poss,
          COUNT(p.possession_id) AS raw_poss,
          ABS(SUM(s.possessions) - COUNT(p.possession_id)) AS delta
   FROM stints s
   JOIN possessions p ON s.game_id = p.game_id
   GROUP BY s.game_id
   HAVING delta > 0
   ORDER BY delta DESC
   LIMIT 5;
   ```

5. **Summarize**: what's healthy, what's missing, what's out of range, and what needs attention before proceeding.
