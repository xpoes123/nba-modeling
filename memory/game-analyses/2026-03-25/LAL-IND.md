# Game Analysis: LAL @ IND, 2026-03-25

## Stored Prediction
- Our spread: LAL -11.87 | Market: LAL -10.5 | Edge: -1.37 (slight adverse — market slightly less confident in LAL) | Tier: HIGH (86% dir acc)
- Coverage: home IND 95.52% | away LAL 100%
- B2B: home=False | away=False
- Injury adj: +0.9 (IND's Ivica Zubac Out — redistribution slightly narrows LAL margin from ~-12.8 base to -11.87)

## Raw Margin Math

```
league_avg_ppp  = 1.1449    league_avg_pace = 96.24
IND team OFF    = -0.963    IND team DEF    = +0.193
LAL team OFF    = +0.793    LAL team DEF    = -0.552

home_ppp (IND) = 1.1449 + (-0.963 + -0.552) / 100 = 1.1298
away_ppp (LAL) = 1.1449 + (+0.793 + +0.193) / 100 = 1.1548

expected_pace  = 96.24 + (0.663 + -0.687) / 2 = 96.23
raw_margin     = (1.1298 - 1.1548) * 96.23 = -2.407  (negative = LAL favored)

Calibration: alpha=6.097 * (-2.407) + HCA(IND)=2.966 = -11.71
Stored: -11.87  (small delta from coverage redistribution and Fix A logic)
```

## Team Lineup Profiles (last 15 games before 2026-03-25)

### IND (home) — window: 15 games
| Player | Games | Eff Share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Jarace Walker | 15 | 13.6% | -2.645 | +1.303 | -3.949 | |
| Aaron Nesmith | 10 | 10.3% | +0.062 | -0.867 | +0.929 | |
| Jay Huff | 15 | 9.3% | -0.666 | +0.314 | -0.980 | |
| Andrew Nembhard | 10 | 7.5% | -1.652 | +0.736 | -2.389 | |
| Kobe Brown | 14 | 7.5% | -2.222 | +1.269 | -3.492 | team_id=None (traded away) |
| Ben Sheppard | 14 | 7.2% | -1.602 | +0.559 | -2.161 | |
| T.J. McConnell | 12 | 7.2% | -1.140 | -0.150 | -0.990 | |
| Pascal Siakam | 6 | 5.9% | +0.414 | -1.086 | +1.500 | Only 6 games — Fix A risk |
| Quenton Jackson | 12 | 5.4% | +0.078 | -0.395 | +0.474 | team_id=None (traded away) |
| Micah Potter | 13 | 5.3% | -0.439 | -0.315 | -0.124 | |
| Obi Toppin | 11 | 5.0% | -0.411 | +0.064 | -0.475 | |
| Jalen Slawson | 5 | 4.8% | +0.950 | -0.862 | +1.812 | Only 5 games — sparse |
| Ivica Zubac | 5 | 4.4% | -0.173 | -0.153 | -0.020 | **OUT (ESPN) — 2-game streak** |
| Kam Jones | 10 | 3.5% | -1.118 | +0.348 | -1.466 | team_id=None (traded away) |
| Taelon Peter | 5 | 2.3% | -1.508 | +1.245 | -2.753 | team_id=None (traded away) |
| Ethan Thompson | 1 | 1.0% | +0.227 | -0.068 | +0.295 | **<3 games — EXCLUDED from profile** |

**Team OFF = -0.963 | Team DEF = +0.193 | Net = -1.156**

IND is well below average on both offense (-0.963) and effectively net negative. The traded-away players (Kobe Brown, Quenton Jackson, Kam Jones, Taelon Peter — all team_id=None) still appear in the possession window and contribute to the profile. Their presence is model-accurate for historical lineup composition but note these players are no longer on the team. IND's active rotation is quite negative.

### LAL (away) — window: 15 games
| Player | Games | Eff Share | OFF | DEF | Overall | Notes |
|--------|-------|-----------|-----|-----|---------|-------|
| Austin Reaves | 15 | 16.0% | +1.942 | -1.345 | +3.287 | |
| Luka Doncic | 15 | 15.9% | +2.175 | -1.329 | +3.505 | |
| LeBron James | 12 | 12.6% | -0.562 | +0.176 | -0.738 | Only 12/15 — DNP days? |
| Deandre Ayton | 14 | 11.2% | -0.341 | -0.018 | -0.323 | |
| Marcus Smart | 13 | 10.0% | +2.616 | -1.495 | +4.112 | |
| Luke Kennard | 15 | 8.6% | -0.142 | +0.126 | -0.269 | |
| Rui Hachimura | 12 | 7.6% | +0.374 | -0.064 | +0.438 | |
| Jake LaRavia | 15 | 7.4% | -0.706 | +0.152 | -0.858 | |
| Jaxson Hayes | 13 | 6.6% | +0.320 | -0.252 | +0.572 | |
| Jarred Vanderbilt | 8 | 2.3% | +0.067 | +0.188 | -0.121 | Only 8 games |
| Drew Timme | 3 | 0.6% | +0.027 | -0.176 | +0.203 | Only 3 games — at floor |
| Maxi Kleber | 3 | 0.4% | +0.776 | -0.801 | +1.577 | Only 3 games |
| Adou Thiero | 3 | 0.3% | -0.229 | +0.133 | -0.362 | Only 3 games |
| Kobe Bufkin | 4 | 0.2% | -0.614 | +0.612 | -1.225 | |
| Dalton Knecht | 4 | 0.2% | -1.265 | +0.747 | -2.012 | |
| Bronny James | 3 | 0.2% | -0.481 | -0.288 | -0.193 | Only 3 games — at floor |
| Chris Manon | 1 | 0.1% | -0.105 | +0.116 | -0.222 | **<3 games — EXCLUDED** |

**Team OFF = +0.793 | Team DEF = -0.552 | Net = +1.345**

LAL has a legitimate top-4 core: Doncic (+3.5 overall), Smart (+4.1), Reaves (+3.3) filling the three largest shares of the rotation. The remaining players are neutral to slightly negative. LeBron is mildly negative on this model (-0.738), which is the key wild card — David should sanity check whether LeBron's current usage/role aligns with this.

## IND Coverage Gap — Ivica Zubac (ESPN Out)

The IND 4.48% coverage gap is precisely explained by **Ivica Zubac** being tagged Out by ESPN at prediction time (2026-03-25 05:59:33).

- Zubac eff_share = 4.44% — excluding him yields coverage = 0.9552 (stored value, exact match)
- Zubac consecutive recent absence streak: **2 games** (missed 2026-03-21 and 2026-03-23)
- Zubac was active 2026-03-12 through 2026-03-18 (5 games), then went out again
- Zubac ratings: OFF=-0.173, DEF=-0.153, overall=-0.020 (essentially league average — near-neutral)
- **Impact**: Excluding a neutral player and redistributing to mostly-negative IND players has marginal impact. The +0.9pt injury adj suggests a small positive shift for IND (their remaining players are collectively slightly different from Zubac's near-zero rating after redistribution).
- Zubac streak=2 is **below** LONG_TERM_INJURY_STREAK=5, so Fix B did NOT pre-exclude him — he was simply caught by the live ESPN filter.

## Traded-Away Players Still in IND Window

Four players with team_id=None still appear in IND's possession history:
- **Kobe Brown** (14g, 7.5% share): team_id=None — traded from IND
- **Quenton Jackson** (12g, 5.4% share): team_id=None — traded from IND
- **Kam Jones** (10g, 3.5% share): team_id=None — traded from IND
- **Taelon Peter** (5g, 2.3% share): team_id=None — traded from IND

These four collectively represent ~18.6% of IND's profile weight. The model correctly uses their historical possession data (they actually played in those games), but they are no longer on IND's roster. As these games age out of the 15-game window, IND's profile will increasingly reflect only their current roster. **David: please confirm whether IND's current rotation has filled these departures or if there are new additions not yet showing up in the window.**

## Sparse Players (< 5 games)

**IND:**
- Jalen Slawson: 5 games (4.8% share, overall=+1.812) — just above minimum; strong rating, but sparse. If active, adds meaningful positive contribution.
- Ivica Zubac: 5 games (4.4%) — Out per ESPN.

**LAL:**
- Maxi Kleber: 3 games (0.4%, overall=+1.577) — minimal share, strong rating
- Drew Timme, Adou Thiero, Bronny James: 3 games each, all <1% share — negligible

## Flags for David

1. **IND coverage gap confirmed: Ivica Zubac (ESPN Out, 2-game streak).** His rating is near-neutral (-0.020), so his absence has minimal model impact — but it does confirm IND is using a depleted frontcourt. Confirm whether Zubac is still out tonight.

2. **Traded-away players dominate ~18.6% of IND's profile.** Kobe Brown (7.5%), Quenton Jackson (5.4%), Kam Jones (3.5%), Taelon Peter (2.3%) all have team_id=None. The model treats them as if they're still contributing to IND's lineup. If IND has added replacement players who haven't yet accumulated 15 games, those replacements are invisible to the model. **This is the key structural uncertainty for IND.**

3. **Pascal Siakam: only 6 games in window (5.9% share, overall=+1.500).** Siakam was the 2026-03-23 steal (37 pts vs ORL per prior post-mortem). If he's been playing more recently, his 6-game share may underestimate his current role. Confirm his current usage level.

4. **LeBron James: 12/15 games (missing 3).** Why did he miss 3 games? Injury rest, DNP-CD? If he's fully healthy tonight, his contribution is mildly negative per RAPM (-0.738 overall). Not a concern for the model, but notable that he's below average by our ratings. Sanity check: does this match his current-season performance?

5. **IND rotation is genuinely weak.** Even including the traded-away players, IND's weighted team OFF=-0.963, DEF=+0.193. Their true active roster (excluding traded players) is likely worse. The model may actually be UNDERESTIMATING LAL's advantage if IND's current rotation has not stabilized.

6. **Marcus Smart's rating (+4.112 overall) is the surprise.** This is the highest overall on LAL. Smart at +4.1 is carrying significant positive weight at 10% of LAL's profile. David: is Smart having a strong season or is this a RAPM artifact?

## Pre-Game Assessment

**Model confidence: HIGH** (86% directional accuracy tier, |pred|=11.87 >= 10)

**Key risks:**
1. **IND profile staleness** — ~18.6% of IND's model profile belongs to traded-away players. If their replacements are stronger (or weaker) than those departed players, the model is miscalibrated in either direction.
2. **Siakam underrepresentation** — At 6/15 games, he's near the edge of the window. If he plays starter minutes tonight (as he did vs ORL), his +1.5 overall adds meaningful positive IND quality that the model may undercount.
3. **Small adverse edge** (-1.37): market is slightly less confident in LAL than we are. This is within noise (could be market pricing in IND home-crowd, Zubac injury news, or minor Vegas adjustments). Not a significant red flag for the model direction.

**Actionable?** YES — HIGH confidence tier, model and market agree on LAL. Edge direction (model stronger on LAL than market) is slightly adverse at -1.37 but within noise. The position is: LAL is the correct side, market has them slightly shorter. If betting, take LAL -10.5 (market) rather than our -11.87. No B2B mitigating factors on either side.

**Bottom line:** LAL has the three highest-RAPM players in Doncic, Smart, Reaves filling 42% of their rotation. IND's active roster is genuinely below average with traded players masking how thin they currently are. The -10.5 to -11.87 spread range is directionally clean. David should verify Siakam's role and confirm the IND roster composition before finalizing.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->
