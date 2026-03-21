"""
Unit tests for models/elo.py — pure functions only, no DB required.
"""

import math
import pytest

from models.elo import sigmoid, elo_update, replay_game_elo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OFF = ["O1", "O2", "O3", "O4", "O5"]
DEF = ["D1", "D2", "D3", "D4", "D5"]


def _make_elos(player_ids: list[str], rapm_off: float = 0.0, rapm_def: float = 0.0, rapm_pace: float = 0.0) -> dict:
    """Create a current_elos dict with all deltas zeroed."""
    return {
        pid: {
            "rapm_offense": rapm_off,
            "rapm_defense": rapm_def,
            "rapm_pace": rapm_pace,
            "offense_delta": 0.0,
            "defense_delta": 0.0,
            "pace_delta": 0.0,
        }
        for pid in player_ids
    }


def _make_possession(
    off_players: list[str],
    def_players: list[str],
    points_scored: int,
) -> dict:
    p = {f"off_player_{i + 1}": pid for i, pid in enumerate(off_players)}
    p.update({f"def_player_{i + 1}": pid for i, pid in enumerate(def_players)})
    p["points_scored"] = points_scored
    return p


# ---------------------------------------------------------------------------
# sigmoid
# ---------------------------------------------------------------------------

def test_sigmoid_midpoint():
    assert sigmoid(0.0) == pytest.approx(0.5)


def test_sigmoid_large_positive():
    assert sigmoid(100.0) == pytest.approx(1.0, abs=1e-6)


def test_sigmoid_large_negative():
    assert sigmoid(-100.0) == pytest.approx(0.0, abs=1e-6)


def test_sigmoid_symmetry():
    assert sigmoid(2.0) + sigmoid(-2.0) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# elo_update
# ---------------------------------------------------------------------------

def test_elo_update_zero_surprise_no_delta_change():
    """When actual PPP equals expected PPP, deltas should not change."""
    league_avg_ppp = 1.1
    # All players at league average RAPM → expected = league_avg_ppp
    current_elos = _make_elos(OFF + DEF)
    possession = _make_possession(OFF, DEF, points_scored=0)
    # actual_ppp = 0, expected = 1.1, surprise = -1.1 — not zero surprise.
    # To get zero surprise: actual must equal expected = league_avg_ppp
    # points_scored is an integer, so use a custom expected instead.
    # Set RAPM so expected = 1.0, then score 1 point.
    # avg_off = 5.0, avg_def = 5.0 → expected = 1.1 + (5.0 - 5.0)/100 = 1.1
    # score 1.1 is not integer — instead test that surprise is computed correctly.
    # Easier: set league_avg = 0, RAPM off=+50, def=+50 → expected=0+(50-50)/100=0
    # then score 0 → surprise = 0 → no delta change.
    current_elos = _make_elos(OFF + DEF, rapm_off=50.0, rapm_def=50.0)
    possession = _make_possession(OFF, DEF, points_scored=0)

    elo_update(possession, current_elos, league_avg_ppp=0.0, K=2.0)

    for pid in OFF:
        assert current_elos[pid]["offense_delta"] == pytest.approx(0.0)
    for pid in DEF:
        assert current_elos[pid]["defense_delta"] == pytest.approx(0.0)


def test_elo_update_positive_surprise_offense_up_defense_down():
    """Offense scores more than expected → offense deltas increase, defense deltas decrease."""
    current_elos = _make_elos(OFF + DEF)
    # expected_ppp = 1.0 (league avg, all RAPM=0)
    # actual = 3 (a 3-pointer) → surprise = 2.0
    possession = _make_possession(OFF, DEF, points_scored=3)

    before_off = [current_elos[p]["offense_delta"] for p in OFF]
    before_def = [current_elos[p]["defense_delta"] for p in DEF]

    elo_update(possession, current_elos, league_avg_ppp=1.0, K=2.0)

    for pid, before in zip(OFF, before_off):
        assert current_elos[pid]["offense_delta"] > before
    for pid, before in zip(DEF, before_def):
        assert current_elos[pid]["defense_delta"] < before


