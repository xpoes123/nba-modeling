# Model Analysis Notes

Ongoing observations about prediction quality, calibration, and areas for improvement.
Update this file as we learn from comparing predictions to actual outcomes.

---

## Calibration (updated 2026-03-22)

### v4: Defense sign bug fix + EB — **DEPLOYED (2026-03-22)**

**Breaking change:** Fixed a fundamental sign bug in `compute_raw_margin` in `downstream/team_ratings.py`
(and the inline duplicate in `downstream/calibration.py::_build_team_ratings_for_game`).

**The bug:** RAPM defense coefficients follow the convention `positive = bad defender (allows more pts)`,
`negative = good defender (allows fewer pts)`. The formula was:
```python
# BUGGY — subtracts defense, so good away defense (negative) ADDS to home scoring (backwards!)
home_ppp = league_avg_ppp + (home_off - away_def) / 100
```
Fix: changed `-` to `+` for defense terms:
```python
# CORRECT — bad away defense (positive) → home scores more ✓
home_ppp = league_avg_ppp + (home_off + away_def) / 100
```
This bug caused the model to treat good defenses as if they boosted the opponent's offense.
The calibration α (8.46→6.14) was inflating raw margins to partially compensate.

With the corrected formula, team-specific HCA variation is now detectable (σ²_between = 4.9966 vs 0).
Val corr improved from 0.548 → **0.586**, and directional accuracy improved from 68.6% → **70.1%**.

| Coefficient     | Value      | Interpretation                              |
|-----------------|------------|---------------------------------------------|
| α (scale)       | 6.1435     | Lower than v3 (8.46) — raw margins now bigger|
| β_hca           | +2.09 pts  | Global HCA (EB grand mean)                  |
| β_b2b_home      | −2.40 pts  | Home team on B2B                            |
| β_b2b_away      | +1.28 pts  | Away team on B2B                            |
| σ_residual      | 13.01 pts  |                                             |
| σ²_between      | **4.9966** | Real team HCA variation now detectable!     |
| avg shrinkage   | 0.618      | Partial pooling (was 1.0 / full pool in v3) |
| Val corr        | **0.586**  | Up from 0.548 in v3                         |
| Train corr      | 0.508      |                                             |

Full-season backtest (1002 games): MAE=10.81, corr=0.512, dir=**70.1%** (702/1002).
Baseline (buggy formula): corr=0.506, MAE=10.84, dir=68.6% (687/1002).

**Notable team HCAs (raw → shrunk):** PHX +8.28→+4.31, GSW +7.91→+4.38, DEN -5.74→-0.72.

---

### v3: Global HCA via Empirical Bayes — **SUPERSEDED by v4 (2026-03-22)**

Empirical Bayes analysis proved that team-specific HCA is undetectable with one season of
data using the (then-buggy) formula. After the defense sign fix, σ²_between = 4.9966 — real
team variation IS detectable. The v3 "all teams collapse to global mean" conclusion was an
artifact of the sign bug inflating noise and masking signal.

| Coefficient     | Value      | Notes                                       |
|-----------------|------------|---------------------------------------------|
| α (scale)       | 8.46       | Inflated to compensate for sign bug         |
| β_hca           | +2.01 pts  | EB grand mean                               |
| β_b2b_home      | −3.07 pts  |                                             |
| β_b2b_away      | +2.09 pts  |                                             |
| σ²_between      | **0.00**   | Was 0 (artifact of sign bug)                |
| Val corr        | 0.548      | Superseded by v4 (0.586)                    |

Full-season backtest (buggy formula, EB calibration): corr=0.506, dir=68.6%

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

### 7. Blowout magnitude compression (diagnosed 2026-03-23)

On large talent mismatches, the model's calibration α=6.097 compresses raw margin predictions
to roughly half the actual blowout severity. Three games on 2026-03-23: ATL +39 (pred -8.5),
POR +35 (pred -16.1), LAC +33 (pred -8.6). All direction-correct; all 24–30 pts above spread.

**Root cause:** Ridge-compressed RAPM ratings + linear calibration produces a roughly Gaussian
prediction centered on the "expected" margin. Actual NBA games have fat tails — when a weak team
plays a strong home team and the weak team is also missing key players, outcomes can cascade.
The model's σ=13.3 pts residual correctly represents average games but the tails are fatter.

**Practical implication:** When our model says `ATL -8`, the true distribution has a longer right
tail than our Gaussian assumption implies. We're systematically underconfident about blowouts.
On games where model predicts 10+ pts home favorite AND market agrees (edge < 3 pts), the actual
margin is often 20+. Do not fade these games on "model shows tighter spread than market."

