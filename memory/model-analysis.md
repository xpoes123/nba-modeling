# Model Analysis Notes

Ongoing observations about prediction quality, calibration, and areas for improvement.
Update this file as we learn from comparing predictions to actual outcomes.

---

## Calibration (updated 2026-03-22)

### v3: Global HCA via Empirical Bayes — **DEPLOYED + IMPLEMENTED IN CODE (2026-03-22)**

Empirical Bayes analysis proved that team-specific HCA is undetectable with one season of
data. EB full-pooling collapses to a single global HCA.

**2026-03-22 update:** EB shrinkage is now implemented directly in `downstream/calibration.py`
(previously only in the experimental `test_hca_approach3_eb.py` and manually copied to JSON).
Re-running `calibration.py` now produces EB coefficients natively. The old v2 OLS-with-30-dummies
code is gone from the production script. 64/64 tests pass.

| Coefficient     | Value      | Interpretation                              |
|-----------------|------------|---------------------------------------------|
| α (scale)       | 8.46       | Raw RAPM margins need ~8.5x scaling to pts  |
| β_hca           | +2.01 pts  | Single global HCA (EB-collapsed)            |
| β_b2b_home      | −3.07 pts  | Home team on B2B                            |
| β_b2b_away      | +2.09 pts  | Away team on B2B                            |
| σ_residual      | 13.20 pts  |                                             |
| Val RMSE        | 14.16 pts  | Best of all approaches tested               |
| Val corr        | **0.548**  | Best of all approaches tested               |

Post-deploy backtest (Mar 16–21, 48 games): MAE=10.68, RMSE=13.46, corr=**0.664**, dir=83.3%

---

### HCA Methodology Analysis (2026-03-21)

Tested 4 approaches on 1,050 games (630 train / 420 val) + full backtest Mar 16–21 (48 games).

**Val set comparison:**

| Approach                    | Val Corr | Val RMSE | Backtest Corr | Backtest MAE | Dir Acc |
|-----------------------------|----------|----------|---------------|--------------|---------|
| v2 — OLS 30 team dummies    | 0.470    | 14.90    | —             | —            | —       |
| v1 — single global HCA      | 0.535    | 14.39    | —             | —            | —       |
| Approach 1 — global (refit) | 0.547    | 14.23    | 0.657         | 10.84        | 81.2%   |
| Approach 2 — Ridge deviations| 0.539   | 14.30    | 0.640         | 11.01        | 81.2%   |
| **Approach 3 — Emp. Bayes** |**0.548** |**14.16** | **0.664**     | **10.68**    |**83.3%**|
| Approach 4 — two-stage resid| 0.468    | 14.86    | 0.511         | 12.02        | 70.8%   |

**Key finding — Empirical Bayes result (Approach 3):**
The EB estimator uses a Normal-Normal hierarchical model:
  τ_i ~ Normal(μ, σ²_between)   [true team HCA drawn from a league distribution]
  θ̂_i ~ Normal(τ_i, σ²_within_i)  [OLS estimate = truth + noise]

σ²_between is estimated from data (method of moments):
  σ²_between = max(0, Var(θ̂_1..30) − mean(σ²_within_i))
             = max(0, 7.88 − 8.36) = **0.00**

Interpretation: the observed spread of raw team HCA estimates (range: −4.6 to +8.0 pts)
is 100% explained by sampling noise alone. σ²_within per team ≈ 13.2² / 21 ≈ 8.3, which
exceeds the raw variance of team estimates (7.88). There is no detectable real between-team
variation. All 30 teams collapse to the grand mean (+2.01 pts). B_i = 1.0 for every team.

**Caveats on the EB conclusion:**
- Assumes team HCAs are *exchangeable* (all draws from the same Normal) — doesn't model
  structural differences like Denver altitude, new arenas, or travel patterns separately.
- Method-of-moments σ²_between truncates at 0, so the conclusion is more precisely:
  "team-specific HCA is undetectable with one season + σ≈13 pts" — not "HCA is uniform."
- With 3+ seasons, σ²_between may become positive and partial pooling would kick in.
- Ridge approach (Approach 2): val RMSE still declining at alpha=100 (tried 1,5,10,25,50,100),
  suggesting optimal Ridge alpha → ∞, i.e. also collapses to global HCA. Converges to same
  answer as EB/Approach 1 from a different direction.
