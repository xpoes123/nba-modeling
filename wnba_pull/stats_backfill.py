"""Free WNBA stat backfill from stats.wnba.com (nba_api) + pbpstats.

Covers the last ~3 seasons. Resumable: per-game outputs are skipped if already
present, so the job can die and restart without re-downloading everything.

Outputs (under wnba_data/):
  schedule_results/season_<S>.parquet      team-game rows (scores, team box basics)
  player_box/<game_id>.parquet             per-player traditional + advanced box
  pbp_events/<game_id>.parquet             lineup-attributed play-by-play (pbpstats)
  shots/season_<S>.parquet                 every shot with x/y court coords
  team_season/base_<S>.parquet, adv_<S>    season team aggregates
  player_season/base_<S>.parquet, adv_<S>  season player aggregates
  players/season_<S>.parquet               player directory (team, years active)
"""
import time

import pandas as pd

from wnba_pull import config, util

# pbpstats falls back to data.wnba.com to cross-check event order on some games,
# but that host is DEAD. The constant is imported by-value per module, so patch
# the data_nba web loader directly to fail fast (6s) instead of hanging 30s.
import pbpstats.data_loader.data_nba.web_loader as _dnw  # noqa: E402
_dnw.REQUEST_TIMEOUT = 6

WNBA_LEAGUE = "10"
_TIMEOUT = 60  # stats.nba.com is slow; give it room


def _sleep():
    time.sleep(config.STATS_SLEEP_SEC)