**Market alignment check:** On MEM@ATL, market had -14 (vs our -8.5). Market was closer but also
badly wrong (-14 vs +39). ATL 146 pts is a true regime-change game beyond any model's distribution.
The 3 blowouts today were distributed: ATL (model+market both badly off), POR (model slightly
above market), LAC (market well above model). Market had better calibration on the latter two.

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

### 2026-03-23 slate (10 games predicted) — context notes

| Game               | Our spread    | Market        | Edge    | David's context                                |
|--------------------|---------------|---------------|---------|------------------------------------------------|
| TOR @ UTA          | TOR -6.1      | TOR -13.0     | +6.9    | TOR on B2B + Jazz HCA stacking — not a real edge |
| MEM @ ATL          | ATL -8.5      | ATL -14.0     | -5.5    | ATL should be higher; MEM gutted               |
| MIL @ LAC          | LAC -8.7      | LAC -13.0     | -4.3    | MIL playing poorly; LAC inconsistent recently  |
| GSW @ DAL          | DAL -2.0      | GSW -2.5      | +4.5    | LOW SIGNAL; directional flip                   |
| OKC @ PHI          | OKC -11.9     | OKC -15.5     | +3.6    | HIGH; agree on direction, disagree on margin   |
| LAL @ DET          | LAL -0.1      | LAL -2.0      | +1.9    | Cade out (collapsed lung); DET 83% coverage    |

**Tanking context (David 2026-03-23):** Kings, Jazz, Wizards, Nets are tanking this season.
No tanking penalty implemented yet — see improvement item #10 in backlog.

---

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

0. ~~**Confidence threshold gate**~~ — **DONE (2026-03-22)**. `_confidence_tier()` helper added to predictions.py; per-game tier label printed in `_print_report()`; confidence breakdown table added to `backtest.py` summary output. Thresholds: HIGH≥10 (86%), MODERATE≥7 (82%), FAIR≥5 (79%), LOW SIGNAL<5 (<73%).

0a. ~~**Fix calibration oracle vs. lookback mismatch**~~ — **DONE (2026-03-22)**. `_build_team_ratings_for_game()` in calibration.py now uses the same 15-game recency-weighted lookback as backtest/predictions instead of oracle game possessions. Alpha 6.14→6.10 (minimal), B2B coefficients shifted more (home -2.40→-3.05, away +1.28→+2.29). Full-season backtest: MAE 10.81→10.76, corr 0.512→0.520, dir 70.1%→69.6%. Essentially a wash on accuracy but conceptually correct now.

0b. ~~**Recency weighting in lineup lookback**~~ — **DONE (2026-03-22)**. `_RECENCY_DECAY=0.85` added to backtest.py, predictions.py, and calibration.py. Lookback functions now weight most-recent game slot=1.0, each older slot ×0.85. Addresses December-January accuracy dip from trade-deadline roster flux.

0c. **HCA recalibration** — current +2.01 (v5) causes ~+4pp home bias (we predict home wins 58.4% vs actual 54.4%). Could reduce to +1.5-1.7 pts. OR wait for more live prediction data to track empirically. Not high-priority since the bias is small and EB shrinkage is already doing the right thing.

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

11. **Fix A extension for 4+ week absences (confirmed need 2026-03-23)** — The current
    `RETURNING_PLAYER_EXTENDED_LOOKBACK=30` only reaches ~3-week absences. Two HIGH-impact
    misses on 2026-03-23 were caused by returning stars with 4-6 week absences not being
    injected: Siakam (5/15 games, IND upset ORL), Moody + Porzingis (both sparse, GSW beat DAL).
    **Options:**
    - Increase `RETURNING_PLAYER_EXTENDED_LOOKBACK` to 45 or 60 games — but risks injecting
      stale pre-injury ratings for players who've changed role or team.
    - Add a `returning_stars_override` list David can manually provide pre-game (quick fix).
    - Check `nba_api.PlayerGameLog` for each ESPN-Active player to see if they're returning
      from a documented absence, then inject from their last N games before the absence.
    **Constraint:** Confirm lookback window change with David. Do not increase autonomously.

