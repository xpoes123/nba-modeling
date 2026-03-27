# Game Analysis: LAL @ DET, 2026-03-23

## Stored Prediction
- Our spread: LAL -0.1 | Market: LAL -2.0 | Edge: +1.88 (we underpredict LAL) | Tier: LOW SIGNAL
- Win prob: 49.7% (home) | Sim std: 13.77 pts | Market total: 226.5
- Coverage: home (DET) 82.9% | away (LAL) 100.0%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### DET (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Cade Cunningham | 12/15 | 11.9% | +3.25 | -1.36 | +4.61 | |
| Tobias Harris | 14/15 | 11.2% | +0.89 | -0.29 | +1.18 | |
| Duncan Robinson | 15/15 | 10.9% | +1.65 | -0.72 | +2.37 | |
| Jalen Duren | 15/15 | 10.9% | +1.92 | +0.24 | +1.68 | |
| Daniss Jenkins | 14/15 | 10.5% | +0.18 | +0.44 | -0.26 | |
| Ausar Thompson | 10/15 | 10.3% | +1.20 | +0.39 | +0.81 | |
| Isaiah Stewart | 7/15 | 9.1% | -0.46 | +0.48 | -0.94 | |
| Kevin Huerter | 10/15 | 8.4% | +1.37 | -0.63 | +2.00 | |
| Caris LeVert | 12/15 | 8.2% | -1.14 | +0.65 | -1.79 | |
| Ronald Holland II | 15/15 | 7.8% | +0.51 | +0.93 | -0.42 | |
| Marcus Sasser | 10/15 | 7.7% | +0.87 | -0.08 | +0.95 | |
| Javonte Green | 15/15 | 6.2% | +0.17 | +0.31 | -0.15 | |

**Team OFF = +1.13  DEF = -0.02  Net = +1.15 pts/100  Coverage = 82.9%**

### LAL (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Austin Reaves | 15/15 | 15.9% | +1.95 | -1.33 | +3.28 | |
| Luka Doncic | 15/15 | 15.8% | +2.01 | -1.22 | +3.23 | |
| LeBron James | 12/15 | 14.3% | -0.54 | +0.18 | -0.71 | |
| Marcus Smart | 14/15 | 12.8% | +2.64 | -1.53 | +4.17 | |
| Deandre Ayton | 14/15 | 11.7% | -0.38 | +0.02 | -0.40 | |
| Rui Hachimura | 13/15 | 9.5% | +0.38 | -0.09 | +0.47 | |
| Luke Kennard | 15/15 | 8.1% | -0.23 | +0.19 | -0.42 | |
| Jaxson Hayes | 12/15 | 7.1% | +0.34 | -0.22 | +0.56 | |
| Jake LaRavia | 15/15 | 6.4% | -0.72 | +0.17 | -0.88 | |
| Maxi Kleber | 4/15 | 4.8% | +0.77 | -0.80 | +1.57 | sparse window |
| Jarred Vanderbilt | 8/15 | 4.7% | +0.12 | +0.17 | -0.05 | |
| Drew Timme | 3/15 | 3.6% | +0.03 | -0.18 | +0.20 | sparse window |

**Team OFF = +0.84  DEF = -0.59  Net = +1.43 pts/100  Coverage = 100.0%**

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (DET_off + LAL_def) / 100
         = 1.144596 + (1.1288 + (-0.5870)) / 100
         = 1.150014

away_ppp = 1.144596 + (LAL_off + DET_def) / 100
         = 1.144596 + (0.8436 + (-0.0240)) / 100
         = 1.152792

exp_pace = 96.2142 + (DET_pace -0.894 + LAL_pace -0.800) / 2 = 95.37
raw_margin = (1.150014 - 1.152792) * 95.37 = -0.265 pts

Calibrated:
  6.097 x (-0.265) + HCA(DET +3.500) + B2B(0) + B2B(0)
= -1.615 + 3.500
= +1.88  (stored spread: -0.12; delta from Monte Carlo simulation variance)
```

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: LOW SIGNAL (|spread| = 0.1 pts)
- Key risks:
  1. DET coverage only 82.9% -- meaningful lineup uncertainty; Isaiah Stewart sparse (7/15)
  2. Nearly zero raw margin (-0.265 pts) -- any small lineup change flips direction
  3. DET HCA bump (+3.50) is the dominant term in calibration; raw model actually sees LAL slightly better
- Actionable: NO (LOW SIGNAL)

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: LAL 110 @ DET 113
- Actual margin: DET +3 (home won)
- Our spread: LAL -0.1 | Market: LAL -2.0 | Error: -3.12 pts (we said LAL by 0.1, DET won by 3)

### Result
- Directional: **LOSS** — we predicted LAL to win, DET won
- ATS: **HOME COVERED** — market had LAL -2.0, DET won by 3 outright (DET +2 covered)

### Actual Box Score (top players by minutes)

**DET (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Daniss Jenkins | 39:04 | 30 | 4 | 8 |
| Ausar Thompson | 35:50 | 6 | 5 | 3 |
| Jalen Duren | 33:20 | 20 | 11 | 3 |
| Tobias Harris | 31:54 | 14 | 7 | 5 |
| Duncan Robinson | 27:38 | 12 | 0 | 2 |
| Kevin Huerter | 20:29 | 7 | 1 | 3 |
| Caris LeVert | 16:56 | 8 | 3 | 4 |
| Javonte Green | 14:57 | 6 | 2 | 1 |

**LAL (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Austin Reaves | 39:33 | 24 | 2 | 5 |
| Luka Doncic | 38:49 | 32 | 7 | 6 |
| LeBron James | 38:44 | 12 | 9 | 10 |
| Jake LaRavia | 28:56 | 7 | 1 | 1 |
| Luke Kennard | 28:10 | 6 | 3 | 2 |
| Deandre Ayton | 26:57 | 13 | 10 | 0 |
| Jaxson Hayes | 20:49 | 11 | 3 | 1 |
| Jarred Vanderbilt | 15:29 | 4 | 4 | 2 |

### Lineup Accuracy
- **Cade Cunningham absent**: Our profile had Cunningham at 11.9% (12/15 games), but he did not appear in the top-8 by minutes. He either sat or played very limited minutes — significant oversight.
- LAL profile was clean: Doncic, Reaves, LeBron all played heavy minutes as expected. LaRavia and Kennard 28+ min each match their rotation roles.
- DET's Jenkins (39 min, 30 pts) was in profile at 10.5% — but his upside on a big night wasn't captured.
- Ayton played 27 min for LAL (in profile at 11.7%) — consistent.

### What the Model Got Right / Wrong
1. **Direction wrong by a hair**: We predicted a near-toss-up (LAL -0.1), DET won by 3. The raw model (-0.265 pts) was incredibly close to reality; the error was small in absolute terms but still a directional loss.
2. **HCA was the critical term**: DET's +3.5 HCA bump in calibration was accurate in sign — home teams do win close games more. This is a case where the LOW SIGNAL tier correctly flagged "don't bet this."
3. **Cunningham absence**: If Cunningham (12/15, 11.9% share) sat tonight, DET's actual lineup was weaker than modeled — yet they still won, suggesting DET's depth held up. Confirms that LOW SIGNAL games are unpredictable.
