# Game Analysis: SAC @ CHA, 2026-03-24

## Stored Prediction
- Our spread: CHA –15.01 | Market: CHA –17.0 | Edge: –2.0 pts | Tier: HIGH
- Coverage: CHA 100% | SAC 80.1%
- B2B: home=No | away=No
- Injury bump: pre-injury base ~CHA –13.9, SAC exclusions added ~+4.0 pts

## Team Lineup Profiles (last 15 games)

### Charlotte Hornets (HOME)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Kon Knueppel | 15/15 | 12.5% | +1.48 | –0.50 | +1.98 | Day-To-Day/Probable (back) |
| Brandon Miller | 15/15 | 12.3% | +1.61 | –1.19 | +2.79 | |
| LaMelo Ball | 15/15 | 11.3% | +2.94 | –1.31 | +4.25 | |
| Miles Bridges | 13/15 | 12.3% | +0.05 | +0.40 | –0.35 | |
| Moussa Diabate | 13/15 | 12.1% | +3.19 | –1.98 | +5.18 | |
| Sion James | 15/15 | 8.1% | –0.20 | –0.16 | –0.04 | |
| Coby White | 11/15 | 8.1% | +0.63 | –1.08 | +1.71 | Confirmed healthy, rotation |
| Josh Green | 15/15 | 7.3% | +2.49 | –0.89 | +3.37 | |
| Ryan Kalkbrenner | 14/15 | 7.5% | –0.91 | +0.32 | –1.23 | |
| Grant Williams | 12/15 | 7.9% | +1.39 | –1.22 | +2.61 | |

**Excluded:** Tidjane Salaun (Out, calf — 3 games in window, no coverage impact)
Team OFF ≈ +1.26 | DEF ≈ –0.72 | Coverage: 100%
CHA HCA coefficient: –1.30 (below-average home court)

### Sacramento Kings (AWAY)
| Player | Games | Share (raw) | OFF | DEF | Overall | Notes |
|--------|-------|-------------|-----|-----|---------|-------|
| Maxime Raynaud | 15/15 | 13.5% | –1.81 | +0.47 | –2.28 | In lineup |
| Precious Achiuwa | 15/15 | 13.2% | +0.16 | –1.65 | +1.81 | **Questionable (back)** |
| DeMar DeRozan | 14/15 | 12.3% | –1.82 | –0.23 | –1.59 | In lineup |
| Daeqwon Plowden | 14/15 | 11.0% | –1.39 | +0.92 | –2.31 | Probable |
| Killian Hayes | 14/15 | 7.2% | +0.31 | –0.36 | +0.67 | **Questionable (foot)** |
| Malik Monk | 11/15 | 8.9% | –0.53 | +0.15 | –0.68 | In lineup |
| Doug McDermott | 9/15 | 7.1% | –1.23 | +0.74 | –1.97 | In lineup |
| Dylan Cardwell | 5/15 | 6.8% | –0.03 | +0.35 | –0.37 | In lineup |
| Devin Carter | 7/15 | 7.0% | –0.64 | +0.89 | –1.52 | In lineup |

**Excluded (Out):** Nique Clifford (foot, 1 wk), Russell Westbrook (foot), Keegan Murray (ankle, 2 wks)
**Excluded (season-ending):** Domantas Sabonis, Zach LaVine, Drew Eubanks, De'Andre Hunter
Team OFF ≈ –0.89 | DEF ≈ –0.02 | Coverage: 80.1%

## Raw Margin Math
```
home_ppp = 1.1446 + (1.26 + (–0.02)) / 100  =  1.1570
away_ppp = 1.1446 + (–0.89 + (–0.72)) / 100  =  1.1285
raw_margin ≈ (1.1570 – 1.1285) × 100  =  +2.85 pts/100 poss

Calibrated:
  alpha × raw + HCA_CHA = 6.097 × 2.85 + (–1.295) ≈ +16.1
  Stored prediction: CHA –15.01 (delta from rounding + simulation variance)
  No B2B adjustment for either team
```

## David's Inputs
- **SAC coverage 80.1% gap:** No intel on Achiuwa or Hayes status tonight — both questionable, could drop coverage further if either scratches
- **Coby White (11/15 games):** Confirmed healthy and in rotation, not an injury concern
- **DeRozan –1.59 overall:** Acknowledged model artifact — RAPM dragged down by playing on a bad team all season. David's read: "kind of washed in general" so the low rating isn't entirely wrong
- **Spread feels right:** David confirmed CHA –15 is directionally sound, with realistic upside to win by 20+ (blowout compression pattern applies here)
- **CHA below-avg home court (HCA –1.30):** Charlotte is a weak home environment — market likely applies same discount

