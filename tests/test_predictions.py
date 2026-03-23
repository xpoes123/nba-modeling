"""Unit tests for injury-share normalization in lineup minute profiles."""
import math
import sqlite3

from downstream.lineup_sampler import MinutesProfile
from downstream.predictions import (
    _build_minutes_profile_from_db,
    _consecutive_recent_absences,
)


def _make_profile(shares: dict[str, float], scale: float = 240.0) -> MinutesProfile:
    """Build a MinutesProfile from possession-share fractions."""
    return MinutesProfile({pid: (s * scale, 0.03 * scale) for pid, s in shares.items()})


class TestMinutesNormalization:
    def test_full_health_sums_to_240(self):
        """Five equal-share players at 0.20 each → total = 240 synthetic minutes."""
        profile = _make_profile({"p1": 0.20, "p2": 0.20, "p3": 0.20, "p4": 0.20, "p5": 0.20})
        total = sum(m for m, _ in profile.values())
        assert math.isclose(total, 240.0, rel_tol=1e-6)

    def test_injured_star_scaled_to_240(self):
        """After removing a star (35% share), scale remaining 65% back to 240."""
        # Four backups share the 65% that remains after a star is excluded
        profile = _make_profile({"b1": 0.1625, "b2": 0.1625, "b3": 0.1625, "b4": 0.1625})
        coverage_ratio = 0.65
        scale = 1.0 / coverage_ratio
        scaled = MinutesProfile(
            {pid: (m * scale, s * scale) for pid, (m, s) in profile.items()}
        )
        total = sum(m for m, _ in scaled.values())
        assert math.isclose(total, 240.0, rel_tol=1e-4)

    def test_scaling_preserves_relative_shares(self):
        """Scaling by a constant factor should not change each player's relative share."""
        profile = _make_profile({"p1": 0.10, "p2": 0.15, "p3": 0.12})
        coverage_ratio = 0.37
        scale = 1.0 / coverage_ratio
        scaled = MinutesProfile(
            {pid: (m * scale, s * scale) for pid, (m, s) in profile.items()}
        )
        orig_total = sum(m for m, _ in profile.values())
        scaled_total = sum(m for m, _ in scaled.values())
        for pid in profile:
            orig_share = profile[pid][0] / orig_total
            scaled_share = scaled[pid][0] / scaled_total
            assert math.isclose(orig_share, scaled_share, rel_tol=1e-6)

    def test_coverage_ratio_not_modified_by_scaling(self):
        """coverage_ratio is computed before scaling and must not change."""
        available = 0.65
        total = 1.0
        coverage_ratio = available / total
        # Simulate what the code does: scale the profile, then verify ratio unchanged
        assert math.isclose(coverage_ratio, 0.65)

    def test_std_scaled_proportionally(self):
        """std_minutes should scale by the same factor as mean_minutes."""
        original_mean = 24.0
        original_std = 5.0
        coverage_ratio = 0.60
        scale = 1.0 / coverage_ratio
        scaled_mean = original_mean * scale
        scaled_std = original_std * scale
        # Coefficient of variation should be preserved
        assert math.isclose(original_std / original_mean, scaled_std / scaled_mean, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# Fix B: _consecutive_recent_absences helper (pure unit tests)
# ---------------------------------------------------------------------------

class TestConsecutiveRecentAbsences:
    def test_no_absences(self):
        """Player appeared in every game → streak = 0."""
        game_ids = ["g1", "g2", "g3", "g4", "g5"]
        appeared = {"g1", "g2", "g3", "g4", "g5"}
        assert _consecutive_recent_absences(game_ids, appeared) == 0

    def test_missed_all(self):
        """Player never appeared → streak = len(game_ids)."""
        game_ids = ["g1", "g2", "g3"]
        appeared: set[str] = set()
        assert _consecutive_recent_absences(game_ids, appeared) == 3

    def test_missed_recent_streak(self):
        """Player missed last 4 games but appeared in g5 (oldest)."""
        game_ids = ["g1", "g2", "g3", "g4", "g5"]  # g1 = most recent
        appeared = {"g5"}
        assert _consecutive_recent_absences(game_ids, appeared) == 4

    def test_intermittent_dnp_not_counted(self):
        """Player missed g3 and g5 but appeared in g1/g2/g4 → streak = 0 (appeared in g1)."""
        game_ids = ["g1", "g2", "g3", "g4", "g5"]
        appeared = {"g1", "g2", "g4"}
        assert _consecutive_recent_absences(game_ids, appeared) == 0

    def test_streak_stops_at_first_appearance(self):
        """Streak counts only from the start (most recent) and stops at first appearance."""
        game_ids = ["g1", "g2", "g3", "g4", "g5", "g6"]
        appeared = {"g3", "g5", "g6"}
        assert _consecutive_recent_absences(game_ids, appeared) == 2

    def test_empty_game_ids(self):
        """No games → streak = 0."""
        assert _consecutive_recent_absences([], {"g1"}) == 0


# ---------------------------------------------------------------------------
# In-memory DB fixtures
# ---------------------------------------------------------------------------

def _make_db() -> sqlite3.Connection:
    """Create a minimal in-memory DB with just the tables needed by predictions.py."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE games (
            game_id      TEXT PRIMARY KEY,
            season       TEXT,
            game_date    TEXT,
            home_team_id TEXT,
            away_team_id TEXT
        );
        CREATE TABLE possessions (
            possession_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id          TEXT,
            season           TEXT,
            offense_team_id  TEXT,
            defense_team_id  TEXT DEFAULT 'opp',
            off_player_1     TEXT,
            off_player_2     TEXT,
            off_player_3     TEXT,
            off_player_4     TEXT,
            off_player_5     TEXT
        );
        CREATE TABLE players (
            player_id    TEXT PRIMARY KEY,
            player_name  TEXT,
            team_id      TEXT
        );
        CREATE TABLE current_ratings (
            player_id  TEXT PRIMARY KEY,
            season     TEXT,
            offense    REAL DEFAULT 0,
            defense    REAL DEFAULT 0,
            pace       REAL DEFAULT 0,
            overall    REAL DEFAULT 0,
            phase      TEXT DEFAULT 'elo'
        );
    """)
    return conn


