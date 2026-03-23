# Current Status

## Current Phase
**P7 — COMPLETE** → P0–P7 done; daily prediction engine running

## Completed
- **P0**: config.py, db/schema.sql, db/init_db.py — validated
- **P1**: ingestion/pbpstats_client.py + ingestion/game_list.py — validated
- **P2**: ingestion/etl.py — validated (single-game ETL, stints sum = possessions, idempotent)
- **P3**: ingestion/backfill.py — complete, 1041/1050 games, ~201K possessions, PPP=1.1441
- **P4**: models/rapm.py + pipeline/phase1_full_season.py + tests/test_rapm.py — validated
  - 567 players rated; SGA +6.1, Wemby +5.8, Holmgren +5.4, Jokic +4.7
  - Targets in per-100-possessions units (×100 multiplier); alpha=5000; pace filters seconds_played=0
- **P5**: ingestion/ingest_daily.py + pipeline/nightly_job.py + scripts/ — validated
  - First run: ingested 7 new games (Mar 20), 567 players re-rated with phase='rapm_rolling'
  - Rolling window union start = 2025-10-21 (season start — see gotcha below)
  - Task Scheduler: scripts/install_task.ps1 registers daily 4am job
- **P6**: models/elo.py + models/composite.py + nightly_job.py integration — validated
  - 29/29 tests pass; composite phase='elo'; Elo delta stdev=0.24 pts/100, mean≈0
  - Top 10: Jokic +5.80, SGA +5.41, Wemby +5.31 overall (composite)
  - K calibrated: ELO_K_OFFENSE_DEFENSE=0.02, ELO_K_PACE=0.01 (K=2.0 was 80x too large)
- **P7**: downstream prediction engine — validated (2026-03-21)
  - 59/59 tests pass
  - downstream/team_ratings.py — pure player→team aggregation (possession-weighted)
  - downstream/lineup_sampler.py — pure Monte Carlo simulation (N=1000)
  - downstream/odds_client.py — Odds API wrapper (spreads, moneylines, totals)
  - downstream/espn_client.py — ESPN public injury API (no auth needed)
  - downstream/calibration.py — OLS + James-Stein (EB) shrinkage → calibration_coeffs.json
  - downstream/predictions.py — daily orchestration, writes to `predictions` table
  - scripts/run_predictions.bat — daily runner (run after nightly_job)
  - Calibration v4 (2026-03-22): defense sign bug fix + EB recalibration.
    α=6.14, HCA=+2.09 pts, B2B home=-2.40 pts, B2B away=+1.28 pts,
    σ=13.01 pts, val_corr=0.586. Full-season backtest corr=0.512, dir_acc=70.1% (702/1002).
    σ²_between=4.9966 (real team HCA variation now detectable; was 0 in v3 due to sign bug).
  - Calibration v3 (superseded): α=8.46, val_corr=0.548, dir=68.6%. Inflated α compensated
    for sign bug; EB found σ²_between=0 (artifact of sign bug masking signal).
  - Availability discount (2026-03-22): both backtest.py and predictions.py now weight each
    player by mean_share × (games_appeared / games_in_window). DNP-heavy players downweighted.

## Key Design Decisions Locked In
- Dependency management: `uv` + `pyproject.toml`
- RAPM: two separate regressions (offense + defense)
- `stints` stores `points_allowed` column
- Elo outcome: continuous PPP
- `overall` = `offense - defense`
- **Season: 2025-26** (switched from 2024-25 — current season)
- **PBP Source: pbpstats 'live' S3 provider** (data.nba.com dead, stats.nba.com PlayByPlayV2 deprecated)
  - URL: `nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/liveData/playbyplay/playbyplay_{game_id}.json`
  - Cache: `data/pbp/live_{game_id}.json`
- Game metadata from: `nba_api.LeagueGameLog` (batch, season-level); `LeagueGameFinder` as fallback
- Player names from: `nba_api.BoxScoreTraditionalV3` per game
- Clock format from live provider: `PT{M}M{S}.{ms}S` (ISO 8601) not MM:SS
- **CLAUDE.md overrides README on rapm.py purity**: rolling RAPM orchestration lives in
  `pipeline/nightly_job.py` (not models/rapm.py), keeping models/rapm.py pure (no DB I/O)

## P7 Architecture
- `downstream/team_ratings.py` — PURE: normalize_name, build_name_to_id, compute_team_ratings,
  compute_raw_margin, shares_from_minutes