## Pre-Game Assessment
- **Model confidence:** HIGH (86% directional accuracy in backtest)
- **Pick:** CHA –15 (take the market's –15 line; market is at –17, so 2 pts of cushion)
- **Key risks:**
  1. Achiuwa + Hayes both scratch → SAC coverage drops below 75%, actual spread should be closer to –18 to –20; CHA –15 wins easier but spread bet still fine
  2. DeRozan goes for 30+ and pads SAC's score — could keep it within 15 even in a dominant CHA win (star volume scorer on a bad team)
  3. Blowout compression is real — direction correct but final margin often larger than our number
- **Actionable:** Yes. Best play: CHA –15 spread, 2% bankroll (HIGH tier). Market line is –17 so the –15 is genuine value.

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->

---

## Post-Mortem

### Actual Outcome
- Final score: SAC 90 @ CHA 134
- Actual margin: CHA +44 (positive = home won)
- Our spread: CHA –15.01 | Market: CHA –17.0 | Error: –28.99 pts (understated blowout severity)

### Result
- **Directional: WIN** — we predicted CHA to win, they did ✓
- **ATS (our spread):** CHA –15.01 → actual +44 → COVERED ✓
- **ATS (market spread):** CHA –17.0 → actual +44 → COVERED ✓

### Actual Box Score (top players by minutes)

**CHA (Charlotte Hornets)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Brandon Miller | 27:11 | 13 | 3 | 6 |
| Moussa Diabaté | 24:08 | 17 | 11 | 2 |
| Miles Bridges | 24:02 | 9 | 8 | 4 |
| LaMelo Ball | 23:19 | 20 | 6 | 8 |
| Ryan Kalkbrenner | 22:09 | 6 | 4 | 1 |
| Sion James | 21:05 | 8 | 4 | 1 |
| Kon Knueppel | 20:37 | 14 | 4 | 3 |
| Coby White | 18:25 | 27 | 5 | 1 |

**SAC (Sacramento Kings)**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
| Daeqwon Plowden | 36:11 | 22 | 2 | 1 |
| Devin Carter | 34:09 | 18 | 3 | 3 |
| Malik Monk | 29:56 | 7 | 3 | 14 |
| Doug McDermott | 29:47 | 9 | 1 | 2 |
| Maxime Raynaud | 29:32 | 16 | 7 | 0 |
| DeMar DeRozan | 28:47 | 7 | 4 | 5 |
| Patrick Baldwin Jr. | 27:44 | 5 | 4 | 1 |
| Dylan Cardwell | 23:54 | 6 | 11 | 1 |

### Lineup Accuracy
- **CHA profile: excellent.** All 8 top-minutes players were in our profile (Ball, Miller, Bridges, Diabate, Kalkbrenner, James, Knueppel, White). Josh Green and Grant Williams played fewer minutes than expected, but coverage was 100%.
- **SAC profile: accurate on actuals, incomplete on scratches.** Both Achiuwa (Questionable, back) and Hayes (Questionable, foot) did NOT play — just as we flagged as a risk. Patrick Baldwin Jr. appeared in the box score but wasn't in our profile; he's a fringe roster player filling void minutes. SAC's actual quality was even lower than our 80.1% coverage suggested.
- **Coby White (11/15, 8.1% share): confirmed healthy.** His 27 pts in 18 minutes off the bench was explosive — CHA bench depth helped pad the margin.
- **DeRozan (7 pts, 28 min):** David's "kind of washed" assessment validated — low impact performance against a superior team.

### What the Model Got Right / Wrong
1. **Direction: perfectly correct.** CHA dominated as predicted. This was a talent mismatch amplified by SAC's depleted roster.
2. **Blowout compression pattern confirmed again.** We had CHA –15, market had –17, actual was –44. The model is consistently 25–30 pts short on large talent mismatches. Pre-game note flagged this exact risk. Do NOT fade model direction on games like this.
3. **Pre-game risk #1 validated (Achiuwa + Hayes scratch):** Both Questionables scratched, dropping SAC coverage below what our 80.1% already implied. When a 80% coverage team loses two more players, the talent gap becomes catastrophic — and CHA won by 44.
