"""Resolve prediction outcomes against actual game scores.

Matches rows in the `predictions` table to completed games in the `games` table
and fills in actual_home_score, actual_away_score, and actual_margin. Prints a
running accuracy report (MAE, bias, correlation, directional accuracy).

Run this BEFORE generating new predictions so last night's results are resolved
before today's predictions write to the log.

Usage:
    PYTHONPATH=. uv run python downstream/track_outcomes.py
"""
import logging
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DB_PATH, NBA_TEAM_MAP

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def _abbrev(team_name: str) -> str:
    return next(
        (v["abbrev"] for v in NBA_TEAM_MAP.values() if v["name"] == team_name),
        team_name[:3].upper(),
    )


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def resolve_outcomes(db_path: str = DB_PATH) -> int:
    """Look up actual scores for unresolved predictions.

    Matches on (game_date, home_team_id, away_team_id).  Falls back to a
    name-based team-ID lookup when IDs are missing from the predictions row.

    Returns:
        Number of predictions newly resolved this run.
    """
    conn = _get_conn(db_path)
    try:
        # Build reverse map: team_name → nba.com team_id (for name-based fallback)
        name_to_id = {v["name"]: k for k, v in NBA_TEAM_MAP.items()}

        # Find predictions that haven't been resolved yet and are in the past
        today = date.today().isoformat()
        pending = conn.execute(
            """
            SELECT id, game_date, home_team_id, away_team_id,
                   home_team_name, away_team_name, predicted_spread
            FROM predictions
            WHERE actual_home_score IS NULL
              AND game_date < ?
            ORDER BY game_date
            """,
            (today,),
        ).fetchall()

        if not pending:
            logger.info("No unresolved predictions to update.")
            return 0

        resolved = 0
        for pred in pending:
            home_id = pred["home_team_id"] or name_to_id.get(pred["home_team_name"])
            away_id = pred["away_team_id"] or name_to_id.get(pred["away_team_name"])

            if not home_id or not away_id:
                logger.warning(
                    "Cannot resolve %s @ %s on %s — no team IDs",
                    pred["away_team_name"], pred["home_team_name"], pred["game_date"],
                )
                continue

            game = conn.execute(
                """
                SELECT home_score, away_score
                FROM games
                WHERE game_date = ? AND home_team_id = ? AND away_team_id = ?
                  AND home_score IS NOT NULL
                """,
                (pred["game_date"], home_id, away_id),
            ).fetchone()

            if game is None:
                logger.debug(
                    "No completed game found for %s @ %s on %s",
                    pred["away_team_name"], pred["home_team_name"], pred["game_date"],
                )
                continue

            actual_margin = game["home_score"] - game["away_score"]
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            conn.execute(
                """
                UPDATE predictions
                SET actual_home_score  = ?,
                    actual_away_score  = ?,
                    actual_margin      = ?,
                    outcome_tracked_at = ?
                WHERE id = ?
                """,
                (game["home_score"], game["away_score"], actual_margin, now, pred["id"]),
            )
            conn.commit()
            resolved += 1

        logger.info("Resolved %d / %d pending predictions.", resolved, len(pending))
        return resolved

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_accuracy_report(db_path: str = DB_PATH) -> None:
    """Print a formatted accuracy report for all resolved predictions."""
    conn = _get_conn(db_path)
    try:
        rows = conn.execute(
            """
            SELECT game_date, home_team_name, away_team_name,
                   predicted_spread, market_spread,
                   actual_margin, actual_home_score, actual_away_score,
                   home_b2b, away_b2b, home_coverage, away_coverage
            FROM predictions
            WHERE actual_margin IS NOT NULL
            ORDER BY game_date, home_team_name
            """,
        ).fetchall()

        if not rows:
            print("\nNo resolved predictions yet.\n")
            return

        print(f"\nPrediction Outcomes - {len(rows)} games resolved")
        print("=" * 80)

        errors: list[float] = []
        correct_dir: int = 0
        market_correct_dir: int = 0
        market_rows: list = []

        print(
            f"{'Date':<12} {'Away':<4} {'Home':<4}  "
            f"{'Our':>6}  {'Mkt':>6}  {'Actual':>7}  {'Error':>6}  {'Dir':>3}"
        )
        print("-" * 80)

        for r in rows:
            pred = r["predicted_spread"]
            actual = r["actual_margin"]
            error = pred - actual
            errors.append(error)

            home_ab = _abbrev(r["home_team_name"])
            away_ab = _abbrev(r["away_team_name"])

            # Direction: positive predicted_spread → we think home wins
            dir_correct = (pred > 0) == (actual > 0)
            correct_dir += int(dir_correct)
            dir_symbol = " Y" if dir_correct else " N"

            mkt = r["market_spread"]
            mkt_str = f"{mkt:+.1f}" if mkt is not None else "  N/A"
            if mkt is not None:
                market_rows.append((mkt, actual))
                market_correct_dir += int((mkt > 0) == (actual > 0))

            notes = []
            if r["home_b2b"]:
                notes.append(f"{home_ab}B2B")
            if r["away_b2b"]:
                notes.append(f"{away_ab}B2B")
            note_str = f"  [{','.join(notes)}]" if notes else ""

            print(
                f"{r['game_date']:<12} {away_ab:<4} {home_ab:<4}  "
                f"{pred:>+6.1f}  {mkt_str:>6}  "
                f"{actual:>+7.1f}  {error:>+6.1f}  {dir_symbol:>3}"
                f"{note_str}"
            )

        print("=" * 80)

        n = len(errors)
        mae = sum(abs(e) for e in errors) / n
        bias = sum(errors) / n
        dir_acc = correct_dir / n

        # Pearson correlation (need at least 2 points)
        if n >= 2:
            preds = [r["predicted_spread"] for r in rows]
            actuals = [r["actual_margin"] for r in rows]
            mean_p = sum(preds) / n
            mean_a = sum(actuals) / n
            num = sum((p - mean_p) * (a - mean_a) for p, a in zip(preds, actuals))
            den_p = sum((p - mean_p) ** 2 for p in preds) ** 0.5
            den_a = sum((a - mean_a) ** 2 for a in actuals) ** 0.5
            corr = num / (den_p * den_a) if den_p > 0 and den_a > 0 else float("nan")
        else:
            corr = float("nan")

        print(f"\nSummary ({n} games):")
        print(f"  MAE              : {mae:.2f} pts")
        print(f"  Bias             : {bias:+.2f} pts  (+ = we over-predict home)")
        corr_str = f"{corr:.3f}" if corr == corr else "N/A"
        print(f"  Correlation      : {corr_str}")
        print(f"  Directional acc  : {correct_dir}/{n} = {dir_acc:.1%}")

        if market_rows:
            n_mkt = len(market_rows)
            mkt_acc = market_correct_dir / n_mkt
            print(f"  Market dir acc   : {market_correct_dir}/{n_mkt} = {mkt_acc:.1%}  (baseline)")

        print()

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    n_resolved = resolve_outcomes()
    if n_resolved > 0:
        logger.info("Updated %d prediction rows with actual results.", n_resolved)
    print_accuracy_report()


if __name__ == "__main__":
    main()
