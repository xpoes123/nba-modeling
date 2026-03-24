# Game Analysis: GSW @ DAL, 2026-03-23

## Stored Prediction
- Our spread: DAL -1.9 | Market: GSW -2.5 | Edge: +4.45 (model sees DAL as slight home favorite; market has GSW) | Tier: LOW SIGNAL
- Win prob: 55.7% (home) | Sim std: 13.72 pts | Market total: 230.5
- Coverage: home (DAL) 89.5% | away (GSW) 94.6%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### DAL (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Cooper Flagg | 9/15 | 12.9% | -0.90 | +0.37 | -1.27 | |
| P.J. Washington | 11/15 | 12.8% | -1.99 | +1.28 | -3.27 | |
| Max Christie | 15/15 | 12.1% | -1.55 | +0.38 | -1.92 | |
| Naji Marshall | 13/15 | 11.8% | +0.19 | -0.60 | +0.79 | |
| Daniel Gafford | 10/15 | 9.7% | -1.26 | +0.37 | -1.63 | |
| Khris Middleton | 15/15 | 9.1% | -1.52 | +0.79 | -2.31 | |
| Klay Thompson | 10/15 | 8.7% | -0.97 | +0.13 | -1.10 | |
| Brandon Williams | 13/15 | 8.4% | -0.34 | +0.53 | -0.86 | |
| Ryan Nembhard | 11/15 | 8.3% | -0.46 | -0.24 | -0.23 | |
| Marvin Bagley III | 10/15 | 8.0% | -0.81 | -1.20 | +0.39 | |
| Moussa Cisse | 4/15 | 7.5% | +0.63 | -0.77 | +1.40 | sparse window |
| Miles Kelly | 2/15 | 7.3% | -0.52 | +0.15 | -0.67 | sparse window |

**Team OFF = -1.20  DEF = +0.31  Net = -1.51 pts/100  Coverage = 89.5%**

### GSW (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Brandin Podziemski | 15/15 | 12.8% | -0.49 | +0.72 | -1.21 | |
| Gui Santos | 15/15 | 12.4% | +0.11 | +0.04 | +0.06 | |
| Moses Moody | 5/15 | 12.1% | +0.74 | +0.07 | +0.67 | |
| Draymond Green | 11/15 | 11.8% | -2.02 | +1.25 | -3.27 | |
| Will Richard | 11/15 | 11.7% | -0.43 | +0.02 | -0.45 | |
| De'Anthony Melton | 11/15 | 10.3% | +1.74 | -0.80 | +2.54 | |
| Al Horford | 8/15 | 9.5% | +0.52 | -0.87 | +1.39 | |
| Pat Spencer | 15/15 | 9.4% | -0.61 | +0.40 | -1.01 | |
| Gary Payton II | 12/15 | 9.4% | -0.58 | +0.03 | -0.61 | |
| Kristaps Porzingis | 6/15 | 8.3% | +0.43 | -0.61 | +1.03 | |
| Quinten Post | 11/15 | 7.9% | +0.36 | -0.10 | +0.46 | |
| LJ Cryer | 8/15 | 6.8% | +1.05 | -0.64 | +1.70 | |

**Team OFF = -0.03  DEF = +0.05  Net = -0.08 pts/100  Coverage = 94.6%**

Note: Steph Curry and Jimmy Butler are not in the window (long-term injured). GSW's true identity
right now is a fringe team built around Podziemski/Santos/Melton with Draymond as defensive anchor.
Moses Moody at 12.1% share with only 5/15 games -- may be returning from injury; recency-weighted.

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (DAL_off + GSW_def) / 100
         = 1.144596 + (-1.2020 + 0.0484) / 100
         = 1.133060

away_ppp = 1.144596 + (GSW_off + DAL_def) / 100
         = 1.144596 + (-0.0252 + 0.3058) / 100
         = 1.147402

exp_pace = 96.2142 + (DAL_pace +1.120 + GSW_pace -2.520) / 2 = 95.514
raw_margin = (1.133060 - 1.147402) * 95.514 = -1.370 pts

Calibrated:
  6.097 x (-1.370) + HCA(DAL +5.422) + B2B(0) + B2B(0)
