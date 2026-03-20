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


def init_db(db_path: Optional[str] = None, schema_path: Optional[str] = None) -> None:
    db_path = db_path or DB_PATH
    schema_path = schema_path or SCHEMA_PATH

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with open(schema_path, "r") as f:
        schema = f.read()

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)

    print(f"Database initialized at {db_path}")


if __name__ == "__main__":
    init_db()
