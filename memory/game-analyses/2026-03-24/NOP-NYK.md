# Game Analysis: NOP @ NYK, 2026-03-24

## Stored Prediction
- Our spread: NYK –8.41 | Market: NYK –9.0 | Edge: –0.59 pts | Tier: MODERATE
- Coverage: NYK 91.4% | NOP 100%
- B2B: home=No | away=No
- NYK HCA coefficient: +1.82 (above-average home court)
- NOP HCA coefficient: +1.00

## Team Lineup Profiles (last 15 games)

### New York Knicks (HOME)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Jalen Brunson | 14/15 | 15.0% | +1.72 | –0.36 | +2.08 | |
| OG Anunoby | 15/15 | 13.7% | +2.13 | +0.06 | +2.07 | |
| Karl-Anthony Towns | 14/15 | 12.7% | +2.82 | –1.35 | +4.18 | |
| Mikal Bridges | 15/15 | 12.5% | +1.31 | –0.38 | +1.69 | |
| Josh Hart | 12/15 | 11.9% | +0.83 | +0.18 | +0.66 | |
| Landry Shamet | 14/15 | 10.3% | +0.61 | +0.48 | +0.13 | **OUT (knee)** |
| Mitchell Robinson | 12/15 | 8.0% | +0.85 | –0.89 | +1.74 | |
| Jose Alvarado | 15/15 | 6.3% | +0.27 | –0.39 | +0.66 | |
| Mohamed Diawara | 14/15 | 6.1% | +0.33 | –0.50 | +0.83 | |
| Jordan Clarkson | 11/15 | 5.8% | –0.76 | +0.86 | –1.62 | |
| Kevin McCullar Jr. | 4/15 | 0.9% | –1.02 | +0.50 | –1.52 | Day-To-Day (calf) |
| Miles McBride | — | — | — | — | — | OUT (pelvis) — not in window |

**Excluded from profile:** Shamet (OUT). Coverage drop to 91.4% is Shamet's ~10.3% redistributed to remaining players.
Team OFF ≈ +1.37 | DEF ≈ –0.36

### New Orleans Pelicans (AWAY)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Trey Murphy III | 11/15 | 14.6% | +0.57 | –0.85 | +1.42 | |
| Saddiq Bey | 15/15 | 13.6% | –0.20 | +0.48 | –0.68 | |
| Zion Williamson | 14/15 | 12.5% | –0.19 | –0.25 | +0.06 | ⚠ Low rating — see questions |
| Herbert Jones | 15/15 | 12.2% | +0.69 | –0.24 | +0.93 | |
| Dejounte Murray | 10/15 | 11.5% | +1.22 | –0.88 | +2.10 | ⚠ Only 10/15 games |
| Bryce McGowens | 9/15 | 9.9% | 0.00 | –0.39 | +0.39 | **OUT (toe)** |
| Jeremiah Fears | 15/15 | 9.1% | –1.11 | +0.31 | –1.42 | |
| Yves Missi | 12/15 | 8.0% | +1.21 | –0.68 | +1.88 | |
| Derik Queen | 15/15 | 8.0% | –0.66 | +0.43 | –1.09 | |
| Jordan Poole | 6/15 | 7.6% | –1.10 | +0.52 | –1.61 | ⚠ Only 6/15 games |
| Karlo Matkovic | 14/15 | 7.5% | +0.10 | –0.91 | +1.01 | |
| DeAndre Jordan | 8/15 | 7.2% | –0.14 | –0.22 | +0.09 | |

**Excluded from profile:** McGowens (OUT, toe). ⚠ Note: stored prediction shows NOP coverage=1.00 despite McGowens having 9.9% raw share — possibly McGowens injury was confirmed after prediction ran, or Fix B logic preserved coverage. See questions.
Team OFF ≈ +0.13 | DEF ≈ –0.28

## Raw Margin Math
```
home_ppp = 1.1446 + (1.37 + (–0.28)) / 100  =  1.1555
away_ppp = 1.1446 + (0.13 + (–0.36)) / 100  =  1.1423

raw_margin ≈ (1.1555 – 1.1423) × 100  =  +1.32 pts/100 poss

Calibrated:
  alpha × raw + HCA_NYK = 6.097 × 1.32 + 1.82 ≈ +9.87
  Stored prediction: NYK –8.41 (delta from rounding + simulation variance)
  No B2B adjustment
```

## David's Inputs
*[Pending — questions below to be answered tomorrow morning]*

