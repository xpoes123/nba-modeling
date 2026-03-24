# Game Analysis: HOU @ CHI, 2026-03-23

## Stored Prediction
- Our spread: HOU -9.6 | Market: HOU -8.0 | Edge: -1.55 (we overpredict HOU) | Tier: MODERATE
- Win prob: 23.7% (home) | Sim std: 13.34 pts | Market total: 228.5
- Coverage: home (CHI) 100.0% | away (HOU) 100.0%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### CHI (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Josh Giddey | 14/15 | 14.0% | +0.46 | -0.26 | +0.72 | |
| Matas Buzelis | 14/15 | 13.6% | -1.23 | +0.18 | -1.41 | |
| Isaac Okoro | 9/15 | 12.9% | -1.63 | +0.94 | -2.57 | |
| Tre Jones | 15/15 | 12.0% | -0.44 | +0.70 | -1.15 | |
| Leonard Miller | 13/15 | 9.9% | +1.41 | -0.79 | +2.20 | |
| Jalen Smith | 8/15 | 9.8% | +2.05 | -1.37 | +3.42 | |
| Guerschon Yabusele | 14/15 | 9.7% | -1.26 | +0.32 | -1.58 | |
| Nick Richards | 15/15 | 9.6% | -1.00 | +0.30 | -1.30 | |
| Patrick Williams | 9/15 | 9.1% | -2.65 | +1.46 | -4.11 | |
| Rob Dillingham | 15/15 | 9.1% | -1.80 | +1.11 | -2.91 | |
| Collin Sexton | 11/15 | 8.9% | -0.74 | +0.62 | -1.36 | |
| Anfernee Simons | 2/15 | 8.5% | -0.11 | +0.96 | -1.08 | sparse window |

**Team OFF = -0.72  DEF = +0.39  Net = -1.11 pts/100  Coverage = 100.0%**

### HOU (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Amen Thompson | 14/15 | 15.6% | +2.27 | -1.29 | +3.56 | |
| Jabari Smith Jr. | 12/15 | 15.0% | +0.83 | +0.21 | +0.62 | |
| Kevin Durant | 15/15 | 14.8% | +1.75 | -0.28 | +2.03 | |
| Alperen Sengun | 13/15 | 13.2% | +0.09 | -0.30 | +0.38 | |
| Reed Sheppard | 15/15 | 13.2% | +1.14 | -1.32 | +2.47 | |
| Tari Eason | 15/15 | 10.7% | -0.11 | +0.22 | -0.33 | |
| Dorian Finney-Smith | 11/15 | 7.8% | -1.13 | +0.81 | -1.95 | |
| Clint Capela | 14/15 | 6.8% | +0.72 | +0.20 | +0.52 | |
| Aaron Holiday | 10/15 | 5.1% | -0.41 | +0.87 | -1.28 | |
| Josh Okogie | 15/15 | 4.8% | +0.13 | +0.67 | -0.54 | |
| Isaiah Crawford | 7/15 | 2.5% | -0.12 | +0.21 | -0.34 | |
| Jeff Green | 8/15 | 2.4% | -0.90 | +0.63 | -1.53 | |

**Team OFF = +0.78  DEF = -0.21  Net = +0.99 pts/100  Coverage = 100.0%**

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (CHI_off + HOU_def) / 100
         = 1.144596 + (-0.7173 + (-0.2133)) / 100
         = 1.135290

away_ppp = 1.144596 + (HOU_off + CHI_def) / 100
         = 1.144596 + (0.7772 + 0.3892) / 100
         = 1.156260

exp_pace = 96.2142 + (CHI_pace +1.238 + HOU_pace -0.198) / 2 = 96.734
raw_margin = (1.135290 - 1.156260) * 96.734 = -2.029 pts

Calibrated:
  6.097 x (-2.029) + HCA(CHI +0.934) + B2B(0) + B2B(0)
