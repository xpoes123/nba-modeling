"""Unit tests for downstream/team_ratings.py (pure functions)."""
import pytest

from downstream.team_ratings import (
    PlayerRating,
    TeamRatings,
    build_name_to_id,
    compute_raw_margin,
    compute_team_ratings,
    normalize_name,
    shares_from_minutes,
)


def _rating(off: float, def_: float, pace: float) -> PlayerRating:
    return PlayerRating(player_id="x", offense=off, defense=def_, pace=pace)


class TestNormalizeName:
    def test_lowercase(self):
        assert normalize_name("LeBron James") == "lebron james"

    def test_strips_accents(self):
        assert normalize_name("Luka Dončić") == "luka doncic"

    def test_removes_jr(self):
        assert normalize_name("Jabari Smith Jr.") == "jabari smith"

    def test_removes_iii(self):
        assert normalize_name("Kelly Oubre III") == "kelly oubre"

    def test_already_clean(self):
        assert normalize_name("steph curry") == "steph curry"


class TestBuildNameToId:
    def test_basic(self):
        players = [
            {"player_id": "1", "player_name": "Shai Gilgeous-Alexander"},
            {"player_id": "2", "player_name": "Luka Dončić"},
        ]
        lookup = build_name_to_id(players)
        assert lookup["shai gilgeous-alexander"] == "1"
        assert lookup["luka doncic"] == "2"


class TestSharesFromMinutes:
    def test_sums_to_one(self):
        mins = {"a": 30.0, "b": 20.0, "c": 10.0}
        shares = shares_from_minutes(mins)
        assert sum(shares.values()) == pytest.approx(1.0)

    def test_proportional(self):
        mins = {"a": 40.0, "b": 40.0}
        shares = shares_from_minutes(mins)
        assert shares["a"] == pytest.approx(0.5)

    def test_zero_total_returns_zeros(self):
        shares = shares_from_minutes({"a": 0.0, "b": 0.0})
        assert shares["a"] == pytest.approx(0.0)


class TestComputeTeamRatings:
    def test_single_player_full_share(self):
        ratings = {"p1": _rating(5.0, 2.0, 1.0)}
        shares = {"p1": 1.0}
        result = compute_team_ratings(ratings, shares)
        assert result["offense"] == pytest.approx(5.0)
        assert result["defense"] == pytest.approx(2.0)
        assert result["pace"] == pytest.approx(1.0)

    def test_equal_weight_two_players(self):
        ratings = {
            "p1": _rating(4.0, 1.0, 0.5),
            "p2": _rating(2.0, 3.0, -0.5),
        }
        shares = {"p1": 0.5, "p2": 0.5}
        result = compute_team_ratings(ratings, shares)
        assert result["offense"] == pytest.approx(3.0)
        assert result["defense"] == pytest.approx(2.0)
        assert result["pace"] == pytest.approx(0.0)

    def test_missing_player_treated_as_league_average(self):
        ratings = {"p1": _rating(4.0, 2.0, 1.0)}
        shares = {"p1": 0.5, "p_unknown": 0.5}
        result = compute_team_ratings(ratings, shares)
        # p_unknown has 0.0 ratings, so average is (4.0*0.5 + 0.0*0.5) / 1.0 = 2.0
        assert result["offense"] == pytest.approx(2.0)

    def test_empty_returns_zeros(self):
        result = compute_team_ratings({}, {})
        assert result["offense"] == pytest.approx(0.0)


class TestComputeRawMargin:
    def test_equal_teams_gives_zero(self):
        team = TeamRatings(offense=3.0, defense=3.0, pace=0.0)
        margin = compute_raw_margin(team, team, league_avg_ppp=1.12, league_avg_pace=100.0)
        assert margin == pytest.approx(0.0)

    def test_better_home_offense_positive_margin(self):
        home = TeamRatings(offense=5.0, defense=0.0, pace=0.0)
        away = TeamRatings(offense=0.0, defense=0.0, pace=0.0)
        margin = compute_raw_margin(home, away, league_avg_ppp=1.12, league_avg_pace=100.0)
        # home_ppp = 1.12 + (5 - 0)/100 = 1.17, away_ppp = 1.12 + (0 - 0)/100 = 1.12
        # margin = (1.17 - 1.12) * 100 = 5.0
        assert margin == pytest.approx(5.0)

    def test_worse_defense_hurts_home(self):
        home = TeamRatings(offense=0.0, defense=5.0, pace=0.0)
        away = TeamRatings(offense=0.0, defense=0.0, pace=0.0)
        margin = compute_raw_margin(home, away, league_avg_ppp=1.12, league_avg_pace=100.0)
        # home allows more → home_ppp unchanged, but away_ppp increases
        # away_ppp = 1.12 + (0 - 5)/100 = 1.07? No: away offense vs home DEFENSE
        # away_ppp = league_avg + (away_off - home_def)/100 = 1.12 + (0 - 5)/100 = 1.07
        # home_ppp = league_avg + (home_off - away_def)/100 = 1.12 + (0 - 0)/100 = 1.12
        # margin = (1.12 - 1.07) * 100 = 5.0
        assert margin == pytest.approx(5.0)

    def test_pace_adjustment_increases_magnitude(self):
        home = TeamRatings(offense=5.0, defense=0.0, pace=5.0)
        away = TeamRatings(offense=0.0, defense=0.0, pace=0.0)
        margin_fast = compute_raw_margin(home, away, league_avg_ppp=1.12, league_avg_pace=100.0)
        home_slow = TeamRatings(offense=5.0, defense=0.0, pace=-5.0)
        margin_slow = compute_raw_margin(home_slow, away, league_avg_ppp=1.12, league_avg_pace=100.0)
        # Faster pace → more possessions → larger expected margin
        assert margin_fast > margin_slow
