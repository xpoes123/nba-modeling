# Game Analysis: MIL @ POR, 2026-03-25

## Stored Prediction
- Our spread: POR -10.4 | Market: POR -12.5 | Edge: -2.1 (market more on POR) | Tier: HIGH (86% dir acc)
- Coverage: home (POR) 100% | away (MIL) 90.8%
- B2B: home=False | away=False
- Injury adj: +1.9 (POR side; net of ESPN exclusions on both sides)
- Prediction ID: 119 | Created: 2026-03-25 05:59:33
- Market total: 226.5

## Injury Situation (MIL 9.2% Coverage Gap)

**Giannis Antetokounmpo (MIL) — CONFIRMED OUT**
- 4 consecutive DNPs: Mar 17, Mar 19, Mar 21, Mar 23
- Active earlier in window: played Mar 2, Mar 4, Mar 7, Mar 10, Mar 12, Mar 15 (6 of 15 games)
- Fix B threshold: 5 consecutive misses required for hard exclusion — NOT triggered (4 misses)
- ESPN marks Out today -> excluded from model via ESPN injury filter
- Rating: OFF=+2.56 DEF=-2.26 OVR=+4.82 — by far MIL's best player

**Coverage gap math:**
- Giannis (recency-weighted per-game-share sum) accounts for ~3.4% of the denominator
- Total coverage gap is 9.23% — approximately 5.8% additional pts unaccounted by Giannis alone
- Second excluded player is likely present — Kevin Porter Jr. (7g in window, OVR~0, heavy usage when active, ~6.2% fraction estimate) is the most probable candidate
- Ask David: Is Kevin Porter Jr. also on the ESPN injury report today?

**Cole Anthony:** Zero possessions in entire 15-game window — likely season-long absence, not a factor in today's profile.

## Team Lineup Profiles (last 15 games before 2026-03-25)

### POR (home) — 1465 offense possessions, 15 games, 100% coverage
| Player | Games | Raw Shr | OFF | DEF | OVR | Notes |
|--------|-------|---------|-----|-----|-----|-------|
| Toumani Camara | 15 | 0.686 | +0.47 | +0.32 | +0.15 | Core rotation |
| Jrue Holiday | 15 | 0.643 | +1.67 | -1.49 | +3.17 | POR's best player |
| Jerami Grant | 13 | 0.587 | -0.26 | -0.29 | +0.03 | |
| Donovan Clingan | 14 | 0.523 | +0.26 | -0.42 | +0.68 | |
| Scoot Henderson | 15 | 0.504 | -0.26 | +0.36 | -0.62 | Negative overall |
| Deni Avdija | 9 | 0.404 | +0.42 | -0.37 | +0.79 | [<10g] |
| Kris Murray | 12 | 0.308 | -0.52 | -0.04 | -0.48 | |
| Matisse Thybulle | 15 | 0.289 | +0.46 | -0.50 | +0.96 | |
| Sidy Cissoko | 14 | 0.288 | -0.34 | +0.76 | -1.10 | Bad defender |
| Robert Williams III | 10 | 0.281 | +0.27 | -0.16 | +0.43 | |
| Vit Krejci | 10 | 0.264 | -0.48 | +0.63 | -1.11 | Bad defender |
| Blake Wesley | 10 | 0.167 | -1.38 | +0.98 | -2.36 | Deep bench |
| Hansen Yang | 5 | 0.029 | -1.62 | +0.66 | -2.28 | [<10g] garbage time |
| Chris Youngblood | 1 | 0.012 | -0.36 | +0.44 | -0.80 | [<5g] minimal impact |
| Jayson Kent | 2 | 0.009 | +0.09 | -0.07 | +0.16 | [<5g] minimal impact |

**Team OFF=+0.19  DEF=-0.15  Net=+0.34**
POR is a slightly above-average team. Core rotation solid — Jrue Holiday at +3.17 is genuine plus player. Clingan and Thybulle provide positive contributions. Weakness: Cissoko and Krejci as bad defenders; Scoot Henderson negative overall.

### MIL (away) — 1410 offense possessions, 15 games, 90.8% coverage
| Player | Games | Raw Shr | OFF | DEF | OVR | Notes |
|--------|-------|---------|-----|-----|-----|-------|
| Ryan Rollins | 15 | 0.674 | +0.17 | -0.94 | +1.11 | MIL's most-used player |
| AJ Green | 15 | 0.472 | +0.93 | -0.74 | +1.67 | |
| Ousmane Dieng | 13 | 0.462 | -1.50 | +0.85 | -2.35 | Significant drag |
| Myles Turner | 14 | 0.460 | -2.01 | +1.45 | -3.46 | Major negative |
| Kyle Kuzma | 12 | 0.433 | -0.50 | +0.43 | -0.93 | |
| Jericho Sims | 14 | 0.427 | -2.21 | +0.95 | -3.16 | Major negative |
| Bobby Portis | 13 | 0.424 | -1.11 | -0.41 | -0.70 | Off-bad but decent def |
| Kevin Porter Jr. | 7 | 0.310 | +0.09 | +0.10 | -0.01 | [<10g] possible ESPN-Out |
| Pete Nance | 13 | 0.275 | +1.33 | -1.12 | +2.45 | Good contributor |
| Cam Thomas | 12 | 0.240 | -1.10 | +0.25 | -1.35 | |
| **Giannis Antetokounmpo** | **6** | **0.231** | **+2.56** | **-2.26** | **+4.82** | **ESPN OUT — excluded** |
| Taurean Prince | 8 | 0.201 | -0.04 | +0.09 | -0.13 | |
| Gary Trent Jr. | 10 | 0.177 | -2.29 | +1.03 | -3.32 | Major negative |
| Gary Harris | 6 | 0.078 | -1.03 | +0.91 | -1.94 | [<8g] |
| Andre Jackson Jr. | 10 | 0.075 | +0.07 | +0.04 | +0.03 | |
| Thanasis Antetokounmpo | 8 | 0.051 | +0.00 | +0.00 | +0.00 | |

