# Game Analysis: WAS @ UTA, 2026-03-25

## Stored Prediction
- Our spread: UTA -7.85 | Market: UTA -4.5 | Edge: +3.35 (we like UTA more) | Tier: MODERATE
- Coverage: UTA 84.7% | WAS 86.2%
- B2B: home=False | away=False
- inj+5.8 = sigma_injury = 5.82 pts (extra UNCERTAINTY, not a point deduction on the spread)
  - Formula: sigma_residual(13.34) * 1.5 * (2.0 - 0.847 - 0.862) = 5.82
  - Total sigma = 14.56 (vs base 13.34)
- Win prob: Our UTA 70.5% | Market UTA 62.8%
- Market total: 240.5

---

## Team Lineup Profiles (last 15 games before 2026-03-25)

### UTA (home) — 84.7% coverage

**Excluded by ESPN injury filter:**
- Brice Sensabaugh (13/15 games, eff=8.8%) — ESPN Out; OFF=-0.51, DEF=-0.06, OVR=-0.45 — below-average player, exclusion slightly helps UTA
- Isaiah Collier (10/15 games, eff=5.3%) — ESPN Out; OFF=-2.78, DEF=+1.48, OVR=-4.27 — bad player, exclusion helps UTA
- Keyonte George (6/15 games, eff=2.7%) — ESPN Out + Fix B (6 consecutive absences >= 5 threshold); hard-excluded from profile entirely
- Lauri Markkanen (1/15 games, eff=0.2%) — ESPN Out + Fix B (14 consecutive absences); hard-excluded; also below min_games=3 threshold

**Active lineup (min_games >= 3):**

| Player | Games | Eff Share | OFF | DEF | OVR | Notes |
|--------|-------|-----------|-----|-----|-----|-------|
| Elijah Harkless | 15 | 11.8% | +1.08 | -0.63 | +1.71 | Full window starter |
| Cody Williams | 14 | 11.2% | -1.16 | +0.33 | -1.48 | Roto rookie |
| Ace Bailey | 13 | 10.8% | -1.58 | -0.12 | -1.47 | High minutes, below avg |
| Kyle Filipowski | 14 | 9.7% | +0.35 | -0.55 | +0.89 | Positive contributor |
| Bez Mbeng | 6 | 9.3% | -1.11 | +0.84 | -1.95 | Recent acquisition (first game 2026-03-13) |
| Oscar Tshiebwe | 13 | 6.7% | +0.82 | -0.83 | +1.66 | Solid big |
| Andersson Garcia | 5 | 6.5% | -0.79 | +0.50 | -1.29 | Recent acquisition (first game 2026-03-11) |
| John Konchar | 11 | 6.4% | -0.23 | -0.01 | -0.22 | Depth, near league avg |
| Blake Hinson | 8 | 3.3% | +0.18 | +0.27 | -0.09 | Fringe |
| Kevin Love | 7 | 1.9% | +0.24 | -0.54 | +0.77 | Veteran depth |
| Svi Mykhailiuk | 3 | 0.5% | +0.78 | -1.14 | +1.92 | Minimal weight (3 games) |

Team OFF = -0.31  DEF = -0.07  PACE = +0.72  Net (OFF - DEF) = -0.24

UTA is a below-average team offensively (-0.31) but near-average on defense (-0.07 = slightly above avg). Pace is elevated (+0.72), which helps total but is roughly neutral on spread.

---

### WAS (away) — 86.2% coverage

**Excluded by ESPN injury filter:**
- Tre Johnson (13/15 games, eff=6.7%) — ESPN Out; OFF=-0.88, DEF=-0.50, OVR=-0.38 — near-average player; exclusion is roughly neutral for WAS
- Alex Sarr (6/15 games, eff=4.4%) — ESPN Out; OFF=-1.67, DEF=-0.00, OVR=-1.67 — below avg; exclusion helps WAS slightly
- Trae Young (5/15 games, eff=2.7%) — ESPN Out; OFF=-1.26, DEF=+1.18, OVR=-2.43 — poor overall; exclusion helps WAS
- Kyshawn George (3/15 games, eff=0.5%) — Fix B (11 consecutive absences); hard-excluded

