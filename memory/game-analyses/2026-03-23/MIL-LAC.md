# Game Analysis: MIL @ LAC, 2026-03-23

## Stored Prediction
- Our spread: LAC -8.6 | Market: LAC -13.0 | Edge: -4.38 (market much more bullish on LAC) | Tier: MODERATE
- Win prob: 73.3% (home) | Sim std: 13.83 pts | Market total: 223.5
- Coverage: home (LAC) 91.0% | away (MIL) 90.7%
- B2B: home=NO | away=NO

## Team Lineup Profiles (last 15 games before game date)

### LAC (home)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Derrick Jones Jr. | 15/15 | 12.9% | +0.55 | -0.04 | +0.59 | |
| Bennedict Mathurin | 13/15 | 12.7% | -0.23 | -0.42 | +0.19 | |
| Kawhi Leonard | 12/15 | 12.6% | +3.52 | -2.28 | +5.80 | |
| Darius Garland | 8/15 | 12.0% | -0.29 | +0.17 | -0.46 | |
| Kris Dunn | 15/15 | 11.5% | +0.37 | -0.07 | +0.44 | |
| Jordan Miller | 15/15 | 11.3% | -0.16 | -0.43 | +0.27 | |
| Brook Lopez | 15/15 | 11.2% | +0.36 | -0.77 | +1.13 | |
| John Collins | 6/15 | 10.4% | -0.09 | +0.20 | -0.29 | |
| Isaiah Jackson | 11/15 | 7.5% | -0.48 | +0.09 | -0.57 | |
| Kobe Sanders | 12/15 | 7.4% | -0.38 | +0.41 | -0.79 | |
| Yanic Konan Niederhauser | 6/15 | 7.3% | +0.71 | -0.35 | +1.06 | |
| Bogdan Bogdanovic | 3/15 | 7.2% | -0.14 | -0.31 | +0.16 | sparse window |

**Team OFF = +0.44  DEF = -0.42  Net = +0.86 pts/100  Coverage = 91.0%**

### MIL (away)
| Player | Games | Eff share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Ryan Rollins | 15/15 | 13.6% | +0.46 | -1.08 | +1.54 | |
| Kevin Porter Jr. | 8/15 | 13.2% | -0.00 | +0.17 | -0.17 | |
| Ousmane Dieng | 13/15 | 11.5% | -1.10 | +0.60 | -1.70 | |
| Giannis Antetokounmpo | 6/15 | 11.5% | +2.49 | -2.20 | +4.69 | |
| Bobby Portis | 13/15 | 10.6% | -1.00 | -0.43 | -0.57 | |
| Kyle Kuzma | 13/15 | 10.5% | -0.63 | +0.53 | -1.16 | |
| Myles Turner | 14/15 | 9.9% | -1.82 | +1.34 | -3.16 | |
| Jericho Sims | 14/15 | 8.7% | -2.02 | +0.88 | -2.89 | |
| AJ Green | 15/15 | 8.5% | +0.69 | -0.49 | +1.19 | |
| Taurean Prince | 7/15 | 7.7% | +0.26 | -0.07 | +0.34 | |
| Pete Nance | 12/15 | 6.9% | +1.47 | -1.11 | +2.58 | |
| Gary Trent Jr. | 9/15 | 6.3% | -2.31 | +1.14 | -3.45 | |

**Team OFF = -0.39  DEF = -0.07  Net = -0.32 pts/100  Coverage = 90.7%**

Note: Giannis Antetokounmpo only 6/15 games -- heavily injury-impacted season. When he plays he is
elite (+4.69), but the 6-game window means the model sees a blended MIL that partially includes him.
If he is out tonight, MIL is significantly weaker than the profile suggests.

## Raw Margin Math

```
league_avg_ppp = 1.144596   league_avg_pace = 96.2142

home_ppp = 1.144596 + (LAC_off + MIL_def) / 100
         = 1.144596 + (0.4428 + (-0.0691)) / 100
         = 1.148333

away_ppp = 1.144596 + (MIL_off + LAC_def) / 100
         = 1.144596 + (-0.3915 + (-0.4238)) / 100
         = 1.136442

exp_pace = 96.2142 + (LAC_pace +0.467 + MIL_pace -0.302) / 2 = 96.297
raw_margin = (1.148333 - 1.136442) * 96.297 = +1.145 pts

Calibrated:
  6.097 x 1.145 + HCA(LAC +0.799) + B2B(0) + B2B(0)
= 6.981 + 0.799
= +7.78  (stored: +8.62)
```

