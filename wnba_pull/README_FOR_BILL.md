# WNBA Data Pack — for Bill

A quant-ready snapshot of WNBA stats + betting/prediction markets. Every dataset
ships as both **`.parquet`** (fast, typed) and **`.csv`** (universal). Load with:

```python
import pandas as pd
df = pd.read_parquet("wnba_data/player_box.parquet")   # or .csv
```

**Conventions (read once):**
- All timestamps are **UTC**, ISO-8601 (`2026-06-06T23:30:00Z`).
- Sportsbook prices are **American odds** (`-150`, `+130`); `point` is the line
  (spread or total). One row per (game, book, market, outcome).
- Kalshi prices: market quotes (`yes_bid`, etc.) are in **cents 0–100** (= implied
  prob × 100). Orderbook `price_dollars` is **0–1** (implied probability). Divide
  cents by 100 to compare with sportsbook implied probabilities.
- Join keys: **`game_id`** (stats, e.g. `1022500001`), **`event_id`**
  (sportsbook, an odds-api hash), **`personId`/player ids** (stats), **player name
  string** (`outcome_desc`) for props. Stats and sportsbook are linked by
  team + date/commence_time (no shared game id — see `schedule_results`).

---

## Market data

### `live_game_lines` — sportsbook moneyline / spread / total, time series
Snapshots taken ~every 20 min overnight across all US books. Use `snapshot_ts`
to build line-movement / steam / closing-vs-open studies.
Cols: `snapshot_ts, event_id, commence_time, home_team, away_team, bookmaker,
market (h2h|spreads|totals), outcome_name, price, point`.

### `live_props` — sportsbook player props, time series
Same shape; `market` ∈ player_points/rebounds/assists/threes/PRA,
`outcome_desc` = player name, `outcome_name` = Over/Under, `point` = the line.

### `historical_closing_lines` — closing lines, 2024–2026 (backfill)
One snapshot per game **at tipoff** (last pre-game odds) across all 11 US books,
all three seasons. The dataset for CLV / closing-line-value backtests.
Cols: `event_id, commence_time, home_team, away_team, bookmaker, market,
outcome_name, price, point`.

### `historical_opening_lines` — opening lines, 2024–2026 (backfill)
Same shape, but snapshotted **~24h before tipoff** (the day-before opener) and
tagged `line_type='open'`. Pair with `historical_closing_lines` to measure
**line movement (open→close)** per book/market.
```python
op = pd.read_parquet("wnba_data/historical_opening_lines.parquet")
cl = pd.read_parquet("wnba_data/historical_closing_lines.parquet")
keys = ["event_id","bookmaker","market","outcome_name"]
mv = op.merge(cl, on=keys, suffixes=("_open","_close"))
mv["point_move"] = mv["point_close"] - mv["point_open"]
```
Note: "opening" = a consistent ~24h-pre-tip snapshot (not the literal first tick;
odds-api snapshots every 5 min so the true first post isn't economically
retrievable). ~9–11 books present at 24h out.

### `kalshi_markets` — Kalshi prediction-market quotes, time series
Game winner, spread, total, halves, and player-prop markets. Cents (0–100).
Cols: `snapshot_ts, series, event_ticker, market_ticker, market_subtitle,
status, yes_bid, yes_ask, no_bid, no_ask, last_price, volume, volume_24h,
open_interest, close_time`.

### `kalshi_orderbook` — Kalshi resting depth, time series
Top-10 levels per side. `price_dollars` 0–1, `size` = contracts.

### `kalshi_trades` — Kalshi executed prints
`created_time, yes_price, no_price, count, taker_side` per market — microstructure.

> **Edge idea:** join `kalshi_markets` (÷100) to `live_game_lines` (convert
> American → implied prob) on team+commence_time to study book-vs-Kalshi divergence.

---

## Stat data (last 3 seasons: 2024, 2025, 2026)

### `schedule_results` — every game, team-level box basics
One row per team per game. Cols include `GAME_ID, GAME_DATE, MATCHUP, WL, PTS,
FGM/FGA, FG3M/FG3A, FTM/FTA, REB, AST, STL, BLK, TOV, PLUS_MINUS`, etc. This is
your schedule + results spine and the bridge between stats and odds (match on
team abbreviation + date).

### `player_box` — per-player box, traditional + advanced
One row per player per game (`game_id`, `personId`, `firstName/familyName`,
`minutes`, points/reb/ast/etc., plus advanced: offensive/defensive rating, usage,
TS%, pace…). Concatenated across all games.

### `pbp_raw` — raw play-by-play, every game (reliable baseline)
nba_api PlayByPlayV2 for all 602 games. Every event: `EVENTMSGTYPE,
HOMEDESCRIPTION/VISITORDESCRIPTION, SCORE, SCOREMARGIN, PERIOD, PCTIMESTRING,
PLAYER1/2/3_ID + names, team`. Complete and reliable — use this as your PBP spine.

### `pbp_events` — lineup-attributed play-by-play (bonus, most games)
pbpstats output with the **exact 5 players on court per team** (`team1_players`,
`team2_players` = dash-joined sorted player ids) per event. Enables on/off, lineup
RAPM, possession reconstruction. **Coverage note:** a minority of games trip a
pbpstats event-ordering check that requires a now-dead NBA host, so they're absent
here — those games still have full `pbp_raw`. Join `pbp_events` to `pbp_raw` on
`game_id` + `event_num`/`EVENTNUM` to attach lineups to raw events.

### `shots` — shot-level with court coordinates
Every field-goal attempt: `LOC_X, LOC_Y` (court coords, tenths of feet),
`SHOT_DISTANCE, SHOT_TYPE, SHOT_ZONE_*, SHOT_MADE_FLAG, PLAYER_ID, TEAM_ID,
GAME_ID, PERIOD`. For shot-quality / expected-points models.

> Season aggregate tables (LeagueDash*) are **not shipped** — those endpoints
> return empty for WNBA. Derive season totals/rates yourself from `player_box`
> (group by `personId`) and `schedule_results` (group by `TEAM_ID`).

### `players` — player directory
Player id ↔ name ↔ team ↔ years active, per season.

---

## Suggested starting points
1. **CLV backtest:** `historical_closing_lines` + `schedule_results` (results).
2. **Live edge monitor:** `live_game_lines` vs `kalshi_markets` divergence.
3. **Player-prop modeling:** `player_box` + `pbp_events` (minutes/usage) → `live_props`.
4. **Lineup value:** `pbp_events` on/off + `shots` shot quality.

Questions on any field → ask David. Generated by the nba-modeling pipeline.
