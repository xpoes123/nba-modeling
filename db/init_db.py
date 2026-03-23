"""Initialize the SQLite database from schema.sql.

Run this once before starting ingestion:
    python db/init_db.py

Safe to re-run — all CREATE statements use IF NOT EXISTS.
"""
import os
import sqlite3
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH, SCHEMA_PATH


def _apply_migrations(conn: sqlite3.Connection) -> None:
    """Idempotent column additions for schema evolution.

    ALTER TABLE ADD COLUMN is used because CREATE TABLE IF NOT EXISTS won't modify
    existing tables. Each migration checks whether the column already exists before
    attempting to add it, so re-running init_db is always safe.
    """
    existing = {row[1] for row in conn.execute("PRAGMA table_info(predictions)")}
    migrations = [
        ("actual_home_score",  "ALTER TABLE predictions ADD COLUMN actual_home_score  INTEGER"),
        ("actual_away_score",  "ALTER TABLE predictions ADD COLUMN actual_away_score  INTEGER"),
        ("actual_margin",      "ALTER TABLE predictions ADD COLUMN actual_margin       REAL"),
        ("outcome_tracked_at", "ALTER TABLE predictions ADD COLUMN outcome_tracked_at  TEXT"),
    ]
    for col, sql in migrations:
        if col not in existing:
            conn.execute(sql)
            print(f"  Migration applied: added predictions.{col}")


def init_db(db_path: Optional[str] = None, schema_path: Optional[str] = None) -> None:
    db_path = db_path or DB_PATH
    schema_path = schema_path or SCHEMA_PATH

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with open(schema_path, "r") as f:
        schema = f.read()

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        _apply_migrations(conn)

    print(f"Database initialized at {db_path}")


if __name__ == "__main__":
    init_db()
