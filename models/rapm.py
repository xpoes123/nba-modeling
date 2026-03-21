"""
P4: RAPM model — pure functions, no database side effects.

Public API:
    build_player_index(stints)              -> dict[str, int]
    build_design_matrix(stints, player_index) -> scipy.sparse.csr_matrix
    fit_rapm(X, y, possessions, alpha)      -> np.ndarray
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.linear_model import Ridge


def build_player_index(stints: pd.DataFrame) -> dict[str, int]:
    """
    Build a mapping from player_id to column index.

    Scans all lineup IDs (both offense and defense) in the stints DataFrame,
    collects unique player IDs, sorts them ascending, and assigns integer indices.

    Args:
        stints: DataFrame with columns offense_lineup_id and defense_lineup_id.
                Lineup IDs are dash-separated sorted player ID strings.

    Returns:
        Dict mapping player_id -> column index (0-based, ascending sort order).
    """
    players: set[str] = set()
    for lid in pd.concat(
        [stints["offense_lineup_id"], stints["defense_lineup_id"]], ignore_index=True
    ):
        players.update(lid.split("-"))
    return {pid: i for i, pid in enumerate(sorted(players))}


def build_design_matrix(
    stints: pd.DataFrame, player_index: dict[str, int]
) -> csr_matrix:
    """
    Build the sparse RAPM design matrix.

    For each stint row:
      - +1 for each of the 5 offensive players
      - -1 for each of the 5 defensive players

    Matrix is unweighted; weighting by sqrt(possessions) is applied in fit_rapm.

    Args:
        stints: DataFrame with offense_lineup_id and defense_lineup_id columns.
        player_index: Mapping from player_id to column index (from build_player_index).

    Returns:
        Sparse CSR matrix of shape (n_stints, n_players).
    """
    n_stints = len(stints)
    n_players = len(player_index)

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []

    for i, row in enumerate(stints.itertuples(index=False)):
        for pid in row.offense_lineup_id.split("-"):
            rows.append(i)
            cols.append(player_index[pid])
            data.append(1.0)
        for pid in row.defense_lineup_id.split("-"):
            rows.append(i)
            cols.append(player_index[pid])
            data.append(-1.0)

    return csr_matrix((data, (rows, cols)), shape=(n_stints, n_players))


def fit_rapm(
    X: csr_matrix,
    y: np.ndarray,
    possessions: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """
    Fit a weighted Ridge regression for RAPM.

    Weighting is applied by pre-multiplying both X and y by sqrt(possessions)
    before fitting. This is the standard RAPM weighting approach (weighted
    least squares) and differs from sklearn's sample_weight (which affects
    the regularization term differently).

    Args:
        X:           Sparse design matrix, shape (n_stints, n_players). Unweighted.
        y:           Target vector, shape (n_stints,). Already centered on league avg.
        possessions: Possession counts per stint, shape (n_stints,).
        alpha:       Ridge regularization strength (RIDGE_ALPHA from config).

    Returns:
        Coefficient array of shape (n_players,). Positive offense coef = scores
        above average; positive defense coef = allows more than average (bad).
    """
    sqrt_w = np.sqrt(possessions.astype(float))
    X_w = X.multiply(sqrt_w[:, np.newaxis])
    y_w = y * sqrt_w

    model = Ridge(alpha=alpha, fit_intercept=False)
    model.fit(X_w, y_w)
    return model.coef_
