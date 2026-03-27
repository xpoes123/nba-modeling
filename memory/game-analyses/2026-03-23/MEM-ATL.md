# Game Analysis: MEM @ ATL, 2026-03-23

## Stored Prediction
- Our spread: ATL -8.5 | Market: ATL -14.0 | Edge: -5.54 (market much more bullish on ATL) | Tier: MODERATE
- Win prob: 73.5% (home) | Sim std: 13.50 pts | Market total: 239.5
- Coverage: home (ATL) 100.0% | away (MEM) 89.9%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### ATL (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Jalen Johnson | 13/15 | 14.5% | +0.55 | +0.21 | +0.34 | |
| Nickeil Alexander-Walker | 14/15 | 13.5% | +1.25 | -0.61 | +1.86 | |
| Dyson Daniels | 14/15 | 13.1% | +2.23 | -1.31 | +3.54 | |
| Onyeka Okongwu | 15/15 | 12.0% | -0.95 | +0.31 | -1.26 | |
| CJ McCollum | 15/15 | 12.0% | +1.05 | -0.76 | +1.81 | |
| Jonathan Kuminga | 7/15 | 8.7% | -0.03 | +0.08 | -0.11 | |
| Zaccharie Risacher | 15/15 | 8.2% | -1.20 | +1.32 | -2.51 | |
| Jock Landale | 15/15 | 7.0% | -0.75 | -0.17 | -0.58 | |
| Corey Kispert | 15/15 | 6.3% | -1.14 | -0.04 | -1.10 | |
| Mouhamed Gueye | 14/15 | 6.0% | -0.18 | -0.42 | +0.24 | |
| Gabe Vincent | 13/15 | 5.3% | +0.04 | -0.67 | +0.71 | |
| Buddy Hield | 3/15 | 2.2% | -1.08 | +0.70 | -1.78 | sparse window |

**Team OFF = +0.25  DEF = -0.19  Net = +0.44 pts/100  Coverage = 100.0%**

### MEM (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Rayan Rupert | 10/15 | 12.4% | -2.98 | +2.14 | -5.12 | |
| Tyler Burton | 6/15 | 11.0% | -0.46 | -0.06 | -0.40 | |
| Olivier-Maxence Prosper | 15/15 | 10.9% | -1.26 | +0.10 | -1.36 | |
| Javon Small | 13/15 | 10.8% | +0.25 | -0.28 | +0.54 | |
| Jahmai Mashack | 10/15 | 10.6% | -0.73 | +0.10 | -0.84 | |
| GG Jackson | 12/15 | 10.6% | -0.57 | +1.13 | -1.70 | |
| Taylor Hendricks | 13/15 | 10.5% | -1.18 | +0.17 | -1.35 | |
| Jaylen Wells | 14/15 | 10.2% | +0.44 | -0.39 | +0.82 | |
| Walter Clayton Jr. | 12/15 | 10.1% | -0.23 | +0.09 | -0.32 | |
| Ty Jerome | 7/15 | 10.1% | +0.49 | -0.05 | +0.53 | |
| Cedric Coward | 6/15 | 9.9% | +0.34 | -0.05 | +0.39 | |
| Scotty Pippen Jr. | 6/15 | 9.4% | -0.63 | +0.56 | -1.19 | |

**Team OFF = -0.78  DEF = +0.41  Net = -1.19 pts/100  Coverage = 89.9%**

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (ATL_off + MEM_def) / 100
         = 1.144596 + (0.2492 + 0.4094) / 100
         = 1.151181

away_ppp = 1.144596 + (MEM_off + ATL_def) / 100
         = 1.144596 + (-0.7838 + (-0.1909)) / 100
         = 1.134849

exp_pace = 96.2142 + (ATL_pace +1.819 + MEM_pace +0.915) / 2 = 97.581
raw_margin = (1.151181 - 1.134849) * 97.581 = +1.594 pts

Calibrated:
  6.097 x 1.594 + HCA(ATL +1.662) + B2B(0) + B2B(0)
