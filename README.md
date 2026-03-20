# NBA Player Rating Engine — Project Spec

## Overview

A hybrid player rating system that combines **Regularized Adjusted Plus-Minus (RAPM)** with **Elo-style incremental updates** to produce dynamic, three-dimensional player ratings (Offense, Defense, Pace). Ratings are computed at the possession level using on-floor lineup data, updated per-possession via Elo mechanics, and re-anchored nightly via ridge regression.

### Design Philosophy

The player ratings are the core product. Downstream applications (spread prediction, live in-game trading, lineup optimization) consume ratings as inputs — the system is not optimized for any single use case.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                              │
│                                                             │
│  pbpstats.com API ──► Possession Parser ──► SQLite DB       │
│  (pre-parsed possessions, lineups, 2 seasons)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   RATING ENGINE                             │
│                                                             │
│  ┌──────────────┐    ┌──────────────────────────────────┐   │
│  │  RAPM Layer   │    │  Elo Layer                       │   │
│  │  (Base Fit)   │    │  (Incremental Updates)           │   │
│  │               │    │                                  │   │
│  │  Ridge reg.   │◄───│  Per-possession updates between  │   │
│  │  30-game      │    │  daily RAPM re-fits              │   │
│  │  rolling      │    │                                  │   │
│  │  window       │    │  K-factor split across 10        │   │
│  │               │────►  players on floor                │   │
│  │  Re-fit       │    │                                  │   │
│  │  nightly      │    │  Resets to RAPM baseline after   │   │
│  └──────────────┘    │  each re-fit                     │   │
│                       └──────────────────────────────────┘   │
│                                                             │
│  Output: 3 ratings per player (Offense, Defense, Pace)      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 DOWNSTREAM CONSUMERS                        │
│                                                             │
│  • Spread / Moneyline Prediction                            │
│  • Live In-Game Model (Kalshi / Polymarket)                 │
│  • Lineup Optimization / Rotation Analysis                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Source: pbpstats.com

pbpstats provides pre-parsed possession data with lineup attribution. Covers current season (2025-26) and previous season (2024-25). ~500K possessions per season.

### SQLite Schema

```sql
-- Raw possession data ingested from pbpstats
CREATE TABLE possessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    season TEXT NOT NULL,            -- '2024-25', '2025-26'
    game_date DATE NOT NULL,
    period INTEGER NOT NULL,
    possession_number INTEGER NOT NULL,
    offense_team_id TEXT NOT NULL,
    defense_team_id TEXT NOT NULL,
    points_scored INTEGER NOT NULL,  -- 0, 1, 2, or 3
    possession_type TEXT,            -- e.g. 'halfcourt', 'transition', 'after_timeout'
    
    -- 10 player IDs on the floor (5 offense, 5 defense)
    off_player_1 TEXT NOT NULL,
    off_player_2 TEXT NOT NULL,
    off_player_3 TEXT NOT NULL,
    off_player_4 TEXT NOT NULL,
    off_player_5 TEXT NOT NULL,
    def_player_1 TEXT NOT NULL,
    def_player_2 TEXT NOT NULL,
    def_player_3 TEXT NOT NULL,
    def_player_4 TEXT NOT NULL,
    def_player_5 TEXT NOT NULL,

    UNIQUE(game_id, period, possession_number)
);

CREATE INDEX idx_possessions_game_date ON possessions(game_date);
CREATE INDEX idx_possessions_season ON possessions(season);
CREATE INDEX idx_possessions_game_id ON possessions(game_id);

-- League averages per season (recalculated nightly)
CREATE TABLE league_averages (
    season TEXT PRIMARY KEY,
    avg_ppp REAL NOT NULL,           -- points per possession
    avg_pace REAL NOT NULL,          -- possessions per 48 min
    total_possessions INTEGER NOT NULL
);

-- Player metadata
CREATE TABLE players (
    player_id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    current_team_id TEXT,
    position TEXT
);

-- RAPM coefficients (re-fit nightly, 30-game rolling window)
CREATE TABLE rapm_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    as_of_date DATE NOT NULL,        -- date the regression was run
    season TEXT NOT NULL,
    window_start_date DATE NOT NULL, -- first game in the 30-game window
    window_end_date DATE NOT NULL,   -- last game in the 30-game window
    window_game_count INTEGER NOT NULL,

    -- Three rating dimensions
    offense_rating REAL NOT NULL,    -- ORAPM: marginal PPP vs league avg
    defense_rating REAL NOT NULL,    -- DRAPM: marginal PPP allowed vs league avg
    pace_rating REAL NOT NULL,       -- marginal possessions per 48 vs league avg

    -- Regression metadata
    possessions_in_window INTEGER NOT NULL,
    ridge_alpha REAL NOT NULL,       -- regularization strength used

    UNIQUE(player_id, as_of_date),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE INDEX idx_rapm_date ON rapm_ratings(as_of_date);
CREATE INDEX idx_rapm_player ON rapm_ratings(player_id);

-- Live Elo ratings (updated per-possession)
CREATE TABLE elo_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    game_id TEXT NOT NULL,
    possession_id INTEGER NOT NULL,  -- FK to possessions.id
    timestamp DATETIME NOT NULL,

    -- Current live ratings (RAPM baseline + Elo delta)
    offense_elo REAL NOT NULL,
    defense_elo REAL NOT NULL,
    pace_elo REAL NOT NULL,

    -- Decomposed components for debugging
    rapm_offense_base REAL NOT NULL, -- from most recent RAPM fit
    rapm_defense_base REAL NOT NULL,
    rapm_pace_base REAL NOT NULL,
    elo_offense_delta REAL NOT NULL, -- accumulated Elo shift since last RAPM
    elo_defense_delta REAL NOT NULL,
    elo_pace_delta REAL NOT NULL,

    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (possession_id) REFERENCES possessions(id)
);

CREATE INDEX idx_elo_player_time ON elo_ratings(player_id, timestamp);
CREATE INDEX idx_elo_game ON elo_ratings(game_id);

-- Snapshot table: current "best" rating per player (for fast lookups)
CREATE TABLE current_ratings (
    player_id TEXT PRIMARY KEY,
    updated_at DATETIME NOT NULL,

    -- Composite ratings (RAPM base + Elo delta)
    offense REAL NOT NULL,
    defense REAL NOT NULL,
    pace REAL NOT NULL,

    -- Overall (offense - defense, higher = better)
    overall REAL GENERATED ALWAYS AS (offense - defense) STORED,

    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
```

