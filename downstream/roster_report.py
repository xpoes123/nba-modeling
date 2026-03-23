"""Roster report: player ratings, recent possession shares, and ESPN injury status.

Usage:
    PYTHONPATH=. uv run python downstream/roster_report.py --team ATL
    PYTHONPATH=. uv run python downstream/roster_report.py --team "Atlanta Hawks"
    PYTHONPATH=. uv run python downstream/roster_report.py --all
"""
import argparse
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DB_PATH, NBA_TEAM_MAP, team_id_from_abbrev, team_id_from_name
from downstream.espn_client import get_nba_injuries
from downstream.team_ratings import normalize_name

# Number of recent team games for recency-weighted possession share estimation
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


def _get_team_players(conn: sqlite3.Connection, team_id: str) -> list[dict]:
    """Return list of dicts with player_id, player_name, offense, defense, overall."""
    rows = conn.execute(
        """
        SELECT p.player_id, p.player_name, cr.offense, cr.defense, cr.overall
        FROM players p
        JOIN current_ratings cr ON p.player_id = cr.player_id
        WHERE p.team_id = ?
        """,
        (team_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _get_recent_game_ids(conn: sqlite3.Connection, team_id: str, n_games: int) -> list[str]:
    """Return up to n_games most recent game IDs for the team (newest first)."""
    rows = conn.execute(
        """
        SELECT game_id
        FROM games
        WHERE (home_team_id = ? OR away_team_id = ?)
        ORDER BY game_date DESC
        LIMIT ?
        """,
        (team_id, team_id, n_games),
    ).fetchall()
    return [r["game_id"] for r in rows]


def _compute_possession_shares(
    conn: sqlite3.Connection,
    team_id: str,
    game_ids: list[str],
) -> dict[str, float]:
    """Return recency-weighted possession share per player.

    Share = (sum of recency-weighted appearance counts) / (sum of all players' weighted counts).
    Players not appearing in any game get share 0.0.
    """
    if not game_ids:
        return {}

    # slot 0 = most recent game (weight 1.0), slot 1 = 0.85, ...
    game_weight: dict[str, float] = {gid: _RECENCY_DECAY ** i for i, gid in enumerate(game_ids)}

    placeholders = ",".join("?" * len(game_ids))
    rows = conn.execute(
        f"""
        SELECT game_id,
               off_player_1, off_player_2, off_player_3, off_player_4, off_player_5
        FROM possessions
        WHERE offense_team_id = ? AND game_id IN ({placeholders})
        """,
        [team_id] + game_ids,
    ).fetchall()

    # Accumulate weighted counts per player
    weighted_counts: dict[str, float] = {}
    off_cols = ["off_player_1", "off_player_2", "off_player_3", "off_player_4", "off_player_5"]

    # Group rows by game_id manually (sqlite3.Row doesn't support pandas)
    by_game: dict[str, list] = {}
    for row in rows:
        gid = row["game_id"]
        by_game.setdefault(gid, []).append(row)

    for gid, game_rows in by_game.items():
        w = game_weight.get(gid, 0.0)
        n_poss = len(game_rows)
        if n_poss == 0:
            continue
        counts: dict[str, int] = {}
        for row in game_rows:
            for col in off_cols:
                pid = row[col]
                if pid:
                    counts[pid] = counts.get(pid, 0) + 1
        for pid, cnt in counts.items():
            # Raw share within this game (each of 5 slots counts once per possession)
            raw_share = cnt / (n_poss * 5)
            weighted_counts[pid] = weighted_counts.get(pid, 0.0) + raw_share * w

    total = sum(weighted_counts.values())
    if total == 0.0:
        return {}

    return {pid: wc / total for pid, wc in weighted_counts.items()}


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def _resolve_team_id(arg: str) -> tuple[str | None, str | None]:
    """Return (team_id, abbrev) for the given team argument.

    Tries abbreviation first, then full name.
    """
    team_id = team_id_from_abbrev(arg.upper())
    if team_id is not None:
        abbrev = arg.upper()
        return team_id, abbrev

    team_id = team_id_from_name(arg)
    if team_id is not None:
        abbrev = NBA_TEAM_MAP[team_id]["abbrev"]
        return team_id, abbrev

    return None, None


def _format_rating(val: float) -> str:
    """Format a rating with explicit sign and 2 decimal places, e.g. '+2.24' or '-1.31'."""
    if val >= 0:
        return f"+{val:.2f}"
    return f"{val:.2f}"


def _build_report_lines(
    team_id: str,
    abbrev: str,
    conn: sqlite3.Connection,
    injury_lookup: dict[str, dict],
    today: date,
) -> list[str]:
    """Build report lines for one team."""
    lines: list[str] = []

    team_name = NBA_TEAM_MAP[team_id]["name"]
    lines.append(f"=== {team_name} ({abbrev}) — Roster Report {today} ===")

    players = _get_team_players(conn, team_id)
    if not players:
        lines.append("  (no players with current_ratings found for this team)")
        return lines

    game_ids = _get_recent_game_ids(conn, team_id, _LINEUP_LOOKBACK_GAMES)
    shares = _compute_possession_shares(conn, team_id, game_ids)

    # Attach possession share and injury info to each player
    enriched = []
    for p in players:
        pid = p["player_id"]
        poss_share = shares.get(pid, 0.0)
        norm = normalize_name(p["player_name"])
        inj = injury_lookup.get(norm)
        enriched.append({
            "player_id": pid,
            "player_name": p["player_name"],
            "offense": p["offense"],
            "defense": p["defense"],
            "overall": p["overall"],
            "poss_share": poss_share,
            "inj": inj,
        })

    # Sort: non-zero share DESC, then zero-share group by overall DESC
    def _sort_key(e: dict) -> tuple:
        if e["poss_share"] > 0:
            return (0, -e["poss_share"])
        return (1, -e["overall"])

    enriched.sort(key=_sort_key)

    # Column header
    lines.append(f"  {'OFF':>6}  {'DEF':>6}  {'OVR':>6}  {'POSS%':>5}  {'STATUS':<7}  PLAYER")

    for e in enriched:
        off_str = _format_rating(e["offense"])
        def_str = _format_rating(e["defense"])
        ovr_str = _format_rating(e["overall"])
        pct_str = f"{round(e['poss_share'] * 100)}%"

        inj = e["inj"]
        if inj is None:
            status_str = ""
            suffix = ""
        elif inj["is_out"]:
            status_str = "[OUT]"
            comment = inj.get("short_comment", "")
            status_raw = inj.get("status", "")
            detail = f"{comment}, {status_raw}" if comment else status_raw
            suffix = f"  ({detail})" if detail else ""
        elif inj["is_questionable"]:
            status_str = "[Q]"
            comment = inj.get("short_comment", "")
            status_raw = inj.get("status", "")
            detail = f"{comment}, {status_raw}" if comment else status_raw
            suffix = f"  ({detail})" if detail else ""
        else:
            status_str = ""
            suffix = ""

        lines.append(
            f"  {off_str:>6}  {def_str:>6}  {ovr_str:>6}  {pct_str:>5}  {status_str:<7}  {e['player_name']}{suffix}"
        )

    return lines


def generate_report(team_arg: str, db_path: str = DB_PATH) -> str:
    """Generate and return the roster report string for a single team."""
    team_id, abbrev = _resolve_team_id(team_arg)
    if team_id is None:
        return f"Error: unknown team '{team_arg}'. Use abbreviation (e.g. ATL) or full name."

    # Fetch ESPN injuries once
    injuries = get_nba_injuries()
    injury_lookup: dict[str, dict] = {inj["normalized_name"]: inj for inj in injuries}

    conn = _get_conn(db_path)
    try:
        lines = _build_report_lines(team_id, abbrev, conn, injury_lookup, date.today())
    finally:
        conn.close()

    return "\n".join(lines)


def generate_all_reports(db_path: str = DB_PATH) -> str:
    """Generate roster reports for all 30 teams."""
    injuries = get_nba_injuries()
    injury_lookup: dict[str, dict] = {inj["normalized_name"]: inj for inj in injuries}

    today = date.today()
    conn = _get_conn(db_path)
    try:
        all_lines: list[str] = []
        teams = sorted(NBA_TEAM_MAP.items(), key=lambda kv: kv[1]["name"])
        for i, (team_id, meta) in enumerate(teams):
            abbrev = meta["abbrev"]
            lines = _build_report_lines(team_id, abbrev, conn, injury_lookup, today)
            all_lines.extend(lines)
            if i < len(teams) - 1:
                all_lines.append("")  # blank line between teams
    finally:
        conn.close()

    return "\n".join(all_lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="NBA roster report: ratings + possession shares + injury status"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--team",
        metavar="TEAM",
        help="Team abbreviation (e.g. ATL) or full name (e.g. 'Atlanta Hawks')",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Print roster report for all 30 teams",
    )
    parser.add_argument("--db", default=DB_PATH, help="Path to SQLite database")
    args = parser.parse_args()

    if args.all:
        report = generate_all_reports(db_path=args.db)
    else:
        report = generate_report(args.team, db_path=args.db)

    # Use buffer write for safe non-ASCII player name output (e.g. Doncic)
    sys.stdout.buffer.write((report + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