= -12.372 + 0.934
= -11.43  (stored: -9.55)
```

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: MODERATE (|spread| = 9.6 pts)
- Key risks:
  1. Model overpredicts HOU by 1.55 pts vs market (HOU -9.6 vs -8.0) -- slight over-confidence
  2. CHI full coverage (100%) -- their weak roster is accurately represented; Patrick Williams is genuinely bad (-4.11)
  3. Kevin Durant joining HOU adds elite talent that may be underweighted if he just arrived (15/15 games = well-integrated)
  4. Anfernee Simons sparse for CHI (2/15) -- if he's actually playing significant minutes, CHI is modestly stronger
- Actionable: YES (MODERATE)

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: CHI 132 @ HOU 124
- Actual margin: CHI +8 (home won — CHI upset)
- Our spread: HOU -9.6 | Market: HOU -8.0 | Error: -17.55 pts

### Result
- Directional: **LOSS** — we predicted HOU to win by 9.6, CHI won by 8
- ATS: **HOME COVERED** — market HOU -8.0; CHI won by 8 (push/CHI covered on -8 away line)

### Actual Box Score (top players by minutes)

**CHI (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Josh Giddey | 38:43 | 15 | 7 | 13 |
| Matas Buzelis | 34:47 | 23 | 4 | 1 |
| Tre Jones | 28:03 | 15 | 5 | 6 |
| Nick Richards | 26:23 | 11 | 8 | 0 |
| Collin Sexton | 25:53 | 25 | 4 | 2 |
| Jalen Smith | 25:47 | 15 | 6 | 2 |
| Leonard Miller | 23:20 | 17 | 9 | 3 |
| Patrick Williams | 18:46 | 2 | 1 | 0 |

**HOU (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Kevin Durant | 39:40 | 40 | 7 | 5 |
| Amen Thompson | 39:20 | 23 | 3 | 1 |
| Alperen Sengun | 37:26 | 33 | 13 | 10 |
| Reed Sheppard | 36:17 | 13 | 5 | 6 |
| Jabari Smith Jr. | 34:11 | 6 | 5 | 1 |
| Aaron Holiday | 21:04 | 3 | 1 | 3 |
| Tari Eason | 14:18 | 4 | 3 | 1 |
| Dorian Finney-Smith | 7:37 | 0 | 2 | 0 |

### Lineup Accuracy
- **HOU's stars delivered individually**: Durant 40/7/5, Sengun 33/13/10 triple-double, Thompson 23 pts. Three of the best individual lines of the day — yet HOU lost. This is a collective efficiency / team chemistry failure, not a talent miss.
- **Sexton and Buzelis not in our CHI profile**: Sexton (25 pts, 25 min) was in our profile at 11th slot (11/15, 8.9%) but carried outsize impact. Buzelis (23 pts) was in profile at 13.6% — the model undervalued him relative to what he delivered.
- **CHI's collective depth overwhelmed HOU**: 6 CHI players scored 11+ points; their team scoring was balanced vs HOU's top-heavy approach.
- **Patrick Williams (18 min, 2 pts)**: Profile had him at -4.11 overall. He played but delivered nothing — consistent with his profile.

### What the Model Got Right / Wrong
1. **Biggest directional flip**: We predicted HOU -9.6, CHI won by 8 — an 18-pt swing. HOU had Durant/Sengun/Thompson combining for 96 pts yet lost. This is the classic case of individual RAPM stars being poor predictors of team outcomes when depth is a mismatch.
2. **CHI's depth > HOU's stars tonight**: Six CHI players hit double digits; HOU got nothing from Jabari Smith (6 pts) or Finney-Smith. The RAPM model treats HOU's depth rotation (Finney-Smith, Eason) as negative contributors — their limited minutes were confirmed.
3. **Anfernee Simons was the pre-game flag**: We noted Simons sparse (2/15) for CHI. He didn't appear in the box score either — CHI won WITHOUT him. Their depth without a star was enough against HOU's stars.
4. **MODERATE tier miss**: We bet HOU direction and lost. Chicago's home court and collective play overcame HOU's individual brilliance.