12. **Recency artifact filtering for 1-game sparse players (confirmed 2026-03-23)** —
    Lauri Markkanen appeared at 13.7% weighted share (1 game, first game back from long injury)
    but DNP'd the next game. Kennedy Chandler appeared at 15.5% (1 game) and DID play. The
    problem: when a player's first game back is recent (slot 0), they get weight=1.0 even if
    it's their only game in 15. This inflates UTA's apparent quality by ~8 pts of predicted margin.
    **Fix idea:** Cap single-game appearances at a lower weight (e.g., 0.3) unless they also
    appeared in 2+ games in the extended lookback window. This reduces noise from one-off
    returns without removing genuinely returning players.

10. **Tanking penalty** — teams with lottery incentives play to lose in the final ~20 games of the
    season. RAPM ratings don't capture this — a tanking team's starters may be healthy but
    intentionally losing close games or resting key players without formal injury designation.
    **2025-26 tanking teams (confirmed by David 2026-03-23):** Kings, Jazz, Wizards, Nets.
    **Implementation idea:** Add a binary `is_tanking` flag to the spread formula as a calibration
    feature. Requires knowing which teams own their draft pick (changes year to year — David to
    provide at season start). Apply a fixed penalty (estimate: -2 to -4 pts against the tanking
    team) for games in the final 3-4 weeks of the season.
    **Constraint:** Need to determine which draft picks these teams own/protect — David is source
    of truth for this. Do not hardcode picks without confirming with David.
    **Note:** Jazz are both injury-depleted AND tanking — double-discount applies.

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

## Backtest Deep-Dive Diagnostics (2026-03-22)

**Run:** full season backtest (Oct 2024 – Mar 21 2026, 1002 games, v4 calibration)

### Confidence Threshold — BIGGEST ACTIONABLE FINDING

The model's directional accuracy depends heavily on how confident its prediction is:

| Threshold    | N games | Dir Acc | Coverage |
|--------------|---------|---------|----------|
| |pred| >= 0  | 1002    | 69.9%   | 100%     |
| |pred| >= 3  |  722    | 73.7%   |  72%     |
| |pred| >= 5  |  512    | 78.7%   |  51%     |
| |pred| >= 7  |  379    | 82.3%   |  38%     |
| |pred| >= 10 |  215    | 86.5%   |  22%     |
| |pred| >= 12 |  135    | 89.6%   |  14%     |

**Implication:** Below |pred| < 5 pts (49% of games), the model has ~61-62% directional
accuracy — barely above chance. **Only predictions with |pred| >= 7-10 pts carry real signal.**
This should gate which predictions are flagged as actionable.

### Error Distribution (fat tails)

| Metric                   | Value    |
|--------------------------|----------|
| Median abs error         | 8.80 pts |
| MAE                      | 10.81    |
| 75th percentile          | 15.45    |
| 90th percentile          | 22.47    |
| 95th percentile          | 27.00    |
| Max abs error            | 50.36    |
| Top 5% games → % sq err  | 29.7%    |
| Top 10% games → % sq err | 45.7%    |

**Fat tail problem:** The top 10% of games (100 games) contribute 46% of total squared error.
The model is decent on 89% of games (MAE ~9 pts) but catastrophic on blowouts.

### Blowout Games (|actual| > 25 pts)

114 games (11.4%) are blowouts. MAE on blowouts: **24.86 pts** vs **9.00 pts** on normal games.
Despite terrible magnitude accuracy, direction accuracy on blowouts is **92.1%** — the model
knows who's better even when it can't predict by how much. Average |pred| on 30+ pt blowouts
is only 8.6 pts — severe compression from ridge regression.

### Spread Compression

- Pred range: [-18.2, +21.6], std=7.59
- Actual range: [-55, +54], std=15.97
- Compression ratio: **0.475** — predictions are 47.5% as variable as reality
- Regression slope (actual ~ pred): **1.077**
  → alpha=6.14 is ~7.7% too small for lookback-estimated lineups
  → Adjusted alpha estimate: **~6.61**

Root cause: calibration trains alpha on actual game possession shares (oracle knowledge of who
played); backtest+predictions use 15-game lookback estimates. Oracle lineups have different
signal than estimated lineups. Alpha fit on oracle data is slightly undersized for the estimation case.

### Home Team Bias

- We predict home wins: **58.4%** of games
- Home teams actually win: **54.4%** of games
- Overpredict home by **+4.0pp** — HCA of +2.09 pts is slightly inflated

### Monthly Breakdown (look-ahead bias / seasonal effects)

