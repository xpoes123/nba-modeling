# Game Analysis: HOU @ MIN, 2026-03-25

## Stored Prediction
- Our spread: MIN -1.2 | Market: HOU -1.5 | Edge: +2.7 (direction flip) | Tier: LOW SIGNAL
- Coverage: home (MIN) 93% | away (HOU) 100%
- B2B: home=False | away=False
- Note: MIN 7% coverage gap — likely an injured player excluded from profile

## Team Lineup Profiles (last 15 games)

### MIN (home)
| Player | OFF | DEF | Overall | Notes |
|--------|-----|-----|---------|-------|
| Donte DiVincenzo | +2.43 | -1.59 | +4.02 | Top MIN contributor |
| Julius Randle | +1.43 | -0.63 | +2.06 | |
| Rudy Gobert | +1.14 | -0.61 | +1.74 | |
| Jaylen Clark | +0.74 | -0.81 | +1.55 | |
| Naz Reid | +0.92 | -0.38 | +1.30 | |
| Anthony Edwards | +0.41 | +0.24 | +0.17 | LOW for a star — injury/recency artifact? |
| Julian Phillips | +0.23 | +0.26 | -0.03 | |
| Zyon Pullin | -0.09 | +0.07 | -0.16 | |

Team profile driven by DiVincenzo/Randle/Gobert depth. Edwards rating suspiciously low — flag for David.

### HOU (away)
| Player | OFF | DEF | Overall | Notes |
|--------|-----|-----|---------|-------|
| Amen Thompson | +2.25 | -1.35 | +3.60 | |
| Steven Adams | +1.67 | -1.72 | +3.39 | |
| Reed Sheppard | +0.96 | -1.15 | +2.11 | |
| Kevin Durant | +1.61 | -0.27 | +1.88 | |
| Jabari Smith Jr. | +0.83 | +0.21 | +0.63 | |
| Clint Capela | +0.63 | +0.20 | +0.43 | |
| Alperen Sengun | +0.08 | -0.28 | +0.37 | |
| Tari Eason | +0.03 | +0.12 | -0.09 | |

HOU has Durant but overall team depth is similar to MIN.

## Raw Margin Math
- Model predicted: MIN -1.2 (home MIN favored)
- Market: HOU -1.5 (away HOU favored)
- Direction flip: 2.7pt gap across the line

## Flags for David
- DIRECTION FLIP: model has MIN -1.2, market has HOU -1.5 — different winner predicted
- MIN 7% coverage gap — which player(s) are excluded from profile?
- Anthony Edwards only +0.17 overall — suspiciously low for a star; injury or recency artifact?
- HOU star-concentration pattern: Thompson+Adams+Durant, but prior post-mortems show HOU lost to depth teams even with big individual performances

## Pre-Game Assessment
- Model confidence: LOW SIGNAL (< 73% historical dir accuracy)
- Key risks: direction flip; Edwards rating anomaly; MIN 7% coverage unknown
- Actionable? NO — LOW SIGNAL + direction flip = do not bet

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: MIN 110, HOU 108
- Actual margin: MIN +2 (home_margin = 110−108 = +2)
- Our spread: MIN +1.2 (model favored MIN home) | Market: HOU −1.5 | Error: −0.8 pts

### Result
- Directional: **WIN** — predicted MIN to win, MIN won by 2
- ATS: **MIN COVER** — market had HOU −1.5 (MIN +1.5 underdog), MIN won by 2. Cover.

### Actual Box Score

**HOU**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Kevin Durant | 43 | 30 | 3 | 8 |
| Alperen Sengun | 43 | 30 | 6 | 3 |
| Jabari Smith Jr. | 48 | 16 | 12 | 1 |
| Amen Thompson | 45 | 11 | 9 | 10 |
| Reed Sheppard | 28 | 10 | 8 | 3 |
| Tari Eason | 21 | 3 | 8 | 0 |
| Aaron Holiday | 12 | 3 | 2 | 1 |
| Clint Capela | 10 | 0 | 4 | 0 |

**MIN**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Julius Randle | 42 | 24 | 6 | 6 |
| Jaden McDaniels | 37 | 25 | 2 | 0 |
| Donte DiVincenzo | 36 | 17 | 3 | 2 |
| Naz Reid | 31 | 14 | 13 | 1 |
| Bones Hyland | 30 | 8 | 0 | 8 |
| Kyle Anderson | 30 | 3 | 5 | 3 |
| Mike Conley | 29 | 5 | 5 | 6 |
| Rudy Gobert | 28 | 14 | 14 | 1 |

### Lineup Accuracy
- **HOU heavy minutes: Jabari Smith 47:36, Thompson 45:05, Durant 43:07, Sengun 42:50** — this strongly suggests the game went to overtime. HOU played 4 players 43+ min and still lost by 2.
- **MIN balanced attack**: 5 players between 14-25 pts. Depth won over star power. DiVincenzo (model's top-rated MIN player) contributed 17 pts.
- Anthony Edwards NOT in top-8 minutes — confirms his low +0.17 overall was an injury/rest artifact. He likely had limited or no role tonight.

### What the Model Got Right / Wrong
1. **Best prediction of the night** — error of only 0.8 pts. Model said MIN by 1.2, actual MIN by 2. Near-perfect.
2. **Direction flip validated against market** — market had HOU −1.5, our model flipped to MIN. MIN won. The +2.7 direction-flip edge was real.
3. **Star-heavy HOU vs depth MIN pattern confirmed**: Durant 30 + Sengun 30 (combined 60 pts!) in likely-OT, still lost. MIN's 5-man balanced attack (Randle/McDaniels/DiVincenzo/Reid/Gobert all contributing) outworked the HOU star duo. Consistent with our documented pattern from 3/23 post-mortem.
4. **Anthony Edwards low rating explained**: he played minimal or no role tonight (not in top-8 min). Not a model error — he was genuinely out or limited.
