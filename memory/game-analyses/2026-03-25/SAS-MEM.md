# Game Analysis: SAS @ MEM, 2026-03-25

## Stored Prediction
- Our spread: SAS -14.4 (inj adj applied) | Market: SAS -16.5 | Edge: +2.1 (MEM +16.5 is our side) | Tier: HIGH (86% dir acc)
- Coverage: home (MEM) 80% | away (SAS) 81%
- B2B: home=False | away=False
- Note: Both teams heavily depleted — some of the lowest coverage on the day

## Team Lineup Profiles (last 15 games)

### MEM (home)
| Player | OFF | DEF | Overall | Notes |
|--------|-----|-----|---------|-------|
| Jaylen Wells | +0.36 | -0.34 | +0.69 | Best MEM player |
| Javon Small | +0.31 | -0.36 | +0.67 | |
| Ty Jerome | +0.45 | -0.12 | +0.57 | |
| Cedric Coward | +0.39 | -0.10 | +0.49 | |
| Lawson Lovering | +0.02 | -0.01 | +0.03 | |
| Taj Gibson | -0.19 | +0.23 | -0.42 | |
| Walter Clayton Jr. | -0.43 | +0.20 | -0.63 | |
| Jahmai Mashack | -0.67 | +0.04 | -0.72 | |
| Tyler Burton | -0.63 | +0.09 | -0.72 | |
| DeJon Jarreau | -0.59 | +0.29 | -0.88 | |

MEM is a **full tank roster** — best player at +0.69. ~20% coverage gap means even these replacement-level players are depleted further. Team NET strongly negative.

### SAS (away)
| Player | OFF | DEF | Overall | Notes |
|--------|-----|-----|---------|-------|
| Victor Wembanyama | +3.74 | -1.67 | +5.41 | Elite anchor |
| Julian Champagnie | +3.39 | -1.71 | +5.10 | |
| Devin Vassell | +2.57 | -1.56 | +4.13 | |
| De'Aaron Fox | +1.71 | -0.81 | +2.52 | |
| Dylan Harper | +1.16 | -0.89 | +2.06 | |
| David Jones Garcia | +1.01 | -0.62 | +1.63 | |
| Keldon Johnson | +1.06 | +0.50 | +0.56 | |
| Stephon Castle | +0.91 | +1.03 | -0.12 | |

SAS full strength: Wembanyama + Champagnie + Vassell are elite. ~19% coverage gap = significant SAS injuries excluded.

## Raw Margin Math
- SAS has arguably the largest talent gap of any game today vs MEM
- Model: SAS -14.4 | Market: SAS -16.5
- Edge = +2.1 → model says MEM covers at market spread of +16.5

## Flags for David
- SAS ~19% coverage gap — who is excluded? At SAS's roster quality, excluded players could be stars
- MEM ~20% coverage gap — at this roster level, all excluded players are replacement-level
- BLOWOUT PATTERN: Model+market both agree large SAS spread. Historical pattern: actual blowout often EXCEEDS market. This conflicts with +2.1 edge signal (edge says MEM covers, pattern says SAS covers bigger).
- KEY CONFLICT: Model says MEM +16.5, blowout compression pattern says fade MEM. Defer to David.

## Pre-Game Assessment
- Model confidence: HIGH (86% dir acc for direction = SAS wins)
- Key risks: Conflicting signals — edge math says MEM +16.5, blowout history says actual outcome > market spread. Both teams heavily depleted; actual lineups very uncertain.
- Actionable? CONDITIONAL — direction clear (SAS wins), magnitude uncertain. Consult David on injury situation and which signal to trust.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: SAS 123, MEM 98
- Actual margin: MEM −25 (home_margin = 98−123 = −25; SAS won by 25)
- Our spread: SAS −14.5 | Market: SAS −16.5 | Error: +10.5 pts (underestimated SAS margin)

### Result
- Directional: **WIN** — predicted SAS to win, SAS won by 25
- ATS: **SAS COVER** — market had SAS −16.5, SAS won by 25. Covered by 8.5 pts.

### Actual Box Score

**SAS**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Victor Wembanyama | 27 | 19 | 15 | 3 |
| Devin Vassell | 26 | 19 | 7 | 4 |
| Stephon Castle | 26 | 15 | 3 | 9 |
| Keldon Johnson | 22 | 15 | 7 | 3 |
| Julian Champagnie | 26 | 13 | 8 | 2 |
| Dylan Harper | 23 | 10 | 5 | 6 |
| Harrison Barnes | 22 | 11 | 2 | 2 |
| Carter Bryant | 15 | 5 | 1 | 0 |

**MEM**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| GG Jackson | 30 | 20 | 7 | 2 |
| Olivier-Maxence Prosper | 25 | 17 | 5 | 0 |
| Walter Clayton Jr. | 22 | 10 | 2 | 6 |
| Javon Small | 30 | 8 | 3 | 5 |
| Cam Spencer | 30 | 1 | 2 | 7 |
| Cedric Coward | 27 | 12 | 1 | 4 |
| Taylor Hendricks | 28 | 2 | 8 | 0 |
| Tyler Burton | 24 | 6 | 2 | 1 |

### Lineup Accuracy
- **Wembanyama managed to 27 min** (comfortable lead) but still 19/15/3. SAS shared the ball well — 5 players in double figures.
- **MEM showed a very thin rotation** — GG Jackson 20 pts was the only real contributor. Cam Spencer 1 pt (starter!). Confirms model's read on MEM as deeply depleted.
- Pre-game file noted both teams heavily depleted (~80% coverage each). Actual lineups matched this assessment.

### What the Model Got Right / Wrong
1. **Direction correct, magnitude compressed** — model said SAS −14.5, market said −16.5, actual was −25. Classic blowout compression. Our model undershoots the magnitude on large mismatches.
2. **Market was right to go −16.5** — market had more aggressive estimate and was still short by 8.5 pts. When model and market both agree on a large spread AND market > model, actual outcomes often exceed both.
3. **Blowout pattern confirmed**: 3rd data point on the same pattern this season (ATL+39, POR+35 from 3/23, now SAS +25). Model gets direction, compresses magnitude by 8-12 pts.
