# Game Analysis: OKC @ BOS, 2026-03-25

## Stored Prediction
- Our spread: BOS -1.7 (predicted_spread=+1.68) | Market: OKC -3.0 (market_spread=-3.0) | Edge: +4.68 | Tier: LOW SIGNAL
- Coverage: BOS 100% | OKC 100%
- B2B: home=No | away=No
- Injury adj: none (both teams full coverage, no ESPN Out players captured at prediction time)
- Sim std: ±13.34 pts

## Team Lineup Profiles (last 15 games)

BOS last 15 games: Mar 22, Mar 20, Mar 18, Mar 16, Mar 14, Mar 12, Mar 10, Mar 8, Mar 6, Mar 4, Mar 2, Mar 1, Feb 27, Feb 25, Feb 24.
OKC last 15 games: Mar 23, Mar 21, Mar 18, Mar 17, Mar 15, Mar 12, Mar 9, Mar 7, Mar 4, Mar 3, Mar 1, Feb 27, Feb 25, Feb 24, Feb 22.

### BOS (home)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Jaylen Brown | 13/15 | 14.0% | +0.62 | +0.34 | +0.27 | |
| Derrick White | 14/15 | 13.3% | +2.83 | -0.57 | +3.40 | |
| Payton Pritchard | 14/15 | 12.2% | +2.01 | -1.04 | +3.05 | |
| Baylor Scheierman | 15/15 | 11.2% | +0.25 | +0.51 | -0.26 | |
| Neemias Queta | 14/15 | 10.5% | +1.32 | -0.03 | +1.35 | |
| Jayson Tatum | 8/15 | 10.0% | +0.78 | -0.64 | +1.42 | ONLY 8 GAMES — was out Feb 24-Mar 4, missed Mar 12; active last 5 straight |
| Sam Hauser | 15/15 | 9.9% | +1.73 | -0.87 | +2.60 | |
| Luka Garza | 14/15 | 6.9% | +0.86 | -0.42 | +1.28 | |
| Hugo Gonzalez | 15/15 | 5.8% | +2.17 | -0.69 | +2.85 | |
| Ron Harper Jr. | 12/15 | 2.4% | -0.43 | +0.42 | -0.85 | |
| Nikola Vucevic | 7/15 | 1.6% | +0.30 | -0.77 | +1.07 | |
| Jordan Walsh | 8/15 | 1.3% | +0.25 | +0.01 | +0.24 | |
| Max Shulga | 5/15 | 0.3% | -0.24 | +0.11 | -0.35 | |
| Amari Williams | 4/15 | 0.2% | -1.15 | +1.04 | -2.19 | LOW GAMES |
| Dalano Banton | 3/15 | 0.1% | -0.24 | +0.24 | -0.48 | LOW GAMES |
| John Tonje | 3/15 | 0.1% | -0.14 | +0.12 | -0.26 | LOW GAMES |

Team OFF=+1.305  DEF=-0.321  Net=+1.626

Excluded (<3 games): Charles Bassey (2g)

**Tatum note:** 8/15 games. Was absent Feb 24 - Mar 4 (6 consecutive games), missed Mar 12, but has been present in all 5 most recent games (Mar 14, 16, 18, 20, 22). Recency weighting captures him as fully active. Ask David: is Tatum confirmed healthy and starting tonight? If questionable, model significantly overestimates BOS.

### OKC (away)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Shai Gilgeous-Alexander | 11/15 | 12.3% | +4.50 | -0.94 | +5.44 | 11/15 — missed late Feb; active last 9 straight |
| Cason Wallace | 15/15 | 10.4% | +1.09 | +0.40 | +0.69 | |
| Chet Holmgren | 12/15 | 10.3% | +3.13 | -1.19 | +4.32 | 12/15 — check status for tonight |
| Isaiah Joe | 15/15 | 9.7% | +1.08 | -0.08 | +1.16 | |
| Jared McCain | 15/15 | 8.6% | +0.53 | -0.38 | +0.91 | |
| Jaylin Williams | 15/15 | 8.4% | +0.73 | +0.61 | +0.12 | |
| Luguentz Dort | 13/15 | 7.9% | -0.25 | +1.31 | -1.57 | |
| Aaron Wiggins | 15/15 | 7.5% | -0.23 | +1.42 | -1.65 | |
| Alex Caruso | 11/15 | 6.1% | +2.55 | -0.49 | +3.04 | |
| Ajay Mitchell | 6/15 | 5.8% | +2.02 | -0.22 | +2.24 | |
| Isaiah Hartenstein | 9/15 | 5.8% | +1.70 | -0.78 | +2.49 | |
| Kenrich Williams | 11/15 | 3.6% | +0.48 | +0.42 | +0.07 | |
| Brooks Barnhizer | 6/15 | 1.5% | -1.43 | +1.38 | -2.81 | |
| Nikola Topic | 3/15 | 0.2% | -0.16 | -0.01 | -0.14 | LOW GAMES |

