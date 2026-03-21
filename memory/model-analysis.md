# Model Analysis Notes

Ongoing observations about prediction quality, calibration, and areas for improvement.
Update this file as we learn from comparing predictions to actual outcomes.

---

## Calibration (as of 2026-03-21)

Fit on 1,041 games (2025-26 season, first 600 train / last 441 val):

| Coefficient     | Value      | Interpretation                              |
|-----------------|------------|---------------------------------------------|
| α (scale)       | 7.98       | Raw RAPM margins need 8x scaling to pts      |
| β_hca           | +2.22 pts  | Home court advantage (reasonable, typical 2–3 pts) |
| β_b2b_home      | −3.41 pts  | Home team on B2B (large — worth watching)   |
| β_b2b_away      | +1.60 pts  | Away team on B2B (hurts them, helps home)   |
| σ_residual      | 13.43 pts  | Model uncertainty — typical for pure-ratings model |
| Train RMSE      | 13.43 pts  |                                             |
| Val RMSE        | 14.39 pts  | ~1 pt degradation out-of-sample (healthy)   |
| Train corr      | 0.480      |                                             |
| Val corr        | 0.535      | Val better than train — no overfitting       |

**Baseline context:** Sharp market models achieve ~0.65–0.70 correlation. Ours at 0.54 is
reasonable for a pure player-rating model with no home-court/schedule features baked in yet.

---

## Known Model Gaps

### 1. Large edges on injury-heavy games
Games where stars are out tend to show large model-vs-market disagreements. This is partly
correct (we adjust via ESPN injury exclusions) but our RAPM may not fully capture how bad
a depleted team's depth really is.

**Example (2026-03-22):**
- GSW @ ATL: market ATL -10, us ATL -2.7 — GSW missing Curry, Butler, Horford, Moody
  Gap likely because our model rates healthy GSW players too highly in the possession-share
  weighting (their recent games include when healthy stars were playing more)
- PHI @ UTA: market PHI -6, us UTA -1.0 — both teams heavily depleted

### 2. Possession share ≠ minutes for injured-team scenarios
When a star sits, their possession share from recent history stays high in our DB, even
though they won't play. We remove injured players, but we don't redistribute their minutes
to backups. This means injured teams look weaker in our model than they should
(total lineup weight is lower), which may actually help accuracy but is architecturally wrong.

**Fix to consider:** After removing injured players, normalize remaining players' shares
back to 1.0 (add their possession share redistributed proportionally to remaining players).

### 3. Lineup estimation from possession history may lag real rotations
We use the last 15 games' possession data. If a team changed rotations recently (trade,
injury return, rookie emergence), the last-15-game average will be stale.

**Mitigation:** Reduce lookback to 7–10 games for pre-deadline predictions; post-deadline
increase for settled rosters.

### 4. sim_std ≈ 0 from Monte Carlo
Possession shares are very stable game-to-game, so Monte Carlo lineup sampling produces
nearly zero variance. Total σ ≈ σ_residual (13.4 pts). The Monte Carlo is doing what it
should — the lineup uncertainty just isn't the dominant source of variance in the NBA.
This is fine. The displayed `± 13.4` is the honest total uncertainty.

### 5. α = 7.98 is large — RAPM units vs game-point units
Raw RAPM margin ≈ (offensive_diff - defensive_diff) / 100 * pace ≈ small numbers.
The 8x scale factor absorbs the per-100 → per-game conversion. This is mathematically
correct but means small rating differences get amplified. If ratings are noisy (sparse
data on some players), the amplification could cause instability. Monitor over time.

---

## Prediction Log

### 2026-03-22 slate (6 games predicted)

| Game               | Our spread    | Market        | Edge    | Notes                          |
|--------------------|---------------|---------------|---------|--------------------------------|
| GSW @ ATL          | ATL -2.7      | ATL -10.0     | -7.3    | GSW missing 5 key players      |
| IND @ SAS          | SAS -15.1     | SAS -18.5     | -3.4    | IND missing Siakam, Haliburton |
| MIA @ HOU          | HOU -3.5      | HOU -2.0      | +1.5    | MIA missing Wiggins, Jaquez    |
| LAC @ DAL          | LAC -3.6      | LAC -7.0      | +3.4    | DAL missing Irving, Lively     |
| PHI @ UTA          | UTA -1.0      | PHI -6.0      | +7.0    | Both teams gutted by injuries  |
| MIL @ PHX          | PHX -6.8      | PHX -11.5     | -4.7    | MIL missing Giannis            |

**Observation:** All large edges coincide with injury-heavy games. When both teams have
many injuries, our model's possession-share redistribution may be inaccurate.

---

## Improvement Ideas (Prioritized)

1. **Redistribute possession shares after injury removal** — normalize remaining players
   to 100% so lineup weight doesn't drop when stars are out.

2. **Position-adjusted replacement** — when a star is out, give their possessions to
   their typical backup (from historical substitution patterns), not just normalize evenly.

3. **Recency weighting** — weight the last 5 games more heavily than games 6–15 in the
   possession-share calculation. Would catch rotation changes faster.

4. **Pace adjustment per matchup** — current pace estimate adds team pace ratings but
   doesn't account for head-to-head pace interactions (two slow teams play even slower).

5. **Track prediction accuracy over time** — once we have 30+ prediction-vs-actual pairs,
   run a post-hoc regression to check if our edges correlate with actual outcomes.
   This is the real calibration check.

6. **Benchmark against naive models** — compare to:
   - Home team always wins (baseline)
   - Previous game's result (momentum model)
   - Pure Elo (no RAPM component)

7. **Closing line value (CLV) tracking** — compare our opening predictions to closing lines
   to see if we predict where the market moves. A good model should predict line movement.
