"""Tests for downstream/track_outcomes.py — outcome resolution and accuracy reporting."""
import sqlite3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from downstream.track_outcomes import resolve_outcomes, print_accuracy_report


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_test_db(tmp_path: Path) -> str:
    """Create a minimal SQLite DB with games and predictions tables."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE games (
            game_id       TEXT PRIMARY KEY,
            season        TEXT NOT NULL,
            game_date     TEXT NOT NULL,
            home_team_id  TEXT NOT NULL,
            away_team_id  TEXT NOT NULL,
            home_score    INTEGER,
            away_score    INTEGER,
            game_pace     REAL,
            ingested_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE predictions (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            odds_event_id       TEXT,
            game_date           TEXT    NOT NULL,
            home_team_id        TEXT,
            away_team_id        TEXT,
            home_team_name      TEXT    NOT NULL,
            away_team_name      TEXT    NOT NULL,
            predicted_spread    REAL,
            predicted_win_prob  REAL,
            sim_std             REAL,
            market_spread       REAL,
            market_win_prob     REAL,
            market_total        REAL,
            spread_edge         REAL,
            win_prob_edge       REAL,
            home_b2b            INTEGER NOT NULL DEFAULT 0,
            away_b2b            INTEGER NOT NULL DEFAULT 0,
            n_simulations       INTEGER,
            home_coverage       REAL,
            away_coverage       REAL,
            actual_home_score   INTEGER,
            actual_away_score   INTEGER,
            actual_margin       REAL,
            outcome_tracked_at  TEXT,
            created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE(game_date, home_team_name, away_team_name)
        );
    """)
    conn.close()
    return db_path


def _insert_game(db_path: str, game_id: str, game_date: str,
                 home_id: str, away_id: str,
                 home_score: int | None, away_score: int | None) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO games (game_id, season, game_date, home_team_id, away_team_id, home_score, away_score)"
        " VALUES (?,?,?,?,?,?,?)",
        (game_id, "2025-26", game_date, home_id, away_id, home_score, away_score),
    )
    conn.commit()
    conn.close()


def _insert_prediction(db_path: str, game_date: str, home_name: str, away_name: str,
                        home_id: str | None, away_id: str | None,
                        predicted_spread: float,
                        market_spread: float | None = None) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        """
        INSERT INTO predictions (game_date, home_team_name, away_team_name,
                                 home_team_id, away_team_id,
                                 predicted_spread, market_spread)
        VALUES (?,?,?,?,?,?,?)
        """,
        (game_date, home_name, away_name, home_id, away_id, predicted_spread, market_spread),
    )
    row_id = cur.lastrowid
    conn.commit()
    conn.close()
    return row_id


# ---------------------------------------------------------------------------
# resolve_outcomes tests
# ---------------------------------------------------------------------------

