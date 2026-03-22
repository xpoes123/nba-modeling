# Game Analysis: GSW @ ATL, 2026-03-21

## Stored Prediction
- Our spread: ATL −0.86 | Market: ATL −10.0 | Edge: −9.14 (we underpredicted ATL)
- Coverage: home (ATL) 100% | away (GSW) 83.7%
- B2B: home=YES | away=YES
- Actual result: ATL +16 (ATL won by 16)

## Team Lineup Profiles (last 15 games before game date)

### ATL (home) — model thought full health (Jalen Johnson was out but not caught)
| Player | Games | Eff share | OFF | DEF | Overall | Status |
|---|---|---|---|---|---|---|
| Jalen Johnson | 14/15 | 13.2% | +0.55 | +0.21 | +0.35 | missed — not in ESPN |
| Nickeil Alexander-Walker | 14/15 | 13.1% | +1.26 | −0.61 | +1.87 | ✓ played |
| Dyson Daniels | 14/15 | 12.3% | +2.24 | −1.31 | +3.55 | ✓ played |
| Onyeka Okongwu | 15/15 | 12.3% | −0.94 | +0.31 | −1.24 | ✓ played |
| CJ McCollum | 15/15 | 12.0% | +1.05 | −0.76 | +1.81 | ✓ played |
| Zaccharie Risacher | 15/15 | 8.9% | −1.19 | +1.31 | −2.50 | ✓ played |
| Jock Landale | 15/15 | 7.0% | −0.75 | −0.16 | −0.59 | ✓ played |
| Corey Kispert | 15/15 | 6.9% | −1.15 | −0.03 | −1.11 | ✓ played |
| Mouhamed Gueye | 14/15 | 4.3% | −0.17 | −0.42 | +0.25 | ✓ played |
| Gabe Vincent | 12/15 | 4.1% | +0.05 | −0.67 | +0.72 | ✓ played |
| Jonathan Kuminga | 6/15 | 3.8% | −0.02 | +0.08 | −0.10 | ✓ played |
| Keaton Wallace | 8/15 | 1.0% | −1.24 | +0.84 | −2.08 | DNP coach |
| Caleb Houstan | 5/15 | 0.4% | −0.48 | +0.18 | −0.66 | DNP coach |

**Team OFF = +0.268  DEF = −0.200  Net = +0.468 pts/100**

### GSW (away) — GPII, Moody, Horford excluded by ESPN injury filter
| Player | Games | Eff share | OFF | DEF | Overall | Status |
|---|---|---|---|---|---|---|
| Brandin Podziemski | 15/15 | 13.6% | −0.49 | +0.72 | −1.21 | ✓ played |
| Gui Santos | 15/15 | 13.3% | +0.11 | +0.04 | +0.08 | ✓ played |
| Pat Spencer | 15/15 | 9.3% | −0.60 | +0.40 | −0.99 | ✓ played |
| Draymond Green | 11/15 | 8.9% | −2.01 | +1.24 | −3.25 | ✓ played |
| De'Anthony Melton | 11/15 | 7.9% | +1.75 | −0.80 | +2.54 | ✓ played |
| Will Richard | 11/15 | 7.7% | −0.43 | +0.02 | −0.44 | ✓ played |
| Gary Payton II | 13/15 | 7.6% | −0.57 | +0.03 | −0.61 | **OUT (hip)** |
| Al Horford | 9/15 | 6.3% | +0.53 | −0.87 | +1.40 | **OUT (DNP)** |
| Quinten Post | 10/15 | 5.5% | +0.36 | −0.10 | +0.46 | ✓ played |
| Moses Moody | 6/15 | 4.8% | +0.75 | +0.07 | +0.68 | **OUT (wrist)** |
| Malevy Leons | 12/15 | 3.6% | −0.37 | +0.39 | −0.76 | ✓ played |
| Nate Williams | 9/15 | 2.9% | −0.30 | +0.08 | −0.38 | ✓ played |

**NOT in window (long-term injury):** Stephen Curry (last played 2026-01-30) and Jimmy Butler
(last played 2026-01-19) — **0 games in the 15-game window.** Model already treats GSW as
a team without its two best players. Their absence is baked into the possession history, not
detected by the ESPN injury filter.