**Active lineup (min_games >= 3):**

| Player | Games | Eff Share | OFF | DEF | OVR | Notes |
|--------|-------|-----------|-----|-----|-----|-------|
| Will Riley | 15 | 13.6% | -2.44 | +0.60 | -3.04 | Starting usage, poor ratings |
| Bub Carrington | 15 | 12.0% | -3.32 | +0.88 | -4.20 | High usage, one of worst rated |
| Bilal Coulibaly | 13 | 9.7% | -0.89 | -0.13 | -0.76 | Decent defender |
| Anthony Gill | 13 | 9.1% | -0.87 | +0.11 | -0.97 | Depth big, below avg |
| Jaden Hardy | 13 | 8.5% | +0.04 | -0.48 | +0.52 | Only positive OA in top group |
| Jamir Watkins | 10 | 8.1% | -0.02 | -0.36 | +0.34 | League avg overall |
| Sharife Cooper | 15 | 7.7% | -1.32 | +0.89 | -2.21 | Heavy usage PG, poor |
| Tristan Vukcevic | 11 | 6.3% | -1.44 | +1.06 | -2.50 | Poor two-way |
| Justin Champagnie | 10 | 4.4% | -0.85 | -0.40 | -0.45 | Depth |
| Leaky Black | 6 | 3.7% | -0.07 | -0.03 | -0.04 | Near avg |
| Julian Reese | 5 | 2.6% | -0.51 | +0.41 | -0.93 | Fringe big |

Team OFF = -1.33  DEF = +0.28  PACE = +0.22  Net (OFF - DEF) = -1.61

WAS is significantly below average across the board. The top two possession holders (Riley -3.04, Carrington -4.20) are among the worst-rated players in the dataset. WAS defense is also poor (+0.28 = allows more than average).

---

## Raw Margin Math

Using injury-filtered lineup profiles (as stored prediction):

```
league_avg_ppp = 1.1449  |  league_avg_pace = 96.24

home_ppp (UTA) = 1.1449 + (-0.3075 + 0.2822) / 100 = 1.1447
away_ppp (WAS) = 1.1449 + (-1.3300 + -0.0726) / 100 = 1.1309

expected_pace = 96.24 + (0.7228 + 0.2242) / 2 = 96.71

raw_margin = (1.1447 - 1.1309) * 96.71 = 1.332 pts/100 * 96.71 poss = +1.33

Calibrated:
  alpha(6.097) * raw_margin(1.332) + HCA_UTA(-0.581) + B2B(0) = +7.54
  Stored (Monte Carlo mean): +7.85 (slight variance from 1000-sim stochasticity)

Market: UTA -4.5
Edge: +3.35 (we like UTA more than market)
```

**Note on inj+5.8:** This is NOT a point adjustment to the spread. It is extra uncertainty (sigma) added because both teams have coverage < 100%. The spread of 7.85 is already derived from the injury-filtered lineup profiles. The 5.82 pts widens total sigma from 13.34 (base) to 14.56, lowering win probability slightly relative to pure spread.

**Pre-injury raw (hypothetical full roster):** Running the same math with all players (no exclusions) gives raw_margin = 1.007, calibrated = 5.56. The injury exclusions actually *helped* UTA's calibrated spread by ~2.3 pts — because WAS's excluded players (Tre Johnson near-average, Alex Sarr -1.67, Trae Young -2.43) are below-average, removing them and redistributing their minutes *makes WAS look slightly worse*, while UTA's excluded players (Sensabaugh -0.45, Collier -4.27) are also below-average and removing them makes *UTA look slightly better*. Net effect: injuries on both sides slightly favor UTA in the model (+2.3 pts).

---

## Flags for David

