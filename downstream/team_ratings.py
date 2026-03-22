"""Pure functions for aggregating player ratings to team-level ratings.

No DB I/O — accepts data as arguments, returns results.
"""
import unicodedata
from typing import TypedDict


class PlayerRating(TypedDict):
    player_id: str
    offense: float
    defense: float
    pace: float


class TeamRatings(TypedDict):
    offense: float   # weighted avg offensive rating (pts/100 above avg)
    defense: float   # weighted avg defensive rating (positive = allows more)
    pace: float      # weighted avg pace rating


def normalize_name(name: str) -> str:
    """Lowercase, strip accents, remove Jr./Sr./II/III suffixes for ID matching."""
    # Normalize unicode (e.g. Dončić → Doncic)
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = nfkd.encode("ascii", "ignore").decode("ascii")
    lower = ascii_name.lower().strip()
    # Remove common suffixes
    for suffix in (" jr.", " sr.", " ii", " iii", " iv"):
        if lower.endswith(suffix):
            lower = lower[: -len(suffix)].strip()
    return lower


def build_name_to_id(players: list[dict]) -> dict[str, str]:
    """Build normalized-name → player_id lookup from a list of player dicts.

    Each dict must have keys: player_id, player_name.
    """
    return {normalize_name(p["player_name"]): p["player_id"] for p in players}


def compute_team_ratings(
    player_ratings: dict[str, PlayerRating],
    possession_shares: dict[str, float],
) -> TeamRatings:
    """Aggregate player ratings into a single team rating vector.

    Args:
        player_ratings: map of player_id → PlayerRating (offense, defense, pace)
        possession_shares: map of player_id → fraction of team possessions
            (values should sum to ~1.0; players absent from player_ratings are skipped)

    Returns:
        TeamRatings with weighted-average offense, defense, pace.
    """
    total_off = 0.0
    total_def = 0.0
    total_pace = 0.0
    total_weight = 0.0

    for pid, share in possession_shares.items():
        if pid not in player_ratings:
            # Treat as league-average (0.0 in all dimensions)
            total_weight += share
            continue
        r = player_ratings[pid]
        total_off += r["offense"] * share
        total_def += r["defense"] * share
        total_pace += r["pace"] * share
        total_weight += share

    if total_weight == 0.0:
        return TeamRatings(offense=0.0, defense=0.0, pace=0.0)

    # Re-normalize in case some players had no ratings
    return TeamRatings(
        offense=total_off / total_weight,
        defense=total_def / total_weight,
        pace=total_pace / total_weight,
    )


def compute_raw_margin(
    home_ratings: TeamRatings,
    away_ratings: TeamRatings,
    league_avg_ppp: float,
    league_avg_pace: float,
) -> float:
    """Compute raw predicted home margin (points) before calibration adjustments.

    Formula:
        expected_home_PPP = league_avg_ppp + (home_off + away_def) / 100
        expected_away_PPP = league_avg_ppp + (away_off + home_def) / 100

    Note: defense coef sign convention — positive = bad defender (allows more than avg),
    negative = good defender (allows fewer). So +away_def means bad away D → home scores more. ✓
        expected_possessions = league_avg_pace + (home_pace + away_pace) / 2
        raw_margin = (expected_home_PPP - expected_away_PPP) * expected_possessions

    Args:
        home_ratings: team ratings for the home team
        away_ratings: team ratings for the away team
        league_avg_ppp: league average points per possession
        league_avg_pace: league average possessions per team per game

    Returns:
        Raw expected home margin in points (positive = home wins).
    """
    home_ppp = league_avg_ppp + (home_ratings["offense"] + away_ratings["defense"]) / 100
    away_ppp = league_avg_ppp + (away_ratings["offense"] + home_ratings["defense"]) / 100
    expected_pace = league_avg_pace + (home_ratings["pace"] + away_ratings["pace"]) / 2
    return (home_ppp - away_ppp) * expected_pace


def shares_from_minutes(minutes: dict[str, float]) -> dict[str, float]:
    """Convert raw minutes dict to possession-share dict (values sum to 1.0).

    Args:
        minutes: player_id → estimated minutes played

    Returns:
        player_id → possession share (0–1)
    """
    total = sum(minutes.values())
    if total == 0.0:
        return {pid: 0.0 for pid in minutes}
    return {pid: mins / total for pid, mins in minutes.items()}