| Month   | Games | MAE   | Corr  | Dir%  |
|---------|-------|-------|-------|-------|
| Oct     |   32  | 11.00 | 0.403 | 65.6% |
| Nov     |  218  |  9.70 | 0.596 | 72.5% |
| **Dec** |**194**|**11.23**|**0.381**|**67.0%**|
| **Jan** |**228**|**11.38**|**0.425**|**64.9%**|
| Feb     |  166  | 11.50 | 0.583 | 68.7% |
| Mar     |  164  | 10.24 | 0.598 | 79.3% |

December-January are systematically the worst months despite being mid-season with ample data.
Likely cause: trade deadline flux (Jan-Feb trades; some start in December). The 15-game lookback
slowly absorbs trades but can take 15+ games to fully flush pre-trade data. March being best (79.3%)
is partly settled rotations, partly the RAPM ratings being freshest relative to that period.

### B2B Breakdown

| Type    | N    | MAE   | Dir%  |
|---------|------|-------|-------|
| B2B     |  309 | 11.83 | 68.0% |
| Non-B2B |  693 | 10.35 | 70.9% |

B2B games are harder (expected) but the gap is modest.

---

## Backtest Results

### Full Season 2025-26 (1002 games) — cumulative improvement history

| Version       | Change                                          | MAE    | Corr  | Dir acc         |
|---------------|-------------------------------------------------|--------|-------|-----------------|
| v2 OLS        | baseline                                        | 11.06  | 0.490 | 67.9% (680)     |
| v3 EB         | EB calibration + avail. discount                | 10.84  | 0.506 | 68.6% (687)     |
| v4 fixed      | defense sign fix + recalibrate                  | 10.81  | 0.512 | 70.1% (702)     |
| **v5 lookback** | **recency weighting + calibration refit + confidence gate** | **10.76** | **0.520** | **69.6% (697)** |

Skipped: 48 games (insufficient early-season lineup history).

**v5 changes (2026-03-22):**
1. Exponential recency weighting (`_RECENCY_DECAY=0.85`) in all lineup lookback functions — most recent game slot=1.0, each older slot ×0.85. Improves Dec-Jan accuracy (trade deadline flux).
2. Calibration refit on lookback lineups (not oracle game possessions) — eliminates train/test distribution mismatch. Alpha 6.14→6.10 (minimal change), but B2B coefficients shifted substantially (see below) because lookback doesn't see who actually sat in B2B games.
3. Confidence tier gate in both backtest output and prediction report (|pred|>=10=HIGH/86%, >=7=MODERATE/82%, >=5=FAIR/79%, <5=LOW SIGNAL/<73%).

**v5 calibration coefficients:**

| Coefficient     | v5 (current)   | v4 (superseded) |
|-----------------|----------------|-----------------|
| alpha           | 6.097          | 6.14            |
| beta_hca        | +2.01 pts      | +2.09 pts       |
| beta_b2b_home   | −3.05 pts      | −2.40 pts       |
| beta_b2b_away   | +2.29 pts      | +1.28 pts       |
| sigma_residual  | 13.34 pts      | 13.01 pts       |
| sigma2_between  | 7.703          | 4.997           |
| avg shrinkage   | 0.537          | 0.618           |
| val_corr        | 0.562          | 0.586           |

Note: B2B coefficients increased substantially because lookback lineups don't capture who sat in B2B games — the B2B dummy must now carry the full fatigue signal explicitly. Val_corr dropped slightly (0.586→0.562) because validation now uses the same noisy estimation approach as training instead of oracle data.

**v4 key insight:** The sign bug caused calibration α to inflate (8.46) to partially offset the
backwards defense contribution. After the fix, α dropped to 6.14 and σ²_between became detectable
(4.9966), meaning team-specific HCA adjustments are now meaningful and partially-pooled (B_i ≈ 0.6
instead of 1.0 full-pool). Getting 15 more game directions right (687→702) is the headline gain.

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

**GSW @ ATL deep dive:** → [Full analysis](game-analyses/2026-03-21/GSW-ATL.md)
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

---

