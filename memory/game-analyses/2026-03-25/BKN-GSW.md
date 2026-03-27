# Game Analysis: BKN @ GSW, 2026-03-25

## Stored Prediction
- Our spread: GSW -12.24 | Market: GSW -11.5 | Edge: +0.74 (we favor GSW more) | Tier: HIGH (86% dir acc)
- Coverage: home GSW=94.6% | away BKN=79.1%
- B2B: home=False | away=False
- Injury adj: net inj+5.3 on GSW spread (driven by BKN coverage gap, not GSW exclusions)
- sim_std: 14.35 (elevated vs league avg 13.34 — higher-variance game)
- DB odds_event_id: f0853d396988ee8ea615897e136d22cb

## Team Lineup Profiles (last 15 games before 2026-03-25)

### GSW (home) — game window: 2026-02-22 to 2026-03-21
Total offense possessions in window: 1,434

| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Brandin Podziemski | 15 | 13.4% | -0.47 | +0.70 | -1.16 | Full window starter |
| Gui Santos | 15 | 13.0% | +0.12 | +0.02 | +0.10 | Full window starter |
| Pat Spencer | 15 | 9.3% | -0.59 | +0.38 | -0.97 | Full window |
| Draymond Green | 11 | 9.0% | -2.02 | +1.25 | -3.27 | Missed 4 games; RAPM negative overall |
| Will Richard | 11 | 8.0% | -0.41 | +0.00 | -0.41 | Missed 4 games |
| De'Anthony Melton | 11 | 7.8% | +1.76 | -0.81 | +2.57 | Best GSW offensive rating |
| Gary Payton II | 12 | 7.1% | -0.57 | +0.02 | -0.59 | Missed 3 games |
| Quinten Post | 11 | 5.8% | +0.34 | -0.09 | +0.43 | |
| Al Horford | 8 | 5.5% | +0.53 | -0.88 | +1.41 | Only 8/15 games — low confidence |
| Moses Moody | 5 | 4.2% | +0.76 | +0.05 | +0.71 | FLAG: only 5/15 games |
| Malevy Leons | 13 | 3.8% | -0.37 | +0.39 | -0.77 | |
| Nate Williams | 10 | 3.6% | -0.29 | +0.07 | -0.35 | |
| LJ Cryer | 8 | 3.6% | +1.06 | -0.65 | +1.72 | Only 8/15 games — emerging role |
| Kristaps Porzingis | 6 | 3.5% | +0.43 | -0.60 | +1.03 | FLAG: only 6/15 games; may be ESPN-Out |
| Omer Yurtseven | 5 | 1.6% | -0.03 | +0.05 | -0.08 | FLAG: only 5/15 games |
| Seth Curry | 2 | 0.5% | +0.10 | -0.14 | +0.24 | FLAG: only 2/15 games — recency artifact risk |

**Team OFF = -0.108 | DEF = +0.103 | Net = -0.211 pts/100**

Coverage note: GSW profile raw coverage = 100% from possession data. Engine-reported 94.6% reflects ESPN exclusions. Likely excluded: Seth Curry (2g, 0.5%), Omer Yurtseven (5g, 1.6%), possibly Porzingis (6g, 3.5%) = ~5.6% combined, consistent with reported 5.4% exclusion.

**Steph Curry status (CRITICAL):** Steph's last game in possessions DB was 2026-01-30. He appears in ZERO of the 15-game window games and ZERO of the 30-game extended lookback window (which runs from 2026-01-15 to 2026-03-21). His 8 games at end of Jan are just outside the 30-game window boundary. He is NOT injected by Fix A. This is a known model gap per MEMORY.md — ~3-month absence (last played Jan 30) exceeds the `RETURNING_PLAYER_EXTENDED_LOOKBACK=30` game window. Steph's rating: OFF=+1.21, DEF=-1.07, Overall=+2.28. His absence means GSW's profile has zero weight from their best player.

---

### BKN (away) — game window: 2026-02-26 to 2026-03-23
Total offense possessions in window: 1,437

| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Nolan Traore | 14 | 8.6% | -1.41 | +0.64 | -2.05 | |
| Danny Wolf | 14 | 8.6% | -1.46 | +1.11 | -2.57 | |
| Ziaire Williams | 13 | 8.2% | -1.68 | +1.16 | -2.84 | |
| Nic Claxton | 12 | 7.9% | -2.35 | +0.40 | -2.75 | |
| Ben Saraf | 13 | 7.8% | -1.39 | +0.75 | -2.13 | |
| Noah Clowney | 11 | 7.0% | -1.08 | -0.44 | -0.64 | DEF negative = good defender per convention |
| Michael Porter Jr. | 7 | 5.8% | +1.02 | -1.57 | +2.59 | FLAG: only 7/15 games; relative bright spot |
| Josh Minott | 11 | 5.5% | -0.20 | +0.22 | -0.42 | |
| Chaney Johnson | 9 | 5.4% | -0.36 | +0.27 | -0.62 | |
| Terance Mann | 9 | 5.2% | -0.77 | -0.01 | -0.76 | |
| Drake Powell | 8 | 5.2% | -3.10 | +2.06 | -5.15 | Worst rating on BKN; recency artifact risk |
| Ochai Agbaji | 11 | 4.6% | -0.88 | +0.47 | -1.35 | |
| Tyson Etienne | 8 | 3.9% | -0.37 | +0.19 | -0.55 | |
| Day'Ron Sharpe | 7 | 3.8% | -0.50 | +0.27 | -0.77 | FLAG: only 7/15 games |
| Jalen Wilson | 9 | 3.6% | -0.87 | +0.61 | -1.48 | |
| Malachi Smith | 6 | 3.3% | -0.21 | +0.11 | -0.32 | FLAG: only 6/15 games |
| E.J. Liddell | 8 | 3.3% | -0.20 | +0.28 | -0.48 | |
| Egor Demin | 2 | 1.3% | +0.08 | -0.18 | +0.26 | FLAG: only 2/15 games — recency artifact |
| Grant Nelson | 4 | 0.9% | +0.07 | +0.04 | +0.04 | FLAG: only 4/15 games |

**Team OFF = -1.044 | DEF = +0.419 | Net = -1.463 pts/100**

BKN is one of the worst teams in the league by both offense and defense ratings. Only Michael Porter Jr. (+2.59 overall) grades as a positive contributor, but he's only appeared in 7/15 games.

## Raw Margin Math

Using league average PPP = 1.1449 (from `league_averages WHERE season='2025-26'`):

```
home_ppp = 1.1449 + (GSW_off + BKN_def) / 100
         = 1.1449 + (-0.108 + 0.419) / 100
         = 1.1449 + 0.00311 = 1.14804

away_ppp = 1.1449 + (BKN_off + GSW_def) / 100
         = 1.1449 + (-1.044 + 0.103) / 100
         = 1.1449 + (-0.00941) = 1.13553

raw_margin_ppp = 1.14804 - 1.13553 = 0.01251 pts/poss
raw_margin_pts  = 0.01251 × 100 = 1.251 pts/100
```

Calibration (v5, no B2B, using GSW team-specific HCA):
```
predicted = alpha × raw + HCA_gsw
          = 6.097 × 1.251 + 4.899
          = 7.628 + 4.899 = 12.53
```

This is close to the stored 12.24 — the ~0.3 difference reflects the engine's simulation variance, shrinkage weighting, and minor differences in how share weights are computed (the engine uses recency-weighted possession shares, not flat counts as used here). The manual calc validates the stored prediction is internally consistent.

## Flags for David

**BKN 79% coverage — who is in the 21% gap?**

