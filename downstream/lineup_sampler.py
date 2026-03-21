"""Pure Monte Carlo lineup simulation.

No DB I/O — accepts player data as arguments, returns simulation results.
"""
import numpy as np

from downstream.team_ratings import (
    PlayerRating,
    TeamRatings,
    compute_raw_margin,
    compute_team_ratings,
    shares_from_minutes,
)


class MinutesProfile(dict):
    """player_id → (mean_minutes, std_minutes)"""


class SimulationResult:
    """Summary of Monte Carlo simulation for a single game."""

    __slots__ = (
        "mean_margin",
        "std_margin",
        "margins",
    )

    def __init__(self, margins: np.ndarray) -> None:
        self.margins = margins
        self.mean_margin: float = float(np.mean(margins))
        self.std_margin: float = float(np.std(margins))


def simulate_game(
    home_minutes: MinutesProfile,
    away_minutes: MinutesProfile,
    home_player_ratings: dict[str, PlayerRating],
    away_player_ratings: dict[str, PlayerRating],
    league_avg_ppp: float,
    league_avg_pace: float,
    n_simulations: int = 1000,
    rng: np.random.Generator | None = None,
) -> SimulationResult:
    """Monte Carlo simulation of a game's point margin.

    For each simulation:
    1. Sample each player's minutes from Normal(μ, max(σ, 1.0)), clipped to [0, 48].
    2. Normalize minutes to possession shares.
    3. Compute weighted team ratings.
    4. Compute raw margin via compute_raw_margin().

    Args:
        home_minutes: player_id → (mean_mins, std_mins) for home roster
        away_minutes: player_id → (mean_mins, std_mins) for away roster
        home_player_ratings: player_id → PlayerRating for home roster
        away_player_ratings: player_id → PlayerRating for away roster
        league_avg_ppp: league average points per possession
        league_avg_pace: league average possessions per team per game
        n_simulations: number of Monte Carlo draws
        rng: optional numpy random generator (for reproducibility in tests)

    Returns:
        SimulationResult with margins array, mean, and std.
    """
    if rng is None:
        rng = np.random.default_rng()

    home_players = list(home_minutes.keys())
    home_means = np.array([home_minutes[p][0] for p in home_players])
    home_stds = np.maximum(np.array([home_minutes[p][1] for p in home_players]), 1.0)

    away_players = list(away_minutes.keys())
    away_means = np.array([away_minutes[p][0] for p in away_players])
    away_stds = np.maximum(np.array([away_minutes[p][1] for p in away_players]), 1.0)

    # Sample all simulations at once: shape (n_simulations, n_players)
    home_sampled = np.clip(
        rng.normal(home_means, home_stds, size=(n_simulations, len(home_players))), 0, 48
    )
    away_sampled = np.clip(
        rng.normal(away_means, away_stds, size=(n_simulations, len(away_players))), 0, 48
    )

    margins = np.empty(n_simulations)

    for i in range(n_simulations):
        home_mins_i = dict(zip(home_players, home_sampled[i]))
        away_mins_i = dict(zip(away_players, away_sampled[i]))

        home_shares = shares_from_minutes(home_mins_i)
        away_shares = shares_from_minutes(away_mins_i)

        home_team = compute_team_ratings(home_player_ratings, home_shares)
        away_team = compute_team_ratings(away_player_ratings, away_shares)

        margins[i] = compute_raw_margin(
            home_team, away_team, league_avg_ppp, league_avg_pace
        )

    return SimulationResult(margins)


def apply_calibration(
    raw_margin: float,
    alpha: float,
    beta_hca: float,
    beta_b2b_home: float,
    beta_b2b_away: float,
    home_b2b: bool = False,
    away_b2b: bool = False,
) -> float:
    """Apply calibration coefficients to a raw margin.

    calibrated_margin = α * raw_margin + β_hca + β_b2b_home * home_b2b + β_b2b_away * away_b2b

    β_hca is always applied (home court advantage baseline).
    β_b2b_home is negative (fatigue penalty for home team on B2B).
    β_b2b_away is negative (fatigue penalty for away team on B2B, so subtracted).
    """
    return (
        alpha * raw_margin
        + beta_hca
        + beta_b2b_home * int(home_b2b)
        + beta_b2b_away * int(away_b2b)
    )


def margin_to_win_prob(margin: float, sigma: float) -> float:
    """Convert expected margin to P(home wins) using normal CDF.

    Args:
        margin: expected home margin (positive = home favored)
        sigma: total uncertainty (calibration residual σ combined with Monte Carlo σ)

    Returns:
        Probability home team wins, in [0, 1].
    """
    from scipy.stats import norm

    if sigma <= 0:
        return 1.0 if margin > 0 else (0.5 if margin == 0 else 0.0)
    return float(norm.cdf(margin / sigma))
