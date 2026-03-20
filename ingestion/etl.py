"""
P2: ETL pipeline — transform parsed game data into SQLite rows.

Public API:
    insert_game(db_path, parsed_game)  -> None
    aggregate_stints(possessions)      -> list[dict]
"""

import sqlite3
import logging
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def insert_game(db_path: str, parsed_game: dict) -> None:
    """
    Insert a parsed game into the database atomically.

    If the game already exists in the `games` table, it is skipped (idempotent).

    Inserts:
      - games row
      - players rows (upsert)
      - possessions rows
      - stints rows (aggregated by lineup pair)
    """
    game_id = parsed_game["game_id"]
    conn = _get_conn(db_path)
    try:
        # Idempotency check — skip if already ingested
        row = conn.execute(
            "SELECT 1 FROM games WHERE game_id = ?", (game_id,)
        ).fetchone()
        if row:
            logger.debug("Game %s already ingested, skipping.", game_id)
            return

        with conn:  # BEGIN / COMMIT / ROLLBACK
            _insert_game_row(conn, parsed_game)
            _upsert_players(conn, parsed_game)
            _insert_possessions(conn, parsed_game)
            _insert_stints(conn, parsed_game)

        logger.info(
            "Inserted game %s: %d possessions, %d stints",
            game_id,
            len(parsed_game["possessions"]),
            len(aggregate_stints(parsed_game["possessions"])),
        )
    finally:
        conn.close()


def aggregate_stints(possessions: list[dict]) -> list[dict]:
    """
    Group possessions by (offense_lineup_id, defense_lineup_id) and aggregate.

    Returns list of dicts with keys:
        offense_lineup_id, defense_lineup_id,
        possessions (count), seconds_played, points_scored,
        points_allowed (filled in later when we see the mirror stint),
        offensive_rating
    """
    # Group: (offense_lineup, defense_lineup) -> accumulator
    groups: dict[tuple[str, str], dict] = defaultdict(lambda: {
        "possessions": 0,
        "seconds_played": 0.0,
        "points_scored": 0,
    })

    for p in possessions:
        key = (p["offense_lineup_id"], p["defense_lineup_id"])
        g = groups[key]
        g["possessions"] += 1
        g["points_scored"] += p["points_scored"]

        # Compute possession duration from clock strings.
        # Clocks are time-remaining (counting down), so duration = start - end.
        start_s = _clock_to_seconds(p.get("start_time") or "")
        end_s = _clock_to_seconds(p.get("end_time") or "")
        duration = max(0.0, start_s - end_s)
        g["seconds_played"] += duration

    # Compute points_allowed: the mirror stint's points_scored
    # Build a lookup first, then cross-reference
    stint_list = []
    for (off_lid, def_lid), g in groups.items():
        poss_count = g["possessions"]
        pts = g["points_scored"]
        secs = g["seconds_played"]
        # points_allowed = what the defense lineup scored when they were on offense
        # against this offense lineup = mirror (def_lid, off_lid)
        mirror = groups.get((def_lid, off_lid), {})
        pts_allowed = mirror.get("points_scored", 0)

        off_rating = round(pts / poss_count * 100, 4) if poss_count > 0 else None

        stint_list.append({
            "offense_lineup_id": off_lid,
            "defense_lineup_id": def_lid,
            "possessions": poss_count,
            "seconds_played": round(secs, 3),
            "points_scored": pts,
            "points_allowed": pts_allowed,
            "offensive_rating": off_rating,
        })

    return stint_list


# ---------------------------------------------------------------------------
# Private insert helpers
# ---------------------------------------------------------------------------

