Sanity-check the player ratings in `current_ratings`.

1. **Check that ratings exist**:
   ```sql
   SELECT COUNT(*), phase, MAX(updated_at) FROM current_ratings GROUP BY phase;
   ```
   If the table is empty, report that RAPM hasn't been run yet (P4 incomplete).

2. **Print the top 20 players by overall rating**:
   ```sql
   SELECT p.player_name, cr.offense, cr.defense, cr.pace, cr.overall, cr.phase
   FROM current_ratings cr
   JOIN players p ON cr.player_id = p.player_id
   ORDER BY cr.overall DESC
   LIMIT 20;
   ```
   Sanity check: Nikola Jokic, Shai Gilgeous-Alexander, Luka Doncic, Giannis Antetokounmpo should appear near the top.

3. **Print the bottom 20 players by overall rating**:
   Due to ridge shrinkage, bottom players should cluster near 0, not have extreme negative ratings. Extreme negatives (< -5) suggest a data problem.

4. **Compute distribution statistics** for offense, defense, pace, overall:
   ```sql
   SELECT
       ROUND(AVG(overall), 3) AS mean,
       ROUND(MIN(overall), 3) AS min,
       ROUND(MAX(overall), 3) AS max,
       COUNT(*) AS n_players
   FROM current_ratings;
   ```
   Expected: mean ≈ 0, range roughly -5 to +8, no |rating| > 10.

5. **Flag anomalies**:
   - Any player with |overall| > 8 (suspicious outlier)
   - Any player with NULL offense, defense, or pace
   - Players with very few possessions who have extreme ratings (sparse data artifact)

6. **Summarize**: is the distribution healthy? Do the top players make basketball sense? Any red flags to investigate?
