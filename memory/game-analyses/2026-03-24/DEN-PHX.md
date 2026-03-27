# Game Analysis: DEN @ PHX, 2026-03-24

## Stored Prediction
- Our spread: DEN –1.2 (effectively PHX –1.2 at home) | Market: DEN –5.0 | Edge: +3.84 (model more bullish on PHX)
- Coverage: PHX 85.3% | DEN 100%
- B2B: home=No | away=No
- Tier: LOW SIGNAL — not actionable per confidence gate
- PHX HCA coefficient: +5.63 (among the highest in the league — see questions)

## Team Lineup Profiles (last 15 games)

### Phoenix Suns (HOME)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Devin Booker | 12/15 | 14.6% | +1.97 | –1.08 | +3.05 | |
| Jalen Green | 15/15 | 12.9% | –0.26 | +0.69 | –0.95 | ⚠ See questions — unexpected on PHX |
| Collin Gillespie | 15/15 | 12.6% | +0.93 | –0.81 | +1.73 | |
| Oso Ighodaro | 15/15 | 11.6% | +2.02 | –0.81 | +2.83 | |
| Royce O'Neale | 12/15 | 11.6% | –1.83 | +0.53 | –2.36 | ⚠ ESPN "Out" but report says "probable" |
| Grayson Allen | 8/15 | 11.1% | +0.35 | +0.46 | –0.11 | ⚠ ESPN "Out" but report says "questionable" |
| Jordan Goodwin | 8/15 | 9.4% | +0.43 | +0.26 | +0.17 | |
| Ryan Dunn | 13/15 | 8.1% | +0.03 | +0.09 | –0.06 | |
| Mark Williams | 4/15 | 7.8% | +0.14 | –0.52 | +0.66 | **OUT** (stress fracture, re-eval 2–3 wks) |
| Rasheer Fleming | 15/15 | 7.6% | +0.50 | +0.13 | +0.38 | |
| Amir Coffey | 10/15 | 5.2% | –0.12 | +0.17 | –0.28 | **OUT** (ankle) |
| Haywood Highsmith | 6/15 | 5.3% | –0.01 | +0.04 | –0.05 | **OUT** (knee) |
| Dillon Brooks | — | — | — | — | — | OUT (hand) — not in window |

