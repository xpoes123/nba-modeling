# Game Analysis: ATL @ DET, 2026-03-25

## Stored Prediction
- Our spread: DET -4.55 | Market: DET -2.5 | Edge: +2.05 (model more bullish on DET) | Tier: FAIR
- Coverage: home (DET) 93.4% | away (ATL) 100.0%
- B2B: home=False | away=False
- Home win prob: 63.3% | Away win prob: 37.2%
- Sim std: 13.41 | Market total: 226.5

## Team Lineup Profiles (last 15 games before 2026-03-25)

### DET (home) — team_id 1610612765

| Player | Games | Share (raw) | OFF | DEF | Overall | Notes |
|--------|-------|-------------|-----|-----|---------|-------|
| Jalen Duren | 15/15 | 11.5% | +2.04 | +0.19 | +1.85 | Starter, full window |
| Duncan Robinson | 15/15 | 11.0% | +1.53 | -0.68 | +2.21 | Starter, full window |
| Tobias Harris | 14/15 | 11.0% | +0.85 | -0.26 | +1.11 | Starter |
| Cade Cunningham | 11/15 | 9.8% | +3.26 | -1.38 | +4.64 | **INJURY FLAG: 0 poss last 3 games (3/19-3/23); only 13 poss on 3/17** |
| Daniss Jenkins | 14/15 | 8.7% | +0.04 | +0.55 | -0.51 | Backup PG filling in |
| Ronald Holland II | 15/15 | 7.4% | +0.39 | +1.01 | -0.63 | Starter |
| Ausar Thompson | 10/15 | 7.1% | +1.22 | +0.41 | +0.81 | Active last 5 games (267 poss); missed mid-window |
| Javonte Green | 15/15 | 6.4% | +0.46 | +0.17 | +0.30 | Reserve, consistent |
| Caris LeVert | 12/15 | 6.0% | -1.10 | +0.60 | -1.70 | Reserve, negative rating |
| Kevin Huerter | 11/15 | 5.8% | +1.46 | -0.64 | +2.10 | Moderate sparsity |
| Marcus Sasser | 10/15 | 5.0% | +0.86 | -0.07 | +0.94 | Reserve |
| Paul Reed | 13/15 | 4.5% | +0.39 | -0.24 | +0.63 | Backup C |
| Isaiah Stewart | 7/15 | 4.2% | -0.46 | +0.47 | -0.93 | **INJURY FLAG: 0 poss last 5 consecutive games (3/15-3/23)** |
| Chaz Lanier | 6/15 | 1.0% | -0.29 | +0.63 | -0.92 | Fringe rotation |
| Bobi Klintman | 2/15 | 0.2% | -0.23 | +0.04 | -0.28 | Garbage time |
| Tolu Smith | 2/15 | 0.1% | +0.07 | -0.06 | +0.14 | Garbage time |
| Isaac Jones | 1/15 | 0.1% | -0.21 | +0.24 | -0.45 | Garbage time |

**Team OFF = +1.02 | DEF = -0.04 | Net = +1.06**

Key note: Cade Cunningham is DET's best player (+4.64 overall) and has 0 possessions in the last 3 games plus minimal role on 3/17. The recency weighting system (decay=0.85^slot) deeply discounts his contribution, which is why the stored prediction (4.55) is significantly lower than the naive share-weighted calculation (~6.4). Isaiah Stewart has 0 poss in last 5 consecutive games — Fix B should have hard-excluded him (6.6% raw share stripped). Fix B exclusion accounts for DET coverage of 93.4% vs 100%.

### ATL (away) — team_id 1610612737

| Player | Games | Share (raw) | OFF | DEF | Overall | Notes |
|--------|-------|-------------|-----|-----|---------|-------|
| Nickeil Alexander-Walker | 14/15 | 12.5% | +1.37 | -0.73 | +2.11 | Starter |
| Dyson Daniels | 14/15 | 12.0% | +2.37 | -1.36 | +3.73 | Starter, strong positive |
| Onyeka Okongwu | 15/15 | 11.9% | -0.85 | +0.28 | -1.13 | Starter but negative rating |
| CJ McCollum | 15/15 | 11.7% | +1.30 | -0.92 | +2.21 | Starter, full window |
| Jalen Johnson | 12/15 | 11.0% | +0.43 | +0.36 | +0.08 | Starter, moderate sparsity |
| Zaccharie Risacher | 15/15 | 8.9% | -1.02 | +1.18 | -2.19 | Starter but significantly negative |
| Jock Landale | 15/15 | 7.1% | -0.61 | -0.32 | -0.29 | Reserve C |
| Corey Kispert | 15/15 | 6.8% | -1.13 | +0.02 | -1.15 | Reserve wing, negative |
| Mouhamed Gueye | 14/15 | 5.1% | -0.12 | -0.41 | +0.29 | Reserve |
| Jonathan Kuminga | 8/15 | 5.1% | +0.19 | -0.13 | +0.32 | Moderate sparsity; on-off pattern |
| Gabe Vincent | 14/15 | 4.9% | +0.04 | -0.66 | +0.71 | Reserve PG |
| Keaton Wallace | 9/15 | 1.2% | -1.30 | +0.96 | -2.26 | Fringe |
| Buddy Hield | 4/15 | 0.6% | -1.04 | +0.70 | -1.74 | Very sparse |
| Caleb Houstan | 6/15 | 0.6% | -0.44 | +0.19 | -0.63 | Very sparse |
| Christian Koloko | 4/15 | 0.4% | -0.11 | +0.27 | -0.38 | Fringe |
| Asa Newell | 1/15 | 0.1% | -0.82 | +0.23 | -1.06 | 1-game artifact |
| RayJ Dennis | 1/15 | 0.1% | -0.82 | +0.69 | -1.51 | 1-game artifact |