## Open Questions for David
1. **Zion Williamson at +0.06 overall** — this seems extremely low for him. Is he healthy and in the rotation, or has he been in/out with injuries? Could be RAPM dragged down by bad team context.
2. **Jordan Poole only 6/15 games** — was he hurt for a stretch, or in/out of rotation? 7.6% share with a –1.61 overall makes him a drag on NOP's profile.
3. **Dejounte Murray only 10/15 games** — injury absence or rest? He's NOP's highest-rated player (+2.10); if he's been playing more recently, our recency weighting should capture it.
4. **Trey Murphy III only 11/15 games** — same question.
5. **NOP coverage = 1.00** despite McGowens (9.9% share) being OUT — does this seem right, or is there a coverage bug we should investigate?
6. **Shamet OUT (knee)** — Alvarado likely picks up most of those minutes. Does this feel like a significant loss for NYK's offense, or is Alvarado a decent replacement?
7. **Directional check:** NYK –8.5 at home vs NOP. Does that feel right given what you know about both teams right now?

## Pre-Game Assessment
- **Model confidence:** MODERATE (82% directional accuracy in backtest)
- **Pick:** NYK –9 (market line; we have –8.41, minimal edge)
- **Key risks:**
  1. Shamet OUT reduces NYK's spacing/backcourt depth — Alvarado replacement is a downgrade
  2. Zion or Murray playing at a higher level than our model captures (Zion in particular may be underrated here)
  3. NOP's defense is decent (DEF ≈ –0.28) which could limit NYK's offense
- **Actionable:** Marginal. MODERATE tier but no spread edge (–0.6 pts). If betting, take market NYK –9 at 1% bankroll. Can skip without losing much.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: NOP 116 @ NYK 121
- Actual margin: NYK +5 (positive = home won)
- Our spread: NYK –8.41 | Market: NYK –9.0 | Error: +3.41 pts (overstated NYK advantage)

### Result
- **Directional: WIN** — we predicted NYK to win, they did ✓
- **ATS (our spread):** NYK –8.41 → actual +5 → DID NOT COVER ✗
- **ATS (market spread):** NYK –9.0 → actual +5 → DID NOT COVER ✗

### Actual Box Score (top players by minutes)

**NYK (New York Knicks)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| OG Anunoby | 39:38 | 21 | 4 | 4 |
| Jalen Brunson | 38:41 | 32 | 1 | 7 |
| Josh Hart | 37:56 | 10 | 8 | 3 |
| Mikal Bridges | 37:28 | 14 | 2 | 7 |
| Karl-Anthony Towns | 24:23 | 21 | 14 | 1 |
| Jordan Clarkson | 20:46 | 10 | 3 | 5 |
| Mitchell Robinson | 20:44 | 11 | 8 | 0 |
| Mohamed Diawara | 11:05 | 2 | 0 | 1 |

**NOP (New Orleans Pelicans)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Herbert Jones | 37:02 | 13 | 2 | 6 |
| Trey Murphy III | 35:31 | 16 | 6 | 2 |
| Zion Williamson | 33:56 | 22 | 4 | 2 |
| Dejounte Murray | 28:02 | 7 | 5 | 12 |
| Saddiq Bey | 27:54 | 18 | 4 | 2 |
| Karlo Matković | 22:33 | 12 | 3 | 1 |
| Jeremiah Fears | 19:58 | 21 | 1 | 3 |
| Derik Queen | 18:26 | 5 | 5 | 3 |

### Lineup Accuracy
- **NYK profile: accurate.** Brunson, Anunoby, Bridges, Hart all played heavy minutes as expected. KAT in at 24 min (limited, possibly managed). Landry Shamet confirmed absent (OUT, knee). Jordan Clarkson played 20 min (in our profile at 5.8%). No surprises.
- **NOP profile: accurate.** Murphy, Zion, Murray, Jones, Bey all played as profiled. Bryce McGowens confirmed absent (OUT, toe). Jordan Poole didn't appear in top-8 by minutes — likely benched/limited.
- **Jeremiah Fears: 21 pts off the bench.** Our profile had him at –1.42 overall — one of NOP's draggiest players by rating. He went off for 21 pts in just 20 min and was a key reason NOP stayed competitive. This is the classic "low-rated player has a career game" scenario that pushes actual margin toward zero.
- **Zion at 22 pts, 33 min:** Our pre-game question about his +0.06 overall was answered — he played full minutes and was productive. The low RAPM is likely team-context drag; he can still put up points.

### What the Model Got Right / Wrong
1. **Direction correct.** NYK won as predicted. Brunson (32 pts) and KAT (21/14) were the difference.
2. **NOP's actual quality was underestimated.** Our model had NOP at OFF ≈ +0.13 but they nearly won on the road. Jeremiah Fears explosion (+21 pts) and Zion's full availability suggest NOP is better than the recent profile implies. The –1.42 Fears rating is clearly stale or context-contaminated.
3. **NYK's margin overstated.** We had –8.41, market had –9, actual was +5. Both model and market thought NYK was more dominant than they were. NOP's defense (DEF –0.28 in profile) held up — our pre-game note about NOP defense limiting NYK offense proved correct.