def test_elo_update_negative_surprise_offense_down_defense_up():
    """Offense scores less than expected → offense deltas decrease, defense deltas increase."""
    current_elos = _make_elos(OFF + DEF)
    # expected_ppp = 1.0, actual = 0 → surprise = -1.0
    possession = _make_possession(OFF, DEF, points_scored=0)

    elo_update(possession, current_elos, league_avg_ppp=1.0, K=2.0)

    for pid in OFF:
        assert current_elos[pid]["offense_delta"] < 0.0
    for pid in DEF:
        assert current_elos[pid]["defense_delta"] > 0.0


def test_elo_update_k_divided_equally_among_5():
    """Each player's delta should be exactly K/5 * surprise."""
    current_elos = _make_elos(OFF + DEF)
    K = 2.0
    league_avg_ppp = 1.0
    # actual=3, expected=1.0, surprise=2.0, k_per_player=0.4
    possession = _make_possession(OFF, DEF, points_scored=3)

    elo_update(possession, current_elos, league_avg_ppp=league_avg_ppp, K=K)

    expected_off_delta = (K / 5) * (3 - league_avg_ppp)
    expected_def_delta = -(K / 5) * (3 - league_avg_ppp)
    for pid in OFF:
        assert current_elos[pid]["offense_delta"] == pytest.approx(expected_off_delta)
    for pid in DEF:
        assert current_elos[pid]["defense_delta"] == pytest.approx(expected_def_delta)


def test_elo_update_cold_starts_unknown_players():
    """Players not in current_elos should be added with cold-start values."""
    current_elos = {}
    possession = _make_possession(OFF, DEF, points_scored=1)

    elo_update(possession, current_elos, league_avg_ppp=1.0, K=2.0)

    assert len(current_elos) == 10
    for pid in OFF + DEF:
        assert pid in current_elos
        # rapm fields initialized to 0
        assert current_elos[pid]["rapm_offense"] == 0.0
        assert current_elos[pid]["rapm_defense"] == 0.0


def test_elo_update_uses_rapm_base_for_expected():
    """High-RAPM offense vs low-RAPM defense: expected PPP should exceed league avg."""
    # avg_off = 10 (pts/100 above avg), avg_def = -10 → expected += (10 - (-10))/100 = +0.2
    current_elos = _make_elos(OFF, rapm_off=10.0) | _make_elos(DEF, rapm_def=-10.0)
    league_avg_ppp = 1.0
    # expected = 1.0 + (10 - (-10))/100 = 1.2
    # actual = 1 → surprise = 1 - 1.2 = -0.2
    possession = _make_possession(OFF, DEF, points_scored=1)

    elo_update(possession, current_elos, league_avg_ppp=league_avg_ppp, K=2.0)

    # surprise is negative → offense delta should decrease
    for pid in OFF:
        assert current_elos[pid]["offense_delta"] < 0.0


def test_elo_update_accumulates_across_possessions():
    """Calling elo_update multiple times accumulates deltas."""
    current_elos = _make_elos(OFF + DEF)
    possession = _make_possession(OFF, DEF, points_scored=3)

    elo_update(possession, current_elos, league_avg_ppp=1.0, K=2.0)
    delta_after_1 = current_elos[OFF[0]]["offense_delta"]

    elo_update(possession, current_elos, league_avg_ppp=1.0, K=2.0)
    delta_after_2 = current_elos[OFF[0]]["offense_delta"]

    # Second update should add to the first (though surprise changes slightly
    # due to updated deltas affecting expected_ppp — just check direction)
    assert delta_after_2 > delta_after_1


# ---------------------------------------------------------------------------
# replay_game_elo
# ---------------------------------------------------------------------------

def test_replay_game_elo_returns_all_appeared_players():
    """All 10 unique players in the possessions should appear in the returned set."""
    current_elos = _make_elos(OFF + DEF)
    possessions = [_make_possession(OFF, DEF, points_scored=1)]

    appeared = replay_game_elo(
        possessions, current_elos,
        league_avg_ppp=1.0, league_avg_pace=95.0, game_pace=100.0,
    )

    assert appeared == set(OFF + DEF)


