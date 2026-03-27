"""Daily prediction script: compare our model's spreads/win probs to market lines.

Run after the nightly job, before the next game slate.

Usage:
    PYTHONPATH=. uv run python downstream/predictions.py [--date YYYY-MM-DD]

Default date: tomorrow (UTC).

Lineup/minutes source: our own DB (possession history — last 15 games per team).
Injury source: BDL (best-effort; skipped gracefully if unavailable or on free tier).
Odds source: Odds API.
"""
import argparse
import logging
import math
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import stdev

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    ADVERSE_MARKET_EDGE_THRESHOLD,
    CALIBRATION_PATH,
    COVERAGE_GATE_THRESHOLD,
    DB_PATH,
    ESPN_TEAM_ID_MAP,
    INITIAL_SEASON,
    LONG_TERM_INJURY_STREAK,
    MONTE_CARLO_SIMULATIONS,
    NBA_TEAM_MAP,
    RETURNING_PLAYER_EXTENDED_LOOKBACK,
    RETURNING_PLAYER_MAX_WINDOW_APPEARANCES,
    RETURNING_PLAYER_MIN_EXTENDED_GAMES,
    RETURNING_PLAYER_MIN_SEASON_GAMES,
    RETURNING_PLAYER_MULTIPLIER,
    RETURNING_PLAYER_SPARSE_MULTIPLIER,
    RETURNING_PLAYER_THRESHOLD,
    team_id_from_name,
)
from downstream.espn_client import EspnRosterPlayer, get_nba_injuries, get_nba_roster, get_out_player_names
from downstream.calibration import load_calibration
from downstream.lineup_sampler import (
    MinutesProfile,
    apply_calibration,
    margin_to_win_prob,
    simulate_game,
)
from downstream.odds_client import GameOdds, get_nba_odds
from downstream.team_ratings import (
    PlayerRating,
    normalize_name,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Number of recent team games to use for possession-share estimation
_LINEUP_LOOKBACK_GAMES = 15
_RECENCY_DECAY = 0.85  # per-game-slot exponential decay; slot 0 = most recent game


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def _load_player_ratings(conn: sqlite3.Connection, season: str) -> dict[str, PlayerRating]:
    rows = conn.execute(
        "SELECT player_id, offense, defense, pace FROM current_ratings WHERE season = ?",
        (season,),
    ).fetchall()
    return {
        r["player_id"]: PlayerRating(
            player_id=r["player_id"],
            offense=r["offense"],
            defense=r["defense"],
            pace=r["pace"],
        )
        for r in rows
    }


def _load_league_avg(conn: sqlite3.Connection, season: str) -> tuple[float, float]:
    row = conn.execute(
        "SELECT avg_ppp, avg_pace FROM league_averages WHERE season = ?", (season,)
    ).fetchone()
    if row is None:
        raise ValueError(f"No league averages found for season {season}")
    return row["avg_ppp"], row["avg_pace"]


def _detect_b2b(team_id: str, game_date: date, conn: sqlite3.Connection) -> bool:
    """Return True if this team played yesterday."""
    prev = (game_date - timedelta(days=1)).isoformat()
    row = conn.execute(
        "SELECT 1 FROM games WHERE game_date = ? AND (home_team_id = ? OR away_team_id = ?) LIMIT 1",
        (prev, team_id, team_id),
    ).fetchone()
    return row is not None


def _upsert_prediction(conn: sqlite3.Connection, pred: dict) -> None:
    conn.execute(
        """
        INSERT INTO predictions (
            odds_event_id, game_date, home_team_id, away_team_id,
            home_team_name, away_team_name,
            predicted_spread, predicted_win_prob, sim_std,
            market_spread, market_win_prob, market_total,
            spread_edge, win_prob_edge,
            home_b2b, away_b2b, n_simulations,
            home_coverage, away_coverage
        ) VALUES (
            :odds_event_id, :game_date, :home_team_id, :away_team_id,
            :home_team_name, :away_team_name,
            :predicted_spread, :predicted_win_prob, :sim_std,
            :market_spread, :market_win_prob, :market_total,
            :spread_edge, :win_prob_edge,
            :home_b2b, :away_b2b, :n_simulations,
            :home_coverage, :away_coverage
        )
        ON CONFLICT(game_date, home_team_name, away_team_name) DO UPDATE SET
            predicted_spread   = excluded.predicted_spread,
            predicted_win_prob = excluded.predicted_win_prob,
            sim_std            = excluded.sim_std,
            market_spread      = excluded.market_spread,
            market_win_prob    = excluded.market_win_prob,
            market_total       = excluded.market_total,
            spread_edge        = excluded.spread_edge,
            win_prob_edge      = excluded.win_prob_edge,
            home_b2b           = excluded.home_b2b,
            away_b2b           = excluded.away_b2b,
            n_simulations      = excluded.n_simulations,
            home_coverage      = excluded.home_coverage,
            away_coverage      = excluded.away_coverage,
            created_at         = datetime('now')
        """,
        pred,
    )


# ---------------------------------------------------------------------------
# DB-based lineup / minutes estimation
# ---------------------------------------------------------------------------

def _get_team_possession_profiles(
    team_id: str,
    conn: sqlite3.Connection,
    n_games: int = _LINEUP_LOOKBACK_GAMES,
    before_date: str | None = None,
) -> tuple[dict[str, list[tuple[float, float]]], list[str], dict[str, set[str]]]:
    """Return (player_shares, game_ids, player_game_ids) for last n games.

    player_shares: player_id → [(raw_share, game_weight), ...]
    game_ids: ordered list of game IDs, newest first (index 0 = most recent game)
    player_game_ids: player_id → set of game_ids the player appeared in

    Possession share = fraction of the team's offensive possessions a player appeared in.
    game_ids come back ORDER BY game_date DESC so index 0 = most recent game,
    weighted by _RECENCY_DECAY ** slot_index.

    Args:
        before_date: if set (YYYY-MM-DD), only include games strictly before this date
    """
    # Get the last n game IDs for this team (ordered newest first via games table)
    if before_date is not None:
        rows = conn.execute(
            """
            SELECT game_id
            FROM games
            WHERE (home_team_id = ? OR away_team_id = ?) AND game_date < ?
            ORDER BY game_date DESC
            LIMIT ?
            """,
            (team_id, team_id, before_date, n_games),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT game_id
            FROM games
            WHERE home_team_id = ? OR away_team_id = ?
            ORDER BY game_date DESC
            LIMIT ?
            """,
            (team_id, team_id, n_games),
        ).fetchall()

    game_ids = [r["game_id"] for r in rows]
    if not game_ids:
        return {}, [], {}

    # slot 0 = most recent game (weight 1.0), slot 1 (0.85), …
    game_weight = {gid: _RECENCY_DECAY ** i for i, gid in enumerate(game_ids)}

    placeholders = ",".join("?" * len(game_ids))
    poss_df = pd.read_sql(
        f"""
        SELECT game_id, off_player_1, off_player_2, off_player_3, off_player_4, off_player_5
        FROM possessions
        WHERE offense_team_id = ? AND game_id IN ({placeholders})
        """,
        conn,
        params=[team_id] + game_ids,
    )

    if poss_df.empty:
        return {}, game_ids, {}

    off_cols = ["off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5"]
    player_shares: dict[str, list[tuple[float, float]]] = {}
    player_game_ids: dict[str, set[str]] = {}

    for game_id, game_df in poss_df.groupby("game_id"):
        n_poss = len(game_df)
        counts: dict[str, int] = {}
        for col in off_cols:
            for pid in game_df[col]:
                counts[pid] = counts.get(pid, 0) + 1
        w = game_weight[game_id]
        for pid, cnt in counts.items():
            # Normalize: each player appears in 5 of every possession's player slots
            share = cnt / (n_poss * 5)
            player_shares.setdefault(pid, []).append((share, w))
            player_game_ids.setdefault(pid, set()).add(game_id)

    return player_shares, game_ids, player_game_ids


def _consecutive_recent_absences(game_ids: list[str], player_game_set: set[str]) -> int:
    """Count consecutive most-recent games a player missed.

    Walks game_ids from most-recent (index 0) forward; stops at the first game the player appeared.
    """
    streak = 0
    for gid in game_ids:
        if gid not in player_game_set:
            streak += 1
        else:
            break
    return streak


def _build_minutes_profile_from_db(
    team_id: str,
    conn: sqlite3.Connection,
    injured_names: set[str],
    player_id_to_name: dict[str, str],
    season: str | None = None,
    n_games: int = _LINEUP_LOOKBACK_GAMES,
    min_games: int = 3,
    before_date: str | None = None,
    espn_roster: list[EspnRosterPlayer] | None = None,
) -> tuple[MinutesProfile, float]:
    """Build MinutesProfile from DB possession history.

    Converts possession shares → synthetic minutes (scaled to ~240 total team minutes
    per game = 5 players × 48 minutes).

    Applies two injury modeling fixes when season is provided:
    - Fix B: Hard-exclude players who are ESPN Out AND missed last LONG_TERM_INJURY_STREAK
      consecutive games (removes their share from coverage_ratio calculation).
    - Fix A: Inject returning players who are NOT injured but absent from the recent window
      and have strong ratings + historical presence in the extended window.

    Args:
        team_id: nba.com team ID
        conn: DB connection
        injured_names: set of normalized player names to exclude
        player_id_to_name: player_id → player_name (for injury filtering)
        season: current season string (e.g. '2025-26'); enables Fix A when provided
        n_games: lookback window
        min_games: minimum appearances to include a player
        before_date: if set (YYYY-MM-DD), only include games strictly before this date

    Returns:
        (MinutesProfile, coverage_ratio) where coverage_ratio is the fraction of normal
        possession-weighted minutes that are NOT excluded by injuries (0–1).
    """
    profiles, game_ids, player_game_ids = _get_team_possession_profiles(
        team_id, conn, n_games, before_date=before_date
    )
    n_window_games = len(game_ids)
    if n_window_games == 0:
        return MinutesProfile(), 1.0

    # Fix B: Hard-exclude long-term injured players BEFORE building the profile.
    # A player who is on the ESPN injury list AND missed the last LONG_TERM_INJURY_STREAK
    # consecutive games is removed from profiles entirely — their historical share from earlier
    # in the window should not inflate the team's apparent quality or coverage_ratio.
    if injured_names and game_ids:
        to_remove: set[str] = set()
        for pid in list(profiles.keys()):
            name = player_id_to_name.get(pid, "")
            if normalize_name(name) not in injured_names:
                continue
            streak = _consecutive_recent_absences(game_ids, player_game_ids.get(pid, set()))
            if streak >= LONG_TERM_INJURY_STREAK:
                to_remove.add(pid)
                logger.debug(
                    "Fix B: Hard-excluding long-term injured %s (%s), streak=%d games",
                    name, pid, streak,
                )
        for pid in to_remove:
            del profiles[pid]

    result: MinutesProfile = MinutesProfile()

    # Recency-weighted availability-discounted share.
    # Weighted mean share × (player_weight_sum / total_window_weight).
    # A player who appeared only in older games is discounted relative to one who
    # appeared in recent games, even if the raw game counts are equal.
    total_window_weight = sum(_RECENCY_DECAY ** i for i in range(n_window_games))

    def _effective_share(pid_shares: list[tuple[float, float]]) -> float:
        w_sum = sum(w for s, w in pid_shares)
        return sum(w * s for s, w in pid_shares) / w_sum * (w_sum / total_window_weight) if w_sum > 0 else 0.0

    # Total weight across all qualified players (before injury filter)
    total_weight = sum(_effective_share(sh) for sh in profiles.values() if len(sh) >= min_games)
    available_weight = 0.0

    for pid, shares in profiles.items():
        if len(shares) < min_games:
            continue

        name = player_id_to_name.get(pid, "")
        eff_share = _effective_share(shares)

        if normalize_name(name) in injured_names:
            logger.debug("Skipping injured player: %s (%s)", name, pid)
            continue

        available_weight += eff_share
        # Stdev computed on raw (unweighted) shares — measures lineup variance, not recency
        raw_shares = [s for s, w in shares]
        std_share = stdev(raw_shares) if len(raw_shares) > 1 else 0.03

        # Convert availability-discounted share → synthetic minutes
        result[pid] = (eff_share * 240, std_share * 240)

    coverage_ratio = available_weight / total_weight if total_weight > 0 else 1.0

    # Redistribute injured players' minutes proportionally to the healthy roster.
    # When coverage_ratio < 1.0, scale each player's synthetic minutes up by 1/coverage_ratio
    # so the MinutesProfile total stays ~240 (= 5 players × 48 min).
    # shares_from_minutes() in simulate_game would normalize anyway, but this keeps
    # synthetic minutes semantically correct and std_minutes proportional to actual usage.
    if 0.0 < coverage_ratio < 1.0:
        scale = 1.0 / coverage_ratio
        result = MinutesProfile(
            {pid: (mean_m * scale, std_m * scale) for pid, (mean_m, std_m) in result.items()}
        )

    # Fix A: Returning player pre-seeding.
    # After the normal profile is built and coverage-scaled, inject players who:
    # - Are NOT on the injury list
    # - Have few appearances in the recent window (effectively absent from our model)
    # - Have strong current_ratings (overall >= threshold)
    # - Have significant presence in an extended lookback window
    # This handles stars returning from long injury absences (e.g. Steph Curry 0/15 appearances).
    if season is not None:
        result = _inject_returning_players(
            result, team_id, conn, injured_names, player_id_to_name,
            profiles, season, n_window_games, before_date,
            espn_roster=espn_roster,
        )

    logger.debug(
        "Team %s: %d players, coverage=%.1f%%", team_id, len(result), coverage_ratio * 100
    )
    return result, coverage_ratio


def _get_season_possession_share(
    player_id: str,
    team_id: str,
    season: str,
    conn: sqlite3.Connection,
    exclude_game_ids: list[str],
) -> tuple[float, int] | None:
    """Return (avg_share, n_games) from season-wide possession data outside the lookback windows.

    Used for ESPN-roster players with zero appearances in both the recent and extended windows
    (e.g. returning from a multi-month injury with no recent DB history).

    Returns None if the player appeared in fewer than RETURNING_PLAYER_MIN_SEASON_GAMES.
    """
    # Fetch all offensive possessions for this team this season, excluding known-window games.
    # We'll count per-game appearances in Python to avoid complex SQL parameter ordering.
    exclusion_clause = ""
    exclusion_params: list = []
    if exclude_game_ids:
        placeholders = ",".join("?" * len(exclude_game_ids))
        exclusion_clause = f"AND game_id NOT IN ({placeholders})"
        exclusion_params = list(exclude_game_ids)

    off_cols = ["off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5"]
    rows = conn.execute(
        f"""
        SELECT game_id, {', '.join(off_cols)}
        FROM possessions
        WHERE offense_team_id = ? AND season = ? {exclusion_clause}
        """,
        [team_id, season] + exclusion_params,
    ).fetchall()

    if not rows:
        return None

    # Group by game and count appearances
    game_counts: dict[str, tuple[int, int]] = {}  # game_id → (appearances, total_poss)
    for row in rows:
        gid = row["game_id"]
        appeared = any(row[col] == player_id for col in off_cols)
        prev = game_counts.get(gid, (0, 0))
        game_counts[gid] = (prev[0] + (1 if appeared else 0), prev[1] + 1)

    # Only count games where player actually appeared
    appeared_games = [(app, total) for app, total in game_counts.values() if app > 0]
    n_games = len(appeared_games)
    if n_games < RETURNING_PLAYER_MIN_SEASON_GAMES:
        return None

    avg_share = sum(app / (total * 5) for app, total in appeared_games) / n_games
    return avg_share, n_games


def _inject_returning_players(
    profile: MinutesProfile,
    team_id: str,
    conn: sqlite3.Connection,
    injured_names: set[str],
    player_id_to_name: dict[str, str],
    window_profiles: dict[str, list[tuple[float, float]]],
    season: str,
    n_window_games: int,
    before_date: str | None,
    espn_roster: list[EspnRosterPlayer] | None = None,
) -> MinutesProfile:
    """Fix A: Inject returning players absent from the recent window but with strong ratings.

    Two-phase injection:
    Phase 1 — scan current_ratings for players with 1–2 recent appearances + ≥5 extended.
               Players with 0 appearances use RETURNING_PLAYER_MULTIPLIER (0.70).
               Players with 1–2 appearances use RETURNING_PLAYER_SPARSE_MULTIPLIER (0.40)
               to reduce recency artifact noise from first-game-back outliers.
    Phase 2 — if espn_roster provided, scan for players who are healthy on the ESPN roster
               but have 0 appearances in BOTH recent + extended windows (multi-month absences).
               Uses season-wide possession history as the injection share source (0.50 discount).

    Returns updated profile (original is unchanged if no players qualify).
    """
    # Get all players on this team with ratings
    team_player_rows = conn.execute(
        """
        SELECT cr.player_id, cr.overall
        FROM current_ratings cr
        JOIN players p ON cr.player_id = p.player_id
        WHERE p.team_id = ? AND cr.season = ?
        """,
        (team_id, season),
    ).fetchall()

    if not team_player_rows:
        return profile

    player_overall: dict[str, float] = {r["player_id"]: r["overall"] for r in team_player_rows}

    # Query extended window once for the whole team (30 games)
    ext_profiles, ext_game_ids, _ = _get_team_possession_profiles(
        team_id, conn, RETURNING_PLAYER_EXTENDED_LOOKBACK, before_date=before_date
    )
    ext_window_weight = sum(_RECENCY_DECAY ** i for i in range(len(ext_game_ids)))

    injected: dict[str, tuple[float, float]] = {}

    # ---- Phase 1: scan current_ratings for sparse-but-appeared players ----
    for pid, overall in player_overall.items():
        # Already in the profile — has sufficient recent history
        if pid in profile:
            continue

        # Skip if injured
        name = player_id_to_name.get(pid, "")
        if normalize_name(name) in injured_names:
            continue

        # Must meet the minimum rating threshold
        if overall < RETURNING_PLAYER_THRESHOLD:
            continue

        # Must have few appearances in the recent window
        recent_appearances = len(window_profiles.get(pid, []))
        if recent_appearances > RETURNING_PLAYER_MAX_WINDOW_APPEARANCES:
            continue

        # Must have sufficient presence in the extended window
        ext_shares = ext_profiles.get(pid, [])
        ext_appearances = len(ext_shares)
        if ext_appearances < RETURNING_PLAYER_MIN_EXTENDED_GAMES:
            continue

        # Compute recency-weighted availability-discounted share from extended window
        w_sum = sum(w for s, w in ext_shares)
        mean_ext_share = sum(w * s for s, w in ext_shares) / w_sum if w_sum > 0 else 0.0
        availability = w_sum / ext_window_weight if ext_window_weight > 0 else 0.0
        effective_ext_share = mean_ext_share * availability

        # 1-2 recent appearances = sparse/uncertain return → lower discount to reduce noise
        multiplier = RETURNING_PLAYER_SPARSE_MULTIPLIER if recent_appearances > 0 else RETURNING_PLAYER_MULTIPLIER
        injected_share = effective_ext_share * multiplier
        injected_minutes = injected_share * 240
        raw_shares = [s for s, w in ext_shares]
        std_share = stdev(raw_shares) if len(raw_shares) > 1 else 0.03

        injected[pid] = (injected_minutes, std_share * 240)
        logger.info(
            "Fix A Phase 1: Injecting %s (%s) | ovr=%.2f | recent=%d/%d | "
            "extended=%d/%d | eff_share=%.1f%% → inject=%.1f%% (mult=%.2f)",
            name, pid, overall,
            recent_appearances, n_window_games,
            ext_appearances, RETURNING_PLAYER_EXTENDED_LOOKBACK,
            effective_ext_share * 100, injected_share * 100, multiplier,
        )

    # ---- Phase 2: ESPN roster scan for players with zero window history ----
    # Catches multi-month absences that Phase 1 misses (ext window doesn't reach them).
    if espn_roster:
        # Build name → player_id lookup for the team
        name_to_pid: dict[str, str] = {
            normalize_name(player_id_to_name.get(pid, "")): pid
            for pid in player_overall
        }

        for roster_player in espn_roster:
            if roster_player["is_injured"]:
                continue
            if roster_player["normalized_name"] in injured_names:
                continue

            pid = name_to_pid.get(roster_player["normalized_name"])
            if pid is None:
                continue

            # Already handled: in main profile or Phase 1 injection
            if pid in profile or pid in injected:
                continue

            overall = player_overall.get(pid, 0.0)
            if overall < RETURNING_PLAYER_THRESHOLD:
                continue

            # Only fire for players with 0 appearances in BOTH windows
            recent_appearances = len(window_profiles.get(pid, []))
            if recent_appearances > 0:
                continue
            if len(ext_profiles.get(pid, [])) > 0:
                continue

            # Use season-wide possession history as injection source
            season_result = _get_season_possession_share(
                pid, team_id, season, conn, list(ext_game_ids)
            )
            if season_result is None:
                continue

            season_share, n_season_games = season_result
            # 0.50 discount: season data may be months old, role may have changed
            injected_share = season_share * 0.50
            injected_minutes = injected_share * 240

            name = player_id_to_name.get(pid, roster_player["display_name"])
            injected[pid] = (injected_minutes, 0.03 * 240)
            logger.info(
                "Fix A Phase 2 (ESPN roster): Injecting %s (%s) | ovr=%.2f | "
                "season=%d games | season_share=%.1f%% → inject=%.1f%%",
                name, pid, overall,
                n_season_games, season_share * 100, injected_share * 100,
            )

    if not injected:
        return profile

    # Merge injected players into profile; simulate_game normalizes via shares_from_minutes()
    return MinutesProfile({**profile, **injected})


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _confidence_tier(pred_spread: float) -> tuple[str, str]:
    """Return (tier_label, accuracy_note) for a predicted spread magnitude."""
    abs_pred = abs(pred_spread)
    if abs_pred >= 10:
        return "HIGH", "86% dir acc (backtest)"
    elif abs_pred >= 7:
        return "MODERATE", "82% dir acc (backtest)"
    elif abs_pred >= 5:
        return "FAIR", "79% dir acc (backtest)"
    else:
        return "LOW SIGNAL", "< 73% dir acc — use caution"


def _abbrev(team_name: str) -> str:
    return next(
        (v["abbrev"] for v in NBA_TEAM_MAP.values() if v["name"] == team_name),
        team_name[:3].upper(),
    )


def _format_spread(spread: float, home_name: str, away_name: str) -> str:
    if spread >= 0:
        return f"{_abbrev(home_name)} -{spread:.1f}"
    return f"{_abbrev(away_name)} -{abs(spread):.1f}"


def _print_report(predictions: list[dict], target_date: date, injuries_available: bool) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\nNBA Predictions — {target_date}  (generated {now})")
    if not injuries_available:
        print("  [WARNING: injury data unavailable — predictions assume full rosters]")
    print("=" * 68)

    spread_edges: list[float] = []
    prob_edges: list[float] = []
    tier_counts: dict[str, int] = {"HIGH": 0, "MODERATE": 0, "FAIR": 0, "LOW SIGNAL": 0}

    for p in predictions:
        home = p["home_team_name"]
        away = p["away_team_name"]
        our_spread = p["predicted_spread"]
        our_prob = p["predicted_win_prob"]
        mkt_spread = p["market_spread"]
        mkt_prob = p["market_win_prob"]
        mkt_total = p["market_total"]
        sim_std = p["sim_std"]

        notes = []
        if p["home_b2b"]:
            notes.append(f"{_abbrev(home)} B2B")
        if p["away_b2b"]:
            notes.append(f"{_abbrev(away)} B2B")

        our_spread_str = _format_spread(our_spread, home, away)
        mkt_spread_str = _format_spread(mkt_spread, home, away) if mkt_spread is not None else "N/A"
        spread_edge = p["spread_edge"]
        prob_edge = p["win_prob_edge"]
        edge_sign = "+" if spread_edge is not None and spread_edge > 0 else ""
        prob_sign = "+" if prob_edge is not None and prob_edge > 0 else ""
        home_cov = p.get("home_coverage", 1.0) or 1.0
        away_cov = p.get("away_coverage", 1.0) or 1.0
        sigma_inj = p.get("sigma_injury", 0.0) or 0.0

        print(f"\n{away} @ {home}")

        spread_line = f"  Spread   : Our {our_spread_str} ± {sim_std:.1f}"
        if sigma_inj > 0.5:
            spread_line += f" (inj+{sigma_inj:.1f})"
        if mkt_spread is not None:
            spread_line += f"    Market: {mkt_spread_str}"
        if spread_edge is not None:
            spread_line += f"    Edge: {edge_sign}{spread_edge:.1f}"
        print(spread_line)

        home_ab = _abbrev(home)
        prob_line = f"  Win prob : Our {home_ab} {our_prob*100:.0f}%"
        if mkt_prob is not None:
            prob_line += f"          Market: {home_ab} {mkt_prob*100:.0f}%"
        if prob_edge is not None:
            prob_line += f"    Edge: {prob_sign}{prob_edge*100:.0f}pp"
        print(prob_line)

        if mkt_total is not None:
            print(f"  Total    : Market O/U {mkt_total:.1f}")
        cov_parts = [f"{home_ab} {home_cov:.0%}"]
        cov_parts.append(f"{_abbrev(away)} {away_cov:.0%}")
        print(f"  Coverage : {' | '.join(cov_parts)}")
        print(f"  Notes    : {', '.join(notes) if notes else 'none'}")

        tier, acc_note = _confidence_tier(our_spread)
        # Coverage gate: downgrade HIGH → MODERATE when either team has weak lineup coverage.
        # A game with <85% coverage has elevated uncertainty regardless of spread magnitude.
        if tier == "HIGH" and min(home_cov, away_cov) < COVERAGE_GATE_THRESHOLD:
            tier = "MODERATE"
            acc_note = f"82% dir acc — downgraded from HIGH (coverage {min(home_cov, away_cov):.0%} < {COVERAGE_GATE_THRESHOLD:.0%})"
        tier_counts[tier] += 1
        print(f"  Confidence: {tier}  ({acc_note})")

        # Adverse market edge warning: market has likely priced in injury intel we're missing.
        if spread_edge is not None and spread_edge < -ADVERSE_MARKET_EDGE_THRESHOLD:
            print(f"  *** ADVERSE MARKET EDGE {abs(spread_edge):.1f} pts — market likely has injury intel. Do not bet against market direction.")

        if spread_edge is not None:
            spread_edges.append(abs(spread_edge))
        if prob_edge is not None:
            prob_edges.append(abs(prob_edge))

    print("\n" + "=" * 68)
    parts = []
    if spread_edges:
        parts.append(f"Avg |spread edge|: {sum(spread_edges)/len(spread_edges):.1f} pts")
    if prob_edges:
        parts.append(f"Avg |win prob edge|: {sum(prob_edges)/len(prob_edges)*100:.1f}pp")
    if parts:
        print("  |  ".join(parts))

    # Confidence tier summary across today's slate
    tier_parts = [
        f"{cnt} {label}"
        for label, cnt in tier_counts.items()
        if cnt > 0
    ]
    if tier_parts:
        print(f"Confidence: {', '.join(tier_parts)}")

    print(f"{len(predictions)} predictions written to DB.\n")


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_predictions(
    target_date: date | None = None,
    db_path: str = DB_PATH,
    season: str = INITIAL_SEASON,
    n_simulations: int = MONTE_CARLO_SIMULATIONS,
) -> list[dict]:
    """Generate and store predictions for all NBA games on target_date."""
    if target_date is None:
        target_date = date.today() + timedelta(days=1)

    logger.info("Generating predictions for %s", target_date)

    # --- Load calibration coefficients ---
    try:
        coeffs = load_calibration(CALIBRATION_PATH)
    except FileNotFoundError:
        logger.error(
            "Calibration file not found. Run: PYTHONPATH=. uv run python downstream/calibration.py"
        )
        return []

    alpha = coeffs["alpha"]
    beta_hca_fallback = coeffs["beta_hca"]
    beta_hca_by_team: dict[str, float] = coeffs.get("beta_hca_by_team", {})
    beta_b2b_home = coeffs["beta_b2b_home"]
    beta_b2b_away = coeffs["beta_b2b_away"]
    sigma_residual = coeffs["sigma_residual"]

    # --- Fetch market odds ---
    logger.info("Fetching Odds API lines for %s...", target_date)
    games_odds: list[GameOdds] = get_nba_odds(target_date=target_date)
    if not games_odds:
        logger.warning("No games found for %s in Odds API", target_date)
        return []
    logger.info("Found %d games in Odds API", len(games_odds))

    # --- Injury report from ESPN (public API, no auth required) ---
    injured_names: set[str] = set()
    injuries_available = False
    try:
        espn_injuries = get_nba_injuries()
        injured_names = get_out_player_names(espn_injuries)
        injuries_available = True
        logger.info("ESPN injury report: %d out/doubtful players excluded from lineups", len(injured_names))
    except Exception as exc:
        logger.warning("Injury report unavailable (%s) — proceeding with full rosters", exc)

    # --- ESPN rosters for all teams playing tonight (Fix A Phase 2) ---
    # Pre-fetch once per team so _inject_returning_players() can detect multi-month returners
    # that have zero appearance history in both the 15- and 30-game lookback windows.
    espn_rosters: dict[str, list[EspnRosterPlayer]] = {}
    team_ids_tonight = set()
    for g in games_odds:
        for team_name in (g["home_team"], g["away_team"]):
            nba_id = team_id_from_name(team_name)
            if nba_id:
                team_ids_tonight.add(nba_id)
    for nba_id in team_ids_tonight:
        espn_id = ESPN_TEAM_ID_MAP.get(nba_id)
        if espn_id:
            try:
                espn_rosters[nba_id] = get_nba_roster(espn_id)
            except Exception as exc:
                logger.warning("ESPN roster fetch failed for team %s: %s", nba_id, exc)

    # --- Map team names from Odds API → nba.com IDs ---
    name_to_nba_id: dict[str, str] = {}
    for g in games_odds:
        for team_name in (g["home_team"], g["away_team"]):
            nba_id = team_id_from_name(team_name)
            if nba_id is None:
                logger.warning("Unknown Odds API team name: '%s'", team_name)
            else:
                name_to_nba_id[team_name] = nba_id

    # --- DB queries ---
    conn = _get_conn(db_path)
    try:
        player_ratings = _load_player_ratings(conn, season)
        league_avg_ppp, league_avg_pace = _load_league_avg(conn, season)

        # Build player_id → name for injury filtering
        player_id_to_name: dict[str, str] = {
            r["player_id"]: r["player_name"]
            for r in conn.execute("SELECT player_id, player_name FROM players").fetchall()
        }

        predictions: list[dict] = []

        for game in games_odds:
            home_name = game["home_team"]
            away_name = game["away_team"]

            home_nba_id = name_to_nba_id.get(home_name)
            away_nba_id = name_to_nba_id.get(away_name)

            if home_nba_id is None or away_nba_id is None:
                logger.warning("Skipping — unmapped team(s): %s @ %s", away_name, home_name)
                continue

            home_b2b = _detect_b2b(home_nba_id, target_date, conn)
            away_b2b = _detect_b2b(away_nba_id, target_date, conn)

            # Build lineup profiles from our DB possession history
            home_mins, home_coverage = _build_minutes_profile_from_db(
                home_nba_id, conn, injured_names, player_id_to_name, season=season,
                espn_roster=espn_rosters.get(home_nba_id),
            )
            away_mins, away_coverage = _build_minutes_profile_from_db(
                away_nba_id, conn, injured_names, player_id_to_name, season=season,
                espn_roster=espn_rosters.get(away_nba_id),
            )

            if not home_mins or not away_mins:
                logger.warning("Insufficient lineup data for %s @ %s", away_name, home_name)
                continue

            # Restrict to players with ratings in our model
            home_ratings = {pid: player_ratings[pid] for pid in home_mins if pid in player_ratings}
            away_ratings = {pid: player_ratings[pid] for pid in away_mins if pid in player_ratings}

            if not home_ratings or not away_ratings:
                logger.warning("No rated players found for %s @ %s", away_name, home_name)
                continue

            # Monte Carlo simulation
            sim = simulate_game(
                home_mins, away_mins,
                home_ratings, away_ratings,
                league_avg_ppp, league_avg_pace,
                n_simulations=n_simulations,
            )

            # Apply calibration to mean raw margin
            team_hca = beta_hca_by_team.get(home_nba_id, beta_hca_fallback)
            predicted_spread = apply_calibration(
                sim.mean_margin,
                alpha=alpha,
                beta_hca=team_hca,
                beta_b2b_home=beta_b2b_home,
                beta_b2b_away=beta_b2b_away,
                home_b2b=home_b2b,
                away_b2b=away_b2b,
            )

            # Injury uncertainty: extra σ when significant minutes are missing.
            # Scale: σ_residual × 1.5 × (2 - home_coverage - away_coverage).
            # At full health (1.0, 1.0): σ_injury = 0. At both 70%: σ_injury ≈ 0.9 × σ_residual.
            sigma_injury = sigma_residual * 1.5 * max(0.0, 2.0 - home_coverage - away_coverage)

            # Total uncertainty: residual + Monte Carlo lineup variance + injury adjustment
            total_sigma = math.sqrt(sim.std_margin ** 2 + sigma_residual ** 2 + sigma_injury ** 2)
            predicted_win_prob = margin_to_win_prob(predicted_spread, total_sigma)

            spread_edge = (
                predicted_spread - game["market_spread"]
                if game["market_spread"] is not None else None
            )
            win_prob_edge = (
                predicted_win_prob - game["market_win_prob"]
                if game["market_win_prob"] is not None else None
            )

            pred = {
                "odds_event_id": game["odds_event_id"],
                "game_date": game["game_date"],
                "home_team_id": home_nba_id,
                "away_team_id": away_nba_id,
                "home_team_name": home_name,
                "away_team_name": away_name,
                "predicted_spread": round(predicted_spread, 2),
                "predicted_win_prob": round(predicted_win_prob, 4),
                "sim_std": round(total_sigma, 2),  # total uncertainty (calibration + injury + lineup)
                "market_spread": game["market_spread"],
                "market_win_prob": (
                    round(game["market_win_prob"], 4) if game["market_win_prob"] is not None else None
                ),
                "market_total": game["market_total"],
                "spread_edge": round(spread_edge, 2) if spread_edge is not None else None,
                "win_prob_edge": round(win_prob_edge, 4) if win_prob_edge is not None else None,
                "home_b2b": int(home_b2b),
                "away_b2b": int(away_b2b),
                "n_simulations": n_simulations,
                "home_coverage": round(home_coverage, 4),
                "away_coverage": round(away_coverage, 4),
                "sigma_injury": round(sigma_injury, 2),  # not stored in DB, used for report
            }
            predictions.append(pred)

        with conn:
            for pred in predictions:
                _upsert_prediction(conn, pred)

    finally:
        conn.close()

    _print_report(predictions, target_date, injuries_available)
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate NBA spread/win probability predictions")
    parser.add_argument("--date", type=date.fromisoformat, default=None,
                        help="Target date YYYY-MM-DD (default: tomorrow)")
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--season", default=INITIAL_SEASON)
    parser.add_argument("--sims", type=int, default=MONTE_CARLO_SIMULATIONS)
    args = parser.parse_args()
    run_predictions(target_date=args.date, db_path=args.db, season=args.season, n_simulations=args.sims)


if __name__ == "__main__":
    main()