- Approach 4 (two-stage residual) is the worst: raw mean of per-team residuals has SE ≈
  13/√21 ≈ 2.8 pts, same variance problem as OLS, no joint shrinkage to help.

**Practical implication for predictions:**
PHX +8.08 and GSW +7.21 inflated every PHX/GSW home prediction by 6 pts. Tonight:
MIL@PHX — v2 predicted +12.5, Approach 3 predicted +6.4, actual was +3.
The overfit team HCA was the single largest correctable error source in calibration.

---

### v2: Team-specific HCA (current — to be replaced)

Fit on 1,041 games (2025-26 season, first 624 train / last 417 val).
**⚠ CONFIRMED OVERFIT** — EB analysis shows 30-team dummies are pure noise at n≈24/team.

| Coefficient     | Value      |
|-----------------|------------|
| α (scale)       | 8.48       |
| β_hca (avg)     | +2.11 pts  |
| β_b2b_home      | −3.20 pts  |
| β_b2b_away      | +2.04 pts  |
| Val RMSE        | 14.90 pts  |
| Val corr        | 0.470      |

Notable overfit outliers: PHX +8.1, GSW +7.2, CHA −4.2, DEN −1.7.
SE per team ≈ 2.7 pts; PHX +8.1 is only ~2.2σ from the mean — noise, not signal.

---

### v1: Single global HCA (archived, superseded by EB refit)

| Coefficient     | Value      |
|-----------------|------------|
| α               | 7.98       |
| β_hca           | +2.22 pts  |
| β_b2b_home      | −3.41 pts  |
| β_b2b_away      | +1.60 pts  |
| Val RMSE        | 14.39 pts  |
| Val corr        | 0.535      |

**Baseline context:** Sharp market models achieve ~0.65–0.70 correlation. v1 at 0.535 was
reasonable; v3 (EB) at 0.548 is the best we've achieved in calibration.

---

## Known Model Gaps

### 6. RAPM compression limits injury-game accuracy (diagnosed 2026-03-22)

When multiple starters are out (e.g., GSW missing Porzingis/Moody/GPII/Horford), the model
shifts its prediction by only ~1 pt. Root cause: ridge regression compresses all player ratings
toward 0. Removing a +1.40 net player and redistributing minutes to ~0 net bench players only
moves the raw margin by ~0.1 pts, which after alpha scaling is ~0.9 pts. The market moves 6–8+
pts because it understands depth cliffs that RAPM averages out.

**Key insight:** The **closing market line is the right benchmark**, not the actual game score.
Actual scores are noisy; closing lines reflect the market's best pre-game information (injuries,
public money, sharp action). For GSW @ ATL (2026-03-21): we predicted ATL +1.6, market closed
ATL -9.5, actual was ATL +16. Our gap vs market (~8 pts) is the actionable signal.

**Availability discount (implemented 2026-03-22):** Partially addresses this by downweighting
players with many DNPs. `effective_share = mean_share × (games_appeared / games_in_window)`.
Al Horford at 9/15 games gets 60% weight rather than full weight. Full-season backtest shows
modest improvement: MAE 11.06→10.84, corr 0.490→0.506, dir_acc 67.9%→68.5%. Does not close
the full gap since RAPM compression is the deeper issue.

**Ceiling:** With only player-rating-based prediction and ridge compression, the model likely
can't capture >3–4 pts of impact from any single player's absence. Possible future fixes:
positional replacement with specific backup data, or a separate "injury penalty" calibration
term fit on coverage-ratio × star-quality proxy.

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

**Fix applied (2026-03-21):** `_build_minutes_profile_from_db()` now scales all remaining
players' minutes by `1/coverage_ratio`. This restores the MinutesProfile total to ~240.
Mean predictions are unchanged (shares_from_minutes normalizes in every simulation draw),
but std_minutes are now proportional to each player's expanded role. 64/64 tests pass.

### 3. Lineup estimation from possession history may lag real rotations
We use the last 15 games' possession data. If a team changed rotations recently (trade,
injury return, rookie emergence), the last-15-game average will be stale.