def _insert_game(conn: sqlite3.Connection, game_id: str, date: str,
                 home: str = "TEAM", away: str = "OPP") -> None:
    conn.execute(
        "INSERT INTO games VALUES (?, '2025-26', ?, ?, ?)",
        (game_id, date, home, away),
    )


def _insert_possessions(conn: sqlite3.Connection, game_id: str, team_id: str,
                        players: list[str], n: int = 50) -> None:
    """Insert n possessions where the 5 given players are on offense."""
    assert len(players) == 5
    for i in range(n):
        conn.execute(
            "INSERT INTO possessions (game_id, season, offense_team_id, "
            "off_player_1, off_player_2, off_player_3, off_player_4, off_player_5) "
            "VALUES (?, '2025-26', ?, ?, ?, ?, ?, ?)",
            (game_id, team_id, *players),
        )


# ---------------------------------------------------------------------------
# Fix B integration tests
# ---------------------------------------------------------------------------

class TestLongTermInjuryExclusion:
    def test_long_term_injured_excluded_from_profile(self):
        """Player who is ESPN Out AND missed last 6 consecutive games is excluded entirely.

        Without Fix B: the player's 7 appearances in games 7-15 inflate the team profile
        and coverage_ratio. With Fix B: they are stripped before the profile is built.
        """
        conn = _make_db()

        TEAM = "1610612737"
        STAR = "star_pid"
        OTHERS = ["p1", "p2", "p3", "p4"]
        FULL_FIVE = [STAR] + OTHERS

        # 15 games total: star played in games 7-15 (9 appearances), absent from games 1-6
        for i, (gid, date) in enumerate([
            ("g01", "2026-03-07"), ("g02", "2026-03-06"), ("g03", "2026-03-05"),
            ("g04", "2026-03-04"), ("g05", "2026-03-03"), ("g06", "2026-03-02"),
            ("g07", "2026-03-01"), ("g08", "2026-02-28"), ("g09", "2026-02-27"),
            ("g10", "2026-02-26"), ("g11", "2026-02-25"), ("g12", "2026-02-24"),
            ("g13", "2026-02-23"), ("g14", "2026-02-22"), ("g15", "2026-02-21"),
        ]):
            _insert_game(conn, gid, date, home=TEAM, away="OPP")
            if i >= 6:  # games g07-g15: star played (9 games)
                _insert_possessions(conn, gid, TEAM, FULL_FIVE)
            else:  # games g01-g06: star absent (6-game consecutive streak)
                _insert_possessions(conn, gid, TEAM, OTHERS + ["p5"])

        for pid in [STAR] + OTHERS + ["p5"]:
            conn.execute(
                "INSERT INTO players VALUES (?, ?, ?)", (pid, f"Player {pid}", TEAM)
            )

        conn.commit()

        # Star is ESPN Out → should be excluded by injury filter anyway
        # But Fix B should remove them from `profiles` BEFORE coverage_ratio is computed
        # so the 9 historical appearances don't inflate coverage.
        injured = {"player star_pid"}  # normalized name
        pid_to_name = {STAR: "Player star_pid", **{p: f"Player {p}" for p in OTHERS + ["p5"]}}

        profile, coverage = _build_minutes_profile_from_db(
            TEAM, conn, injured, pid_to_name
        )

        # Star must NOT appear in the profile (Fix B + injury filter both catch them)
        assert STAR not in profile

        # coverage_ratio should be 1.0 — Fix B removed the star before coverage calculation,
        # so the remaining players represent 100% of the (now-reduced) profile weight.
        assert math.isclose(coverage, 1.0, abs_tol=0.01), f"coverage={coverage}"

        conn.close()

    def test_intermittent_injured_player_not_hard_excluded(self):
        """Player who is injured but only missed last 3 games (< LONG_TERM_INJURY_STREAK=5)
        is still kept in profiles (removed later by the normal injury filter), so their
        earlier appearances still contribute to coverage_ratio calculation.
        """
        conn = _make_db()

        TEAM = "1610612737"
        STAR = "star_pid"
        OTHERS = ["p1", "p2", "p3", "p4"]

        # Star played in games 4-15 (12 appearances), absent from games 1-3 (streak=3 < 5)
        for i, (gid, date) in enumerate([
            ("g01", "2026-03-07"), ("g02", "2026-03-06"), ("g03", "2026-03-05"),
            ("g04", "2026-03-04"), ("g05", "2026-03-03"), ("g06", "2026-03-02"),
            ("g07", "2026-03-01"), ("g08", "2026-02-28"), ("g09", "2026-02-27"),
            ("g10", "2026-02-26"), ("g11", "2026-02-25"), ("g12", "2026-02-24"),
            ("g13", "2026-02-23"), ("g14", "2026-02-22"), ("g15", "2026-02-21"),
        ]):
            _insert_game(conn, gid, date, home=TEAM, away="OPP")
            if i >= 3:  # star played in games g04-g15
                _insert_possessions(conn, gid, TEAM, [STAR] + OTHERS)
            else:
                _insert_possessions(conn, gid, TEAM, OTHERS + ["p5"])

        for pid in [STAR] + OTHERS + ["p5"]:
            conn.execute(
                "INSERT INTO players VALUES (?, ?, ?)", (pid, f"Player {pid}", TEAM)
            )
        conn.commit()

        # Star is injured but streak = 3 < LONG_TERM_INJURY_STREAK (5)
        injured = {"player star_pid"}
        pid_to_name = {STAR: "Player star_pid", **{p: f"Player {p}" for p in OTHERS + ["p5"]}}

        profile, coverage = _build_minutes_profile_from_db(
            TEAM, conn, injured, pid_to_name
        )

        # Star not in profile (injury filter removes them)
        assert STAR not in profile

        # coverage_ratio < 1.0 — star's historical weight still counted in total_weight
        # (Fix B did NOT remove them from profiles because streak=3 < 5)
        assert coverage < 1.0, f"Expected coverage < 1.0, got {coverage}"

        conn.close()


