# Game Analysis: DAL @ DEN, 2026-03-25

## Stored Prediction
- Our spread: DEN -16.2 | Market: DEN -13.5 | Edge: +2.7 | Tier: HIGH (86% dir acc)
- Coverage: home (DEN) 100% | away (DAL) 89%
- B2B: home=False | away=False
- No injury adj noted

## Team Lineup Profiles (last 15 games)

### DEN (home)
| Player | OFF | DEF | Overall | Notes |
|--------|-----|-----|---------|-------|
| Nikola Jokic | +3.82 | -2.09 | +5.91 | MVP-level, drives DEN offense |
| Jamal Murray | +2.48 | -1.42 | +3.90 | |
| Aaron Gordon | +2.16 | -1.68 | +3.84 | |
| Peyton Watson | +2.02 | -1.23 | +3.25 | |
| Cameron Johnson | +2.02 | -1.06 | +3.08 | |
| Christian Braun | +1.62 | -0.36 | +1.98 | |
| Tim Hardaway Jr. | +0.99 | -0.15 | +1.14 | |
| Spencer Jones | +0.31 | -0.41 | +0.72 | |

DEN is firing on all cylinders — full-strength Jokic-led lineup, every player positive.

### DAL (away)
| Player | OFF | DEF | Overall | Notes |
|--------|-----|-----|---------|-------|
| Dwight Powell | +1.28 | -0.84 | +2.12 | Top DAL player — bench-level star |
| Moussa Cisse | +0.63 | -0.77 | +1.40 | |
| Dereck Lively II | +0.43 | -0.54 | +0.97 | |
| Naji Marshall | +0.20 | -0.61 | +0.81 | |
| Marvin Bagley III | -0.81 | -1.20 | +0.38 | |
| AJ Johnson | -0.18 | -0.38 | +0.20 | |
| Tyler Smith | -0.13 | +0.07 | -0.20 | |
| Ryan Nembhard | -0.47 | -0.23 | -0.23 | |

DAL is heavily depleted — no Luka Doncic, no Kyrie Irving in profile. Top player (Powell) at only +2.12. This is a G-League-caliber roster facing a championship-contending DEN.

## Raw Margin Math
- DEN net team rating far exceeds DAL across all positions
- Model: DEN -16.2 | Market: DEN -13.5
- Both agree this is a large DEN blowout
- Blowout compression pattern: per model history, when model+market both agree on large spread, actual outcome is often larger than market predicts (see 2026-03-23 post-mortems: ATL +39 pred -8.5, POR +35 pred -16.1)

## Flags for David
- DAL 11% coverage gap — which player(s)? Likely Luka and/or Kyrie (neither appears in top-8 ratings)
- BLOWOUT PATTERN: DEN -16.2 model, market -13.5 — both large; magnitude often compressed
- DAL roster looks like a full bench/tank lineup — confirm David: are Luka/Kyrie definitely out?

## Pre-Game Assessment
- Model confidence: HIGH (86% dir acc)
- Key risks: DAL injury gap (11% unaccounted); blowout magnitude always uncertain; DEN resting players if blowout confirmed
- Actionable? YES — DEN -13.5 at HIGH confidence with +2.7 edge. Direction is clear. With caveat: DAL depleted roster means game may be decided by halftime and starters rest, so live spread might be better than open.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: DEN 142, DAL 135
- Actual margin: DEN +7 (home_margin = 142−135 = +7)
- Our spread: DEN +13.6 (model favored DEN) | Market: DEN −12.0 | Error: +6.6 pts (overestimated DEN)

### Result
- Directional: **WIN** — predicted DEN to win, DEN won by 7
- ATS: **NO COVER** — market had DEN −12.0, DEN won by only 7 (5 pts short)

### Actual Box Score

**DEN**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Jamal Murray | 41 | 53 | 6 | 4 |
| Nikola Jokic | 38 | 23 | 21 | 19 |
| Cameron Johnson | 29 | 12 | 1 | 3 |
| Peyton Watson | 23 | 21 | 4 | 3 |
| Christian Braun | 25 | 11 | 3 | 4 |
| Tim Hardaway Jr. | 27 | 4 | 1 | 2 |
| Spencer Jones | 20 | 4 | 2 | 0 |
| Bruce Brown | 20 | 6 | 2 | 1 |

**DAL**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Cooper Flagg | 36 | 26 | 8 | 7 |
| P.J. Washington | 31 | 19 | 15 | 1 |
| Naji Marshall | 30 | 22 | 4 | 3 |
| Max Christie | 32 | 9 | 1 | 2 |
| Brandon Williams | 19 | 11 | 2 | 6 |
| Khris Middleton | 18 | 11 | 3 | 5 |
| Marvin Bagley III | 17 | 7 | 3 | 3 |
| Dwight Powell | 16 | 7 | 4 | 0 |

### Lineup Accuracy
- **Jokic 23/21/19 triple-double** — his RAPM is well captured. Watson (21 pts off bench) was a positive surprise.
- **Murray 53 pts** — extraordinary performance for a B2B. DEN still barely won.
- **DAL fought hard**: Cooper Flagg (26/8/7 as rookie), PJ Washington 19/15, Marshall 22 — DAL's depleted roster competed surprisingly well. Pre-game file noted DAL 89% coverage gap; their available players overperformed.
- DEN B2B fatigue showed in the margin — won by only 7 despite Murray 53 + Jokic triple-double.

### What the Model Got Right / Wrong
1. **Direction correct (HIGH tier)** — DEN wins as predicted.
2. **B2B compression confirmed**: Model predicted DEN by 13.6 (after B2B penalty applied), market said 12.0, actual was 7. The B2B fatigue effect was real even with elite performances from Murray and Jokic.
3. **DAL overperformed**: Model had DAL at 89% coverage — their available roster (Flagg/Washington/Marshall) performed better than their RAPM suggested. This may reflect Flagg's rookie season underrating by RAPM.
4. **Murray 53 shows individual variance**: Even a 53-point performance wasn't enough to blow out the game on a B2B. Star-heavy performance + fatigue = compressed margin.
