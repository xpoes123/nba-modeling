# WNBA pull — pending follow-up

## ⏰ After June 17, 2026 — pull 2025 closing lines

**Why it's deferred:** the overnight run used the entire 20,000-credit monthly
the-odds-api quota (1 credit left). Bill asked for 2025 data — the 2025 **season
stats** are already in the pack, but 2025 **closing lines** still need ~8,580
credits. Your quota resets on the **17th** (billing anniversary), next on
**2026-06-17**.

**What to run** (any time on/after June 17):

```bash
cd ~/code/nba-modeling
./wnba_pull/pull_2025_odds.sh
```

That script:
1. Checks you actually have ≥9,000 credits (aborts if the quota hasn't reset).
2. Pulls 2025 closing lines (`odds_historical 2025`, ~8,580 credits).
3. Re-zips + re-uploads the pack to https://share.djiang.xyz/wnba/wnba_data.zip.

Then tell Bill the updated zip has 2025 closing lines in
`historical_closing_lines` (alongside 2026).

## Already delivered (overnight run, 2026-06-06)
- Full pack live at **https://share.djiang.xyz/wnba/** (zip, 24 MB).
- 3 seasons of stats (2024/25/26): schedule, player box, raw PBP, lineup PBP,
  shots, players directory.
- Live sportsbook lines + props (overnight time series), 2026 closing lines.
- Kalshi markets / orderbook / trades.

## If you ever do another live-capture night
Player props were the credit hog (5 markets × every event × every cycle). Raise
`PROPS_EVERY_N_CYCLES` and/or trim `ODDS_PROP_MARKETS` in `wnba_pull/config.py`,
and consider lowering `RUN_HOURS`, before launching `run_overnight`.