**Mitigation:** Reduce lookback to 7–10 games for pre-deadline predictions; post-deadline
increase for settled rosters.

### 4. sim_std is now injury-adjusted (as of 2026-03-21)
The displayed `± X` now includes an injury uncertainty component:
  `sigma_injury = sigma_residual * 1.5 * max(0, 2.0 - home_coverage - away_coverage)`
  `total_sigma = sqrt(sim.std^2 + sigma_residual^2 + sigma_injury^2)`
Coverage ratio = fraction of normal possession weight that is healthy and available.
Examples: PHI@UTA (both ~78% coverage) → ±16.1; GSW@ATL (84% away) → ±13.8.
The scale factor 1.5 is not empirically calibrated yet — track accuracy vs sigma over time.

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

**Root cause (diagnosed 2026-03-21):**
- Our model re-normalizes remaining players to 100% of minutes. Backup players with
  neutral RAPM (~0) fill in for missing stars. The market knows these backups can't
  replicate star production at 35+ mpg (depth cliff effect).
- PHI@UTA: both teams so depleted that the HCA term (+2.22) dominates a tiny raw margin.
  UTA's rookies (Bailey off=-1.67, Garcia off=-0.86) drag their team off=-0.17, but
  PHI's depleted roster is even worse (off=-0.41). Market prices PHI better.
- RAPM is noisier for low-minutes players who suddenly take on heavy usage.

---

## Improvement Ideas (Prioritized)

1. ~~**Ridge regularization / EB shrinkage on team HCA**~~ — **RESOLVED + IMPLEMENTED (2026-03-22)**.
   EB logic from `test_hca_approach3_eb.py` merged into production `downstream/calibration.py`.
   Re-running `calibration.py` now natively produces EB-shrunk coefficients. Old OLS-with-30-dummies
   code removed from production path.

1a. ~~**Ridge regularization on team HCA dummies**~~ — **RESOLVED (2026-03-21)**.
   Tested 4 HCA approaches. Empirical Bayes analysis is decisive: σ²_between = 0, meaning
   one season of data cannot distinguish team-specific HCA from noise. All approaches that
   regularize (Ridge, EB) converge to a single global HCA (~+2.01 pts). Ridge val RMSE
   still declining at alpha=100, confirming optimal is full pooling. **Action: deploy v3
   (EB/global) by copying `calibration_coeffs_approach3.json` → `calibration_coeffs.json`.**
   Scripts: `downstream/test_hca_approach{1,2,3,4}_*.py`, results in approach{1..4}.json.

   **Also tested (2026-03-21): context-dependent HCA** — rest-differential (continuous days
   since last game), quadratic raw_margin² term, and closeness interaction HCA×1/(1+|RM|).
   None improved val_corr vs global baseline (all regressions of 0.001–0.004). Residual
   diagnostic by |raw_margin| bin showed no systematic crowd-modulated HCA pattern.
   Interpretation: Coby Yellow's intuition (HCA is state-dependent) is directionally
   reasonable but not detectable pre-game at this sample size and noise level (σ≈13 pts,
   ~630 train games). Rest coefficients had correct sign (+0.72/day home, −0.69/day away)
   but zero OOS lift — B2B already captures the most extreme fatigue case. Could revisit
   with multi-season data or as an in-game live-betting model.
   Script: `downstream/test_hca_approach5_contextual.py`

2. ~~**Availability discount for frequent-DNP players**~~ — **DONE (2026-03-22)**.
   `effective_share = mean_share × (games_appeared / games_in_window)` applied in both
   `backtest.py::_build_minutes_profile` and `predictions.py::_build_minutes_profile_from_db`.
   Full-season improvement: MAE 11.06→10.84, corr 0.490→0.506, dir_acc 67.9→68.5%.
   This also fixes the Al Horford problem: 9/15 games → 60% weight instead of 100%.

3. ~~**Redistribute possession shares after injury removal**~~ — **DONE (2026-03-21)**.
   `_build_minutes_profile_from_db()` now scales remaining players' synthetic minutes by
   `1/coverage_ratio` after injury exclusion, so MinutesProfile total stays ~240.
   **Note:** This is mean-neutral (predicted spreads unchanged) because `shares_from_minutes()`
   inside `simulate_game()` already normalizes. The fix makes the representation semantically
   correct and std_minutes proportional to actual usage.