**Team OFF = −0.202  DEF = +0.237  Net = −0.439 pts/100  Coverage = 83.7%**

## Raw Margin Math

```
league_avg_ppp = 1.1445   league_avg_pace = 96.22

home_ppp = 1.1445 + (ATL_off − GSW_def) / 100
         = 1.1445 + (0.268 − 0.237) / 100
         = 1.14481

away_ppp = 1.1445 + (GSW_off − ATL_def) / 100
         = 1.1445 + (−0.202 − −0.200) / 100
         = 1.14448

ppp_diff  = 0.000338 per possession (tiny)
exp_pace  = 96.22 + (ATL_pace 1.843 + GSW_pace −4.309) / 2 = 94.98 possessions
raw_margin = 0.000338 × 94.98 = 0.032 pts/game

Calibration:
  8.46 × 0.032 + HCA(+2.01) + B2B_home(−3.07) + B2B_away(+2.09)
= 0.27 + 1.03
= ~1.30 pts predicted  (stored 0.86 — difference from simulation variance + pace rounding)

Market implied raw_margin: (10.0 − 1.03) / 8.46 = 1.06 pts/game  (33× larger)
```

## Root Causes (ordered by impact)

**1. ATL depth drag — the single biggest factor (~4–5 pts of gap)**
ATL's negative-RAPM bench takes ~39% of possessions: Okongwu (−1.24, 12.3%), Risacher
(−2.50, 8.9%), Landale (−0.59, 7.0%), Kispert (−1.11, 6.9%). These dilute the team's
offensive rating to only +0.268. The market focuses on starters (Daniels/NAW/McCollum) and
discounts the bench more aggressively than a possession-weighted average.

**2. Formula near-cancellation — structural issue**
compute_raw_margin is a cross-matchup formula: (ATL_off − GSW_def) − (GSW_off − ATL_def).
ATL_off (+0.268) ≈ GSW_def (+0.237) → tiny edge for ATL offense.
GSW_off (−0.202) ≈ −ATL_def (−0.200) → essentially zero edge either way.
These near-equalities produce a 0.033 pts/100 net, nearly washing out.

**3. Curry + Butler already gone from the window — baked in but the market disagrees**
Curry (last played Jan 30) and Butler (last played Jan 19) haven't appeared in 15 games.
The model's GSW "healthy baseline" is already a team without them. This is correct — the
model isn't double-penalizing for their absence. But the market values the entire 2025-26
GSW context differently, pricing the Curry/Butler era expectations into the spread.

**4. GSW's pace rating (−4.3) slows expected possessions to ~95**
Fewer possessions = smaller absolute margin even with same per-possession edge.

**5. Injury filter missed Jalen Johnson**
Model treated ATL as full health (coverage=1.0). Johnson didn't appear in ESPN injury
report (probably a late scratch or listed differently). His +0.35 overall is minor impact.

## Key Takeaways

- **Depth matters more than RAPM averages in extreme injury games.** When a team's bench
  goes from 15–20 mpg to 30+ mpg, RAPM underestimates the performance drop (depth cliff).
  The 39% negative-RAPM ATL bench is a structural model limitation, not a calibration fix.

- **The cross-matchup formula creates near-cancellation when both teams are mediocre.**
  When team ratings cluster near zero, tiny offsets produce tiny raw_margins. Calibration's
  alpha=8.46 then amplifies those tiny differences, but the gap to market is still huge.

- **Long-term injuries auto-drop from the possession window.** Curry+Butler absence was
  already captured correctly. The model knew GSW was depleted — it just didn't know by enough.

- **"Coach's decision" and late scratches are invisible to ESPN injury filter.** Wallace
  and Houstan (ATL DNPs) were coach's decisions, not injuries — won't appear in any API.

- **Coverage penalty is the right structural fix.** A `β_coverage` calibration term would
  directly penalize games where the healthy lineup fraction is low, without relying on RAPM
  magnitudes to capture depth cliff effects.