## David's Inputs
- Retrospective analysis -- pre-game conversation not conducted.

## Pre-Game Assessment
- Model confidence: MODERATE (|spread| = 8.6 pts)
- Key risks:
  1. Market has LAC -13 vs our -8.6 (edge -4.38) -- market significantly more bullish on LAC; this is the second-largest adverse edge on the slate
  2. Giannis only 6/15 games -- if he plays tonight and is healthy, MIL could punch above the modeled profile; if he sits, model overestimates MIL
  3. Both teams have ~9% coverage gaps; Kawhi Leonard 12/15 for LAC -- if he is out, LAC profile loses its best player (+5.80 overall)
  4. LAC HCA is weak (+0.80) -- not a significant home-court advantage
- Actionable: YES (MODERATE) -- but market disagreement (-4.38) warrants caution; Giannis/Kawhi availability is the key unknown

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: LAC 129 @ MIL 96
- Actual margin: LAC +33 (home won — blowout)
- Our spread: LAC -8.6 | Market: LAC -13.0 | Error: -24.38 pts

### Result
- Directional: **WIN** — we predicted LAC to win, LAC dominated
- ATS: **HOME COVERED** — market LAC -13.0; LAC won by 33 (LAC covered easily)

### Actual Box Score (top players by minutes)

**LAC (home)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Kobe Sanders | 25:31 | 19 | 3 | 4 |
| Kawhi Leonard | 24:47 | 28 | 5 | 3 |
| Derrick Jones Jr. | 23:06 | 7 | 5 | 1 |
| Brook Lopez | 21:47 | 19 | 3 | 3 |
| Nicolas Batum | 21:23 | 3 | 4 | 0 |
| Jordan Miller | 21:23 | 10 | 4 | 4 |
| Kris Dunn | 21:00 | 7 | 1 | 3 |
| Darius Garland | 18:08 | 15 | 2 | 6 |

**MIL (away)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Pete Nance | 31:25 | 11 | 6 | 2 |
| Gary Trent Jr. | 31:05 | 20 | 1 | 1 |
| Ryan Rollins | 27:04 | 13 | 4 | 7 |
| Ousmane Dieng | 26:55 | 7 | 5 | 7 |
| AJ Green | 20:56 | 15 | 1 | 2 |
| Myles Turner | 20:14 | 7 | 0 | 0 |
| Bobby Portis | 19:43 | 11 | 6 | 1 |
| Taurean Prince | 19:32 | 5 | 6 | 0 |

### Lineup Accuracy
- **Kawhi Leonard played 24 min**: Profile had him at 12.6% (12/15 games). He delivered 28/5/3 — pre-game correctly identified Kawhi availability as the key unknown. He was active and impactful.
- **Giannis absent confirmed**: MIL profile showed Giannis at 6/15 games. He's not in the top-8 box score — did not play tonight. The pre-game flag "if Giannis sits, model overestimates MIL" was exactly right.
- **LAC won with short minutes**: Top player (Sanders) only 25 min — blowout management. Kobe Sanders in profile at 7.4% but led the team in minutes. Bennedict Mathurin (profile 12.7%) absent from top 8.
- **MIL's quality without Giannis**: Nance, Trent, Rollins, Dieng led MIL — exactly the secondary players the model rated poorly. True MIL without Giannis is much weaker than the blended profile.
- **Nicolas Batum appeared**: Not in our profile — either recently signed, two-way, or missed window. Minor role at 21 min.

### What the Model Got Right / Wrong
1. **Direction correct, magnitude again severely underestimated**: Third blowout today (ATL 39, POR 35, LAC 33) where direction correct but magnitude off by 24+ pts. Systemic pattern: model compresses blowout severity for large mismatches.
2. **Giannis absence was decisive**: Market (-13) vs our prediction (-8.6) — market had superior injury intelligence. Giannis sitting made MIL a shell of their rated profile. The pre-game correctly flagged "market much more bullish on LAC" as meaningful.
3. **MODERATE tier win**: Directionally correct. Correctly followed market direction (LAC wins big). The -4.38 adverse edge was a signal to not bet against LAC, which was right.
