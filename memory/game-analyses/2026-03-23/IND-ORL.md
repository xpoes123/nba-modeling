# Game Analysis: IND @ ORL, 2026-03-23

## Stored Prediction
- Our spread: ORL -14.4 | Market: ORL -13.0 | Edge: +1.44 (we agree direction, slight size diff) | Tier: HIGH
- Win prob: 86.0% (home) | Sim std: 13.38 pts | Market total: 233.5
- Coverage: home (ORL) 100.0% | away (IND) 94.7%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### ORL (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Paolo Banchero | 15/15 | 14.7% | -0.32 | -0.42 | +0.10 | |
| Desmond Bane | 15/15 | 14.3% | +0.65 | -0.04 | +0.69 | |
| Jalen Suggs | 13/15 | 12.5% | +1.13 | -0.33 | +1.45 | |
| Wendell Carter Jr. | 13/15 | 12.4% | +1.09 | +0.06 | +1.03 | |
| Tristan da Silva | 15/15 | 11.9% | +0.87 | -0.54 | +1.41 | |
| Anthony Black | 5/15 | 8.4% | +0.30 | +0.16 | +0.14 | |
| Jevon Carter | 15/15 | 8.1% | -0.11 | -0.43 | +0.31 | |
| Jett Howard | 13/15 | 6.9% | -0.07 | +0.48 | -0.56 | |
| Noah Penda | 11/15 | 6.2% | -0.01 | -0.39 | +0.39 | |
| Jamal Cain | 8/15 | 6.0% | +0.64 | +0.07 | +0.56 | |
| Moritz Wagner | 14/15 | 5.8% | -1.23 | +0.96 | -2.19 | |
| Goga Bitadze | 9/15 | 5.0% | +0.55 | -0.94 | +1.49 | |

**Team OFF = +0.41  DEF = -0.17  Net = +0.58 pts/100  Coverage = 100.0%**

### IND (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Ethan Thompson | 1/15 | 15.9% | +0.24 | -0.08 | +0.32 | sparse window |
| Jarace Walker | 15/15 | 13.5% | -2.68 | +1.29 | -3.96 | |
| Pascal Siakam | 5/15 | 13.0% | +0.32 | -1.01 | +1.33 | |
| Jalen Slawson | 5/15 | 11.4% | +0.95 | -0.86 | +1.81 | |
| Aaron Nesmith | 9/15 | 11.3% | -0.11 | -0.65 | +0.54 | |
| Andrew Nembhard | 9/15 | 11.3% | -1.83 | +0.90 | -2.72 | |
| Ivica Zubac | 5/15 | 10.1% | -0.13 | -0.18 | +0.05 | |
| Kobe Brown | 15/15 | 9.1% | -2.23 | +1.29 | -3.52 | |
| Jay Huff | 15/15 | 8.8% | -0.85 | +0.44 | -1.30 | |
| Ben Sheppard | 14/15 | 8.2% | -1.56 | +0.42 | -1.98 | |
| T.J. McConnell | 12/15 | 8.2% | -1.21 | +0.04 | -1.25 | |
| Quenton Jackson | 13/15 | 7.7% | +0.10 | -0.42 | +0.52 | |

**Team OFF = -1.14  DEF = +0.20  Net = -1.34 pts/100  Coverage = 94.7%**

Note: Ethan Thompson at 15.9% weighted share with only 1 game appearance (sparse window) -- likely
a recent call-up who dominated the most recent game and thus receives high recency weight. This
inflates his share and distorts the IND profile. Flag as unreliable.

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (ORL_off + IND_def) / 100
         = 1.144596 + (0.4054 + 0.2014) / 100
         = 1.150665

away_ppp = 1.144596 + (IND_off + ORL_def) / 100
         = 1.144596 + (-1.1362 + (-0.1674)) / 100
         = 1.131560

exp_pace = 96.2142 + (ORL_pace +1.943 + IND_pace +1.607) / 2 = 97.989
raw_margin = (1.150665 - 1.131560) * 97.989 = +1.872 pts

Calibrated:
  6.097 x 1.872 + HCA(ORL +2.851) + B2B(0) + B2B(0)