### Post-Mortem: 2026-03-23
- **Games:** 10 predicted | **Directional:** 6-4 (60.0%) | **HIGH ATS:** 2-1 (67%) | **MODERATE ATS:** 2-1 (67%) | **MAE (all):** 15.89 pts | **MAE (HIGH only):** 14.48 pts
- **Biggest miss:** MEM@ATL — predicted ATL -8.5, actual ATL +39 (error -30.54) — ATL exploded for 146 pts
- **Biggest hit:** LAL@DET — predicted LAL -0.1, actual DET +3 (error -3.12) — near-perfect pick'em call
- **Directional wins:** SAS@MIA, OKC@PHI, MEM@ATL, TOR@UTA, BKN@POR, MIL@LAC
- **Directional losses:** LAL@DET, IND@ORL, HOU@CHI, GSW@DAL
- **Key pattern — blowout magnitude compression**: Three games (ATL +39, POR +35, LAC +33) ended 24-30 pts above our spread. All three were direction-correct. The model's calibration α=6.097 compresses raw margins significantly; large talent mismatches produce blowouts the model consistently underestimates. Market was closer but also badly wrong on ATL (+39 vs mkt -14).
- **Key pattern — returning players**: Two direction misses linked to Fix A failure. IND@ORL: Siakam (37 pts) only 5/15 games in window. GSW@DAL: Moody + Porzingis both sparse, combined for 45 pts. Pre-game flagged both as risks; missed anyway.
- **Key pattern — star individual lines overcome by depth**: HOU@CHI — Durant 40 + Sengun 33/13/10, still lost. RAPM stars producing individually ≠ team win when depth is a mismatch.
- **Giannis/injury intelligence gap**: MIL@LAC: Giannis sat (pre-game correctly flagged as risk). LAC@MIL: market had -13, we had -8.6. Market -4.38 gap was correct signal — market knew Giannis out. Similar for PHI@OKC: market knew Maxey+Embiid out.
- **Recency artifact confirmed**: TOR@UTA — Markkanen appeared at 13.7% with 1 game but DNP'd. Error inflated by ~+8 pts. Kennedy Chandler (1/15) was real this time (29 min). Sparse = noise for players who happened to play 1 game; need better sparse filtering.
- **Full analyses:** [LAL@DET](game-analyses/2026-03-23/LAL-DET.md) | [IND@ORL](game-analyses/2026-03-23/IND-ORL.md) | [SAS@MIA](game-analyses/2026-03-23/SAS-MIA.md) | [OKC@PHI](game-analyses/2026-03-23/OKC-PHI.md) | [MEM@ATL](game-analyses/2026-03-23/MEM-ATL.md) | [HOU@CHI](game-analyses/2026-03-23/HOU-CHI.md) | [TOR@UTA](game-analyses/2026-03-23/TOR-UTA.md) | [GSW@DAL](game-analyses/2026-03-23/GSW-DAL.md) | [BKN@POR](game-analyses/2026-03-23/BKN-POR.md) | [MIL@LAC](game-analyses/2026-03-23/MIL-LAC.md)

---

### Post-Mortem: 2026-03-24
- **Games:** 4 predicted, 4 completed | **Directional:** 4-0 (100%) | **MAE:** 8.43 pts
- **ATS (our spread):** 3-1 (SAC@CHA ✓, ORL@CLE ✓, DEN@PHX ✓, NOP@NYK ✗) | **ATS (market spread):** 1-3 (only SAC@CHA covered market)
- **Biggest miss:** SAC@CHA — predicted CHA –15.01, actual CHA +44 (error –28.99) — classic blowout compression; both Achiuwa and Hayes scratched day-of, SAC was historically depleted
- **Best predictions:** ORL@CLE (error –0.48) and DEN@PHX (error +0.84) — both LOW SIGNAL games where market was off by 5–6 pts and our number was essentially exact
- **Directional wins:** SAC@CHA ✓, NOP@NYK ✓, ORL@CLE ✓, DEN@PHX ✓
- **Key pattern — two LOW SIGNAL games were the best predictions:** ORL@CLE (–0.48 error) and DEN@PHX (+0.84 error) were our two most accurate predictions. Both were flagged LOW SIGNAL. Market was badly wrong on both (CLE –10.5 vs actual +5; DEN –5 vs actual –2). When LOW SIGNAL is driven by a known structural factor (HCA coefficient, confirmed injury exclusion) rather than pure noise, the model number can still be informative — even if not bet-worthy.
- **Key pattern — blowout compression again (SAC@CHA):** SAC had 4 season-ending absences + Achiuwa + Hayes both scratched day-of. CHA won by 44. Direction correct; magnitude off by 29 pts. Market (–17) was also badly wrong. When coverage ≤80% AND day-of questionables scratch, the outcome is typically a blowout far exceeding any model.
- **Key pattern — PHX HCA validated:** PHX HCA = +5.63 (highest in our calibration). DEN (Jokic, Murray) is far superior on talent but won by only 2 on the road. The PHX home environment is real. Do not dismiss the HCA coefficient as a calibration artifact.
- **Key pattern — Jeremiah Fears model outlier (NOP@NYK):** Fears rated –1.42 overall but scored 21 pts in 20 min off the bench. Negative RAPM likely reflects context (bad lineups) not individual skill. Worth watching going forward.
- **Full analyses:** [SAC@CHA](game-analyses/2026-03-24/SAC-CHA.md) | [NOP@NYK](game-analyses/2026-03-24/NOP-NYK.md) | [ORL@CLE](game-analyses/2026-03-24/ORL-CLE.md) | [DEN@PHX](game-analyses/2026-03-24/DEN-PHX.md)