3. **Position-adjusted replacement** — when a star is out, give their possessions to
   their typical backup (from historical substitution patterns), not just normalize evenly.

4. **Recency weighting** — weight the last 5 games more heavily than games 6–15 in the
   possession-share calculation. Would catch rotation changes faster.

5. **Pace adjustment per matchup** — current pace estimate adds team pace ratings but
   doesn't account for head-to-head pace interactions (two slow teams play even slower).

6. **Track prediction accuracy over time** — once we have 30+ prediction-vs-actual pairs,
   run a post-hoc regression to check if our edges correlate with actual outcomes.
   This is the real calibration check. Use `downstream/backtest.py` for this.

7. **Benchmark against naive models** — compare to:
   - Home team always wins (baseline)
   - Previous game's result (momentum model)
   - Pure Elo (no RAPM component)

8. **Closing line value (CLV) tracking** — compare our opening predictions to closing lines
   to see if we predict where the market moves. A good model should predict line movement.

9. **Matchup-specific adjustments via play style clustering** — RAPM measures each player
   against the average opponent, but certain team style matchups create systematic edges that
   the current model misses (e.g., a physical paint-dominant team may consistently
   neutralize pace-and-space offenses).

   **Approach:**
   - Cluster all 30 teams into 4–6 style archetypes using season-level features derived
     from the DB: pace rating, 3PA tendency, paint possession share, offensive rebound rate,
     pick-and-roll frequency (all computable from possession-level data we already have).
   - Fit a cluster-pair interaction term in calibration: does model error correlate with
     (home_cluster, away_cluster)? If a "slow-halfcourt" cluster consistently outperforms
     model predictions vs. "fast-transition" clusters, add that interaction as a calibration
     feature.
   - Alternatively, track per-matchup residuals over the season: for each (team_A, team_B)
     style combination, do we systematically over- or under-predict? At n≈2–4 H2H games per
     pair per season, direct team-vs-team residuals will be noise-dominated (same EB problem
     as team HCA). Cluster-level aggregation pools enough games to potentially detect signal.

   **Why this is worth exploring:**
   - RAPM is fit on all opponents equally — a player's rating reflects their average performance
     against the league mix. When the opponent is systematically outside that mix (extreme pace,
     extreme size, unique defensive scheme), RAPM under- or over-estimates true impact.
   - Examples David flagged: OKC vs SAS/MIL, LAL vs ORL — worth tracking whether our model
     shows systematic residuals for those matchup types.

   **Prerequisites:** Need 2+ seasons for robust cluster-pair signal. Flag for revisit at
   season end or when multi-season data is available. Can prototype now with current season
   using leave-one-out validation on cluster-pair residuals.

   **Data already available:** pace_rating, offense, defense all in current_ratings.
   Could cluster today with k-means on (offense, defense, pace) — 3 features, 30 teams.
   Verify with backtest before adding any interaction term to calibration_coeffs.json.

---

## Backtest Results

### Full Season 2025-26 (1002 games, EB calibration + availability discount)

Run 2026-03-22 with EB calibration + availability discount applied.

| Metric       | Baseline (v2 OLS) | With EB + avail. discount | Delta   |
|--------------|-------------------|---------------------------|---------|
| MAE          | 11.06 pts         | 10.84 pts                 | −0.22   |
| Correlation  | 0.490             | 0.506                     | +0.016  |
| Dir accuracy | 67.9% (680/1002)  | 68.5% (686/1002)          | +0.6%   |
| Bias         | n/a               | +0.39 pts                 |         |

Skipped: 48 games (insufficient early-season lineup history).

### Mar 21, 2026 — 9 games (EB calibration + availability discount)