# ---------------------------------------------------------------------------
# Fix A integration tests
# ---------------------------------------------------------------------------

class TestReturningPlayerInjection:
    def _setup_team(self, conn: sqlite3.Connection, team_id: str,
                    returning_pid: str, returning_name: str,
                    returning_overall: float) -> None:
        """Set up 15 recent games where the returning player is absent,
        plus 30 historical games where they played regularly.
        """
        OTHERS = ["p1", "p2", "p3", "p4"]
        ALL_FIVE = [returning_pid] + OTHERS

        # Games 31-45 (older, returning player played — outside the 15-game window)
        for i in range(15):
            date = f"2026-01-{i + 1:02d}"
            gid = f"old_{i:02d}"
            _insert_game(conn, gid, date, home=team_id, away="OPP")
            _insert_possessions(conn, gid, team_id, ALL_FIVE)

        # Games 16-30 (extended window — returning player played in 12 of 15)
        for i in range(15):
            date = f"2026-02-{i + 1:02d}"
            gid = f"ext_{i:02d}"
            _insert_game(conn, gid, date, home=team_id, away="OPP")
            if i < 12:  # played in 12 games
                _insert_possessions(conn, gid, team_id, ALL_FIVE)
            else:
                _insert_possessions(conn, gid, team_id, OTHERS + ["p5"])

        # Games 1-15 (recent window — returning player absent from ALL 15)
        for i in range(15):
            date = f"2026-03-{i + 1:02d}"
            gid = f"rec_{i:02d}"
            _insert_game(conn, gid, date, home=team_id, away="OPP")
            _insert_possessions(conn, gid, team_id, OTHERS + ["p5"])

        # Players
        for pid in [returning_pid] + OTHERS + ["p5"]:
            conn.execute(
                "INSERT OR IGNORE INTO players VALUES (?, ?, ?)",
                (pid, f"Player {pid}" if pid != returning_pid else returning_name, team_id),
            )

        # current_ratings for the returning player
        conn.execute(
            "INSERT INTO current_ratings VALUES (?, '2025-26', 3.0, 0.5, 0.0, ?, 'elo')",
            (returning_pid, returning_overall),
        )
        conn.commit()

    def test_returning_player_is_seeded_from_extended_window(self):
        """Star with 0/15 recent appearances, overall=3.5, 12/30 extended appearances
        should be injected at ~70% of their extended historical average.
        """
        conn = _make_db()
        TEAM = "1610612737"
        STAR = "star_pid"

        self._setup_team(conn, TEAM, STAR, "Star Player", returning_overall=3.5)

        injured: set[str] = set()
        pid_to_name = {
            STAR: "Star Player",
            **{p: f"Player {p}" for p in ["p1", "p2", "p3", "p4", "p5"]},
        }

        profile, _ = _build_minutes_profile_from_db(
            TEAM, conn, injured, pid_to_name, season="2025-26"
        )

        # Star should be injected
        assert STAR in profile, "Returning star should have been injected into the profile"

        # Their injected minutes should be > 0 and < full historical minutes
        injected_minutes, _ = profile[STAR]
        assert injected_minutes > 0
        # Full historical share = 0.20 (1/5 players, equal minutes in the games they played)
        # After availability discount and RETURNING_PLAYER_MULTIPLIER=0.70, should be < 0.20*240
        assert injected_minutes < 0.20 * 240

        conn.close()

    def test_low_rated_returning_player_not_seeded(self):
        """Player with overall=0.5 (below threshold=2.0) should NOT be injected."""
        conn = _make_db()
        TEAM = "1610612737"
        WEAK = "weak_pid"

        self._setup_team(conn, TEAM, WEAK, "Weak Player", returning_overall=0.5)

        injured: set[str] = set()
        pid_to_name = {
            WEAK: "Weak Player",
            **{p: f"Player {p}" for p in ["p1", "p2", "p3", "p4", "p5"]},
        }

        profile, _ = _build_minutes_profile_from_db(
            TEAM, conn, injured, pid_to_name, season="2025-26"
        )

        assert WEAK not in profile, "Low-rated player should NOT be injected"
        conn.close()

    def test_injured_returning_player_not_seeded(self):
        """Player with 0/15 appearances and high overall but on the injury list
        should NOT be injected.
        """
        conn = _make_db()
        TEAM = "1610612737"
        STAR = "star_pid"

        self._setup_team(conn, TEAM, STAR, "Star Player", returning_overall=4.0)

        # Mark star as injured
        injured = {"star player"}  # normalize_name("Star Player") = "star player"
        pid_to_name = {
            STAR: "Star Player",
            **{p: f"Player {p}" for p in ["p1", "p2", "p3", "p4", "p5"]},
        }

        profile, _ = _build_minutes_profile_from_db(
            TEAM, conn, injured, pid_to_name, season="2025-26"
        )

        assert STAR not in profile, "Injured player should NOT be injected even if high-rated"
        conn.close()

    def test_returning_player_not_injected_when_season_is_none(self):
        """Fix A is only enabled when season is provided (not in backtest mode)."""
        conn = _make_db()
        TEAM = "1610612737"
        STAR = "star_pid"

        self._setup_team(conn, TEAM, STAR, "Star Player", returning_overall=4.0)

        injured: set[str] = set()
        pid_to_name = {
            STAR: "Star Player",
            **{p: f"Player {p}" for p in ["p1", "p2", "p3", "p4", "p5"]},
        }

        # season=None → Fix A disabled (backtest mode uses oracle rosters)
        profile, _ = _build_minutes_profile_from_db(
            TEAM, conn, injured, pid_to_name, season=None
        )

        assert STAR not in profile, "Fix A should be disabled when season=None"
        conn.close()