def test_replay_game_elo_multiple_possessions_same_players():
    current_elos = _make_elos(OFF + DEF)
    possessions = [
        _make_possession(OFF, DEF, points_scored=2),
        _make_possession(OFF, DEF, points_scored=0),
        _make_possession(DEF, OFF, points_scored=3),
    ]

    appeared = replay_game_elo(
        possessions, current_elos,
        league_avg_ppp=1.0, league_avg_pace=95.0, game_pace=95.0,
    )

    assert appeared == set(OFF + DEF)


def test_replay_game_elo_pace_update_fast_game():
    """In a faster-than-expected game, pace_delta should increase for all players."""
    current_elos = _make_elos(OFF + DEF, rapm_pace=0.0)
    possessions = [_make_possession(OFF, DEF, points_scored=1)]
    league_avg_pace = 95.0
    game_pace = 105.0  # much faster than expected

    replay_game_elo(
        possessions, current_elos,
        league_avg_ppp=1.0, league_avg_pace=league_avg_pace, game_pace=game_pace,
    )

    for pid in OFF + DEF:
        assert current_elos[pid]["pace_delta"] > 0.0


def test_replay_game_elo_pace_update_slow_game():
    """In a slower-than-expected game, pace_delta should decrease for all players."""
    current_elos = _make_elos(OFF + DEF, rapm_pace=0.0)
    possessions = [_make_possession(OFF, DEF, points_scored=1)]
    league_avg_pace = 95.0
    game_pace = 85.0  # much slower than expected

    replay_game_elo(
        possessions, current_elos,
        league_avg_ppp=1.0, league_avg_pace=league_avg_pace, game_pace=game_pace,
    )

    for pid in OFF + DEF:
        assert current_elos[pid]["pace_delta"] < 0.0


def test_replay_game_elo_none_game_pace_skips_pace_update():
    """When game_pace is None, pace_delta should remain 0 for all players."""
    current_elos = _make_elos(OFF + DEF)
    possessions = [_make_possession(OFF, DEF, points_scored=1)]

    replay_game_elo(
        possessions, current_elos,
        league_avg_ppp=1.0, league_avg_pace=95.0, game_pace=None,
    )

    for pid in OFF + DEF:
        assert current_elos[pid]["pace_delta"] == pytest.approx(0.0)


def test_replay_game_elo_empty_possessions_returns_empty_set():
    current_elos = _make_elos(OFF + DEF)

    appeared = replay_game_elo(
        [], current_elos,
        league_avg_ppp=1.0, league_avg_pace=95.0, game_pace=100.0,
    )

    assert appeared == set()


def test_replay_game_elo_multiple_lineups():
    """Players from different lineups across possessions all appear in the set."""
    off2 = ["X1", "X2", "X3", "X4", "X5"]
    def2 = ["Y1", "Y2", "Y3", "Y4", "Y5"]
    current_elos = _make_elos(OFF + DEF + off2 + def2)

    possessions = [
        _make_possession(OFF, DEF, points_scored=2),
        _make_possession(off2, def2, points_scored=0),
    ]

    appeared = replay_game_elo(
        possessions, current_elos,
        league_avg_ppp=1.0, league_avg_pace=95.0, game_pace=95.0,
    )

    assert appeared == set(OFF + DEF + off2 + def2)


def test_replay_game_elo_pace_update_magnitude():
    """Verify the pace update magnitude matches K_pace / n_unique * pace_surprise."""
    current_elos = _make_elos(OFF + DEF, rapm_pace=0.0)
    possessions = [_make_possession(OFF, DEF, points_scored=1)]
    league_avg_pace = 95.0
    game_pace = 100.0
    K_pace = 1.0
    n_unique = 10  # 5 off + 5 def, all distinct

    replay_game_elo(
        possessions, current_elos,
        league_avg_ppp=1.0, league_avg_pace=league_avg_pace, game_pace=game_pace,
        K_pace=K_pace,
    )

    # expected pace = 95 + 0 = 95, pace_surprise = 5.0, per player = 1.0/10 * 5.0 = 0.5
    expected_delta = (K_pace / n_unique) * (game_pace - league_avg_pace)
    for pid in OFF + DEF:
        assert current_elos[pid]["pace_delta"] == pytest.approx(expected_delta)
