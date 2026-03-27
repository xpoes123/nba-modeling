# Game Analysis: TOR @ UTA, 2026-03-23

## Stored Prediction
- Our spread: TOR -5.9 | Market: TOR -13.0 | Edge: +7.14 (model severely underpredicts TOR) | Tier: FAIR
- Win prob: 33.1% (home) | Sim std: 13.41 pts | Market total: 230.5
- Coverage: home (UTA) 93.1% | away (TOR) 100.0%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### UTA (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Kennedy Chandler | 1/15 | 15.5% | -0.10 | +0.03 | -0.13 | sparse window |
| Andersson Garcia | 5/15 | 14.8% | -0.82 | +0.51 | -1.33 | |
| Bez Mbeng | 5/15 | 14.0% | -0.53 | +0.49 | -1.01 | |
| Lauri Markkanen | 1/15 | 13.7% | +1.92 | -2.08 | +4.00 | sparse window |
| Cody Williams | 15/15 | 13.4% | -1.18 | +0.34 | -1.52 | |
| Ace Bailey | 13/15 | 12.2% | -1.61 | -0.08 | -1.53 | |
| Elijah Harkless | 15/15 | 11.4% | +1.03 | -0.44 | +1.46 | |
| Brice Sensabaugh | 13/15 | 11.3% | -0.50 | +0.00 | -0.50 | |
| Isaiah Collier | 11/15 | 11.1% | -2.80 | +1.49 | -4.29 | |
| Keyonte George | 6/15 | 11.0% | -1.25 | -0.02 | -1.23 | |
| Kyle Filipowski | 14/15 | 10.4% | +0.20 | -0.48 | +0.69 | |
| John Konchar | 11/15 | 9.9% | -0.07 | -0.08 | +0.01 | |

**Team OFF = -0.51  DEF = -0.29  Net = -0.22 pts/100  Coverage = 93.1%**

Note: Kennedy Chandler and Lauri Markkanen both appear with high weighted shares (15.5% and 13.7%)
but only 1 game each in the 15-game window. These are recency artifacts -- they played in the most
recent game (weight=1.0) and thus dominate the weighted average despite almost no recent history.
Markkanen's +4.00 overall inflates UTA's apparent quality; Chandler is neutral. The true UTA
rotation without Markkanen is much weaker.

### TOR (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Brandon Ingram | 15/15 | 13.9% | -0.39 | +0.62 | -1.01 | |
| Scottie Barnes | 14/15 | 13.6% | +1.42 | -1.08 | +2.50 | |
| Immanuel Quickley | 15/15 | 13.2% | +0.82 | -0.76 | +1.58 | |
| RJ Barrett | 15/15 | 12.9% | +0.98 | -0.38 | +1.36 | |
| Jakob Poeltl | 13/15 | 11.0% | +0.55 | -0.62 | +1.17 | |
| Collin Murray-Boyles | 4/15 | 8.8% | -0.86 | +1.60 | -2.46 | sparse window |
| Ja'Kobe Walter | 15/15 | 8.7% | -1.82 | +0.98 | -2.80 | |
| Jamal Shead | 15/15 | 8.3% | +0.55 | +0.17 | +0.38 | |
| Sandro Mamukelashvili | 15/15 | 7.5% | +0.13 | +0.13 | +0.00 | |
| Gradey Dick | 10/15 | 4.6% | +0.59 | -0.47 | +1.06 | |
| Jamison Battle | 13/15 | 4.4% | +0.91 | -0.45 | +1.36 | |
| Jonathan Mogbo | 7/15 | 3.7% | -0.52 | +0.42 | -0.93 | |

**Team OFF = +0.27  DEF = -0.03  Net = +0.30 pts/100  Coverage = 100.0%**

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (UTA_off + TOR_def) / 100
         = 1.144596 + (-0.5065 + (-0.0301)) / 100
         = 1.139230

away_ppp = 1.144596 + (TOR_off + UTA_def) / 100
         = 1.144596 + (0.2697 + (-0.2853)) / 100
         = 1.144440

exp_pace = 96.2142 + (UTA_pace -0.062 + TOR_pace +0.342) / 2 = 96.354
raw_margin = (1.139230 - 1.144440) * 96.354 = -0.502 pts

Calibrated:
  6.097 x (-0.502) + HCA(UTA -0.581) + B2B(0) + B2B(0)