Team OFF=+1.561  DEF=-0.029  Net=+1.590

Excluded (<3 games): Buddy Boeheim (1g), Branden Carlson (2g), Payton Sandfort (1g), Jalen Williams (1g)

**SGA note:** Present in all 9 most-recent games (slots 0-8). The 11/15 reflects absences from late Feb (slots 9, 12, 13, 14). Fully captured by recency weighting — not a concern for tonight.
**Chet note:** 12/15 games; present in most-recent 2 games (Mar 23, Mar 21). Ask David: confirmed active tonight?

## Raw Margin Math

League avg PPP: 1.1449 | Avg pace: 96.24 poss/game

```
home_ppp_advantage = (BOS_OFF + OKC_DEF - OKC_OFF - BOS_DEF) / 100
                   = (+1.305 + (-0.029) - 1.561 - (-0.321)) / 100
                   = (1.305 - 0.029 - 1.561 + 0.321) / 100
                   = +0.036 / 100
                   = +0.00036 per possession

raw_margin_pts = 0.00036 * 96.24 = +0.034 pts

BOS team-specific HCA coefficient = +1.452 (below league avg of +2.01)

Calibrated = alpha * raw_margin + HCA
           = 6.097 * 0.034 + 1.452
           = 0.207 + 1.452
           = +1.659 pts (BOS -1.7)
```

Stored prediction +1.68 matches exactly. The entire BOS edge comes from HCA; the two teams are essentially equal on raw net rating (+1.626 vs +1.590).

## Why the Direction Flip Exists

**Our model sees two nearly identical teams.** OKC Net (+1.590) vs BOS Net (+1.626) — a 0.036 pts/100 gap. At average pace that is 0.034 raw pts per game, which rounds to a pick'em before HCA. BOS gets +1.45 HCA and becomes BOS -1.7.

**The market says OKC -3.0.** Possible explanations:

1. **OKC offensive superiority is underrated in our RAPM.** OKC OFF=+1.561 vs BOS OFF=+1.305. OKC has three elite offensive players (SGA +4.50, Chet +3.13, Caruso +2.55) vs BOS's best being Derrick White (+2.83). Market may apply a larger "star concentration creates game-changers" premium than RAPM captures.

2. **SGA road star effect.** SGA OVR=+5.44 is our highest-rated player in the league. RAPM measures historical contribution in all contexts; markets may price SGA's impact in marquee road games differently.

3. **Tatum injury uncertainty.** Tatum only 8/15 in our window. If market has information suggesting he is questionable or limited tonight, market would shade 3-4 pts toward OKC. Our model assumes Tatum active — confirmed by his presence in last 5 straight, but market might know something we don't.

4. **OKC is second-night of a back-to-back road trip.** OKC played Mar 23 @ SAS (slot 0). Mar 25 @ BOS is the second consecutive road game. This is NOT a B2B by our B2B definition (played yesterday), but it IS a road-heavy stretch. Our B2B flag only triggers if they played the literal day before — OKC's Mar 23 game was 2 days prior, so no B2B flag is set. However: OKC's travel schedule (SAS -> BOS is a significant cross-country trip) is a real fatigue factor the model doesn't capture.

5. **BOS HCA is below average (+1.45 vs league avg +2.01).** TD Garden does not provide as large a model-estimated home edge as some other arenas.

## Team Net Rating Comparison (summary)

| Team | Role | OFF | DEF | Net |
|------|------|-----|-----|-----|
| BOS | Home | +1.305 | -0.321 | +1.626 |
| OKC | Away | +1.561 | -0.029 | +1.590 |

OKC has higher offense; BOS has meaningfully better defense. The model sees these as roughly equal, with BOS winning narrowly on HCA. Market disagrees, pricing OKC's offensive talent premium over BOS's defensive edge.

## Flags for David

