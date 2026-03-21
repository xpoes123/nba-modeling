-- NBA Player Rating Engine — SQLite Schema
-- Single source of truth for all table definitions.
-- Read by db/init_db.py at setup time.

-- ---------------------------------------------------------------------------
-- games: one row per game, used for idempotency and metadata
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS games (
    game_id         TEXT PRIMARY KEY,
    season          TEXT NOT NULL,
    game_date       TEXT NOT NULL,           -- YYYY-MM-DD
    home_team_id    TEXT NOT NULL,
    away_team_id    TEXT NOT NULL,
    home_score      INTEGER,
    away_score      INTEGER,
    game_pace       REAL,                    -- possessions per 48 minutes
    ingested_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- players: player metadata, upserted during ETL
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS players (
    player_id       TEXT PRIMARY KEY,        -- nba.com/stats integer as string
    player_name     TEXT NOT NULL,
    team_id         TEXT,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- possessions: one row per possession — primary Elo input
-- Lineup IDs are dash-separated sorted player ID strings, e.g.
-- "201566-203507-203954-1629029-1630567"
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS possessions (
    possession_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id                 TEXT    NOT NULL REFERENCES games(game_id),
    season                  TEXT    NOT NULL,
    period                  INTEGER NOT NULL,
    possession_number       INTEGER NOT NULL,  -- sequential within game
    offense_team_id         TEXT    NOT NULL,
    defense_team_id         TEXT    NOT NULL,
    points_scored           INTEGER NOT NULL DEFAULT 0,
    fg2a                    INTEGER NOT NULL DEFAULT 0,
    fg2m                    INTEGER NOT NULL DEFAULT 0,
    fg3a                    INTEGER NOT NULL DEFAULT 0,
    fg3m                    INTEGER NOT NULL DEFAULT 0,
    turnovers               INTEGER NOT NULL DEFAULT 0,
    offensive_rebounds      INTEGER NOT NULL DEFAULT 0,
    free_throw_points       INTEGER NOT NULL DEFAULT 0,
    start_time              TEXT,
    end_time                TEXT,
    start_type              TEXT,
    start_score_differential INTEGER,
    offense_lineup_id       TEXT NOT NULL,
    defense_lineup_id       TEXT NOT NULL,
    off_player_1            TEXT NOT NULL,
    off_player_2            TEXT NOT NULL,
    off_player_3            TEXT NOT NULL,
    off_player_4            TEXT NOT NULL,
    off_player_5            TEXT NOT NULL,
    def_player_1            TEXT NOT NULL,
    def_player_2            TEXT NOT NULL,
    def_player_3            TEXT NOT NULL,
    def_player_4            TEXT NOT NULL,
    def_player_5            TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- stints: aggregated 10-man matchup data — primary RAPM input
-- One row per unique (game, offense_lineup, defense_lineup) combination.
-- points_allowed is stored explicitly (opponent's points_scored for the
-- same matchup) so the defensive regression target is readily available.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stints (
    stint_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id             TEXT    NOT NULL REFERENCES games(game_id),
    season              TEXT    NOT NULL,
    game_date           TEXT    NOT NULL,    -- denormalized for window queries
    offense_lineup_id   TEXT    NOT NULL,
    defense_lineup_id   TEXT    NOT NULL,
    possessions         INTEGER NOT NULL,
    seconds_played      REAL    NOT NULL,
    points_scored       INTEGER NOT NULL DEFAULT 0,
    points_allowed      INTEGER NOT NULL DEFAULT 0,
    offensive_rating    REAL,                -- points_scored / possessions * 100
    UNIQUE(game_id, offense_lineup_id, defense_lineup_id)
);

-- ---------------------------------------------------------------------------
-- league_averages: season-level PPP and pace, computed after backfill
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS league_averages (
    season              TEXT PRIMARY KEY,
    avg_ppp             REAL    NOT NULL,    -- expected: 1.10-1.15
    avg_pace            REAL    NOT NULL,    -- possessions per 48 minutes
    total_possessions   INTEGER NOT NULL,
    computed_at         TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- rapm_ratings: RAPM coefficients with window metadata
-- phase = 'rapm_full' for full-season, 'rapm_rolling' for 30-game window
-- window_start_date is NULL for full-season runs
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rapm_ratings (
    rating_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id           TEXT    NOT NULL REFERENCES players(player_id),
    season              TEXT    NOT NULL,
    phase               TEXT    NOT NULL,    -- 'rapm_full' | 'rapm_rolling'
    window_start_date   TEXT,                -- NULL for full-season
    window_end_date     TEXT    NOT NULL,
    offense             REAL    NOT NULL,
    defense             REAL    NOT NULL,
    pace                REAL    NOT NULL,
    computed_at         TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(player_id, season, phase, window_end_date)
);

-- ---------------------------------------------------------------------------
-- elo_ratings: per-game cumulative Elo delta snapshots
-- Stores the cumulative delta (on top of RAPM base) after each game.
-- current_ratings = rapm_base + latest elo_delta for each player.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS elo_ratings (
    elo_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id       TEXT    NOT NULL REFERENCES players(player_id),
    season          TEXT    NOT NULL,
    game_id         TEXT    NOT NULL REFERENCES games(game_id),
    offense_delta   REAL    NOT NULL DEFAULT 0.0,
    defense_delta   REAL    NOT NULL DEFAULT 0.0,
    pace_delta      REAL    NOT NULL DEFAULT 0.0,
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(player_id, game_id)
);

-- ---------------------------------------------------------------------------
-- current_ratings: best current rating per player — the main output table
-- overall = offense - defense (positive defense = allows fewer points)
-- phase tracks which model produced the current rating
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS current_ratings (
    player_id   TEXT PRIMARY KEY REFERENCES players(player_id),
    season      TEXT NOT NULL,
    offense     REAL NOT NULL,
    defense     REAL NOT NULL,
    pace        REAL NOT NULL,
    overall     REAL NOT NULL,  -- offense - defense
    phase       TEXT NOT NULL,  -- 'rapm_full' | 'rapm_rolling' | 'elo'
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- predictions: pre-game model predictions vs market lines
-- predicted_spread > 0 means home team is favored in our model
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS predictions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    odds_event_id       TEXT,                       -- Odds API event ID
    game_date           TEXT    NOT NULL,            -- YYYY-MM-DD
    home_team_id        TEXT,                        -- nba.com team ID (if mappable)
    away_team_id        TEXT,                        -- nba.com team ID (if mappable)
    home_team_name      TEXT    NOT NULL,
    away_team_name      TEXT    NOT NULL,
    predicted_spread    REAL,                        -- home margin (positive = home favored)
    predicted_win_prob  REAL,                        -- P(home wins), 0-1
    sim_std             REAL,                        -- Monte Carlo std dev
    market_spread       REAL,                        -- Odds API home spread
    market_win_prob     REAL,                        -- vig-adjusted implied P(home wins)
    market_total        REAL,                        -- over/under line
    spread_edge         REAL,                        -- predicted_spread - market_spread
    win_prob_edge       REAL,                        -- predicted_win_prob - market_win_prob
    home_b2b            INTEGER NOT NULL DEFAULT 0,
    away_b2b            INTEGER NOT NULL DEFAULT 0,
    n_simulations       INTEGER,
    home_coverage       REAL,                        -- fraction of normal home minutes available (0-1)
    away_coverage       REAL,                        -- fraction of normal away minutes available (0-1)
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(game_date, home_team_name, away_team_name)
);

-- ---------------------------------------------------------------------------
-- Indexes for common query patterns
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_games_season
    ON games(season);

CREATE INDEX IF NOT EXISTS idx_possessions_game_id
    ON possessions(game_id);

CREATE INDEX IF NOT EXISTS idx_possessions_season
    ON possessions(season);

CREATE INDEX IF NOT EXISTS idx_possessions_offense_lineup
    ON possessions(offense_lineup_id);

CREATE INDEX IF NOT EXISTS idx_possessions_defense_lineup
    ON possessions(defense_lineup_id);

CREATE INDEX IF NOT EXISTS idx_stints_game_id
    ON stints(game_id);

CREATE INDEX IF NOT EXISTS idx_stints_season
    ON stints(season);

CREATE INDEX IF NOT EXISTS idx_stints_game_date
    ON stints(game_date);

CREATE INDEX IF NOT EXISTS idx_rapm_player_season
    ON rapm_ratings(player_id, season);

CREATE INDEX IF NOT EXISTS idx_elo_player_season
    ON elo_ratings(player_id, season);
