"""
P6: Elo model — pure functions for per-possession Elo updates.

No database I/O. All data is passed in as arguments; results are returned or
mutated in place. DB reads/writes belong in the nightly_job.py orchestrator.

State representation
--------------------
current_elos: dict[str, dict] mapping player_id to:
    {
        'rapm_offense' : float,   # RAPM base (pts per 100 above league avg)
        'rapm_defense' : float,   # RAPM base (pts per 100 allowed above avg, positive = bad)
        'rapm_pace'    : float,   # RAPM base (possessions per 48 above avg)
        'offense_delta': float,   # cumulative Elo delta (offense)
        'defense_delta': float,   # cumulative Elo delta (defense)
        'pace_delta'   : float,   # cumulative Elo delta (pace)
    }

All deltas start at 0.0. current_ratings = RAPM base + Elo delta.

Public API
----------
    sigmoid(x)               -> float
    elo_update(...)          -> None   (mutates current_elos in place)
    replay_game_elo(...)     -> set[str]
"""

import math

# Default state for a player with no prior data (cold start at league average).
_COLD_START: dict = {
    "rapm_offense": 0.0,
    "rapm_defense": 0.0,
    "rapm_pace": 0.0,
    "offense_delta": 0.0,
    "defense_delta": 0.0,
    "pace_delta": 0.0,
}


def sigmoid(x: float) -> float:
    """Standard logistic function. Used for calibration analysis."""
    return 1.0 / (1.0 + math.exp(-x))


def elo_update(
    possession: dict,
    current_elos: dict,
    league_avg_ppp: float,
    K: float = 2.0,
) -> None:
    """
    Apply one possession's Elo update. Mutates current_elos in place.

    Expected PPP is computed from the average of the 5 offensive players'
    combined ratings (RAPM base + Elo delta) minus the average of the 5
    defensive players' combined ratings, added on top of league average:

        avg_off        = mean(rapm_offense + offense_delta for 5 off players)
        avg_def        = mean(rapm_defense + defense_delta for 5 def players)
        expected_ppp   = league_avg_ppp + (avg_off - avg_def) / 100

    Surprise = possession['points_scored'] - expected_ppp

    Updates (K divided equally across 5 players per side):
        offensive players: offense_delta += (K/5) * surprise
        defensive players: defense_delta -= (K/5) * surprise

    Players not in current_elos are cold-started at league average (all zeros).

    Args:
        possession:     Dict with keys off_player_1..5, def_player_1..5,
                        and points_scored (raw points, e.g. 0, 1, 2, or 3).
        current_elos:   Mutable state dict (player_id -> ratings dict).
        league_avg_ppp: League average points per possession (e.g. ~1.14).
        K:              Elo K-factor (total per possession, split across 5 players).
    """
    off_players = [possession[f"off_player_{i}"] for i in range(1, 6)]
    def_players = [possession[f"def_player_{i}"] for i in range(1, 6)]

    # Cold-start any players not yet seen
    for pid in off_players + def_players:
        if pid not in current_elos:
            current_elos[pid] = dict(_COLD_START)

    avg_off = sum(
        current_elos[p]["rapm_offense"] + current_elos[p]["offense_delta"]
        for p in off_players
    ) / 5.0

    avg_def = sum(
        current_elos[p]["rapm_defense"] + current_elos[p]["defense_delta"]
        for p in def_players
    ) / 5.0

    expected_ppp = league_avg_ppp + (avg_off - avg_def) / 100.0
    surprise = possession["points_scored"] - expected_ppp

    k_per_player = K / 5.0
    for pid in off_players:
        current_elos[pid]["offense_delta"] += k_per_player * surprise
    for pid in def_players:
        current_elos[pid]["defense_delta"] -= k_per_player * surprise


def replay_game_elo(
    possessions: list[dict],
    current_elos: dict,
    league_avg_ppp: float,
    league_avg_pace: float,
    game_pace: float | None,
    K: float = 2.0,
    K_pace: float = 1.0,
) -> set[str]:
    """
    Replay all possessions in a game, updating Elo state in place.

    Per-possession Elo update:
        Calls elo_update() for each possession in the order provided.
        Possession order must be chronological (by possession_number).

    Game-level pace Elo update (applied once after all possessions):
        avg_pace_rating = mean(rapm_pace + pace_delta for all unique players)
        expected_pace   = league_avg_pace + avg_pace_rating
        pace_surprise   = game_pace - expected_pace
        each unique player: pace_delta += (K_pace / n_unique_players) * pace_surprise

    Pace update is skipped if game_pace is None.

    Args:
        possessions:     List of possession dicts in chronological order.
                         Each must have off_player_1..5, def_player_1..5, points_scored.
        current_elos:    Mutable state dict (mutated in place).
        league_avg_ppp:  League average points per possession.
        league_avg_pace: League average possessions per 48 minutes.
        game_pace:       Actual pace for this game (possessions per 48 min),
                         or None if unavailable (pace update is skipped).
        K:               Elo K-factor for offense/defense updates.
        K_pace:          Elo K-factor for the game-level pace update.

    Returns:
        Set of player IDs who appeared in any possession of this game.
    """
    appeared: set[str] = set()

    for possession in possessions:
        elo_update(possession, current_elos, league_avg_ppp, K)
        for i in range(1, 6):
            appeared.add(possession[f"off_player_{i}"])
            appeared.add(possession[f"def_player_{i}"])

    # Game-level pace update
    if appeared and game_pace is not None:
        n = len(appeared)
        avg_pace_rating = sum(
            current_elos[p]["rapm_pace"] + current_elos[p]["pace_delta"]
            for p in appeared
        ) / n
        expected_pace = league_avg_pace + avg_pace_rating
        pace_surprise = game_pace - expected_pace
        k_pace_per_player = K_pace / n
        for pid in appeared:
            current_elos[pid]["pace_delta"] += k_pace_per_player * pace_surprise

    return appeared