---

### Post-Mortem: 2026-03-25
- **Games:** 12 predicted | **Directional:** 7-5 (58.3%) | **HIGH tier directional:** 5-0 (100%) | **HIGH tier ATS:** 2-3 | **MAE (all):** 13.5 pts | **MAE (HIGH only):** 10.1 pts
- **Biggest miss:** WAS@UTA — predicted UTA +7.85, actual WAS +23 (error +29.7 pts). UTA lost by 23 despite model seeing them as a 7.85-pt home favorite.
- **Best prediction:** HOU@MIN — predicted MIN +1.2, actual MIN +2 (error −0.8 pts). Near-perfect. Also correctly flipped direction vs market (market had HOU −1.5).
- **Directional wins (7):** OKC@BOS ✓, SAS@MEM ✓, LAL@IND ✓, HOU@MIN ✓, DAL@DEN ✓, BKN@GSW ✓, MIL@POR ✓
- **Directional losses (5):** ATL@DET ✗, MIA@CLE ✗, CHI@PHI ✗, TOR@LAC ✗, WAS@UTA ✗
- **HIGH tier went 5-0 directional** (LAL, SAS, DEN, GSW, POR) — consistent with 86% historical accuracy. All 5 correct.
- **Key pattern — adverse edge ≥4 pts = market knows, do not bet against**: CHI@PHI (edge −7.68, PHI won by 20 — Embiid/George both returned), TOR@LAC (edge −4.71, LAC won by 25 — Kawhi/Garland both active). Pre-game files correctly identified both as "do not bet" situations. Model missed returning stars on both — same Fix A / long-return-window blind spot.
- **Key pattern — blowout compression on large mismatches**: SAS@MEM (pred −14.5, actual −25), MIL@POR (pred +10.4, actual +31). 4th and 5th data points confirming this pattern. Model undershoots blowout magnitude by 10-20 pts consistently.
- **Key pattern — B2B coefficient underestimates fatigue**: MIA@CLE — CLE on B2B, model gave −3.05 penalty, CLE lost by 17 (miss of 19.8 pts). This is the 2nd time a B2B home team lost badly when model still predicted them as favorites post-penalty. The −3.05 coefficient may need upward adjustment.
- **Key pattern — HIGH tier coverage gap risk**: BKN@GSW — model predicted GSW blowout (−12.3), GSW barely won by 3. BKN had 79% coverage (unknown players competed hard). When HIGH tier games have coverage < 85% for one team, treat as MODERATE confidence — elevated sim_std (14.35) was the warning signal.
- **Key pattern — individual game variance from bad-rated players**: WAS@UTA — Riley (−3.04 RAPM) 19/10, Carrington (−4.20 RAPM) 12 pts. Worst-rated players can have career nights. Avoid fading bad teams on spread when they're getting 7+ pts.
- **Star-heavy team vs. depth pattern**: HOU had Durant 30 + Sengun 30 (likely OT), still lost to MIN's balanced attack. Confirmed pattern from 3/23.
- **Full analyses:** [ATL@DET](game-analyses/2026-03-25/ATL-DET.md) | [LAL@IND](game-analyses/2026-03-25/LAL-IND.md) | [CHI@PHI](game-analyses/2026-03-25/CHI-PHI.md) | [OKC@BOS](game-analyses/2026-03-25/OKC-BOS.md) | [MIA@CLE](game-analyses/2026-03-25/MIA-CLE.md) | [SAS@MEM](game-analyses/2026-03-25/SAS-MEM.md) | [WAS@UTA](game-analyses/2026-03-25/WAS-UTA.md) | [HOU@MIN](game-analyses/2026-03-25/HOU-MIN.md) | [DAL@DEN](game-analyses/2026-03-25/DAL-DEN.md) | [BKN@GSW](game-analyses/2026-03-25/BKN-GSW.md) | [MIL@POR](game-analyses/2026-03-25/MIL-POR.md) | [TOR@LAC](game-analyses/2026-03-25/TOR-LAC.md)