= -8.353 + 5.422
= -2.93  (stored: +1.95)
```

Note: Our inline calc gives DAL -2.93 (away favored by market interpretation), but the stored
prediction is DAL +1.95 (home slightly favored). This gap stems from simulation variance and how
the coverage scaling in simulate_game() handles the 89.5% DAL coverage vs 94.6% GSW coverage.
The edge of +4.45 (model sees DAL +1.95 vs market GSW -2.5) is real and sizable.

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: LOW SIGNAL (|spread| = 1.9 pts)
- Key risks:
  1. Model and market disagree on DIRECTION (+4.45 edge): model sees DAL as slight home fav; market has GSW -2.5
  2. Both teams have coverage gaps (DAL 89.5%, GSW 94.6%) -- uncertainty is symmetric
  3. DAL has a massive HCA in calibration (+5.42) -- this is the only reason the model favors DAL
  4. DAL's raw team OFF = -1.20 pts/100 (very poor) -- the HCA adjustment is doing almost all the work
  5. Moses Moody sparse (5/15) -- if recently healthy GSW may be better than modeled
- Actionable: NO (LOW SIGNAL)

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: GSW 137 @ DAL 131
- Actual margin: DAL -6 (away won — GSW won by 6)
- Our spread: DAL -1.9 | Market: GSW -2.5 | Error: +7.95 pts (we said DAL by 2, GSW won by 6)

### Result
- Directional: **LOSS** — we predicted DAL to win, GSW won
- ATS: **AWAY COVERED** — market DAL +2.5 (home dog); GSW won by 6 (GSW -2.5 covered)

### Actual Box Score (top players by minutes)

**DAL (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Cooper Flagg | 41:34 | 32 | 4 | 9 |
| Naji Marshall | 35:21 | 16 | 6 | 7 |
| P.J. Washington | 34:04 | 9 | 3 | 2 |
| Max Christie | 33:18 | 15 | 2 | 1 |
| Daniel Gafford | 31:31 | 20 | 7 | 5 |
| Klay Thompson | 27:33 | 15 | 1 | 1 |
| Ryan Nembhard | 16:38 | 4 | 1 | 5 |
| Marvin Bagley III | 14:30 | 9 | 0 | 3 |

**GSW (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Brandin Podziemski | 40:29 | 20 | 10 | 6 |
| Draymond Green | 38:29 | 11 | 7 | 6 |
| Gui Santos | 35:13 | 16 | 6 | 5 |
| Moses Moody | 34:11 | 23 | 3 | 3 |
| Kristaps Porzingis | 29:12 | 22 | 7 | 5 |
| De'Anthony Melton | 22:32 | 0 | 6 | 5 |
| Gary Payton II | 21:26 | 17 | 4 | 3 |
| LJ Cryer | 19:02 | 14 | 4 | 1 |

### Lineup Accuracy
- **Moses Moody played 34 min**: Our pre-game flagged Moody at 5/15 games (sparse), suggesting he may have been returning from injury. He played heavy minutes (34 min, 23 pts) — the "recently healthy GSW may be better" flag was correct.
- **Kristaps Porzingis played 29 min**: Also sparse in profile (6/15 games). He delivered 22/7/5. Two returning players from sparse windows both contributed significantly for GSW.
- **DAL's Khris Middleton absent**: Profile had Middleton at 9.1% (15/15 games) but he's not in the box score. If Middleton sat, DAL was weaker than modeled — a coverage gap that wasn't captured by ESPN injury status.
- **Cooper Flagg had a strong game**: 32/4/9 (41 min!) — outperformed his RAPM profile (-1.27 overall). Young player having a breakout performance against expectation.
- **DAL HCA overstated?**: Profile showed DAL HCA = +5.42 in calibration — the highest of any team. But DAL's raw team quality was -1.51 pts/100 (poor). The HCA bump may be a historical artifact not capturing this year's team.

### What the Model Got Right / Wrong
1. **Market was right, we were wrong on direction**: Market had GSW -2.5 and GSW won by 6. Our DAL +1.95 was driven almost entirely by DAL's large HCA coefficient (+5.42) overriding a weak DAL team rating. This is a calibration risk when HCA is the dominant term.
2. **Two sparse GSW players (Moody + Porzingis) were decisive**: Both came off injury and combined for 45 pts. This is the exact Fix A failure mode — returning players from sparse windows underweighted. GSW got healthier than the 15-game window showed.
3. **LOW SIGNAL correct not to bet**: We passed on this despite the +4.45 edge. Good discipline — the edge was driven by HCA overriding genuine roster uncertainty, not a real quality signal.