---

## Model Design

### 1. RAPM Layer (Base Fit)

**Purpose:** Produce statistically rigorous player ratings by isolating individual contribution from lineup context.

**Method:** Ridge regression on possession-level data.

**Design matrix (per possession):**

For ~N possessions and ~P unique players:
- Matrix `X` is N × P
- For each possession row:
  - `+1` for each offensive player on floor
  - `-1` for each defensive player on floor
  - `0` for all other players
- Target vector `y`:
  - **Offense/Defense model:** `points_scored - league_avg_ppp`
  - **Pace model:** `possessions_in_game / 48 * minutes_duration - league_avg_pace` (aggregated at the game-stint level)

**Rolling window:** 30 games per player (not calendar-based). A player's window includes the last 30 *team games in which they appeared*. This means different players may have slightly different window boundaries.

**Re-fit cadence:** Nightly, after all games complete.

**Regularization:** Ridge (L2). Hyperparameter `alpha` selected via cross-validation on first build, then held constant unless performance degrades. Starting point: `alpha = 5000` (typical for RAPM at possession level).

**Cold start:** New players initialize at 0 (league average) for all three dimensions. Ridge naturally shrinks low-sample players toward zero.

**Output:** Three coefficients per player: `offense_rating`, `defense_rating`, `pace_rating`.

### 2. Elo Layer (Incremental Updates)

**Purpose:** Allow ratings to drift between nightly RAPM re-fits, capturing within-day and within-game momentum.

**Update rule (per possession):**

```
For each player on the floor:
    expected = sigmoid(sum of offense Elo ratings - sum of defense Elo ratings)
    actual   = 1 if points_scored > league_avg_ppp else 0
    surprise = actual - expected

    For offensive players:
        elo_offense_delta += K * surprise / 5
    For defensive players:
        elo_defense_delta -= K * surprise / 5
```

Division by 5 distributes credit equally among the 5 players on each side.

**K-factor:** Start with `K = 2.0` (small, since these are micro-adjustments on top of a regression baseline). Tune empirically.

**Reset:** After each nightly RAPM re-fit, Elo deltas reset to 0 and the RAPM base updates.

**Pace Elo:** Updated at the game level (not per-possession), since individual possession duration is noisy. After each game, compare actual game pace to expected pace given the 10-man rotation, and distribute the surprise.

### 3. Composite Rating

```
player.offense = rapm.offense_rating + elo.offense_delta
player.defense = rapm.defense_rating + elo.defense_delta
player.pace    = rapm.pace_rating    + elo.pace_delta
player.overall = player.offense - player.defense
```

Higher offense = better (adds more points).
Lower defense = better (allows fewer points), so `overall = offense - defense` means higher = better net impact.

---

## Pipeline

### Nightly Job (runs after last game completes)

```
1. INGEST
   - Fetch new game possessions from pbpstats for today's games
   - Upsert into possessions table
   - Update player metadata

2. COMPUTE LEAGUE AVERAGES
   - Recalculate season-level avg_ppp and avg_pace
   - Update league_averages table

3. RAPM FIT
   - For each player with >= 1 game in the last 30 team games:
     a. Build design matrix from possessions in their window
     b. Run ridge regression (offense/defense model)
     c. Run ridge regression (pace model)
     d. Store coefficients in rapm_ratings

4. RESET ELO
   - For all players: set elo deltas to 0, update RAPM base
   - Update current_ratings snapshot table

5. REPLAY ELO (for today's games)
   - For each game played today, replay possessions chronologically
   - Apply Elo updates per possession
   - Store final elo_ratings state
   - Update current_ratings snapshot
```

### Live Game Processing (future — for Kalshi/Polymarket)

