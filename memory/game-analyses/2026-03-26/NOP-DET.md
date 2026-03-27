# Game Analysis: NOP @ DET, 2026-03-26

## Stored Prediction
- Our spread (raw model, Cunningham still in): DET −3.7 | Market: DET −4.5 | Raw edge: −0.8 DET
- **Adjusted spread (Cunningham + Sasser stripped, ESPN-Out):** est. DET −1.5 | Adjusted edge: +3.0 NOP
- Coverage: home ~100% | away ~99%
- B2B: home=**True** (DET played BOS yesterday, lost 129-130) | away=False
- Market total: 226.5

## Critical Injury: Cade Cunningham OUT
DET's star player (9.3% share, OFF=+3.23, DEF=−1.34, overall=+4.57) is OUT per ESPN (4 consecutive games missed — does NOT trigger Fix B threshold of 5, but IS stripped by ESPN-Out filter in predictions.py). This is a ~3pt swing in the predicted spread that the raw subagent numbers don't reflect.

## Team Lineup Profiles (last 15 games)

### DET (Home)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Daniss Jenkins | 14 | 10.1% | +0.09 | +0.53 | -0.44 | |
| Jalen Duren | 15 | 9.7% | +2.20 | +0.06 | +2.15 | |
| Tobias Harris | 14 | 9.5% | +0.88 | -0.30 | +1.18 | |
| Ausar Thompson | 10 | 9.4% | +1.27 | +0.34 | +0.94 | |
| Cade Cunningham | 10 | 9.3% | +3.23 | -1.34 | +4.57 | **OUT** (4 consec missed) |
| Duncan Robinson | 15 | 8.9% | +1.66 | -0.74 | +2.40 | |
| Isaiah Stewart | 7 | 7.3% | -0.45 | +0.47 | -0.92 | **OUT** (6 consec — Fix B excluded) |
| Kevin Huerter | 11 | 6.7% | +1.41 | -0.58 | +1.99 | |
| Marcus Sasser | 10 | 6.2% | +0.87 | -0.08 | +0.95 | **OUT** (3 consec — ESPN-Out) |
| Caris LeVert | 12 | 6.1% | -1.25 | +0.63 | -1.88 | |
| Ronald Holland II | 15 | 5.2% | +0.32 | +1.08 | -0.76 | |
| Javonte Green | 15 | 4.9% | +0.51 | +0.15 | +0.36 | |
| Paul Reed | 13 | 4.5% | +0.19 | -0.06 | +0.26 | |
| Chaz Lanier | 6 | 2.1% | -0.30 | +0.63 | -0.93 | |

**Raw Team OFF: +0.96 | DEF: −0.03** (before stripping OUT players)
**Adjusted Team OFF: est. ~+0.65 | DEF: est. ~+0.11** (after stripping Cunningham + Sasser)

B2B penalty: −3.05 pts applied to DET.

### NOP (Away)
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
| Trey Murphy III | 12 | 12.1% | +0.53 | -0.87 | +1.40 | Day-To-Day (active in recent games) |
| Saddiq Bey | 15 | 11.1% | -0.11 | +0.39 | -0.50 | |
| Herbert Jones | 15 | 10.4% | +0.84 | -0.42 | +1.25 | |
| Zion Williamson | 14 | 10.4% | +0.11 | -0.46 | +0.57 | |
| Dejounte Murray | 11 | 9.6% | +1.27 | -0.89 | +2.15 | Day-To-Day (active recently) |
| Bryce McGowens | 8 | 7.5% | +0.03 | -0.41 | +0.43 | **OUT** (7 consec — Fix B excluded) |
| Jeremiah Fears | 15 | 6.9% | -1.11 | +0.25 | -1.36 | |
| Yves Missi | 13 | 6.8% | +0.95 | -0.47 | +1.42 | |
| Karlo Matkovic | 14 | 6.2% | +0.22 | -1.04 | +1.26 | |
| Derik Queen | 15 | 6.1% | -0.71 | +0.42 | -1.12 | |
| Jordan Poole | 5 | 5.9% | -1.09 | +0.52 | -1.61 | |
| DeAndre Jordan | 7 | 5.1% | -0.15 | -0.21 | +0.06 | |
| Jordan Hawkins | 5 | 1.0% | -1.28 | +0.50 | -1.77 | |
| Micah Peavy | 6 | 0.9% | -0.36 | +0.13 | -0.49 | |

**Team OFF: +0.15 | DEF: −0.30**

## Raw Margin Math
```
Raw (Cunningham still in):
  home_ppp = 1.1456 + (0.96 + (−0.30)) / 100 = 1.1456 + 0.0066 = 1.1522
  away_ppp = 1.1456 + (0.15 + (−0.03)) / 100 = 1.1456 + 0.0012 = 1.1468
  raw_margin = +0.54  →  calibrated = 6.097 × 0.54 + 3.500 − 3.049 = DET −3.7

Adjusted (Cunningham stripped):
  home_off drops ~0.23 pts/100, home_def worsens ~0.13 pts/100
  raw_margin ≈ +0.17  →  calibrated = 6.097 × 0.17 + 3.500 − 3.049 ≈ DET −1.5
```

## David's Inputs
- No specific inputs (moved to quick analysis mode)

## Pre-Game Assessment
- Model confidence: LOW SIGNAL (|pred| < 5 after Cunningham adjustment)
- Key risks: DET's star Cade Cunningham is OUT — model raw numbers overstate DET strength by ~2 pts; adjusted model says DET −1.5 vs market DET −4.5 (~3pt NOP edge); DET also on B2B (model already prices it, market does too)
- **Actionable? Lean YES — NOP +4.5 has ~3pt model edge after Cunningham adjustment. LOW SIGNAL tier but the injury adjustment is real and the cushion is meaningful.**

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->