def _insert_game_row(conn: sqlite3.Connection, g: dict) -> None:
    conn.execute(
        """
        INSERT INTO games
            (game_id, season, game_date, home_team_id, away_team_id,
             home_score, away_score, game_pace)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            g["game_id"],
            g["season"],
            g.get("game_date"),
            g.get("home_team_id"),
            g.get("away_team_id"),
            g.get("home_score"),
            g.get("away_score"),
            g.get("game_pace"),
        ),
    )


def _upsert_players(conn: sqlite3.Connection, g: dict) -> None:
    """Upsert player metadata.  Name comes from parse_game's BoxScoreTraditionalV3 call."""
    players: dict[str, str] = g.get("players", {})

    # Collect all player IDs from possessions too (in case players dict is sparse)
    all_ids: set[str] = set(players.keys())
    player_keys = [
        "off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5",
        "def_player_1", "def_player_2", "def_player_3", "def_player_4", "def_player_5",
    ]
    for p in g.get("possessions", []):
        for k in player_keys:
            pid = p.get(k)
            if pid:
                all_ids.add(pid)

    # Determine team_id for each player from possessions
    player_teams: dict[str, Optional[str]] = {}
    for p in g.get("possessions", []):
        for k in ["off_player_1","off_player_2","off_player_3","off_player_4","off_player_5"]:
            pid = p.get(k)
            if pid:
                player_teams[pid] = p.get("offense_team_id")
        for k in ["def_player_1","def_player_2","def_player_3","def_player_4","def_player_5"]:
            pid = p.get(k)
            if pid:
                player_teams.setdefault(pid, p.get("defense_team_id"))

    for pid in all_ids:
        name = players.get(pid, "Unknown")
        team_id = player_teams.get(pid)
        conn.execute(
            """
            INSERT INTO players (player_id, player_name, team_id)
            VALUES (?, ?, ?)
            ON CONFLICT(player_id) DO UPDATE SET
                player_name = CASE WHEN excluded.player_name != 'Unknown'
                              THEN excluded.player_name ELSE player_name END,
                team_id     = excluded.team_id,
                updated_at  = datetime('now')
            """,
            (pid, name, team_id),
        )


def _insert_possessions(conn: sqlite3.Connection, g: dict) -> None:
    for p in g["possessions"]:
        conn.execute(
            """
            INSERT INTO possessions (
                game_id, season, period, possession_number,
                offense_team_id, defense_team_id,
                points_scored, fg2a, fg2m, fg3a, fg3m,
                turnovers, offensive_rebounds, free_throw_points,
                start_time, end_time, start_type, start_score_differential,
                offense_lineup_id, defense_lineup_id,
                off_player_1, off_player_2, off_player_3, off_player_4, off_player_5,
                def_player_1, def_player_2, def_player_3, def_player_4, def_player_5
            ) VALUES (
                ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
            """,
            (
                g["game_id"], g["season"], p["period"], p["possession_number"],
                p["offense_team_id"], p["defense_team_id"],
                p["points_scored"], p["fg2a"], p["fg2m"], p["fg3a"], p["fg3m"],
                p["turnovers"], p["offensive_rebounds"], p["free_throw_points"],
                p.get("start_time"), p.get("end_time"),
                p.get("start_type"), p.get("start_score_differential"),
                p["offense_lineup_id"], p["defense_lineup_id"],
                p["off_player_1"], p["off_player_2"], p["off_player_3"],
                p["off_player_4"], p["off_player_5"],
                p["def_player_1"], p["def_player_2"], p["def_player_3"],
                p["def_player_4"], p["def_player_5"],
            ),
        )


def _insert_stints(conn: sqlite3.Connection, g: dict) -> None:
    game_id = g["game_id"]
    season = g["season"]
    game_date = g.get("game_date")
    stints = aggregate_stints(g["possessions"])

    for s in stints:
        conn.execute(
            """
            INSERT OR IGNORE INTO stints (
                game_id, season, game_date,
                offense_lineup_id, defense_lineup_id,
                possessions, seconds_played,
                points_scored, points_allowed, offensive_rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                game_id, season, game_date,
                s["offense_lineup_id"], s["defense_lineup_id"],
                s["possessions"], s["seconds_played"],
                s["points_scored"], s["points_allowed"],
                s["offensive_rating"],
            ),
        )


# ---------------------------------------------------------------------------
# Clock helper (duplicated from pbpstats_client to keep etl.py self-contained)
# ---------------------------------------------------------------------------

def _clock_to_seconds(clock: str) -> float:
    """Convert clock string (MM:SS or PTxMy.zS) to seconds remaining."""
    try:
        clock = clock.strip()
        if not clock:
            return 0.0
        if clock.startswith("PT"):
            clock = clock[2:]
            minutes = 0.0
            seconds = 0.0
            if "M" in clock:
                m_idx = clock.index("M")
                minutes = float(clock[:m_idx])
                clock = clock[m_idx + 1:]
            if clock.endswith("S"):
                clock = clock[:-1]
            if clock:
                seconds = float(clock)
            return minutes * 60 + seconds
        else:
            parts = clock.split(":")
            return float(parts[0]) * 60 + float(parts[1])
    except Exception:
        return 0.0