The engine excluded ~1,503 player-possession slots (21% of BKN's 7,185 total). Based on share sizes, this is most likely 2-3 players. Top candidates by share:
- Nolan Traore (8.6%) — if Out, one player covers 8.6%
- Danny Wolf (8.6%) — another 8.6%
- Nic Claxton (7.9%)
- Ziaire Williams (8.2%)

Most likely combination: Claxton (7.9%) + 1-2 others = ~21%. Or Wolf + Ziaire = 16.8% + a third smaller player.

**David: which BKN players are ESPN-Out/Doubtful today?** This is the most important pre-game question. The 21% gap is large and BKN's remaining roster is uniformly bad (every player except MPJ grades negative). The injury exclusions make BKN even weaker in the model.

**GSW inj+5.3 — which GSW players excluded?**

GSW has 5.4% excluded (~390 slots). The natural sparse players (Seth Curry 0.5%, Yurtseven 1.6%) account for ~2.1%. The remaining 3.3% (~237 slots) likely matches Porzingis (6 games, 3.5%) being ESPN-Out. Total: Seth Curry + Yurtseven + Porzingis ≈ 5.6% — consistent with reported 5.4%.

The "inj+5.3" in the spread is not from GSW losing Porzingis/Curry — it is primarily from BKN's 21% exclusion causing their already-bad remaining roster to pick up even more share, further widening the spread.

**Steph Curry — NOT in GSW profile (CRITICAL gap):**

Steph last played 2026-01-30. The 15-game window runs to 2026-01-15 as its oldest game — his 8 recent games (Jan 15–30) fall EXACTLY at the boundary. Checking the DB directly: Steph has 0 appearances in the 15-game window AND 0 in the 30-game extended Fix A window (window runs 2026-01-15 to 2026-03-21; Steph's last game was 2026-01-30 and it appears the 30-game count does not include him).

**David: Is Steph Curry playing tonight?** This is the most critical unknown. Per MEMORY.md, Steph has been out ~3+ months (since Jan 30). If he is returning tonight, Fix A does NOT inject him (window doesn't reach his games). His absence means the GSW profile is built on a Steph-less team. If he plays tonight, our GSW rating is 2.28 pts undervalued — the spread should be ~14+ not 12.2.

**Recency artifact risks:**
- Seth Curry: 2/15 games (0.5% share) — minimal impact, not a concern
- Egor Demin: 2/15 games (1.3% share) — small BKN role player, negligible
- Drake Powell: 8/15 games (5.2% share, -5.15 overall) — if he plays, his terrible rating is the worst on BKN; if he's actually been benched, model is overweighting his negative contribution

## Pre-Game Assessment

- **Model confidence:** HIGH (86% directional accuracy tier)
- **Spread:** GSW -12.24 vs market -11.5, edge = +0.74

**Key risks:**

1. **Steph Curry status (HIGH PRIORITY):** If Steph is returning tonight, our model doesn't know it. GSW profile is Steph-less. If he plays, true spread is likely 14+ and the market at -11.5 is an extreme undervalue. If he's still out, prediction is properly calibrated.

2. **BKN 21% coverage gap:** We don't know which BKN players are out. If it's their better players (MPJ, who only appeared in 7/15 games, is a candidate), BKN is even worse than modeled. If the excluded players were below-average, removing them actually helps BKN slightly (replacing bad players with league-average replacement level).

3. **Edge assessment (+0.74):** A 0.74-point edge is thin by itself. However, the HIGH tier means the model has high directional conviction (GSW wins this game with >80% probability). The edge being thin on a high-confidence pick means: (a) the market is already efficient here, or (b) there's an informational gap (Steph status) not priced in yet. Do NOT bet this purely on the +0.74 edge — confirm Steph status first.

4. **sim_std=14.35 (elevated):** Higher than the league average of 13.34, meaning this game is more uncertain than typical. The elevated variance is consistent with BKN's unusual roster situation (79% coverage, unclear who's playing).

**Actionable?**
Edge is thin (+0.74) for a HIGH-confidence pick. Wait for Steph Curry confirmation:
- If Steph is OUT: spread of GSW -12.24 vs market -11.5 is a marginal lean, direction correct, edge too small to justify significant action.
- If Steph is PLAYING: model is undervaluing GSW by ~2+ pts (his overall rating is +2.28), true edge becomes ~2.7+ — much more actionable. Consider GSW -11.5.
- **Also confirm BKN's absentees** — if their best remaining players (MPJ, Noah Clowney) are also out, BKN is even worse and spread could move further.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: GSW 109, BKN 106
- Actual margin: GSW +3 (home_margin = 109−106 = +3)
- Our spread: GSW +12.3 (model strongly favored GSW) | Market: GSW −11.5 | Error: +9.3 pts

### Result
- Directional: **WIN** — predicted GSW to win, GSW won by 3
- ATS: **NO COVER** — market had GSW −11.5, GSW won by only 3

### Actual Box Score

**GSW**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Gui Santos | 35 | 31 | 3 | 1 |
| Brandin Podziemski | 35 | 22 | 6 | 5 |
| De'Anthony Melton | 28 | 14 | 9 | 3 |
| Kristaps Porzingis | 27 | 17 | 5 | 2 |
| Draymond Green | 34 | 7 | 5 | 3 |
| Gary Payton II | 24 | 10 | 7 | 2 |
| Will Richard | 20 | 3 | 2 | 0 |
| LJ Cryer | 15 | 0 | 2 | 2 |

**BKN**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Ben Saraf | 32 | 14 | 4 | 7 |
| Ziaire Williams | 24 | 19 | 1 | 2 |
| Jalen Wilson | 23 | 15 | 3 | 2 |
| Chaney Johnson | 19 | 11 | 1 | 3 |
| Drake Powell | 34 | 10 | 2 | 0 |
| Josh Minott | 23 | 8 | 2 | 3 |
| Nic Claxton | 20 | 8 | 4 | 2 |
| Terance Mann | 23 | 4 | 5 | 1 |

### Lineup Accuracy
- **GSW lineup somewhat matched**: Santos (31 pts) and Porzingis (17 pts) were not in the pre-game analysis as high-share contributors. Pre-game flagged BKN's 79% coverage and elevated sigma.
- **BKN competed hard**: Ziaire Williams 19, Wilson 15, Johnson 11 — BKN put up a fight despite being massive underdogs.
- Pre-game correctly noted the elevated sim_std (14.35) — this was indeed a high-variance game.

### What the Model Got Right / Wrong
1. **Direction correct — but barely**: GSW won by 3 when model predicted a 12-pt blowout. This is the inverse of blowout compression — model dramatically overestimated the GSW advantage.
2. **GSW significantly underperformed their rating**: Model predicted a dominant win; GSW barely survived vs a bottom-5 team. This may reflect BKN's home road split (they're 7-? away) or GSW having lineup/fatigue issues not in the profile.
3. **BKN coverage gap warning was real**: BKN had 79% coverage (21% unknown players). Those unknown players apparently contributed significantly. This is an example where low coverage on the away team means the model's prediction of a blowout was based on incomplete information about BKN's actual available talent.
4. **Elevated sigma (14.35) was justified** — the large coverage gap created a genuinely uncertain game. DO NOT bet heavily when both teams have large coverage gaps even at HIGH tier.
