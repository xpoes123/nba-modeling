# Model Analysis Notes

Ongoing observations about prediction quality, calibration, and areas for improvement.
Update this file as we learn from comparing predictions to actual outcomes.

---

## Calibration (as of 2026-03-21, updated 2026-03-21)

### v2: Team-specific HCA (current)

Fit on 1,041 games (2025-26 season, first 624 train / last 417 val).
Replaces single β_hca intercept with 30 team-specific HCA dummies (one per home team).

| Coefficient     | Value      | Interpretation                              |
|-----------------|------------|---------------------------------------------|
| α (scale)       | 8.48       | Raw RAPM margins need ~8.5x scaling to pts  |
| β_hca (avg)     | +2.11 pts  | League-average HCA (fallback for unknowns)  |
| β_b2b_home      | −3.20 pts  | Home team on B2B                            |
| β_b2b_away      | +2.04 pts  | Away team on B2B (hurts them, helps home)   |
| σ_residual      | 13.18 pts  |                                             |
| Train RMSE      | 13.18 pts  |                                             |
| Val RMSE        | 14.90 pts  | 1.7 pt gap — slight overfitting vs v1       |
| Train corr      | 0.509      |                                             |
| Val corr        | 0.470      | Worse than v1 (0.535) — see note below      |

**Team HCAs (notable outliers):**
- PHX +8.1, GSW +7.2, HOU +5.1, MEM +4.4 (high)
- CHA −4.2, DEN −1.7, BOS −1.2, PHI −1.1 (low)
- DEN negative is counterintuitive given altitude — likely noise (SE ≈ 2.7 pts per team)

**⚠ Overfitting warning:** Val corr dropped 0.535 → 0.470 vs v1. Added 29 parameters
(4→33) with only ~24 home games per team in training. SE per team ≈ 13/√24 ≈ 2.7 pts,
meaning estimates like PHX +8.1 are only ~2 SEs from the mean. The extreme values are
likely noise, not real signal. Ridge regularization on the team dummies would fix this.

### v1: Single global HCA (archived)

| Coefficient     | Value      |
|-----------------|------------|
| α               | 7.98       |
| β_hca           | +2.22 pts  |
| β_b2b_home      | −3.41 pts  |
| β_b2b_away      | +1.60 pts  |
| σ_residual      | 13.43 pts  |
| Val RMSE        | 14.39 pts  |
| Val corr        | 0.535      |

**Baseline context:** Sharp market models achieve ~0.65–0.70 correlation. Ours at 0.54 (v1)
is reasonable for a pure player-rating model. v2 regressed on val — ridge regularization
for team dummies is the priority next improvement.

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

1. **Ridge regularization on team HCA dummies** — current OLS team HCAs overfit (val corr
   dropped 0.535→0.470). Switch team dummies to Ridge with a small alpha to shrink extreme
   estimates toward the league average. Expected to recover the val corr regression.
   Implementation: replace `LinearRegression` with `Ridge(alpha=X, fit_intercept=False)`;
   tune X on val set. The raw_margin and B2B columns should NOT be regularized (only team
   dummies) — requires `RidgeCV` with a custom penalty mask or a two-stage fit.

2. ~~**Redistribute possession shares after injury removal**~~ — **DONE (2026-03-21)**.
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

---

## Backtest Results (2026-03-21)

### Mar 16-20, 2026 (39 games, no injury exclusions — full-roster backtest)

| Metric           | Value        | Notes                                      |
|------------------|--------------|--------------------------------------------|
| MAE              | 11.98 pts    | Better than sigma_residual=13.4 (good)     |
| RMSE             | 14.69 pts    | Consistent with calibration val RMSE=14.4  |
| Bias             | -2.33 pts    | We underestimate home advantage slightly   |
| Correlation      | 0.631        | Excellent — up from val_corr=0.535         |
| Dir accuracy     | 82.1% (32/39)| Strong winner prediction                   |

Coverage is 100%/100% for all games (no injury filtering in backtest — uses actual lineups).
Correlation of 0.631 is at the top end of where sharp models operate (~0.65-0.70).
Bias of -2.33 pts: HCA might be slightly underfit in the calibration (beta_hca = +2.22).

**Notable misfires:** MIL@UTA (-34.6 error), TOR@CHI (+28.4), MIA@CHA (-27.6), PHI@DEN (-20.5)
— all large blowouts where one team had an exceptional night. These are inherently unpredictable.

**Run command:** `PYTHONPATH=. uv run python downstream/backtest.py --start YYYY-MM-DD --end YYYY-MM-DD`