```
1. Stream live play-by-play (source TBD — pbpstats may have delay)
2. Parse possessions as they complete
3. Apply Elo updates in real-time
4. Feed updated ratings into live win probability / spread model
```

---

## Repo Structure

```
nba-rating-engine/
├── README.md
├── CLAUDE.md                    # AI assistant context
├── requirements.txt
├── config.py                    # Constants: seasons, alpha, K-factor, etc.
├── db/
│   ├── schema.sql               # Full schema from above
│   ├── init_db.py               # Create tables
│   └── nba_ratings.db           # SQLite database (gitignored)
├── ingestion/
│   ├── pbpstats_client.py       # Fetch possession data from pbpstats
│   ├── ingest_season.py         # Backfill full season
│   └── ingest_daily.py          # Nightly incremental fetch
├── models/
│   ├── rapm.py                  # Ridge regression: build matrix, fit, store
│   ├── elo.py                   # Elo update logic: per-possession, reset
│   └── composite.py             # Combine RAPM + Elo into current ratings
├── pipeline/
│   ├── nightly_job.py           # Orchestrator: ingest → RAPM → Elo
│   └── backfill.py              # One-time: process historical seasons
├── analysis/
│   ├── validate_ratings.py      # Sanity checks, known-player spot checks
│   ├── calibration.py           # Elo calibration plots, K-factor tuning
│   └── notebooks/               # Jupyter exploration
│       └── rapm_exploration.ipynb
├── downstream/                  # Future: consumers of the ratings
│   ├── spread_model.py
│   ├── live_model.py
│   └── lineup_optimizer.py
└── tests/
    ├── test_rapm.py
    ├── test_elo.py
    └── test_pipeline.py
```

---

## Implementation Plan

### Phase 1: Data Pipeline (Week 1)
- [ ] Set up repo, SQLite schema, config
- [ ] Build pbpstats client (fetch possessions + lineups)
- [ ] Backfill 2024-25 full season
- [ ] Backfill 2025-26 season through current date
- [ ] Validate data: spot-check possession counts, lineup integrity

### Phase 2: RAPM Model (Week 2)
- [ ] Build design matrix constructor from possessions table
- [ ] Implement rolling 30-game window logic
- [ ] Ridge regression for offense/defense model
- [ ] Ridge regression for pace model
- [ ] Backfill historical RAPM ratings for both seasons
- [ ] Validation: compare top/bottom players to public RAPM sources

### Phase 3: Elo Layer (Week 3)
- [ ] Implement per-possession Elo update function
- [ ] Implement game-level pace Elo update
- [ ] Build Elo replay for historical games
- [ ] Nightly reset + RAPM re-anchor logic
- [ ] Calibration: tune K-factor, plot expected vs actual
- [ ] Composite rating assembly + current_ratings snapshot

### Phase 4: Nightly Pipeline (Week 4)
- [ ] Nightly orchestrator (ingest → RAPM → Elo)
- [ ] Scheduling (cron or similar)
- [ ] Monitoring: alerts on data freshness, rating drift
- [ ] current_ratings API or export for downstream use

### Phase 5: Downstream Applications (Week 5+)
- [ ] Spread / moneyline projection from lineup-weighted ratings
- [ ] Integration with live model (Matthew's Brownian motion work)
- [ ] Lineup optimization tooling

---

## Key Parameters

| Parameter | Initial Value | Notes |
|-----------|--------------|-------|
| Ridge alpha | 5000 | Typical for possession-level RAPM; CV to tune |
| Elo K-factor (offense/defense) | 2.0 | Small — micro-adjustments on regression base |
| Elo K-factor (pace) | 1.0 | Game-level updates, less reactive |
| Rolling window | 30 games | Per-player, not calendar |
| Seasons in scope | 2024-25, 2025-26 | ~1M total possessions |
| Cold start rating | 0.0 | League average for all dimensions |
| Expected points baseline | League avg PPP per season | Recalculated nightly |

---

## Open Questions & Future Considerations

1. **pbpstats API stability** — Need to verify rate limits, data freshness (how quickly do new games appear?), and whether historical data access requires any auth.

2. **Live data source for in-game Elo** — pbpstats likely has a delay. May need to supplement with nba_api live play-by-play or another real-time source for the Kalshi/Polymarket use case.

3. **Cross-season continuity** — Should a player's RAPM window span the season boundary? Current design: no, each season is independent. Could add a decay factor to carry ratings across seasons.

4. **Bayesian priors** — Ridge keeps things simple, but if low-minute player ratings are noisy, informing priors with box score stats (BPM, usage rate) is a natural upgrade path.

5. **Pace-efficiency correlation** — The decomposed model assumes some independence. If this introduces systematic bias, a correction term or joint model may be needed.

6. **K-factor scheduling** — Could vary K by context: higher for early season (more uncertainty), lower for playoffs. Also could be player-specific (higher K for players with fewer possessions).

7. **Defensive rating attribution** — On-floor binary is a known limitation for defense, where individual impact is harder to isolate. Future upgrade: weight by proximity/matchup data if tracking data becomes accessible.
