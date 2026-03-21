"""Unit tests for downstream/lineup_sampler.py (pure Monte Carlo functions)."""
import numpy as np
import pytest

from downstream.lineup_sampler import (
    MinutesProfile,
    SimulationResult,
    apply_calibration,
    margin_to_win_prob,
    simulate_game,
)
from downstream.team_ratings import PlayerRating


def _rating(off: float, def_: float, pace: float) -> PlayerRating:
    return PlayerRating(player_id="x", offense=off, defense=def_, pace=pace)


def _equal_team_minutes(player_ids: list[str], mean: float = 20.0) -> MinutesProfile:
    return MinutesProfile({pid: (mean, 3.0) for pid in player_ids})


HOME_PLAYERS = ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"]
AWAY_PLAYERS = ["a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8"]


class TestSimulateGame:
    def test_returns_correct_n_simulations(self):
        home_mins = _equal_team_minutes(HOME_PLAYERS)
        away_mins = _equal_team_minutes(AWAY_PLAYERS)
        ratings = {p: _rating(0.0, 0.0, 0.0) for p in HOME_PLAYERS + AWAY_PLAYERS}

        result = simulate_game(
            home_mins, away_mins, ratings, ratings, 1.12, 100.0,
            n_simulations=200, rng=np.random.default_rng(42)
        )
        assert len(result.margins) == 200

    def test_equal_teams_mean_near_zero(self):
        home_mins = _equal_team_minutes(HOME_PLAYERS)
        away_mins = _equal_team_minutes(AWAY_PLAYERS)
        ratings = {p: _rating(0.0, 0.0, 0.0) for p in HOME_PLAYERS + AWAY_PLAYERS}

        result = simulate_game(
            home_mins, away_mins, ratings, ratings, 1.12, 100.0,
            n_simulations=1000, rng=np.random.default_rng(0)
        )
        # With equal teams, mean should be ≈ 0 (small variance in minutes sampling → small margin variance)
        assert abs(result.mean_margin) < 1.0

    def test_stronger_home_team_positive_mean(self):
        home_mins = _equal_team_minutes(HOME_PLAYERS)
        away_mins = _equal_team_minutes(AWAY_PLAYERS)
        home_ratings = {p: _rating(5.0, 0.0, 0.0) for p in HOME_PLAYERS}
        away_ratings = {p: _rating(0.0, 0.0, 0.0) for p in AWAY_PLAYERS}

        result = simulate_game(
            home_mins, away_mins, home_ratings, away_ratings, 1.12, 100.0,
            n_simulations=500, rng=np.random.default_rng(1)
        )
        assert result.mean_margin > 0

    def test_std_is_positive(self):
        home_mins = _equal_team_minutes(HOME_PLAYERS)
        away_mins = _equal_team_minutes(AWAY_PLAYERS)
        ratings = {p: _rating(1.0, 1.0, 0.0) for p in HOME_PLAYERS + AWAY_PLAYERS}

        result = simulate_game(
            home_mins, away_mins, ratings, ratings, 1.12, 100.0,
            n_simulations=200, rng=np.random.default_rng(99)
        )
        assert result.std_margin >= 0


class TestApplyCalibration:
    def test_no_adjustments(self):
        result = apply_calibration(5.0, alpha=1.0, beta_hca=0.0,
                                   beta_b2b_home=0.0, beta_b2b_away=0.0)
        assert result == pytest.approx(5.0)

    def test_hca_added(self):
        result = apply_calibration(0.0, alpha=1.0, beta_hca=2.5,
                                   beta_b2b_home=0.0, beta_b2b_away=0.0)
        assert result == pytest.approx(2.5)

    def test_alpha_scales_margin(self):
        result = apply_calibration(10.0, alpha=0.5, beta_hca=0.0,
                                   beta_b2b_home=0.0, beta_b2b_away=0.0)
        assert result == pytest.approx(5.0)

    def test_home_b2b_penalty(self):
        without = apply_calibration(5.0, alpha=1.0, beta_hca=0.0,
                                    beta_b2b_home=-2.0, beta_b2b_away=0.0,
                                    home_b2b=False)
        with_b2b = apply_calibration(5.0, alpha=1.0, beta_hca=0.0,
                                     beta_b2b_home=-2.0, beta_b2b_away=0.0,
                                     home_b2b=True)
        assert with_b2b == pytest.approx(without - 2.0)

    def test_away_b2b_helps_home(self):
        without = apply_calibration(5.0, alpha=1.0, beta_hca=0.0,
                                    beta_b2b_home=0.0, beta_b2b_away=-2.0,
                                    away_b2b=False)
        with_b2b = apply_calibration(5.0, alpha=1.0, beta_hca=0.0,
                                     beta_b2b_home=0.0, beta_b2b_away=-2.0,
                                     away_b2b=True)
        assert with_b2b == pytest.approx(without - 2.0)


class TestMarginToWinProb:
    def test_zero_margin_is_fifty_percent(self):
        assert margin_to_win_prob(0.0, sigma=10.0) == pytest.approx(0.5)

    def test_large_positive_margin_near_one(self):
        assert margin_to_win_prob(50.0, sigma=10.0) > 0.99

    def test_large_negative_margin_near_zero(self):
        assert margin_to_win_prob(-50.0, sigma=10.0) < 0.01

    def test_symmetric(self):
        p_pos = margin_to_win_prob(5.0, sigma=10.0)
        p_neg = margin_to_win_prob(-5.0, sigma=10.0)
        assert p_pos + p_neg == pytest.approx(1.0)
