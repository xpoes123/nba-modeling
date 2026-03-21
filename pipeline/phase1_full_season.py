"""
P4: Full-season RAPM — DB orchestrator.

Loads stints from SQLite, fits three Ridge regressions (offense, defense, pace),
and writes results to rapm_ratings and current_ratings.

Usage:
    uv run python pipeline/phase1_full_season.py
"""

import logging
import sqlite3
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

import config
from models.rapm import build_design_matrix, build_player_index, fit_rapm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Connection helper (mirrors etl.py — kept local to avoid cross-module coupling)
# ---------------------------------------------------------------------------

def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_full_season_rapm(
    db_path: str,
    season: str,
    alpha: float,
) -> dict:
    """
    Fit full-season RAPM and write results to the database.

    Performs a clean overwrite: deletes any existing rapm_full rows for the
    season before inserting fresh results.

    Args:
        db_path: Path to SQLite database.
        season:  Season string, e.g. '2025-26'.
        alpha:   Ridge regularization strength.

    Returns:
        Dict with summary stats: n_players, offense_mean/std, defense_mean/std,
        pace_mean/std, window_end_date.
    """
    conn = _get_conn(db_path)
    try:
        # ------------------------------------------------------------------
        # 1. Load league averages
        # ------------------------------------------------------------------
        row = conn.execute(
            "SELECT avg_ppp, avg_pace FROM league_averages WHERE season = ?",
            (season,),
        ).fetchone()
        if row is None:
            raise ValueError(
                f"No league_averages row for season '{season}'. Run backfill first."
            )
        avg_ppp, avg_pace = row
        logger.info("League averages: avg_ppp=%.4f, avg_pace=%.2f", avg_ppp, avg_pace)

        # ------------------------------------------------------------------
        # 2. Load stints
        # ------------------------------------------------------------------
        stints = pd.read_sql(
            "SELECT * FROM stints WHERE season = ?",
            conn,
            params=(season,),
        )
        if stints.empty:
            raise ValueError(f"No stints found for season '{season}'. Run backfill first.")

        logger.info("Loaded %d stints for season %s", len(stints), season)

        # ------------------------------------------------------------------
        # 3. Build player index (shared across all three regressions)
        # ------------------------------------------------------------------
        player_index = build_player_index(stints)
        player_ids = sorted(player_index.keys(), key=lambda pid: player_index[pid])
        n_players = len(player_ids)
        logger.info("Distinct players: %d", n_players)

        # ------------------------------------------------------------------
        # 4. Build design matrix for offense/defense (all stints)
        # ------------------------------------------------------------------
        X = build_design_matrix(stints, player_index)
        possessions = stints["possessions"].values.astype(float)

        # ------------------------------------------------------------------
        # 5. Compute offense and defense targets (points per 100 possessions,
        #    centered on league avg). Multiply by 100 so targets are in the
        #    same unit as conventional RAPM (e.g. +3.5 off = 3.5 pts/100 above
        #    avg), and because alpha=5000 is calibrated for this scale.
        # ------------------------------------------------------------------
        y_offense = (
            stints["points_scored"].values / possessions - avg_ppp
        ) * 100.0
        y_defense = (
            stints["points_allowed"].values / possessions - avg_ppp
        ) * 100.0

        # ------------------------------------------------------------------
        # 6. Fit offense and defense regressions
        # ------------------------------------------------------------------
        logger.info("Fitting offense regression (alpha=%.0f)...", alpha)
        offense_coefs = fit_rapm(X, y_offense, possessions, alpha)

        logger.info("Fitting defense regression (alpha=%.0f)...", alpha)
        defense_coefs = fit_rapm(X, y_defense, possessions, alpha)

        # ------------------------------------------------------------------
        # 7. Pace regression — filter out stints with seconds_played = 0
        # ------------------------------------------------------------------
        pace_mask = stints["seconds_played"] > 0
        n_excluded = (~pace_mask).sum()
        if n_excluded > 0:
            logger.warning(
                "Excluding %d stints with seconds_played=0 from pace regression.",
                n_excluded,
            )
        stints_pace = stints[pace_mask].reset_index(drop=True)
        X_pace = build_design_matrix(stints_pace, player_index)
        poss_pace = stints_pace["possessions"].values.astype(float)
        y_pace = (
            stints_pace["possessions"].values / stints_pace["seconds_played"].values * 2880
            - avg_pace
        )

        logger.info("Fitting pace regression (alpha=%.0f, %d stints)...", alpha, len(stints_pace))
        pace_coefs = fit_rapm(X_pace, y_pace, poss_pace, alpha)

        # ------------------------------------------------------------------
        # 8. Window metadata
        # ------------------------------------------------------------------
        window_end_date: str = stints["game_date"].max()

        # ------------------------------------------------------------------
        # 9. Atomic DB write — overwrite existing rapm_full rows
        # ------------------------------------------------------------------
        logger.info("Writing results to database...")
        computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        with conn:
            conn.execute(
                "DELETE FROM rapm_ratings WHERE season = ? AND phase = 'rapm_full'",
                (season,),
            )
            conn.execute(
                "DELETE FROM current_ratings WHERE season = ?",
                (season,),
            )

            rapm_rows = [
                (
                    player_ids[i],
                    season,
                    "rapm_full",
                    None,  # window_start_date — NULL for full-season
                    window_end_date,
                    float(offense_coefs[i]),
                    float(defense_coefs[i]),
                    float(pace_coefs[i]),
                    computed_at,
                )
                for i in range(n_players)
            ]
            conn.executemany(
                """
                INSERT INTO rapm_ratings
                    (player_id, season, phase, window_start_date, window_end_date,
                     offense, defense, pace, computed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rapm_rows,
            )

            cr_rows = [
                (
                    player_ids[i],
                    season,
                    float(offense_coefs[i]),
                    float(defense_coefs[i]),
                    float(pace_coefs[i]),
                    float(offense_coefs[i]) - float(defense_coefs[i]),
                    "rapm_full",
                )
                for i in range(n_players)
            ]
            conn.executemany(
                """
                INSERT INTO current_ratings
                    (player_id, season, offense, defense, pace, overall, phase)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                cr_rows,
            )

        logger.info(
            "Done: %d players written, window_end_date=%s", n_players, window_end_date
        )

        return {
            "n_players": n_players,
            "offense_mean": float(offense_coefs.mean()),
            "offense_std": float(offense_coefs.std()),
            "defense_mean": float(defense_coefs.mean()),
            "defense_std": float(defense_coefs.std()),
            "pace_mean": float(pace_coefs.mean()),
            "pace_std": float(pace_coefs.std()),
            "window_end_date": window_end_date,
            "offense_coefs": offense_coefs,
            "defense_coefs": defense_coefs,
            "pace_coefs": pace_coefs,
            "player_ids": player_ids,
        }

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Validation output
# ---------------------------------------------------------------------------