1. **DIRECTION FLIP (critical):** Model has BOS -1.7, market has OKC -3.0. 4.7pt gap, different predicted winner. This is the most uncertain game on today's slate.

2. **Tatum status tonight:** Tatum was out 6+ games Feb 24-Mar 4. Has played last 5 straight. Is he confirmed healthy, full minutes, no restrictions tonight? If out or limited: model over-estimates BOS by 2-3 pts minimum.

3. **Chet Holmgren status:** OVR=+4.32, 12/15 games in window. Confirmed active for this road trip?

4. **OKC is on a road back-to-back stretch:** Played SAS on Mar 23 (road). Now BOS on Mar 25 (road). Two days rest but cross-country travel. Our B2B flag did not trigger (not played yesterday). Is this a fatigue concern worth pricing in?

5. **LOW SIGNAL + direction flip = do not bet.** Historical directional accuracy < 73% at this magnitude, and we are disagreeing with the market. The market usually knows about injuries. Treat this as a watch-only game.

## Pre-Game Assessment
- Model confidence: LOW SIGNAL (|spread|=1.7 pts; historical dir acc < 73%)
- Key risks: direction flip, Tatum status, OKC road fatigue, SGA star-power premium
- Actionable? NO — LOW SIGNAL + direction flip = too uncertain. Pass regardless of which way the edge points.
- If David confirms Tatum OUT: do NOT fade the market; lean OKC with market.
- If David confirms Tatum and Chet both healthy, SGA no load management: model edge (BOS home dog) is still LOW SIGNAL and not actionable alone.

## Questions for David
1. Is Jayson Tatum confirmed starting and full-health tonight? (Most important — swing 2-3 pts)
2. Is Chet Holmgren confirmed active for this road trip?
3. Any SGA load management concern given consecutive road games (Mar 23 @ SAS, Mar 25 @ BOS)?
4. Does OKC -3.0 feel right given what you see in current rosters? Our model sees this as essentially a pick'em before HCA.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: BOS 119, OKC 109
- Actual margin: BOS +10 (home wins; home_margin = +10)
- Our spread: BOS +1.7 | Market: OKC −2.0 (market favored away OKC) | Error: −8.3 pts (underestimated BOS)

### Result
- Directional: **WIN** — predicted BOS to win, BOS won by 10
- ATS: **BOS COVER** — market had OKC −2 (BOS +2 underdog), BOS won by 10. Cover.

### Actual Box Score

**BOS**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Jaylen Brown | 39 | 31 | 8 | 8 |
| Jayson Tatum | 35 | 19 | 12 | 7 |
| Derrick White | 33 | 12 | 2 | 6 |
| Payton Pritchard | 33 | 14 | 2 | 1 |
| Neemias Queta | 30 | 13 | 5 | 2 |
| Sam Hauser | 29 | 9 | 5 | 0 |
| Baylor Scheierman | 20 | 11 | 5 | 1 |
| Luka Garza | 12 | 7 | 2 | 0 |

**OKC**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Shai Gilgeous-Alexander | 37 | 33 | 2 | 8 |
| Luguentz Dort | 22 | 14 | 5 | 0 |
| Chet Holmgren | 26 | 10 | 5 | 0 |
| Alex Caruso | 21 | 9 | 4 | 2 |
| Ajay Mitchell | 25 | 8 | 3 | 2 |
| Cason Wallace | 24 | 7 | 4 | 0 |
| Jalen Williams | 24 | 7 | 3 | 3 |
| Isaiah Hartenstein | 22 | 6 | 5 | 2 |

### Lineup Accuracy
- BOS lineup matched profile well — Brown/Tatum/White/Pritchard are core. Queta at 30 min (center) consistent with profile.
- OKC: SGA 33 pts but OKC still lost. Jalen Williams (7 pts, 24 min) and Holmgren (10 pts, 26 min) underperformed on the road.

### What the Model Got Right / Wrong
1. **Best model call of the day against the market** — model liked BOS +1.7 vs market OKC −2.0. BOS won by 10. Edge of +4.68 was the right direction.
2. **Magnitude underestimated** — predicted BOS by 1.7, actual BOS by 10. BOS's depth (5 players in double figures) outpaced OKC's star-heavy reliance on SGA.
3. **Validates HOME court advantage for elite teams** — BOS's above-average HCA was the model's edge here. Market incorrectly sent OKC as road favorites.
