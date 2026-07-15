# WNBA Edge Research — Decision-Grade Report

**Prepared for:** David & Bill
**Scope:** ~600 WNBA games (2024–2026), 11–14 sportsbooks, Kalshi single-night snapshot, props single-night snapshot
**Method:** 8 research lenses, each independently red-teamed (join rebuilt from raw parquet, vig enforced at 52.38% breakeven, look-ahead and pseudo-replication audited)
**Bottom line up front:** No edge survives adversarial review at deployable confidence. Everything that looked tradeable either (a) was measured at the un-bettable closing/settle line, (b) was a per-book pseudo-replication artifact, (c) failed multiple-testing correction, or (d) collapsed to a single non-stationary season. Read the TL;DR before getting excited about any number below.

---

## 1. TL;DR

**Nothing clears the bar for capital deployment today.** The WNBA market in this dataset is efficient against every naive signal we threw at it (power ratings, rolling totals, situational biases, cross-venue arb, microstructure). The few cells that printed >55% win rates all died under one of four standard failure modes.

The honest ranking of "least dead" ideas:

1. **Line shopping (vig mitigation, NOT a standalone edge).** This is the only thing that is *mechanically real* and reproduces: shopping the best of ~11 books recovers ~3.1 percentage points of vig per moneyline bet (EV improves from −4.17% to −1.05%). But corrected for outcome luck, EV-at-best is **still negative** (−1.05%/bet). It is a mandatory discipline that makes a *separate* winning model cheaper to run — it is not profit on its own. **Use it, don't bet on it.**

2. **Early-season away-ATS bias — the single most promising *predictive* direction, but not yet bettable.** Away teams cover the closing spread ~61% in the first ~14 days of each season (real at the close, survives a window-search permutation test p=0.040). BUT at the **opening line you can actually transact**, it falls to 58.2% (n=98, p=0.148) — fails significance. Worth **paper-trading forward**, not betting.

3. **Seasonal totals bias (Aug/Sep UNDER) — interesting but corrected to ~zero.** Raw 58.8% UNDER in Aug/Sep, but multiple-testing-corrected p=0.43 and out-of-sample 2025 p=0.12. The combined "+10.5% ROI" headline was propped up by a fake June OVER leg. **Dead as claimed; only Sep-UNDER worth pre-registering.**

**Recommendation: deploy zero capital on a backtest edge. Adopt line shopping as standing discipline. Paper-trade the two seasonal/situational leans forward for one to two seasons before risking money.** The structural problem is sample size — ~600 games over 2 full seasons cannot distinguish a 2–3% edge from zero (power analysis: detecting 53.8% vs 52.38% at p<.05 needs ~3,356 games).

---

## 2. RANKED EDGES (survivors only)

Ranked by (exploitability × confidence × effect). Note: "survivor" here means *not pure noise* — none are deployable today.

### #1 — Line shopping as vig mitigation
- **What it is:** Place each ticket at whichever of the ~11 books shows the best price/number at tip. Pure execution, no prediction.
- **Real numbers (red-team corrected):** Moneyline single-book hold 4.42% → best-of-11 synthetic hold 2.00%. Paired price improvement +3.13%/bet (t=14, n=1206 sides / 605 games) — reproduces exactly. Totals shopping +3.21%/bet, spreads +2.29%/bet (both t>5; the original "spreads are worthless" claim was a baseline artifact and is **false** — spreads benefit too because WNBA spreads are integers 42.5% of the time).
- **The catch (load-bearing):** Graded against the market's own de-vigged fair probability (removing outcome luck), **EV-at-best is −1.05%/bet — still negative.** Shopping cuts the loss from −4.17% to −1.05%; it does NOT flip to +EV. The original "turns a vig-losing strategy positive" claim is wrong. Best dog prices cluster on soft/offshore books (BetOnline, Bovada, MyBookie, LowVig) with low limits and winner-banning.
- **How to trade it:** Maintain accounts at multiple books; always take the best line. Treat it as a cost-reduction layer underneath any *future* predictive model — it lowers your required win rate from ~52.4% toward ~51%.
- **Confidence:** High (mechanically certain). **Exploitability:** High *as a discipline*, zero as standalone profit. **Effect:** ~3pp vig recovered.
- **Next validation step:** None needed for the cost-saving fact. Do NOT bet it blind — it requires a side-selection edge to become +EV.