**Team OFF = +0.33 | DEF = -0.25 | Net = +0.57**

ATL has 100% coverage — no significant injury exclusions. Jonathan Kuminga (8/15) shows an on-off pattern rather than a trending injury. Asa Newell and RayJ Dennis are 1-game artifacts (weight negligible).

## Raw Margin Math

```
league_avg_ppp = 1.1449  |  league_avg_pace = 96.24

home_ppp = 1.1449 + (det_off=+1.02 + atl_def=-0.25) / 100 = 1.1449 + 0.0077 = 1.1527
away_ppp = 1.1449 + (atl_off=+0.33 + det_def=-0.04) / 100 = 1.1449 + 0.0029 = 1.1478

det_pace = -0.73  |  atl_pace = +1.67
expected_pace = 96.24 + (-0.73 + 1.67) / 2 = 96.24 + 0.47 = 96.71

raw_margin = (1.1527 - 1.1478) * 96.71 = 0.0049 * 96.71 = +0.475 pts

Calibration (v5):
  alpha = 6.097
  HCA (DET-specific) = +3.500
  B2B_home = 0 (not B2B)
  B2B_away = 0 (not B2B)

calibrated_naive = 6.097 * 0.475 + 3.500 = 2.896 + 3.500 = +6.40 pts
```

**Stored prediction = +4.55** — lower than the naive calculation (+6.40) by ~1.85 pts. This discrepancy is fully explained by recency weighting: Cade Cunningham (DET's best player, +4.64 overall) had 0 possessions in the 3 most recent games. At slot 3 (weight = 0.85^3 = 0.614) and beyond, his contribution is deeply decayed, materially reducing DET's effective team ratings versus a naive equal-weight calculation.

## Flags for David

1. **Cade Cunningham likely injured or resting (CRITICAL)**: 0 possessions in last 3 games (3/19, 3/20, 3/23) and only 13 possessions on 3/17. His presence at tip-off is the single largest swing factor — if Cade plays, our model effectively underestimates DET's strength (recency-discounted). If he remains out, the stored +4.55 spread is more appropriate. **Please confirm Cade's status before tip-off.**

2. **Isaiah Stewart excluded by Fix B**: 0 poss in last 5 consecutive games (3/15-3/23). Fix B correctly identified him as long-term absent from ESPN injury report + 5-game streak. DET coverage 93.4% confirms his 6.6% raw share was stripped. This is handled correctly — no edge risk from Stewart's absence.

3. **Market spread DET -2.5 vs model DET -4.55 (+2.05 edge)**: A 2-pt edge is within FAIR tier noise (sigma=13.4). However, the market at -2.5 may be pricing in Cade's ongoing absence more aggressively than our model's recency weighting. If market knows Cade is confirmed out and has adjusted to -2.5 accordingly, our effective edge narrows significantly.

4. **ATL's Onyeka Okongwu + Zaccharie Risacher drag**: These two starters have negative ratings (-1.13 and -2.19) and high possession shares (~12% each). They are a significant reason ATL's team net is only +0.57 despite having several positive-rated players. If Risacher or Okongwu are on injury report, ATL actually improves in their absence.

5. **Coverage is solid**: DET 93.4%, ATL 100%. No major coverage concern outside of the Cade flag.

## Pre-Game Assessment

- **Model confidence: FAIR** — |4.55| is just above the 5.0 FAIR threshold (79% historical dir. acc.). The spread is borderline LOW SIGNAL/FAIR, and the actionability depends heavily on Cade's status.

- **Key risks**:
  1. **Cade Cunningham status** — if he's confirmed out, effective DET team rating drops substantially and the stored +4.55 overestimates DET's advantage. The market's -2.5 could be the correct number or even generous to DET.
  2. **Isaiah Stewart return** — currently stripped by Fix B (5-game streak). If Stewart plays tonight, he is not in the model's profile and would be a positive surprise for DET (his -0.93 overall is a negative rater — his return could actually hurt the DET lineup depending on matchup).
  3. **ATL's defensive depth** (Dyson Daniels +3.73) — Daniels is a genuinely strong defender whose RAPM should give ATL a real shot to hold DET's replacement-level lineup.

- **Actionable? CONDITIONAL** — Do not bet DET -2.5 before confirming Cade's status. If Cade is playing, model edge of +2.05 becomes real (model probably underestimates because recency-discounted his contribution) and DET at -2.5 is potentially the right side. If Cade is confirmed out, the edge collapses — pass.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->