def _retry(fn, what: str, tries: int = 4):
    """stats.nba.com is flaky — retry with backoff. Returns fn() or None."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            util.log(f"  {what} retry {i+1}/{tries}: {e}")
            time.sleep(3 * (i + 1))
    util.log(f"  {what} GAVE UP after {tries} tries")
    return None


def schedule_and_team_box() -> list[str]:
    """LeagueGameLog per season -> team-game rows. Returns all game_ids found."""
    from nba_api.stats.endpoints import LeagueGameLog
    all_ids = set()
    for s in config.SEASONS:
        df = _retry(lambda s=s: LeagueGameLog(
            league_id=WNBA_LEAGUE, season=s, season_type_all_star="Regular Season",
            timeout=_TIMEOUT).get_data_frames()[0], f"schedule {s}")
        if df is None:
            continue
        util.write_dataset(df, "schedule_results", f"season_{s}")
        all_ids.update(df["GAME_ID"].unique().tolist())
        util.log(f"  schedule {s}: {len(df)} team-game rows, {df['GAME_ID'].nunique()} games")
        _sleep()
    return sorted(all_ids)


def season_aggregates() -> None:
    # NOTE: LeagueDashTeamStats / LeagueDashPlayerStats return empty bodies for
    # WNBA (league_id=10) — those dashboards are not WNBA-supported. Season
    # aggregates are instead derivable from player_box + schedule_results.
    # CommonAllPlayers DOES work, so we keep the player directory.
    from nba_api.stats.endpoints import CommonAllPlayers
    for s in config.SEASONS:
        ap = _retry(lambda s=s: CommonAllPlayers(
            league_id=WNBA_LEAGUE, season=s, is_only_current_season=0,
            timeout=_TIMEOUT).get_data_frames()[0], f"players {s}")
        if ap is not None:
            util.write_dataset(ap, "players", f"season_{s}")
        _sleep()
        util.log(f"  players {s}: done")


def shots() -> None:
    from nba_api.stats.endpoints import ShotChartDetail
    for s in config.SEASONS:
        out = config.OUT / "shots" / f"season_{s}.parquet"
        if out.exists():
            util.log(f"  shots {s}: already present, skip")
            continue
        df = _retry(lambda s=s: ShotChartDetail(
            team_id=0, player_id=0, season_nullable=s,
            season_type_all_star="Regular Season", league_id=WNBA_LEAGUE,
            context_measure_simple="FGA", timeout=90).get_data_frames()[0],
            f"shots {s}")
        if df is not None:
            util.write_dataset(df, "shots", f"season_{s}")
            util.log(f"  shots {s}: {len(df)} shots")
        _sleep()


def player_box_for_game(game_id: str) -> bool:
    """Traditional + advanced player box for one game. Returns True if written."""
    out = config.OUT / "player_box" / f"{game_id}.parquet"
    if out.exists():
        return False
    from nba_api.stats.endpoints import BoxScoreTraditionalV3, BoxScoreAdvancedV3
    trad = _retry(lambda: BoxScoreTraditionalV3(
        game_id=game_id, timeout=_TIMEOUT).player_stats.get_data_frame(),
        f"box {game_id}")
    if trad is None:
        return False
    _sleep()
    adv = _retry(lambda: BoxScoreAdvancedV3(
        game_id=game_id, timeout=_TIMEOUT).player_stats.get_data_frame(),
        f"box-adv {game_id}", tries=2)
    if adv is not None:
        keep = [c for c in adv.columns if c not in trad.columns or c == "personId"]
        df = trad.merge(adv[keep], on="personId", how="left", suffixes=("", "_adv"))
    else:
        df = trad
    df.insert(0, "game_id", game_id)
    util.write_dataset(df, "player_box", game_id)
    _sleep()
    return True


def pbp_raw_for_game(game_id: str) -> bool:
    """Raw play-by-play via nba_api PlayByPlayV2 (stats.wnba.com — reliable for
    every game). The guaranteed baseline; pbpstats lineups are a bonus on top."""
    out = config.OUT / "pbp_raw" / f"{game_id}.parquet"
    if out.exists():
        return False
    from nba_api.stats.endpoints import PlayByPlayV2
    df = _retry(lambda: PlayByPlayV2(game_id=game_id, timeout=_TIMEOUT).get_data_frames()[0],
                f"pbp_raw {game_id}")
    if df is None:
        return False
    util.write_dataset(df, "pbp_raw", game_id)
    _sleep()
    return True


def pbp_for_game(game_id: str) -> bool:
    """Lineup-attributed play-by-play via pbpstats. Best-effort: some WNBA games
    trip a rebound-order check that needs the dead data.wnba.com host and fail
    fast (~6s). Returns True if written."""
    out = config.OUT / "pbp_events" / f"{game_id}.parquet"
    if out.exists():
        return False
    from pbpstats.client import Client
    settings = {"Games": {"source": "web", "data_provider": "stats_nba"},
                "Possessions": {"source": "web", "data_provider": "stats_nba"}}
    g = _retry(lambda: Client(settings).Game(game_id), f"pbp {game_id}", tries=1)
    if g is None:
        return False
    try:
        rows = []
        events = [e for p in g.possessions.items for e in p.events]
        for ev in events:
            cp = getattr(ev, "current_players", {}) or {}
            # flatten on-court players into two team columns (sorted id strings)
            teams = sorted(cp.keys())
            lineup = {f"team{i+1}_id": t for i, t in enumerate(teams)}
            for i, t in enumerate(teams):
                lineup[f"team{i+1}_players"] = "-".join(str(x) for x in sorted(cp[t]))
            rows.append({
                "game_id": game_id,
                "period": getattr(ev, "period", None),
                "event_num": getattr(ev, "event_num", None),
                "clock": getattr(ev, "clock", None),
                "seconds_remaining": getattr(ev, "seconds_remaining", None),
                "team_id": getattr(ev, "team_id", None),
                "player1_id": getattr(ev, "player1_id", None),
                "player2_id": getattr(ev, "player2_id", None),
                "player3_id": getattr(ev, "player3_id", None),
                "event_type": type(ev).__name__,
                "description": getattr(ev, "description", None),
                "score_margin": getattr(ev, "score_margin", None),
                **lineup,
            })
        util.write_dataset(pd.DataFrame(rows), "pbp_events", game_id)
        return True
    except Exception as e:  # noqa: BLE001
        util.log(f"  pbp {game_id} FAILED: {e}")
        return False


def run() -> None:
    util.log("STATS BACKFILL: starting")
    util.log("STATS: schedule + team box")
    game_ids = schedule_and_team_box()
    util.log(f"STATS: {len(game_ids)} unique games across {config.SEASONS}")
    util.log("STATS: season aggregates + players")
    season_aggregates()
    util.log("STATS: shot charts")
    shots()
    util.log("STATS: per-game box + raw pbp (all games) + lineup pbp (best-effort), resumable")
    done_box = done_raw = done_pbp = 0
    for i, gid in enumerate(game_ids, 1):
        if player_box_for_game(gid):
            done_box += 1
        if pbp_raw_for_game(gid):
            done_raw += 1
        if pbp_for_game(gid):
            done_pbp += 1
        if i % 25 == 0:
            util.log(f"STATS: {i}/{len(game_ids)} games "
                     f"(new box={done_box}, raw={done_raw}, lineup={done_pbp})")
    util.log(f"STATS BACKFILL: done. new box={done_box}, raw={done_raw}, lineup={done_pbp}")


if __name__ == "__main__":
    run()