### #2 — Early-season away-team ATS bias
- **What it is:** Bet the road team ATS during the first ~14 days of each WNBA season; thesis is the market carries stale home-court value before recalibrating.
- **Real numbers (red-team corrected):** Closing line, ≤14d: away covers **61.1%** (n=108, +16.7% ROI, p=0.042) — survives the join fix (PHX/PHO + PDX/POR alias bug), a 5000-iter window-search permutation test (p=0.040), and a placebo-anchor test (p=0.011). Monotonic decay as window widens (66% ≤10d → 55% ≤42d) is the right signature for a real recalibration effect.
- **The catch:** The 61% is at the **closing/settle line you cannot bet.** At the **opening line with real opener prices**, ≤14d drops to **58.2% (n=98, +10.9% ROI, p=0.148) — NOT significant.** ≤10d open is p=0.058. Per-season it's fragile (2024 leans hard, 2025 essentially flat at 52.9%), and leans on expansion-team-heavy early schedules. Only ~6–9 qualifying games per season.
- **How to trade it (if it confirms):** Pre-tip rule, no in-game info needed: bet road ATS at the opener for the first 2 weeks of the season. Low-volume seasonal play.
- **Confidence:** Medium. **Exploitability:** Medium (tradeable mechanism, sub-significant at the bettable line). **Effect:** point estimate +5 to +11% ROI, 95% CI includes 0.
- **Next validation step:** **Paper-trade the open-line road-ATS bet live for the first 2 weeks of the next 1–2 seasons.** This is the only true out-of-sample test. Do not deploy capital on the backtest.

### #3 — Seasonal totals bias (Sep UNDER at the open)
- **What it is:** Openers set too high late in the season; bet UNDER in Aug/Sep at the opening total.
- **Real numbers (red-team corrected):** Raw Aug/Sep UNDER 58.8% (n=194, +12.2% gross ROI at real prices) — but this is the survivor of screening 5 months × 2 directions (10 cells). **Bonferroni-corrected p=0.43. Out-of-sample 2025 p=0.12.** The headline "combined +10.5% ROI" was inflated by a **fake June OVER leg** (June openers are near-perfectly calibrated; the 56.7% was median-vs-mean noise, p=0.21). Standalone September (n=80, 60%) is the only cell with any signal.
- **The catch:** Corrected edge ~0pp over breakeven; 95% CI lower bound sits essentially ON the 52.38% vig line. Rests on ~2 Septembers of playoff-context games — tiny, regime-specific. Market moves the total UP into Sep while results go under, so the under-outcomes look like variance the market is also missing (not pre-bettable info).
- **How to trade it (if it confirms):** Month is known pre-open, so bet UNDER on Aug/Sep games at the opening total.
- **Confidence:** Low. **Exploitability:** Low. **Effect:** ~0pp corrected.
- **Next validation step:** Pre-register **only "September UNDER at open"** and paper-trade it against actual bettable lines/limits for the 2026 playoffs. Do not bet the 2-season backtest.

---

## 3. THE GRAVEYARD (do not re-run)