- `downstream/lineup_sampler.py` — PURE: simulate_game, apply_calibration, margin_to_win_prob
- `downstream/odds_client.py` — Odds API: get_nba_odds(target_date) → list[GameOdds]
  - **Spread convention**: we negate Odds API home team point so positive = home favored throughout
  - market_spread = -odds_api_home_point (e.g. ATL -10 stored as +10 in our DB)
- `downstream/espn_client.py` — ESPN public injury API: get_nba_injuries(), get_out_player_names()
  - No auth required; returns Out/Doubtful/Suspension as is_out=True
- `downstream/balldontlie_client.py` — BDL wrapper (free tier only has /v1/teams; injuries/stats are paid)
- `downstream/calibration.py` — run once to fit OLS, saves downstream/calibration_coeffs.json
- `downstream/predictions.py` — daily orchestration:
  1. Load calibration_coeffs.json
  2. Fetch Odds API lines
  3. Fetch ESPN injuries (exclude Out/Doubtful from lineups)
  4. Build lineup profiles from DB possession history (last 15 games per team)
  5. Monte Carlo simulation (N=1000) per game
  6. Apply calibrated adjustments
  7. Write to `predictions` table, print report

## P6 Architecture
- `models/elo.py` — PURE: sigmoid, elo_update (mutates in-place), replay_game_elo (takes possessions list)
- `models/composite.py` — update_current_ratings: joins rapm_rolling + latest elo_ratings → current_ratings
- `pipeline/nightly_job.py` Elo helpers: _load_elo_state, _get_unreplayed_game_ids, _load_game_possessions,
  _upsert_elo_ratings, run_elo_replay — all DB I/O here, pure logic in models/elo.py
- Nightly job flow: ingest → league_avgs → rolling_RAPM → elo_replay → composite_ratings
- Elo K calibration: K=0.02 (offense/defense), K=0.01 (pace). Original K=2.0 gave 80x too-large
  random walk over a full season (σ≈49 vs target σ≈0.5 for "micro-adjustments < 10% of RAPM")

## P5 Architecture
- `ingestion/ingest_daily.py` — `get_new_game_ids()` + `ingest_new_games()`: fetches full season
  schedule from nba_api, filters to IDs not in games table, parses + ETLs with rate limiting
- `pipeline/nightly_job.py` — `run_rolling_rapm()` + `main()`: union window logic, calls
  models/rapm.py pure functions, upserts rapm_ratings (phase='rapm_rolling') + current_ratings
- `scripts/run_nightly.bat` — sets PYTHONPATH, redirects stdout/stderr to logs/nightly_YYYY-MM-DD.log
- `scripts/install_task.ps1` — registers Windows Task Scheduler task (run once, elevated PS)
- nightly_job.py logs to stdout only; bat file handles file redirect

