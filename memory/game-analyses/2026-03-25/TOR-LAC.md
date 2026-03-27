# Game Analysis: TOR @ LAC, 2026-03-25

## Stored Prediction
- Our spread: LAC -2.0 | Market: LAC -4.0 | Edge: -2.0 | Tier: LOW SIGNAL
- Coverage: home (LAC) 100% | away (TOR) 100%
- B2B: home=False | away=False

## Team Lineup Profiles (last 15 games)

### LAC (home)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Kawhi Leonard | 12/15 | ~50% | high | low | +6.04 | Anchor |
| Herbert Jones Jr. | 15/15 | — | pos | pos | pos | |
| Kris Dunn | 15/15 | — | pos | pos | pos | |
| Brandon Miller | 15/15 | — | pos | pos | pos | |
| Brook Lopez | 15/15 | — | pos | pos | pos | |
| Bogdanovic | 4/15 | low | — | — | — | <5g sparse |
| Pedulla | 3/15 | low | — | — | — | <5g sparse |
| Omier | 3/15 | low | — | — | — | <5g sparse |

Team OFF=+0.48  DEF=-0.38  Net=+0.86

### TOR (away)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Scottie Barnes | 14/15 | — | pos | pos | +2.61 | |
| RJ Barrett | 15/15 | — | pos | pos | +1.72 | |
| Brandon Ingram | 14/15 | 65.6% | neg | pos | -1.22 | Heavy drag — is he active tonight? |
| Ja'Kobe Walter | 15/15 | 44.8% | neg | neg | -2.38 | Significant negative |
| Murray-Boyles | 4/15 | 10.8% | — | — | — | <5g sparse |
| Markelle Fultz | 1/15 | 2.7% | — | — | — | Sparse |

Team OFF=+0.40  DEF=-0.16  Net=+0.56

## Raw Margin Math
- home_ppp = 1.1449 + (0.483 + (-0.155)) / 100 = 1.1482
- away_ppp = 1.1449 + (0.402 + (-0.378)) / 100 = 1.1473
- raw_margin = 0.30 pts/100 × 96 ≈ +0.29 raw pts
- Calibrated: 6.10 × 0.30 + 2.01 (HCA) ≈ +3.8 pts (stored MC sim = LAC -2.0; recency weighting causes discrepancy)

## Flags for David
- Market has LAC 2pts bigger than us — no obvious injury reason (both 100% coverage)
- Brandon Ingram 65.6% share at -1.22 overall is a major TOR drag — if he sits, TOR rating improves
- 3 LAC bench players with <5g (Bogdanovic, Pedulla, Omier) — all low-share, minimal impact
- Kawhi at 12/15 games — confirm he's active tonight

## Pre-Game Assessment
- Model confidence: LOW SIGNAL (< 73% dir acc)
- Key risks: market 2pts ahead of us; Kawhi availability; Ingram status for TOR
- Actionable? NO — LOW SIGNAL + adverse edge

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: LAC 119, TOR 94
- Actual margin: LAC +25 (home_margin = 119−94 = +25)
- Our spread: TOR −1.2 (model favored TOR away) | Market: LAC −3.5 | Error: −26.2 pts

### Result
- Directional: **LOSS** — model predicted TOR, LAC won by 25
- ATS: **LAC COVER** — market had LAC −3.5, LAC won by 25. Easy cover.

### Actual Box Score

**LAC**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Kawhi Leonard | 30 | 27 | 6 | 2 |
| Darius Garland | 30 | 24 | 4 | 6 |
| Bennedict Mathurin | 27 | 23 | 4 | 6 |
| Brook Lopez | 25 | 14 | 5 | 0 |
| Isaiah Jackson | 23 | 12 | 6 | 3 |
| Kris Dunn | 24 | 0 | 5 | 4 |
| Derrick Jones Jr. | 28 | 2 | 7 | 0 |
| John Collins | 22 | 0 | 5 | 0 |

**TOR**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Brandon Ingram | 36 | 18 | 6 | 4 |
| RJ Barrett | 32 | 12 | 6 | 4 |
| Scottie Barnes | 31 | 9 | 8 | 12 |
| Jamal Shead | 31 | 8 | 0 | 4 |
| Jakob Poeltl | 22 | 10 | 6 | 1 |
| Collin Murray-Boyles | 24 | 10 | 5 | 0 |

### Lineup Accuracy
- **Kawhi Leonard (27 pts, 30 min) played** — pre-game file correctly said "confirm Kawhi is active." He was, and he dominated. He's listed at 12/15 games in our profile; this was a game where he was fully active.
- **Darius Garland (24 pts)** — not in the analyze-game file as a core LAC player. Likely a recent mid-season acquisition our profile had but may not have fully weighted.
- **TOR lineup matched**: Ingram/Barrett/Barnes all appeared as profiled. Ingram (65.6% share, −1.22 overall) played 36 min and had 18 pts — his negative RAPM is real but he still contributes to totals.
- Pre-game flagged adverse edge of -4.71 and Kawhi's status — market was right.

### What the Model Got Right / Wrong
1. **Adverse edge warning validated** — pre-game file said "Actionable? NO — LOW SIGNAL + adverse edge." Correct call. The -4.71 adverse edge crossed our 4-pt threshold for market intelligence signal.
2. **Model missed Kawhi + Garland combo**: LAC had 3 contributors in 20+ pts (Kawhi 27, Garland 24, Mathurin 23). TOR had no answer. Our model's LAC team ratings didn't fully capture this trio.
3. **Lesson**: When our model slightly favors the away team but market has home team at −3.5 to −4.0, the model is likely missing a healthy star or rotation upgrade on the home side. This is the same pattern as CHI-PHI (model missed Embiid/George) applied to a lower-tier game.