| Idea | One-line cause of death |
|---|---|
| Openers are "set poorly" / beatable on average | False — opener MAE ≈ closer MAE (totals 12.99 vs 12.82; spreads 9.79 vs 9.80). Opener is efficient. |
| Open→close movement is tradeable | Classic CLV trap — requires seeing the close; prior-game pace that drives the move is already priced into the opener. |
| "Movement is informed" (8.8pp UP/DOWN spread) | Pseudo-replication — collapses to n=509 game-level, result-follows-move 53.4% p=0.13, indistinguishable from vig breakeven. Spreads: no improvement at all (p=0.61). |
| Margin-Elo beats the opening spread ATS | Null at every threshold; lone positive cell (60.6%) is a single-2025-season fluke (2024=47.6%, 2026=50%), p=0.11. |
| Rolling point-differential rating beats opener | Null across 84 configs; zero cells with raw p<0.05. Opener prices aggregate margin efficiently. |
| Favorites ATS at open (favorite-drift folk edge) | 49–51% ATS at every favorite-size threshold; below 52.38% breakeven. Drift is real but converts to <50% ATS. |
| Moneyline underdogs underpriced at open | ROI +0.98% but game-block 95% CI [−11.3%, +19.8%]; dogs win 31.5% vs 30.6% implied (p=0.66). Fairly priced. |
| Book vs Kalshi accuracy comparison | Untestable — Kalshi data is a single snapshot of 6 *unplayed future* games; 0 gradeable outcomes. |
| Book↔Kalshi moneyline divergence arb | Mean div 1.3pp, well inside ~3.8–4.8pp round-trip cost; Kalshi H2H markets have zero volume. |
| Cross-venue best-price arb (the "+1.7% SEA" trade) | Fabricated inputs (the +650 quote doesn't exist in data) + cross-time price cherry-picking; 0 executable arbs simultaneously. |
| Moneyline line shopping "turns vig-losing positive" | The +2.35% absolute ROI was underdog outcome-luck; de-vigged EV-at-best is still −1.05%. |
| Cross-book true arbitrage (3% of games, +1% locked) | 14/18 require offshore books; US-regulated count is 0.7%, at T-4min with $20–100 limits. Economically trivial. |
| Spread/total middles | Abundant on paper (93–98% of games) but hit 1.4–2.0% vs 4.76% breakeven; EV ≈ −5 to −6% per pair. |
| Stat-based (pace×efficiency) totals model | Strictly worse than the line (MAE 13.40 vs 12.84); betting it returns ~−8% ROI. |
| Walk-forward calibrated totals (close + our pred) | Our stats carry zero orthogonal signal; adding pred *raises* OOS MAE. |
| "Always UNDER" totals | 51.5% vs close — below 52.38% breakeven and decaying by season. |
| WNBA totals over/under bias by band | Efficiently priced — over rate 49.2%, mean bias −0.32 pts (p=0.74). No bettable band survives p-hack stress. |
| Full-season away/favorite ATS bias | Join-artifact + non-stationary (2025 exactly 50.0% on n=280); corrected to ~0%, line is statistically unbiased. |
| Props form/usage/over-under mispricing | Untestable — live_props covers only 4 *future* games; n_gradeable=0. |
| Cross-book prop arbitrage (up to 11%) | Stale-line cross-snapshot artifact; 0 of 1,851 simultaneous-snapshot cells show an arb. |
| Kalshi order-book depth imbalance → price | corr ≈ 0; expected move 0.05–0.29c vs 2.7–5c spread. Untradeable. |
| Kalshi signed taker-flow → direction (73%) | Contemporaneous look-ahead; lagged (tradeable) version is 49.0% (p=0.87). No signal at all. |
| Kalshi wide-spread market-making | Wide spreads only in dead books (median 1 lifetime trade); fillable cells net −1.39c after fees. |

---

## 4. DATA GAPS (what would most increase our edge)

Ranked by expected value of acquisition:

1. **More seasons of game results + historical odds.** The single biggest constraint. ~600 games over 2 full seasons is ~6x underpowered to detect a 2–3% edge. Every "promising" lean (early-season away ATS, Sep UNDER) is starved for sample. 3–5 seasons would let us actually pre-register and confirm.
2. **Sharp/Pinnacle lines (EU region of the odds API).** The current book universe is soft/US + offshore, no true sharp anchor. A Pinnacle line lets us (a) measure real CLV, (b) define "fair" probability without the soft-book vig, and (c) test whether soft-book deviations from sharp are bettable — the most likely place a real edge lives.
3. **Historical player-props archive overlapping the box-score window (2024-05 → 2026-06).** The entire props lens is currently n=0 gradeable. Props are the most likely WNBA inefficiency (thin markets, slow line-setting), and we literally cannot test them. This is the highest-upside *new* research area, completely blocked by data.
4. **Multi-night Kalshi tick data with non-null volume/trade prices.** Current Kalshi data is one 11-hour snapshot of 6 unplayed games, with null prices in markets/trades and 21-min orderbook cadence. Cannot test book-vs-Kalshi accuracy, lead-lag, or microstructure. A full-season sub-minute feed with traded volume would make the entire Kalshi line of research possible.
5. **Injury / lineup / rest feeds (pre-tip).** The recurring conclusion across lenses: the opener already prices everything derivable from past scores. The only way to beat it is information the market underweights — injuries, rest, lineup changes, pace-of-specific-matchup. We have none of this in structured form. This is the orthogonal-information gap that all the power-rating nulls point to.

---

## METHODOLOGY NOTES (carry forward to every future study)

- **Always dedup to one bet per game** (median or best line across books) before any hit-rate or significance test. Per-book pooling inflated n ~8x in multiple lenses and *fabricated* significance every time.
- **Grade at the line you can actually bet** (open, or live pre-tip), never the close/settle. Multiple "edges" existed only at the un-bettable closing line.
- **Enforce a single simultaneous snapshot** in any arb scan. Cross-time price cherry-picking manufactured every fake arb.
- **Apply multiple-testing correction** whenever screening months/thresholds/params. Bonferroni killed the seasonal-totals and favorite-threshold "edges."
- **Watch the join:** UTC commence_time vs GAME_DATE (±1 day) and per-era team abbreviations (PHX/PHO 2024 vs 2025-26; PDX/POR 2026) silently dropped games and distorted per-season numbers.