**UTA injury exclusions (84.7% coverage):**
- Brice Sensabaugh — Out, was starting-level usage (13 games, 8.8% eff share). Below average (-0.45 OVR), so his absence slightly helps UTA's model rating. Ask David: is this a short-term injury or game-to-game?
- Isaiah Collier — Out, significant usage (10 games, 5.3% eff share). Very poor (-4.27 OVR), his absence clearly helps UTA. Fix B correctly captured this.
- Keyonte George — Out, Fix B excluded (6 consecutive absences). Was a 6-game contributor (2.7% eff) before streak. Ask David: is George expected back soon or extended absence?
- Lauri Markkanen — Out, Fix B excluded (14 consecutive absences). Last played 2026-02-23. His OVR=+4.05 is the best on the team. Fix A correctly skips injection because he is on ESPN Out list. Ask David: what is Markkanen's injury status/timeline? He is UTA's best player by a large margin — if he returns soon, the model will significantly undervalue UTA.
- Walker Kessler — ESPN Out, 0 appearances in 30-game window. Long-term out, not in any profile. Likely season-ending or extended injury.

**WAS injury exclusions (86.2% coverage):**
- Tre Johnson — Out, heaviest excluded contributor (13 games, 6.7% eff share). Near-average (-0.38 OVR). His exclusion matters for WAS coverage but is roughly neutral on model output.
- Alex Sarr — Out, 6 games in window (4.4% eff, -1.67 OVR). Below average; exclusion helps WAS slightly.
- Trae Young — Out, 5 games in window (2.7% eff, -2.43 OVR). Poor player in current ratings; exclusion is slightly positive for WAS model.
- Kyshawn George — Out, Fix B excluded (11 consecutive absences). 3 games in window before streak.
- Bradley Beal — ESPN Out list, but no possession history for WAS in the current window — he is likely no longer on WAS (traded or waived). No impact on model.

**Lauri Markkanen recency artifact check:**
- Markkanen appeared in only 1 of last 15 UTA games (2026-02-23) and has been absent 14 straight.
- Fix B hard-excluded him from the profile (streak=14 >= threshold=5). He does NOT inflate UTA's rating.
- Fix A checked: he meets all criteria (OVR +4.05 >= 2.0, 1 recent appearance <= 2, 9 extended appearances >= 5) but is blocked because he is on the ESPN Out list.
- Conclusion: Markkanen is NOT a recency artifact risk tonight. He is correctly excluded.

**Recent acquisitions (context for David):**
- Bez Mbeng joined UTA rotation 2026-03-13 (6 games). OVR -1.95, currently taking 9.3% eff share. Below average.
- Andersson Garcia joined UTA rotation 2026-03-11 (5 games). OVR -1.29. Limited history, modest weight.
- Both are near the min_games threshold; their sample sizes are small enough to treat their ratings with caution.

**Bez Mbeng recency artifact risk:** 6 games, 9.3% share. His OVR -1.95 is below average, so if he is overweighted it would hurt UTA, not inflate them. Lower priority concern.

---

## Model Logic Summary

WAS is being modeled as a genuinely poor team. Their top two usage players (Riley -3.04, Carrington -4.20) are among the worst-rated in the league, and their primary ball-handlers (Cooper -2.21, Vukcevic -2.50) are also weak. Even after removing injured players (whose exclusion was slightly positive for WAS), the team rating (OFF=-1.33, DEF=+0.28) is significantly below average.

UTA is modeled as a below-average team (NET=-0.24) but is above-average relative to WAS. The home court calibration is slightly negative for UTA (-0.58 vs +2.01 league baseline), meaning UTA plays about 2.6 pts worse than average at home from the calibration perspective. Despite this, the talent gap drives a +7.85 calibrated spread.

---

## Pre-Game Assessment
- Model confidence: MODERATE (82% dir acc)
- Our spread: UTA -7.85 vs Market: UTA -4.5 — edge of +3.35 in favor of UTA
- Key risks:
  1. **Markkanen timeline** — if he is closer to return than ESPN Out implies, market may have a read our model misses. At OVR +4.05 he would meaningfully change UTA's floor.
  2. **WAS excluded player quality** — Tre Johnson (6.7% eff) is near-average; if he actually plays despite ESPN listing, WAS gets slightly better. Trae Young (ESPN Out) would not help WAS based on current RAPM (-2.43).
  3. **Bez Mbeng/Garcia limited history** — both recent UTA acquisitions have only 5-6 games. Sample size is small; they could be better or worse than rated.
  4. **Market injury intelligence** — market at UTA -4.5 vs our -7.85 is a meaningful gap. Market may be accounting for uncertainty around UTA's injury situation (Markkanen, George both Out) more conservatively than our model, which simply excludes those players and redistributes minutes.
