"""
P6: Composite ratings — combine RAPM base + cumulative Elo delta into current_ratings.

Public API:
    update_current_ratings(db_path, season) -> None
"""

import sqlite3


def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def update_current_ratings(db_path: str, season: str) -> None:
    """
    Combine RAPM base ratings with latest cumulative Elo deltas, write to current_ratings.

    For each player with a rapm_rolling rating:
        offense = rapm_offense + elo_offense_delta  (elo_delta = 0 if no Elo data yet)
        defense = rapm_defense + elo_defense_delta
        pace    = rapm_pace    + elo_pace_delta
        overall = offense - defense

    Sources:
        RAPM base:  most recent rapm_rolling row per player (by window_end_date)
        Elo deltas: most recent elo_ratings row per player (by updated_at)

    Updates current_ratings with phase='elo'.

    Args:
        db_path: Path to SQLite database.
        season:  Season string, e.g. '2025-26'.
    """
    conn = _get_conn(db_path)
    try:
        # Latest rolling RAPM per player (most recent window_end_date)
        rapm_rows = conn.execute(
            """
            SELECT r.player_id, r.offense, r.defense, r.pace
            FROM rapm_ratings r
            INNER JOIN (
                SELECT player_id, MAX(window_end_date) AS latest
                FROM rapm_ratings
                WHERE season = ? AND phase = 'rapm_rolling'
                GROUP BY player_id
            ) sub ON r.player_id = sub.player_id
                  AND r.window_end_date = sub.latest
            WHERE r.season = ? AND r.phase = 'rapm_rolling'
            """,
            (season, season),
        ).fetchall()

        if not rapm_rows:
            raise ValueError(
                f"No rapm_rolling ratings found for season '{season}'. "
                "Run rolling RAPM first."
            )

        # Latest cumulative Elo delta per player (most recent updated_at)
        elo_rows = conn.execute(
            """
            SELECT e.player_id, e.offense_delta, e.defense_delta, e.pace_delta
            FROM elo_ratings e
            INNER JOIN (
                SELECT player_id, MAX(updated_at) AS latest
                FROM elo_ratings
                WHERE season = ?
                GROUP BY player_id
            ) sub ON e.player_id = sub.player_id
                  AND e.updated_at = sub.latest
            WHERE e.season = ?
            """,
            (season, season),
        ).fetchall()

        elo_deltas: dict[str, tuple[float, float, float]] = {
            row[0]: (row[1], row[2], row[3]) for row in elo_rows
        }

        rows_to_upsert = []
        for player_id, rapm_off, rapm_def, rapm_pace in rapm_rows:
            elo_off_d, elo_def_d, elo_pace_d = elo_deltas.get(player_id, (0.0, 0.0, 0.0))
            offense = rapm_off + elo_off_d
            defense = rapm_def + elo_def_d
            pace = rapm_pace + elo_pace_d
            overall = offense - defense
            rows_to_upsert.append((player_id, season, offense, defense, pace, overall))

        with conn:
            conn.executemany(
                """
                INSERT INTO current_ratings
                    (player_id, season, offense, defense, pace, overall, phase)
                VALUES (?, ?, ?, ?, ?, ?, 'elo')
                ON CONFLICT(player_id) DO UPDATE SET
                    season     = excluded.season,
                    offense    = excluded.offense,
                    defense    = excluded.defense,
                    pace       = excluded.pace,
                    overall    = excluded.overall,
                    phase      = excluded.phase,
                    updated_at = datetime('now')
                """,
                rows_to_upsert,
            )

    finally:
        conn.close()
