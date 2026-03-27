# Game Analysis: SAS @ MIA, 2026-03-23

## Stored Prediction
- Our spread: SAS -3.2 | Market: SAS -5.0 | Edge: +1.78 (we underpredict SAS) | Tier: LOW SIGNAL
- Win prob: 40.5% (home) | Sim std: 13.34 pts | Market total: 240.5
- Coverage: home (MIA) 100.0% | away (SAS) 100.0%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### MIA (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Bam Adebayo | 14/15 | 15.6% | +2.32 | -1.31 | +3.63 | |
| Tyler Herro | 13/15 | 13.8% | -0.61 | +0.60 | -1.21 | |
| Pelle Larsson | 15/15 | 13.4% | +0.28 | -0.18 | +0.46 | |
| Norman Powell | 7/15 | 12.3% | +0.59 | -0.68 | +1.27 | |
| Davion Mitchell | 14/15 | 12.0% | +2.11 | -0.62 | +2.73 | |
| Andrew Wiggins | 7/15 | 11.8% | -0.47 | +0.78 | -1.25 | |
| Jaime Jaquez Jr. | 13/15 | 11.6% | +1.43 | -0.31 | +1.73 | |
| Simone Fontecchio | 10/15 | 9.5% | +0.13 | -0.22 | +0.35 | |
| Kel'el Ware | 14/15 | 8.9% | -0.95 | +1.15 | -2.10 | |
| Kasparas Jakucionis | 15/15 | 7.7% | -0.67 | +0.47 | -1.14 | |
| Keshad Johnson | 4/15 | 7.1% | +0.07 | -0.27 | +0.35 | sparse window |
| Dru Smith | 12/15 | 5.8% | -1.21 | +0.91 | -2.12 | |

**Team OFF = +0.55  DEF = -0.08  Net = +0.63 pts/100  Coverage = 100.0%**

### SAS (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Devin Vassell | 13/15 | 13.6% | +2.53 | -1.57 | +4.10 | |
| De'Aaron Fox | 15/15 | 12.6% | +1.56 | -0.71 | +2.27 | |
| Victor Wembanyama | 14/15 | 12.5% | +3.65 | -1.64 | +5.29 | |
| Stephon Castle | 13/15 | 12.4% | +0.81 | +1.09 | -0.29 | |
| Julian Champagnie | 15/15 | 11.9% | +3.30 | -1.75 | +5.05 | |
| Dylan Harper | 13/15 | 10.0% | +1.11 | -0.88 | +1.99 | |
| Keldon Johnson | 15/15 | 9.1% | +0.98 | +0.59 | +0.39 | |
| Harrison Barnes | 10/15 | 8.9% | +0.34 | +0.53 | -0.20 | |
| Luke Kornet | 14/15 | 7.4% | -0.42 | +1.01 | -1.43 | |
| Carter Bryant | 15/15 | 6.6% | -0.96 | +0.72 | -1.68 | |
| Lindy Waters III | 8/15 | 5.3% | -0.27 | +0.09 | -0.35 | |
| Jordan McLaughlin | 10/15 | 3.6% | -1.60 | +1.43 | -3.03 | |

**Team OFF = +1.48  DEF = -0.35  Net = +1.83 pts/100  Coverage = 100.0%**

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (MIA_off + SAS_def) / 100
         = 1.144596 + (0.5548 + (-0.3519)) / 100
         = 1.146625

away_ppp = 1.144596 + (SAS_off + MIA_def) / 100
         = 1.144596 + (1.4764 + (-0.0752)) / 100
         = 1.158608

exp_pace = 96.2142 + (MIA_pace +3.921 + SAS_pace +1.716) / 2 = 99.033
raw_margin = (1.146625 - 1.158608) * 99.033 = -1.187 pts

Calibrated:
  6.097 x (-1.187) + HCA(MIA +3.135) + B2B(0) + B2B(0)
= -7.236 + 3.135
= -4.10  (stored: -3.22)
```

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: LOW SIGNAL (|spread| = 3.2 pts)
- Key risks:
  1. SAS has elite talent (Wembanyama +5.29, Champagnie +5.05, Vassell +4.10) -- strongest away roster in this slate
  2. Both teams at 100% coverage -- no lineup uncertainty, just genuine quality gap
  3. Market has SAS -5 vs our -3.2; we see smaller SAS edge (+1.78 edge) -- notable disagreement
  4. High expected pace (99 possessions) amplifies SAS offensive advantage
- Actionable: NO (LOW SIGNAL)

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: SAS 136 @ MIA 111
- Actual margin: MIA -25 (away won — SAS blowout)
- Our spread: SAS -3.2 | Market: SAS -5.0 | Error: +21.78 pts (we said SAS by 3, SAS won by 25)

### Result
- Directional: **WIN** — we predicted SAS to win, SAS dominated
- ATS: **AWAY COVERED** — market SAS -5.0; SAS won by 25 (covered easily)

### Actual Box Score (top players by minutes)

**MIA (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Norman Powell | 29:43 | 21 | 4 | 2 |
| Bam Adebayo | 28:42 | 18 | 3 | 4 |
| Tyler Herro | 26:14 | 18 | 5 | 2 |
| Pelle Larsson | 22:38 | 7 | 1 | 3 |
| Kel'el Ware | 22:19 | 7 | 7 | 1 |
| Kasparas Jakucionis | 22:17 | 8 | 6 | 5 |
| Davion Mitchell | 22:10 | 2 | 2 | 3 |
| Andrew Wiggins | 19:38 | 9 | 3 | 1 |

**SAS (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| De'Aaron Fox | 28:56 | 14 | 3 | 6 |
| Victor Wembanyama | 26:19 | 26 | 15 | 4 |
| Dylan Harper | 24:31 | 21 | 4 | 6 |
| Keldon Johnson | 23:32 | 21 | 6 | 1 |
| Stephon Castle | 22:53 | 19 | 7 | 6 |
| Julian Champagnie | 21:57 | 3 | 5 | 0 |
| Harrison Barnes | 21:47 | 13 | 3 | 1 |
| Devin Vassell | 21:02 | 6 | 2 | 4 |

### Lineup Accuracy
- **SAS rotation matched profile closely**: Wembanyama, Fox, Harper, Johnson, Castle, Champagnie, Barnes, Vassell all played heavy minutes as expected. 100% coverage was accurate.
- **MIA bench rotation differs**: Davion Mitchell (22 min) and Andrew Wiggins (19 min) appeared instead of Jaime Jaquez Jr. (in profile at 11.6%). Jaquez may have been out or limited — profile had him sparse at 7/15 games.
- **SAS kept their starters short**: Minutes were capped ~29 min each for all starters — typical of a blowout where the bench finishes. The real margin likely would've been even larger with starters playing 36.

### What the Model Got Right / Wrong
1. **Direction correct, magnitude wildly off**: Both model and market underestimated SAS by 20+ pts. Wembanyama (26/15/4) and 5 SAS players scoring 13+ is a complete team performance.
2. **Both teams' profiles were accurate**: 100% coverage on both sides. The miss wasn't lineup uncertainty — it's that the raw RAPM gap translated to only -3.2 pts calibrated, but the actual talent gap was worth 25 pts. This suggests the calibration α=6.097 compresses blowout risk.
3. **LOW SIGNAL non-actionable call was correct**: We didn't flag this as a bet. The market was closer (-5 vs actual -25) but also way off. Correctly passed.
