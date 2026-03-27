# Game Analysis: BKN @ POR, 2026-03-23

## Stored Prediction
- Our spread: POR -16.1 | Market: POR -14.5 | Edge: +1.61 (we overpredict POR slightly) | Tier: HIGH
- Win prob: 88.3% (home) | Sim std: 13.52 pts | Market total: 219.5
- Coverage: home (POR) 95.8% | away (BKN) 93.4%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### POR (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Deni Avdija | 9/15 | 13.9% | +0.50 | -0.42 | +0.92 | |
| Jerami Grant | 14/15 | 13.6% | -0.14 | -0.43 | +0.29 | |
| Toumani Camara | 15/15 | 13.4% | +0.35 | +0.36 | -0.01 | |
| Jrue Holiday | 15/15 | 12.7% | +1.54 | -1.42 | +2.97 | |
| Donovan Clingan | 14/15 | 11.3% | +0.35 | -0.53 | +0.88 | |
| Scoot Henderson | 15/15 | 10.2% | -0.50 | +0.54 | -1.03 | |
| Robert Williams III | 11/15 | 8.2% | +0.34 | -0.25 | +0.59 | |
| Vit Krejci | 11/15 | 7.2% | -0.45 | +0.61 | -1.07 | |
| Kris Murray | 12/15 | 7.2% | -0.90 | +0.23 | -1.12 | |
| Matisse Thybulle | 15/15 | 6.4% | +0.38 | -0.49 | +0.87 | |
| Sidy Cissoko | 14/15 | 5.4% | -0.58 | +0.92 | -1.50 | |
| Blake Wesley | 10/15 | 3.8% | -1.49 | +1.06 | -2.56 | |

**Team OFF = +0.12  DEF = -0.14  Net = +0.26 pts/100  Coverage = 95.8%**

### BKN (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Michael Porter Jr. | 8/15 | 12.6% | +1.02 | -1.55 | +2.56 | |
| Egor Demin | 3/15 | 10.5% | +0.07 | -0.15 | +0.21 | sparse window |
| Ben Saraf | 12/15 | 10.4% | -1.35 | +0.69 | -2.04 | |
| Drake Powell | 9/15 | 10.1% | -3.14 | +2.11 | -5.24 | |
| Nic Claxton | 12/15 | 9.6% | -2.32 | +0.34 | -2.66 | |
| Nolan Traore | 14/15 | 9.6% | -1.29 | +0.56 | -1.85 | |
| Ziaire Williams | 12/15 | 9.3% | -1.58 | +1.08 | -2.66 | |
| Chaney Johnson | 8/15 | 9.0% | +0.07 | -0.04 | +0.12 | |
| Danny Wolf | 15/15 | 8.9% | -1.51 | +1.17 | -2.68 | |
| Terance Mann | 10/15 | 8.5% | -0.79 | +0.02 | -0.81 | |
| Noah Clowney | 12/15 | 8.4% | -1.09 | -0.42 | -0.67 | |
| Day'Ron Sharpe | 8/15 | 8.1% | -0.53 | +0.30 | -0.82 | |

**Team OFF = -1.23  DEF = +0.40  Net = -1.63 pts/100  Coverage = 93.4%**

Note: Egor Demin sparse (3/15) and Michael Porter Jr. sparse (8/15) -- BKN's best player has only
been available in just over half the window. BKN team OFF = -1.23 is one of the weakest on the slate.
Drake Powell is an exceptionally low-rated player (-5.24 overall) with significant share.

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (POR_off + BKN_def) / 100
         = 1.144596 + (0.1210 + 0.4025) / 100
         = 1.149831

away_ppp = 1.144596 + (BKN_off + POR_def) / 100
         = 1.144596 + (-1.2320 + (-0.1405)) / 100
         = 1.130871

exp_pace = 96.2142 + (POR_pace +2.060 + BKN_pace -0.810) / 2 = 96.839
raw_margin = (1.149831 - 1.130871) * 96.839 = +1.836 pts

Calibrated:
  6.097 x 1.836 + HCA(POR +3.419) + B2B(0) + B2B(0)
= 11.196 + 3.419
= +14.61  (stored: +16.11)
```

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: HIGH (|spread| = 16.1 pts)
- Key risks:
  1. BKN is genuinely one of the weakest rosters in the league by RAPM; POR has solid veterans (Holiday, Avdija, Grant)
  2. Market agrees direction (-14.5 vs our -16.1); we slightly oversize the spread
  3. Michael Porter Jr. only 8/15 games -- if he's healthier than modeled, BKN gets modest boost but still very weak
  4. Drake Powell at 10.1% share with -5.24 overall is a major drag on BKN
- Actionable: YES (HIGH) -- both model and market agree on a large POR win

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: POR 134 @ BKN 99
- Actual margin: POR +35 (home won — massive blowout)
- Our spread: POR -16.1 | Market: POR -14.5 | Error: -18.89 pts (we said POR by 16, POR won by 35)

### Result
- Directional: **WIN** — we predicted POR to win, POR dominated
- ATS: **HOME COVERED** — market POR -14.5; POR won by 35 (POR covered easily)

### Actual Box Score (top players by minutes)

**POR (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Kris Murray | 30:30 | 16 | 5 | 5 |
| Toumani Camara | 28:14 | 35 | 3 | 3 |
| Sidy Cissoko | 27:52 | 5 | 2 | 4 |
| Jrue Holiday | 27:15 | 11 | 7 | 4 |
| Donovan Clingan | 24:09 | 7 | 15 | 0 |
| Scoot Henderson | 23:50 | 13 | 3 | 4 |
| Deni Avdija | 20:53 | 18 | 5 | 2 |
| Blake Wesley | 20:11 | 9 | 2 | 5 |

**BKN (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Josh Minott | 32:44 | 15 | 5 | 1 |
| Jalen Wilson | 31:21 | 11 | 4 | 1 |
| Chaney Johnson | 26:29 | 12 | 5 | 3 |
| Malachi Smith | 24:17 | 5 | 2 | 3 |
| Tyson Etienne | 24:02 | 18 | 1 | 4 |
| Ziaire Williams | 23:58 | 16 | 4 | 1 |
| Nic Claxton | 21:31 | 10 | 4 | 2 |
| Ben Saraf | 18:47 | 10 | 3 | 2 |

### Lineup Accuracy
- **POR's Jerami Grant absent**: Profile had Grant at 13.6% (14/15 games) but he's absent from the box score top 8. POR won by 35 without their second-best player — depth is strong enough.
- **Toumani Camara had a career game**: In profile at 13.4% (-0.01 overall). Scored 35 pts — a significant outperformance vs his RAPM rating.
- **Michael Porter Jr. absent from BKN box**: Profile had MPJ at 12.6% (8/15 games, sparse). He didn't appear in top 8 — possibly out. BKN's best player missing amplified the blowout.
- **BKN's Egor Demin (sparse) not in top 8**: Another missing piece from a depleted BKN roster.
- **POR played full depth rotation**: No starter exceeded 30 min — blowout management. Bench players (Cissoko, Wesley, Henderson) got meaningful time.

### What the Model Got Right / Wrong
1. **Direction correct by a mile**: Both model and market agreed POR wins big. POR was 35 instead of 16, which is again in the systemic blowout underestimation category seen today (ATL, LAC).
2. **BKN weaker than modeled**: MPJ absent (only 8/15 anyway), Egor Demin absent. The 93.4% coverage flag was meaningful — BKN's few halfway-decent players (MPJ) sat out.
3. **HIGH tier win**: Both model and market agreed, both covered. Clean directional pick.