def _print_validation(result: dict, db_path: str) -> None:
    """Print top/bottom 20 players and distribution stats."""

    def _safe_print(text: str) -> None:
        """Print UTF-8 text safely on Windows terminals that default to cp1252."""
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()

    # Top 20 / bottom 20 overall — fetch names from DB
    conn = _get_conn(db_path)
    try:
        df = pd.read_sql(
            """
            SELECT p.player_name, cr.offense, cr.defense, cr.pace, cr.overall
            FROM current_ratings cr
            JOIN players p ON cr.player_id = p.player_id
            WHERE cr.season = ?
            ORDER BY cr.overall DESC
            """,
            conn,
            params=(config.INITIAL_SEASON,),
        )
    finally:
        conn.close()

    def _fmt(df_slice: pd.DataFrame) -> str:
        return df_slice.to_string(index=False, float_format=lambda x: f"{x:+.3f}")

    _safe_print("\n" + "=" * 60)
    _safe_print("Top 20 Players by Overall Rating")
    _safe_print("=" * 60)
    _safe_print(_fmt(df.head(20)))

    _safe_print("\n" + "=" * 60)
    _safe_print("Bottom 20 Players by Overall Rating")
    _safe_print("=" * 60)
    _safe_print(_fmt(df.tail(20)))

    _safe_print(f"\nTotal players rated: {len(df)}")

    # Distribution stats
    offense_coefs = result["offense_coefs"]
    defense_coefs = result["defense_coefs"]
    pace_coefs = result["pace_coefs"]
    overall = offense_coefs - defense_coefs

    _safe_print("\n" + "=" * 60)
    _safe_print("RAPM Distribution Stats")
    _safe_print("=" * 60)
    for label, coefs in [
        ("Offense", offense_coefs),
        ("Defense", defense_coefs),
        ("Pace   ", pace_coefs),
        ("Overall", overall),
    ]:
        _safe_print(
            f"  {label}: mean={coefs.mean():+.4f}  std={coefs.std():.4f}"
            f"  min={coefs.min():+.4f}  max={coefs.max():+.4f}"
        )

    extremes_off = int(np.sum(np.abs(offense_coefs) > 10))
    extremes_def = int(np.sum(np.abs(defense_coefs) > 10))
    if extremes_off or extremes_def:
        _safe_print(
            f"\n  WARNING: {extremes_off} offense and {extremes_def} defense"
            " coefs have |rating| > 10 — check for data issues."
        )
    else:
        _safe_print("\n  OK: No |rating| > 10 extremes detected.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info(
        "Starting full-season RAPM: season=%s, alpha=%.0f",
        config.INITIAL_SEASON,
        config.RIDGE_ALPHA,
    )

    result = run_full_season_rapm(
        db_path=config.DB_PATH,
        season=config.INITIAL_SEASON,
        alpha=config.RIDGE_ALPHA,
    )

    _print_validation(result, config.DB_PATH)
    sys.exit(0)