**Team OFF=-0.49  DEF=+0.01  Net=-0.50** (WITH Giannis in profile, model excludes him via ESPN)
**Team OFF=-0.64  DEF=+0.12  Net=-0.76** (effectively, WITHOUT Giannis contribution)

MIL is a weak team without Giannis. Three major negative players (Myles Turner -3.46, Jericho Sims -3.16, Gary Trent Jr. -3.32) anchor the rotation. Pete Nance (+2.45) and AJ Green (+1.67) are the only meaningful positive contributors without Giannis. This is a bad basketball team tonight.

## Raw Margin Math

Simple weighted-average approximation (does not include recency decay; for directional verification only):
```
home_ppp = 1.1449 + (POR_off + MIL_def) / 100
         = 1.1449 + (0.1925 + 0.0060) / 100
         = 1.1449 + 0.0020 = 1.1469

away_ppp = 1.1449 + (MIL_off + POR_def) / 100
         = 1.1449 + (-0.4934 + -0.1453) / 100
         = 1.1449 - 0.0064 = 1.1386

raw_margin (per 100 poss) = (1.1469 - 1.1386) * 100 = +0.837 pts/100

Calibrated: alpha * raw + HCA_POR = 6.097 * 0.0084 + 3.419 = ~3.47 pts (simple approx)
```

Note: Simple approximation gives ~3.5 pts vs stored prediction of 10.4 pts. The gap is expected — the actual model uses recency-weighted shares (0.85^slot decay), simulation over 1000 games, and coverage-based redistribution. The stored 10.42 is authoritative. The approximation confirms direction (POR favored) but not magnitude.

Calibration v5 params used: alpha=6.097, HCA_POR=+3.419, B2B_home=-3.049, B2B_away=+2.292 (neither team on B2B today).

## Flags for David

**FLAG (HIGH): Giannis OUT — 4th straight DNP**
Giannis has missed the last 4 MIL games. He is MIL's only elite player (OVR +4.82). Without him, MIL's effective team rating drops from -0.50 to -0.76 on net. The model has already incorporated this exclusion (ESPN Out flag), contributing to the +1.9 injury adjustment favoring POR.

**FLAG (MODERATE): MIL 9.2% coverage gap exceeds Giannis alone**
Giannis's recency-weighted contribution accounts for only ~3.4% of the coverage denominator. The full 9.23% gap implies a second player excluded by ESPN today. Most likely candidate: **Kevin Porter Jr.** (7 games in window, ~6.2% estimated denominator fraction). Please confirm: is Kevin Porter Jr. on the ESPN injury report for tonight? If yes, market spread and model are aligned. If not, the gap may reflect a different player.

**FLAG (LOW): Market has POR 2.1 pts bigger than us (-12.5 vs -10.4)**
This is a moderate adverse edge. Per our pattern notes: market > our spread by 4+ pts signals injury intel; at 2.1 pts gap, this is not a strong signal but worth monitoring. If Kevin Porter Jr. is also confirmed Out, it would explain the market being more aggressive. The direction (POR) is correct at HIGH confidence — question is only whether market is ahead of our injury model.

**Players with < 5 games in window (noise risk):**
- POR: Chris Youngblood (1g, 0.012 share) — negligible impact
- POR: Jayson Kent (2g, 0.009 share) — negligible impact
- MIL: Gary Harris (6g, 0.078 share) — low share, low risk

**Deni Avdija (9g in window):** Below full-window threshold. Worth confirming he's playing tonight.

## Pre-Game Assessment

**Model confidence: HIGH** (86% directional accuracy at |pred| >= 10 tier)

**POR side narrative:**
- Jrue Holiday (+3.17 OVR) vs a Giannis-less MIL is a significant matchup advantage
- MIL rotation features three major negative players (Turner -3.46, Sims -3.16, Trent -3.32)
- POR home court adds +3.42 (above-average HCA for Portland)
- No B2B fatigue on either side

**Key risks:**
1. MIL injury situation: if Kevin Porter Jr. or another MIL player returns tonight despite ESPN Out status, model underestimates MIL strength (Fix A risk — returning player not pre-seeded)
2. Market at -12.5: market may know about an additional MIL absence not yet in our ESPN feed (Cole Anthony context? He has zero possessions all window — possibly traded or injured all year)
3. Blowout compression: if MIL is truly as depleted as data suggests, actual margin could be 15-20 pts while model predicts 10. Model direction correct but magnitude compressed (known bias from post-mortem analysis).

**Actionable assessment:**
POR is the correct side at HIGH confidence. The -2.1 adverse edge (market more aggressive on POR) is concerning but not disqualifying at this tier. If Kevin Porter Jr. is confirmed Out, the model's +1.9 injury adjustment may be understated and market is right to push to -12.5. If MIL has additional news, lean POR more aggressively. At current numbers (POR -10.4 model, -12.5 market), POR at -10.4 is the better entry if available — avoid the -12.5 line given the 2.1 pt gap.

**Ask David before acting:** Is Giannis out confirmed? Is Kevin Porter Jr. also Out? Any other MIL injury news overnight?

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->