- Actionable? Edge is +3.35 at MODERATE tier (82% dir acc). Both teams are well below 90% coverage so sigma is elevated (14.56 vs 13.34 base). The edge is real but the uncertainty is higher than usual. WAS is modeled as a genuinely bad team with no star players to cover a spread — this supports the edge. Key question for David: is the market soft because of UTA injury uncertainty (Markkanen timeline), or because WAS is quietly better than their ratings suggest?

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: WAS 133, UTA 110
- Actual margin: UTA −23 (home_margin = 110−133 = −23; WAS won by 23)
- Our spread: UTA +7.85 (model favored UTA) | Market: UTA −4.5 | Error: +29.7 pts

### Result
- Directional: **LOSS** — predicted UTA to win, WAS won by 23
- ATS: **NO COVER** — market had UTA −4.5, UTA lost by 23

### Actual Box Score

**WAS**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Julian Reese | 30 | 26 | 17 | 0 |
| Jaden Hardy | 27 | 21 | 2 | 0 |
| Will Riley | 22 | 19 | 10 | 5 |
| Sharife Cooper | 25 | 17 | 4 | 6 |
| Bub Carrington | 24 | 12 | 2 | 3 |
| Leaky Black | 40 | 11 | 7 | 3 |
| Jamir Watkins | 29 | 8 | 6 | 2 |
| Anthony Gill | 22 | 8 | 6 | 5 |

**UTA**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Cody Williams | 37 | 24 | 4 | 1 |
| Kennedy Chandler | 34 | 14 | 1 | 8 |
| Blake Hinson | 11 | 21 | 0 | 1 |
| Ace Bailey | 29 | 15 | 5 | 3 |
| Bez Mbeng | 44 | 11 | 5 | 6 |
| Elijah Harkless | 30 | 10 | 3 | 6 |
| John Konchar | 38 | 8 | 14 | 5 |
| Oscar Tshiebwe | 17 | 7 | 8 | 4 |

### Lineup Accuracy
- **Lauri Markkanen NOT in the box score** — correctly excluded by Fix B (14 consecutive DNPs). The pre-game file was correct that he is not a recency artifact risk — he simply didn't play.
- **WAS exceeded their model rating dramatically**: Riley (−3.04 OVR) put up 19/10, Carrington (−4.20 OVR) had 12 pts — two of the worst-rated players on the roster outperformed their RAPM by a wide margin.
- **UTA's healthy lineup was weak**: Mbeng (44 min! = likely OT), Konchar (14 reb), Williams (24 pts) — but the bench depth completely collapsed.
- Kyle Filipowski (profiled, 9.7% share) did NOT appear in top minutes — likely short rotations or DNP.

### What the Model Got Right / Wrong
1. **Biggest miss of the night (+29.7 pts off)** — worst prediction of the post-mortem. Model had UTA +7.85, WAS won by 23.
2. **UTA's "healthy" roster was worse than rated** — model saw a below-average but real team (NET=−0.24); actual UTA played like a G-League squad without Markkanen, George, and Kessler. The modeled healthy players (Harkless, Ace Bailey, Cody Williams) just lost badly.
3. **WAS individual game-to-game variance is extreme** — WAS's top players (Riley −3.04, Carrington −4.20 RAPM) put up 19/10 and 12 pts respectively. RAPM can't predict hot shooting nights from bad players. WAS's very-negative-rated players are dangerous to bet against on any given night.
4. **The pre-game analysis asked the right question**: "is the market soft because of UTA injury uncertainty, or because WAS is quietly better?" Answer: WAS had a historically good offensive night against a depleted UTA team.