= 11.41 + 2.85
= +14.27  (stored: +14.44)
```

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: HIGH (|spread| = 14.4 pts)
- Key risks:
  1. IND roster heavily disrupted -- Ethan Thompson at 15.9% share with 1 game (sparse) signals major rotation flux; Siakam, Slawson, Zubac all sparse (5/15)
  2. IND team OFF = -1.14 pts/100 is extremely weak; if any veteran returns unexpectedly the model underestimates them
  3. Market agrees direction (-13 vs our -14.4) -- small disagreement on magnitude only
- Actionable: YES (HIGH) -- market agreement confirms direction

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: IND 128 @ ORL 126
- Actual margin: ORL -2 (away won — IND upset)
- Our spread: ORL -14.4 | Market: ORL -13.0 | Error: +16.44 pts (we said ORL by 14, IND won by 2)

### Result
- Directional: **LOSS** — we predicted ORL to win by 14, IND won
- ATS: **AWAY COVERED** — market ORL -13.0; IND won outright (IND +13 covered massively)

### Actual Box Score (top players by minutes)

**ORL (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Paolo Banchero | 36:44 | 39 | 4 | 6 |
| Tristan da Silva | 34:01 | 21 | 3 | 5 |
| Desmond Bane | 32:29 | 17 | 6 | 7 |
| Wendell Carter Jr. | 28:06 | 17 | 5 | 2 |
| Jevon Carter | 23:46 | 2 | 2 | 0 |
| Jamal Cain | 22:46 | 5 | 5 | 1 |
| Goga Bitadze | 19:54 | 6 | 7 | 4 |
| Jase Richardson | 18:32 | 9 | 1 | 3 |

**IND (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Aaron Nesmith | 35:21 | 19 | 2 | 2 |
| Andrew Nembhard | 34:48 | 13 | 7 | 14 |
| Pascal Siakam | 33:33 | 37 | 6 | 1 |
| Jarace Walker | 33:20 | 20 | 5 | 2 |
| Jay Huff | 27:40 | 7 | 6 | 0 |
| Micah Potter | 20:20 | 6 | 4 | 3 |
| T.J. McConnell | 19:41 | 13 | 0 | 6 |
| Ben Sheppard | 18:22 | 5 | 3 | 0 |

### Lineup Accuracy
- **Siakam played 33 min**: Our profile showed him at only 5/15 games (sparse). He showed up as IND's best player with 37 pts. This is exactly the returning-player gap Fix A was designed to address — Siakam was underweighted due to sparse window.
- **Nembhard 34 min / 14 ast**: Also sparse in our window (9/15); his 14 assists changed the game flow entirely.
- **IND rotation showed up strong**: Walker (33 min), Nesmith (35 min) matched their profile presence. The deep IND bench (McConnell 13 pts off bench) delivered.
- **Ethan Thompson**: Had 15.9% share from 1 game (sparse artifact) but doesn't appear in the box score top 8 — confirms he was a noise artifact, not a real rotation player.
- **Jalen Suggs absent from ORL box score**: Had 12.5% share in our profile (13/15 games) but wasn't in top 8 by minutes — possible DNP or injury limitation.

### What the Model Got Right / Wrong
1. **Biggest miss: returning stars underweighted**. Siakam (37 pts) was barely in our 15-game window. The model saw an extremely weak IND team (OFF = -1.14) because their good players were absent during the window. This is the canonical Fix A failure mode: a returning star not captured.
2. **IND rotation flux worked against ORL**: Jarace Walker, Nesmith, Nembhard all stepped up — the "sparse window" warning in the pre-game was vindicated, but IND's talent exceeded the profile, not fell below it.
3. **Model correctly flagged risk**: Pre-game noted "if any veteran returns unexpectedly the model underestimates them." That is exactly what happened. The flag was right; the bet was still HIGH tier and missed badly.
4. **HIGH tier miss on a directional upset**: This will lower our HIGH-tier accuracy meaningfully. A 14-pt favorite losing outright is a rare event but our uncertainty bands (σ=13.4) implied only ~16% chance IND won — and it happened.