## Known Issues / Gotchas
- **Rolling window = full season right now**: union window logic takes min(all players' window starts).
  Bench players and cut 10-day contract guys who only played in October drag it back to Oct 21.
  This is correct per spec. Rolling will differentiate more from full-season once we filter
  "active" players, or next season when the window genuinely covers only recent games.
- `ingest_daily.py` fetches the full season schedule on every run (one nba_api call). Fine for now.
- ~9/1050 games fail ingestion: 4 with NULL home_team_id (API returns incomplete metadata for some
  games), 5 with 4-player OT lineups. Pre-existing issue, handled gracefully (log + continue).
- `nba_api.LeagueGameFinder` ignores `game_id_nullable` on server side — must filter client-side
- `BoxScoreSummaryV2` has missing data for games after 4/10/2025 — don't use it
- `stats.nba.com PlayByPlayV2` is dead (returns `{}`) — pbpstats stats_nba provider broken
- `data.nba.com` PBP endpoint times out in 2025 — pbpstats data_nba provider unreliable
- Live S3 provider: some possessions have 4 players (fouled out / substitution edge cases) — skipped
- `datetime.utcnow()` deprecated in Python 3.14 — use `datetime.now(timezone.utc)`
- **BDL free tier**: only /v1/teams works; /v1/player_injuries, /v1/players/active, /v1/stats all 401
- **Possession share redistribution gap**: when injured players are removed, remaining players'
  shares don't sum to 1.0 — this makes depleted teams look weaker than they are. Fix: normalize
  shares after injury removal. See memory/model-analysis.md for details.

## Key Commands
- `PYTHONPATH=. uv run python pipeline/nightly_job.py` — run nightly job manually
- `PYTHONPATH=. uv run python pipeline/phase1_full_season.py` — re-run full-season RAPM
- `PYTHONPATH=. uv run python downstream/predictions.py` — predict tomorrow's slate
- `PYTHONPATH=. uv run python downstream/predictions.py --date YYYY-MM-DD` — specific date
- `PYTHONPATH=. uv run python downstream/calibration.py` — refit calibration coefficients
- `uv run pytest tests/` — run all tests (59 tests, all passing as of P7)
- `powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1` — register Task Scheduler

## DB State (as of 2026-03-21)
- 1041 games, ~55,923 stints, ~201,361 possessions, 567 players rated
- current_ratings: phase='elo' (P6 composite — RAPM base + Elo delta)
- rapm_ratings: has both rapm_full (historical) and rapm_rolling (latest) rows
- elo_ratings: 22,572 rows (per-player-per-game cumulative deltas)
- predictions: rows for 2026-03-21 slate (9 resolved with actual outcomes) + 2026-03-22 slate

## Next Steps
1. **`/roster` skill + `downstream/roster_report.py`** — live roster + injury lookup from DB + ESPN.
   Full spec at `memory/specs/roster-report.md`. Run `/fresh-eyes` then implement the spec.
   Prevents Claude from using stale internal roster knowledge during game analysis.
2. **Coverage-ratio → calibration penalty** — add `β_coverage * (2 - home_cov - away_cov)` term
   to calibration to further shrink predictions for depleted teams. Availability discount helps
   but ridge compression limits injury-game accuracy; a coverage penalty is more direct.
3. **CLV tracking** — will eventually come via a separate repo that David owns; connect that repo
   to this one when ready. Do not build CLV infrastructure here for now.
4. See `memory/model-analysis.md` for full improvement backlog.

## Completed This Session (2026-03-22, second pass)
- **Outcome tracking pipeline** (2026-03-22): `downstream/track_outcomes.py` resolves predictions
  against actual scores in the `games` table after nightly ingestion. 4 new columns added to
  `predictions` table: `actual_home_score`, `actual_away_score`, `actual_margin`,
  `outcome_tracked_at`. `db/init_db.py` has idempotent ALTER TABLE migration. `run_predictions.bat`
  now runs `track_outcomes.py` before generating new predictions. 74/74 tests pass.
  First resolved results (2026-03-21 slate, 9 games): MAE=6.25, Corr=0.794, Dir=7/9 (77.8%).
  Market baseline on same 9 games: 9/9 (100%) — large gap on injury games (PHI@UTA, LAL@ORL).
- **CLV tracking**: deferred — David has a separate CLV repo; will connect when ready.

## Completed This Session (2026-03-22)
- **Defense sign bug fix** (2026-03-22, second session): Fixed `compute_raw_margin` in
  `downstream/team_ratings.py` and inline duplicate in `downstream/calibration.py`.
  Bug: formula used `(home_off - away_def)` but RAPM defense sign convention is
  positive=bad/negative=good, so subtraction was backwards. Fix: `(home_off + away_def)`.
  After recalibration: val_corr 0.548→0.586, backtest dir_acc 68.6%→70.1% (+15 games correct).
  Bonus: σ²_between went from 0→4.9966 — real team HCA variation now detectable; v3 "full pooling"
  conclusion was an artifact of the sign bug inflating noise.
- **EB calibration in production code**: merged James-Stein shrinkage from `test_hca_approach3_eb.py`
  into `downstream/calibration.py`. Re-running `calibration.py` now natively produces EB coefficients.
  Old OLS-with-30-dummies code removed from production path. 64/64 tests pass.
- **Availability discount**: both `backtest.py::_build_minutes_profile` and
  `predictions.py::_build_minutes_profile_from_db` now apply
  `effective_share = mean_share × (games_appeared / window_games)`. Players with many DNPs
  get proportionally less weight. Full-season improvement: MAE 11.06→10.84, corr 0.490→0.506.
- **GSW @ ATL diagnosis**: RAPM ridge compression limits injury-game accuracy. Closing line
  (ATL -9.5) is right benchmark vs actual score (+16). Documented in model-analysis.md.

## Completed This Session (2026-03-21)
- Possession share redistribution fix: `_build_minutes_profile_from_db()` now scales remaining
  players' minutes by `1/coverage_ratio` after injury exclusion. Mean-neutral, semantically correct.
  64/64 tests pass (5 new in tests/test_predictions.py).
- Added NBA Domain Knowledge Rules to CLAUDE.md: always backtest, never rely on Claude's internal
  NBA knowledge, ask David for sanity checks on domain-specific questions.
