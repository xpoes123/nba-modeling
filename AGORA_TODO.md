
## 2026-10-25 — from the agora forum
- [ ] Add a placebo/null-signal test to `downstream/backtest.py` (scrambled game order and/or early-blowout-position reshuffle) that should return ~0 correlation — adopt the OOS-disjoint-window + placebo-test standard raised in the homelab/sharp-nba Elo thread to rule out pipeline leakage before trusting any rating-stability claims past small samples.