| Game       | Predicted | Actual | Error  | Notes                              |
|------------|-----------|--------|--------|------------------------------------|
| OKC @ WAS  | −17.1     | −21    | +3.9   |                                    |
| MEM @ CHA  | +10.6     | +23    | −12.4  | MEM B2B; lineup miss               |
| LAL @ ORL  | +1.3      | −1     | +2.3   |                                    |
| CLE @ NOP  | −3.6      | −5     | +1.4   |                                    |
| GSW @ ATL  | +1.6      | +16    | −14.4  | Both B2B; GSW missing 4 (see below)|
| MIA @ HOU  | −0.1      | +1     | −1.1   | HOU B2B                            |
| IND @ SAS  | +17.1     | +15    | +2.1   |                                    |
| PHI @ UTA  | −1.8      | −10    | +8.2   |                                    |
| MIL @ PHX  | +7.2      | +3     | +4.2   |                                    |

MAE=5.56, RMSE=7.28, Corr=0.846, Dir=8/9 (88.9%).

**GSW @ ATL deep dive:** → [Full analysis](game-analyses/2026-03-21-GSW-ATL.md)
Model predicted ATL +0.86 (home margin). Closing market: ATL -9.5. Actual: ATL +16.
Root causes: (1) ATL depth drag — Okongwu/Risacher/Landale/Kispert hold 39% of possessions
at −1 to −2.5 overall, diluting team OFF to only +0.268. (2) Formula near-cancellation —
(ATL_off − GSW_def) ≈ (GSW_off − ATL_def) ≈ 0, raw_margin only 0.032 pts/game. (3) Curry +
Butler already absent from 15-game window — model correctly baked in, but gap vs market is
still 9 pts because market values depth cliff more than RAPM linear averages do.

### Mar 16–21, 2026 — HCA approach comparison (48 games, Approach 3 coefficients)

Run with Approach 3 (EB/global HCA) coefficients — the best-performing approach.

| Metric       | Value          | Notes                                          |
|--------------|----------------|------------------------------------------------|
| MAE          | 10.68 pts      | Best of 4 approaches tested                    |
| RMSE         | 13.46 pts      |                                                |
| Bias         | −2.18 pts      | Slight under-prediction of home margin         |
| Correlation  | **0.664**      | At top end of sharp model range (0.65–0.70)    |
| Dir accuracy | 83.3% (40/48)  |                                                |

### Mar 21, 2026 — 9 games (v2 current coefficients, actual results)

9 of 19 scheduled games successfully ingested (10 failed: NULL home_team_id or OT 4-player).

| Game                  | Predicted | Actual | Error  | Notes            |
|-----------------------|-----------|--------|--------|------------------|
| OKC @ WAS             | −17.5     | −21    | +3.5   |                  |
| MEM @ CHA             | +3.5      | +23    | −19.6  | MEM B2B; big miss|
| LAL @ ORL             | +3.0      | −1     | +4.0   |                  |
| CLE @ NOP             | −5.7      | −5     | −0.7   | Near-perfect      |
| GSW @ ATL             | −1.6      | +16    | −17.6  | Both B2B; injury miss |
| MIA @ HOU             | +3.1      | +1     | +2.1   | HOU B2B           |
| IND @ SAS             | +12.8     | +15    | −2.2   | Near-perfect      |
| PHI @ UTA             | −1.4      | −10    | +8.6   |                  |
| MIL @ PHX             | +12.5     | +3     | +9.5   | PHX HCA overfit   |

MAE=7.53 · Corr=0.655 · Dir=7/9 (77.8%). MIL@PHX error (+9.5) directly attributable to
inflated PHX HCA (+8.08 in v2 vs ~+2.0 actual). With v3 coefficients Approach 3 predicted
PHX +6.4, cutting the error from 9.5 → 3.4 pts on that game alone.

### Mar 16–20, 2026 (39 games, v2 coefficients)

| Metric       | Value          | Notes                                      |
|--------------|----------------|--------------------------------------------|
| MAE          | 11.98 pts      |                                            |
| RMSE         | 14.69 pts      |                                            |
| Bias         | −2.33 pts      | Consistent under-prediction of home margin |
| Correlation  | 0.631          |                                            |
| Dir accuracy | 82.1% (32/39)  |                                            |

Notable misfires: MIL@UTA (−34.6), TOR@CHI (+28.4), MIA@CHA (−27.6), PHI@DEN (−20.5)
— large blowouts, inherently unpredictable.

**Run command:** `PYTHONPATH=. uv run python downstream/backtest.py --start YYYY-MM-DD --end YYYY-MM-DD`