class TestResolveOutcomes:
    def test_resolves_matching_game(self, tmp_path):
        """A completed game with matching IDs should fill in actual scores."""
        db = _make_test_db(tmp_path)
        _insert_game(db, "G1", "2026-03-20", "H1", "A1", 110, 100)
        _insert_prediction(db, "2026-03-20", "HomeTeam", "AwayTeam", "H1", "A1", +5.0)

        n = resolve_outcomes(db_path=db)

        assert n == 1
        conn = sqlite3.connect(db)
        row = conn.execute("SELECT actual_home_score, actual_away_score, actual_margin FROM predictions").fetchone()
        conn.close()
        assert row[0] == 110
        assert row[1] == 100
        assert row[2] == 10.0  # 110 - 100

    def test_does_not_resolve_game_without_score(self, tmp_path):
        """A game with NULL scores (in-progress) should not be resolved."""
        db = _make_test_db(tmp_path)
        _insert_game(db, "G1", "2026-03-20", "H1", "A1", None, None)
        _insert_prediction(db, "2026-03-20", "HomeTeam", "AwayTeam", "H1", "A1", +5.0)

        n = resolve_outcomes(db_path=db)

        assert n == 0

    def test_skips_already_resolved(self, tmp_path):
        """Predictions with existing actual_home_score should not be re-resolved."""
        db = _make_test_db(tmp_path)
        _insert_game(db, "G1", "2026-03-20", "H1", "A1", 110, 100)
        _insert_prediction(db, "2026-03-20", "HomeTeam", "AwayTeam", "H1", "A1", +5.0)
        # Pre-populate actual score to simulate already resolved
        conn = sqlite3.connect(db)
        conn.execute("UPDATE predictions SET actual_home_score=110, actual_away_score=100, actual_margin=10")
        conn.commit()
        conn.close()

        n = resolve_outcomes(db_path=db)
        assert n == 0

    def test_skips_future_games(self, tmp_path):
        """Predictions for today or the future should not be resolved yet."""
        from datetime import date, timedelta
        db = _make_test_db(tmp_path)
        future = (date.today() + timedelta(days=1)).isoformat()
        _insert_game(db, "G1", future, "H1", "A1", 110, 100)
        _insert_prediction(db, future, "HomeTeam", "AwayTeam", "H1", "A1", +5.0)

        n = resolve_outcomes(db_path=db)
        assert n == 0

    def test_negative_actual_margin(self, tmp_path):
        """Away win → actual_margin should be negative (away scored more)."""
        db = _make_test_db(tmp_path)
        _insert_game(db, "G1", "2026-03-20", "H1", "A1", 98, 105)
        _insert_prediction(db, "2026-03-20", "HomeTeam", "AwayTeam", "H1", "A1", -3.0)

        resolve_outcomes(db_path=db)

        conn = sqlite3.connect(db)
        row = conn.execute("SELECT actual_margin FROM predictions").fetchone()
        conn.close()
        assert row[0] == -7.0  # 98 - 105

    def test_resolves_multiple_games(self, tmp_path):
        """Multiple unresolved predictions are all resolved in one run."""
        db = _make_test_db(tmp_path)
        _insert_game(db, "G1", "2026-03-20", "H1", "A1", 110, 100)
        _insert_game(db, "G2", "2026-03-20", "H2", "A2", 95, 108)
        _insert_prediction(db, "2026-03-20", "Home1", "Away1", "H1", "A1", +5.0)
        _insert_prediction(db, "2026-03-20", "Home2", "Away2", "H2", "A2", -2.0)

        n = resolve_outcomes(db_path=db)
        assert n == 2


# ---------------------------------------------------------------------------
# print_accuracy_report tests (smoke tests — just verify it doesn't crash)
# ---------------------------------------------------------------------------

class TestPrintAccuracyReport:
    def test_no_resolved_predictions(self, tmp_path, capsys):
        """With no resolved predictions, should print a 'no results' message."""
        db = _make_test_db(tmp_path)
        print_accuracy_report(db_path=db)
        out = capsys.readouterr().out
        assert "No resolved" in out

    def test_single_resolved_prediction(self, tmp_path, capsys):
        """With one resolved prediction, should print summary without crashing."""
        db = _make_test_db(tmp_path)
        _insert_prediction(db, "2026-03-20", "HomeTeam", "AwayTeam", "H1", "A1", +5.0)
        conn = sqlite3.connect(db)
        conn.execute("UPDATE predictions SET actual_home_score=110, actual_away_score=100, actual_margin=10")
        conn.commit()
        conn.close()

        print_accuracy_report(db_path=db)
        out = capsys.readouterr().out
        assert "games resolved" in out
        assert "MAE" in out

    def test_directional_accuracy_correct(self, tmp_path, capsys):
        """Home win predicted (+) and actual home win (+) → 1/1 direction correct."""
        db = _make_test_db(tmp_path)
        _insert_prediction(db, "2026-03-20", "HomeTeam", "AwayTeam", "H1", "A1", +5.0)
        conn = sqlite3.connect(db)
        conn.execute("UPDATE predictions SET actual_home_score=110, actual_away_score=100, actual_margin=10")
        conn.commit()
        conn.close()

        print_accuracy_report(db_path=db)
        out = capsys.readouterr().out
        assert "1/1" in out

    def test_directional_accuracy_wrong(self, tmp_path, capsys):
        """Home win predicted (+) but away wins (-) → 0/1 direction correct."""
        db = _make_test_db(tmp_path)
        _insert_prediction(db, "2026-03-20", "HomeTeam", "AwayTeam", "H1", "A1", +5.0)
        conn = sqlite3.connect(db)
        conn.execute("UPDATE predictions SET actual_home_score=95, actual_away_score=110, actual_margin=-15")
        conn.commit()
        conn.close()

        print_accuracy_report(db_path=db)
        out = capsys.readouterr().out
        assert "0/1" in out