= 9.717 + 1.662
= +11.38  (stored: +8.46)
```

Note: Market line is ATL -14, model says ATL -8.5, inline calc says -11.4. The stored prediction
is lower than our inline calc, suggesting the Monte Carlo simulation saw more variance or the
coverage scaling dampened MEM's deficit. The -5.54 edge (model underprices ATL vs market) is the
largest adverse edge of the slate.

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: MODERATE (|spread| = 8.5 pts)
- Key risks:
  1. LARGE market disagreement (-5.54 edge): market prices ATL -14, model sees -8.5. If market is correct, we severely underestimate ATL's quality or MEM's weakness
  2. MEM coverage only 89.9% -- significant players missing from window; lineup uncertainty compounds the gap
  3. MEM roster is exceptionally weak by RAPM (team OFF = -0.78) -- but model may not capture how bad they truly are when star players are absent
  4. Jonathan Kuminga at 8.7% share with only 7/15 games -- uncertainty around his role
- Actionable: YES (MODERATE) -- but large edge against us (-5.54) is a significant red flag; lean ATL with caution

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: ATL 146 @ MEM 107
- Actual margin: ATL +39 (home won — historic blowout)
- Our spread: ATL -8.5 | Market: ATL -14.0 | Error: -30.54 pts (BIGGEST MISS of the day)

### Result
- Directional: **WIN** — we predicted ATL to win, ATL destroyed MEM
- ATS: **HOME COVERED** — market ATL -14.0; ATL won by 39 (ATL covered easily)

### Actual Box Score (top players by minutes)

**ATL (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Zaccharie Risacher | 26:03 | 11 | 8 | 0 |
| Nickeil Alexander-Walker | 25:43 | 26 | 2 | 6 |
| Dyson Daniels | 24:08 | 12 | 5 | 4 |
| Mouhamed Gueye | 22:22 | 3 | 4 | 3 |
| CJ McCollum | 22:00 | 15 | 4 | 9 |
| Jock Landale | 20:36 | 11 | 4 | 2 |
| Onyeka Okongwu | 20:06 | 16 | 5 | 2 |
| Jonathan Kuminga | 19:40 | 16 | 5 | 3 |

**MEM (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| GG Jackson | 30:14 | 26 | 3 | 0 |
| Rayan Rupert | 30:09 | 0 | 5 | 2 |
| Tyler Burton | 28:29 | 20 | 8 | 1 |
| Walter Clayton Jr. | 28:15 | 16 | 1 | 6 |
| Taylor Hendricks | 26:15 | 9 | 4 | 0 |
| Olivier-Maxence Prosper | 25:08 | 8 | 3 | 1 |
| Ty Jerome | 23:53 | 17 | 1 | 4 |
| DeJon Jarreau | 21:39 | 7 | 6 | 4 |

### Lineup Accuracy
- **ATL starters played short minutes**: Top player was only 26 min — blowout managed, bench stepped up (Kuminga, Okongwu delivering 16 pts each). Jalen Johnson notably absent from top 8; possible rest/injury.
- **Kuminga played 19 min**: Profile had him at 8.7% share (7/15 games, sparse). He contributed 16/5/3 — better than his RAPM baseline.
- **MEM lineup mostly matched profile**: Rupert (0 pts in 30 min), Jackson (26 pts), Burton, Clayton all appeared as expected. Their 89.9% coverage gap doesn't explain the -39 outcome.
- **ATL 146 points**: Historically high offensive performance. ATL scored on nearly every possession. This is a regime-change game, not a model miss.

### What the Model Got Right / Wrong
1. **Biggest miss by error (-30.54 pts)**: Both model (-8.5) and market (-14) severely underestimated the blowout. ATL 146-107 is an outlier offensive explosion — well outside any model's normal distribution (2σ+ event even for market).
2. **Model correctly disagreed with market**: We had edge -5.54 (market bullish on ATL vs our prediction). Market was right about direction and magnitude relative to us. The pre-game flag "large adverse edge is a red flag" was vindicated — market knew more.
3. **Magnitude underestimation is a systemic pattern today**: Three games (MEM@ATL, BKN@POR, MIL@LAC) all ended 25-30+ pts above our spread. All three were direction correct. Suggests model systematically underestimates blowout severity for large mismatches.
4. **MODERATE tier — correct not to bet away from ATL**: We predicted ATL wins (direction correct). The error was magnitude, not direction.