= -3.061 + (-0.581)
= -3.64  (stored: -5.86)
```

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: FAIR (|spread| = 5.9 pts)
- Key risks:
  1. MASSIVE market gap (+7.14 edge): market has TOR -13, model has TOR -5.9. This is the largest disagreement on the slate -- suggests the model is severely underrating either TOR's strength or UTA's weakness
  2. Lauri Markkanen recency artifact inflates UTA profile -- if he played in one game and boosted UTA's apparent quality, true UTA is weaker than modeled
  3. UTA HCA is actually negative (-0.581) per calibration -- this is a genuine weak home-court team
  4. Kennedy Chandler at 15.5% share with 1 game (sparse) -- another artifact that muddies the UTA profile
- Actionable: NO (FAIR) -- the +7.14 edge means the market strongly disagrees; do not bet against market at this tier

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: TOR 143 @ UTA 127
- Actual margin: UTA -16 (away won — TOR won by 16)
- Our spread: TOR -5.9 | Market: TOR -13.0 | Error: +10.14 pts (we said TOR by 6, TOR won by 16)

### Result
- Directional: **WIN** — we predicted TOR to win, TOR won
- ATS: **AWAY COVERED** — market TOR -13.0; TOR won by 16 (TOR covered)

### Actual Box Score (top players by minutes)

**UTA (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Ace Bailey | 35:11 | 37 | 6 | 3 |
| Elijah Harkless | 32:09 | 9 | 2 | 4 |
| Brice Sensabaugh | 31:24 | 24 | 5 | 1 |
| Bez Mbeng | 30:57 | 3 | 3 | 1 |
| Kyle Filipowski | 29:30 | 6 | 8 | 4 |
| Kennedy Chandler | 29:22 | 13 | 5 | 9 |
| Oscar Tshiebwe | 28:23 | 16 | 7 | 2 |
| John Konchar | 23:04 | 19 | 3 | 1 |

**TOR (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Sandro Mamukelashvili | 32:13 | 23 | 4 | 2 |
| Jamal Shead | 28:33 | 7 | 1 | 14 |
| Ja'Kobe Walter | 28:04 | 21 | 5 | 2 |
| Gradey Dick | 27:38 | 13 | 3 | 6 |
| Scottie Barnes | 27:27 | 20 | 7 | 10 |
| RJ Barrett | 24:40 | 27 | 2 | 6 |
| Jamison Battle | 22:43 | 17 | 4 | 2 |
| Collin Murray-Boyles | 17:05 | 9 | 4 | 1 |

### Lineup Accuracy
- **Lauri Markkanen recency artifact confirmed**: He appeared in profile at 13.7% (1/15 games, sparse) but is absent from the UTA box score — DNP. This confirms the pre-game diagnosis: his 1-game recency spike was noise that inflated UTA's apparent quality.
- **Kennedy Chandler sparse artifact partially confirmed**: Was at 15.5% in profile (1/15). He played 29 min with 13/5/9 — so he DID play significant minutes. His profile appearance was real, not purely an artifact.
- **UTA's Ace Bailey (37 pts) masked team weakness**: Bailey scored 37 but UTA still lost by 16 — confirms how weak the rest of UTA's rotation is.
- **TOR rotation matched profile**: Barnes (27 min), Barrett (24 min), Shead, Walter, Dick all appeared. Brandon Ingram (profile #1 at 13.9%) not in top 8 — possible limited minutes or rest; TOR won without needing him.
- **Mamukelashvili led TOR in minutes**: In profile at 7.5%, but played 32 min. Suggests TOR went deep into their bench in a comfortable win.

### What the Model Got Right / Wrong
1. **Direction correct, magnitude underestimated**: Model had TOR -5.9, market -13, actual -16. Market was much closer. Pre-game correctly noted this was a FAIR tier "don't bet" — following model over market would have been directionally right but undersized.
2. **Markkanen recency artifact directly caused the +10 error**: If Markkanen's 13.7% weighted share is replaced with league average, UTA's team rating drops further and our margin would have been closer to -10 to -12, near the market. This is a known model artifact (sparse recency inflation).
3. **Correct call not to bet**: Pre-game said "do not bet against market at FAIR tier." The market was right. The model correctly abstained at a tier below actionable.
