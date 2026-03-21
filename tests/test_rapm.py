"""
Unit tests for models/rapm.py — pure functions only, no DB required.
"""

import numpy as np
import pandas as pd
import pytest

from models.rapm import build_player_index, build_design_matrix, fit_rapm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_stints(*rows: tuple) -> pd.DataFrame:
    """Create a minimal stints DataFrame from (offense_lineup_id, defense_lineup_id, possessions) tuples."""
    return pd.DataFrame(
        rows, columns=["offense_lineup_id", "defense_lineup_id", "possessions"]
    )


# ---------------------------------------------------------------------------
# build_player_index
# ---------------------------------------------------------------------------

def test_build_player_index_basic():
    stints = _make_stints(
        ("A-B", "C-D", 5),
        ("C-D", "A-B", 3),
    )
    idx = build_player_index(stints)
    assert len(idx) == 4
    assert set(idx.keys()) == {"A", "B", "C", "D"}
    # All indices unique and in range
    assert sorted(idx.values()) == list(range(4))


def test_build_player_index_ascending_sort():
    stints = _make_stints(("Z-A", "M-B", 10))
    idx = build_player_index(stints)
    # Should be sorted ascending: A=0, B=1, M=2, Z=3
    assert idx["A"] < idx["B"] < idx["M"] < idx["Z"]


def test_build_player_index_deduplicates():
    # Same player appears on both sides — should count once
    stints = _make_stints(
        ("A-B", "A-C", 5),
    )
    idx = build_player_index(stints)
    assert len(idx) == 3
    assert set(idx.keys()) == {"A", "B", "C"}


# ---------------------------------------------------------------------------
# build_design_matrix
# ---------------------------------------------------------------------------

def test_build_design_matrix_shape():
    stints = _make_stints(
        ("A-B", "C-D", 5),
        ("C-D", "A-B", 3),
    )
    idx = build_player_index(stints)
    X = build_design_matrix(stints, idx)
    assert X.shape == (2, 4)


def test_build_design_matrix_values():
    stints = _make_stints(("A-B", "C-D", 5))
    idx = {"A": 0, "B": 1, "C": 2, "D": 3}
    X = build_design_matrix(stints, idx).toarray()
    # Offensive players get +1
    assert X[0, idx["A"]] == 1.0
    assert X[0, idx["B"]] == 1.0
    # Defensive players get -1
    assert X[0, idx["C"]] == -1.0
    assert X[0, idx["D"]] == -1.0


def test_build_design_matrix_row_sum_zero():
    # When same players are on offense and defense, the column cancels out.
    # For a normal 5v5 situation with distinct players, row sum = 5 - 5 = 0.
    stints = _make_stints(("A-B-C-D-E", "F-G-H-I-J", 10))
    idx = build_player_index(stints)
    X = build_design_matrix(stints, idx).toarray()
    assert X[0].sum() == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# fit_rapm
# ---------------------------------------------------------------------------

def test_fit_rapm_trivial():
    """
    Lineup AB always scores high (PPP 1.2), lineup CD always scores low (PPP 0.8).
    Centered on 1.0. With small alpha, A and B should have positive coefs,
    C and D should have negative coefs.
    """
    stints = pd.DataFrame({
        "offense_lineup_id": ["A-B", "C-D"],
        "defense_lineup_id": ["C-D", "A-B"],
        "possessions":       [100,   100],
    })
    idx = {"A": 0, "B": 1, "C": 2, "D": 3}
    X = build_design_matrix(stints, idx)
    y = np.array([1.2 - 1.0, 0.8 - 1.0])  # centered on league avg of 1.0
    poss = np.array([100.0, 100.0])

    coefs = fit_rapm(X, y, poss, alpha=1.0)  # small alpha: signal dominates
    assert coefs[idx["A"]] > 0
    assert coefs[idx["B"]] > 0
    assert coefs[idx["C"]] < 0
    assert coefs[idx["D"]] < 0


def test_fit_rapm_symmetry():
    """When offense and defense targets are symmetric, coefs should be symmetric."""
    stints = pd.DataFrame({
        "offense_lineup_id": ["A-B", "C-D"],
        "defense_lineup_id": ["C-D", "A-B"],
        "possessions":       [50,    50],
    })
    idx = {"A": 0, "B": 1, "C": 2, "D": 3}
    X = build_design_matrix(stints, idx)
    y = np.array([0.2, -0.2])
    poss = np.array([50.0, 50.0])

    coefs = fit_rapm(X, y, poss, alpha=1.0)
    # A and B should have equal coefs; C and D should have equal coefs
    assert coefs[idx["A"]] == pytest.approx(coefs[idx["B"]], rel=1e-6)
    assert coefs[idx["C"]] == pytest.approx(coefs[idx["D"]], rel=1e-6)


def test_fit_rapm_high_alpha_shrinks_to_zero():
    """With extremely high alpha, all coefs should be near zero (heavy regularization)."""
    stints = pd.DataFrame({
        "offense_lineup_id": ["A-B", "C-D"],
        "defense_lineup_id": ["C-D", "A-B"],
        "possessions":       [10,    10],
    })
    idx = {"A": 0, "B": 1, "C": 2, "D": 3}
    X = build_design_matrix(stints, idx)
    y = np.array([0.5, -0.5])
    poss = np.array([10.0, 10.0])

    coefs = fit_rapm(X, y, poss, alpha=1e9)
    assert np.all(np.abs(coefs) < 0.01)


def test_fit_rapm_returns_correct_shape():
    stints = pd.DataFrame({
        "offense_lineup_id": ["A-B-C", "D-E-F"],
        "defense_lineup_id": ["D-E-F", "A-B-C"],
        "possessions":       [20,      20],
    })
    idx = build_player_index(stints)
    X = build_design_matrix(stints, idx)
    y = np.array([0.1, -0.1])
    poss = np.array([20.0, 20.0])

    coefs = fit_rapm(X, y, poss, alpha=100.0)
    assert coefs.shape == (len(idx),)