**Excluded:** Mark Williams (OUT), Coffey (OUT), Highsmith (OUT). Coverage = 85.3%.
**⚠ ESPN inconsistency:** O'Neale and Allen have `is_out=True` in ESPN API but injury comment text says "probable" and "questionable" respectively. Whether they play is critical — see questions.
**Key nuance:** O'Neale (–2.36 overall) is a NEGATIVE player. If he's excluded from our profile, our model OVER-rates PHX. If he actually plays, PHX is weaker than our model says.
Team OFF ≈ +0.86 | DEF ≈ –0.28 (with O'Neale/Allen excluded)

### Denver Nuggets (AWAY)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Nikola Jokic | 15/15 | 15.1% | +3.81 | –2.08 | +5.88 | |
| Christian Braun | 15/15 | 14.2% | +1.60 | –0.33 | +1.94 | |
| Jamal Murray | 15/15 | 13.7% | +2.47 | –1.41 | +3.89 | |
| Cameron Johnson | 13/15 | 12.6% | +2.01 | –1.05 | +3.05 | |
| Aaron Gordon | 7/15 | 10.8% | +2.15 | –1.67 | +3.82 | ⚠ Only 7/15 games — injury absence? |
| Tim Hardaway Jr. | 15/15 | 10.7% | +0.98 | –0.14 | +1.12 | |
| Bruce Brown | 15/15 | 9.6% | –1.30 | +1.46 | –2.76 | |
| Spencer Jones | 12/15 | 7.5% | +0.29 | –0.40 | +0.69 | |
| Julian Strawther | 13/15 | 6.2% | +0.27 | +0.23 | +0.04 | |
| Jonas Valanciunas | 13/15 | 3.8% | –0.26 | –0.35 | +0.09 | |
| Peyton Watson | 1/15 | 8.0% | +2.01 | –1.21 | +3.22 | **OUT** (hamstring) — ⚠ 1-game recency artifact |

**Excluded:** Peyton Watson (OUT). Coverage = 100%.
**⚠ Watson recency artifact:** 1 game in 15-game window = slot-0 weight of 1.0. His 8.0% share inflates DEN slightly before exclusion. Consistent with Lauri Markkanen pattern from 2026-03-23.
Team OFF ≈ +1.66 | DEF ≈ –0.78

## Raw Margin Math
```
home_ppp (PHX) = 1.1446 + (0.86 + (–0.78)) / 100  =  1.1454
away_ppp (DEN) = 1.1446 + (1.66 + (–0.28)) / 100  =  1.1584

raw_margin = (1.1454 – 1.1584) × 100 = –1.30 (DEN favored per 100 poss)

Calibrated:
  alpha × raw + HCA_PHX = 6.097 × (–1.30) + 5.626 ≈ –7.93 + 5.63 = –2.30
  Stored prediction: DEN –1.16 for PHX (delta from approx vs simulation)
  PHX HCA (+5.63) is doing almost all the work here — without it, model would show DEN –7 to –8
  No B2B adjustment
```

**The +3.84 "edge" on PHX is almost entirely PHX home court (+5.63 HCA).** Raw talent clearly favors DEN (Jokic + Murray + full supporting cast). The model's pick-em result is PHX HCA overpowering DEN's talent edge.

## David's Inputs
*[Pending — questions below to be answered tomorrow morning]*

## Open Questions for David
1. **O'Neale and Allen status — CRITICAL:** ESPN API marks both as "Out" but injury description text says O'Neale is "probable" and Allen is "questionable." Are they playing tonight? Note: O'Neale (–2.36 overall) is a negative player, so if he plays, PHX is actually WEAKER than our model shows — which would support the market's DEN –5 line.
2. **Aaron Gordon only 7/15 games** — injury absence? He's rated +3.82 overall. If he's been sidelined and is back tonight, DEN is even better than our model shows.
3. **Jalen Green showing 15/15 games on PHX** — Is this the HOU star or a different player? Rated –0.95 overall (much lower than you'd expect for HOU's Jalen Green), so this may be a different/bench player with the same name, or a 2025-26 trade we don't have context on.
4. **PHX HCA = +5.63** — highest team HCA in our calibration. Does PHX genuinely have exceptional home court advantage, or does this seem like a calibration artifact inflating their home numbers?
5. **Directional gut check:** DEN with Jokic traveling to PHX — does DEN –5 feel right, or does the PHX home environment genuinely make this closer?

## Pre-Game Assessment
- **Model confidence:** LOW SIGNAL — not actionable
- **Do not bet this game.** The +3.84 edge on PHX is driven by a very high HCA coefficient (+5.63) and possible ESPN inconsistencies, not genuine model signal. Market at DEN –5 reflects a fully healthy DEN roster vs a decimated PHX lineup.
- **Key risks if betting anyway:**
  1. PHX HCA may be real (+5.63) and DEN struggles on the road at PHX
  2. O'Neale/Allen actually play → PHX slightly weaker than model (supports DEN)
  3. Aaron Gordon returns for DEN → DEN significantly stronger than model shows
- **Actionable:** No. LOW SIGNAL + conflicting injury signals + HCA-driven edge is not a real edge.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: DEN 125 @ PHX 123
- Actual margin: PHX –2 (DEN won on the road by 2)
- Our spread: DEN –1.16 (effectively PHX +1.16) | Market: DEN –5.0 | Error: +0.84 pts (**2nd best prediction of the day**)

### Result
- **Directional: WIN** — we predicted DEN to win (spread negative = PHX home underdog), DEN won ✓
- **ATS (our spread):** DEN –1.16 → actual DEN won by 2 → DEN COVERED ✓
- **ATS (market spread):** DEN –5.0 → actual DEN won by 2 → DEN DID NOT COVER ✗; PHX +5 covered ✓

### Actual Box Score
*Player stats not yet published by nba_api (game just ended — stats typically lag 15–30 min). Will remain blank; refer to nba.com box score if needed.*

**Final by quarter:**
- DEN: 28 + 39 + 30 + 28 = 125
- PHX: 35 + 22 + 38 + 28 = 123

### Lineup Accuracy
- *Box score stats unavailable at time of writing — nba_api player endpoint still showing 0s for all players despite Final status.*
- Pre-game flagged risks: O'Neale/Allen ESPN inconsistency (both marked Out but reports said probable/questionable), Aaron Gordon sparse window (7/15 games), Peyton Watson recency artifact (excluded OUT).

### What the Model Got Right / Wrong
1. **Second-best prediction of the day: error = +0.84 pts.** Our –1.16 vs actual –2 was nearly exact. PHX HCA (+5.63) did its job — it correctly counterbalanced DEN's raw talent edge and landed us at a near-pick-em result.
2. **PHX HCA (+5.63) validated.** DEN is far superior on paper (Jokic, Murray, Gordon, Johnson) but only won by 2 on the road. The PHX home court advantage appears genuine, not a calibration artifact as pre-game question #4 raised. Market at DEN –5 overcounted DEN's talent advantage.
3. **Market overcorrected in DEN's direction.** Same pattern as ORL@CLE: market went –5 for DEN, actual margin was –2. PHX +5 was a clear cover. Our LOW SIGNAL call was validated again — this wasn't a betting game, but had we bet it, PHX +5 was the correct side.
4. **LOW SIGNAL flag correct.** Pre-game reasoning (HCA-driven edge + conflicting injury signals) was sound. The model happened to nail the number but the uncertainty was real — HCA coefficients are noisy, and the O'Neale/Allen status was unresolved. Right call to stay out.
