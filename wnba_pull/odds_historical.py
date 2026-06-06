"""Current-season WNBA closing lines from the-odds-api historical endpoints.

Strategy (credit-bounded):
  1. Enumerate season game dates from nba_api (free).
  2. One historical *events* snapshot per date (1 credit each) -> unique event ids
     + commence times.
  3. For each completed event, one per-event historical *odds* call at the game's
     commence_time (= last pre-tip snapshot = closing line). 30 credits each
     (10x x 3 markets x 1 region).

Hard credit cap from config.HIST_ODDS_CREDIT_CAP; stops before exceeding it.
"""
from datetime import datetime, timedelta, timezone

import pandas as pd

from wnba_pull import config, util

_HIST_BASE = f"https://api.the-odds-api.com/v4/historical/sports/{config.ODDS_SPORT}"


def _season_dates(season: str) -> list[str]:
    from nba_api.stats.endpoints import LeagueGameLog
    df = LeagueGameLog(league_id="10", season=season,
                       season_type_all_star="Regular Season").get_data_frames()[0]
    return sorted(df["GAME_DATE"].unique().tolist())  # 'YYYY-MM-DD'


def _enumerate_events(dates: list[str]) -> dict[str, dict]:
    """Return {event_id: {commence_time, home, away}} deduped across date snapshots."""
    events: dict[str, dict] = {}
    for d in dates:
        snap = f"{d}T12:00:00Z"
        data, headers = util.get_json(f"{_HIST_BASE}/events",
                                      {"apiKey": config.ODDS_API_KEY, "date": snap})
        util.record_credits(headers, 1)
        rows = (data or {}).get("data", []) if isinstance(data, dict) else []
        for e in rows:
            events.setdefault(e["id"], {
                "commence_time": e.get("commence_time"),
                "home_team": e.get("home_team"),
                "away_team": e.get("away_team"),
            })
    util.log(f"  historical: enumerated {len(events)} unique events over {len(dates)} dates")
    return events


def _odds_at(event_id: str, meta: dict, date_iso: str, line_type: str) -> list[dict]:
    """Pull the historical odds snapshot at/just-before date_iso for one event.
    line_type tags rows 'close' (snapshot at tipoff) or 'open' (snapshot ~lead h before)."""
    cost = 10 * len(config.HIST_MARKETS) * len(config.ODDS_REGIONS.split(","))
    params = {
        "apiKey": config.ODDS_API_KEY,
        "regions": config.ODDS_REGIONS,
        "markets": ",".join(config.HIST_MARKETS),
        "oddsFormat": config.ODDS_BOOKMAKER_FORMAT,
        "date": date_iso,
    }
    data, headers = util.get_json(f"{_HIST_BASE}/events/{event_id}/odds", params)
    util.record_credits(headers, cost)
    ev = (data or {}).get("data", {}) if isinstance(data, dict) else {}
    snap_ts = (data or {}).get("timestamp") if isinstance(data, dict) else None
    rows = []
    for bm in ev.get("bookmakers", []):
        for mk in bm.get("markets", []):
            for oc in mk.get("outcomes", []):
                rows.append({
                    "event_id": event_id,
                    "line_type": line_type,
                    "snapshot_ts": snap_ts,
                    "commence_time": meta["commence_time"],
                    "home_team": meta["home_team"],
                    "away_team": meta["away_team"],
                    "bookmaker": bm.get("key"),
                    "market": mk.get("key"),
                    "outcome_name": oc.get("name"),
                    "price": oc.get("price"),
                    "point": oc.get("point"),
                })
    return rows


def run(season: str | None = None, credit_cap: int | None = None,
        line_type: str = "close", lead_hours: int | None = None) -> None:
    """line_type='close' snapshots at tipoff; 'open' snapshots `lead_hours`
    before tipoff (default config.HIST_OPEN_LEAD_HOURS) as the day-before opener."""
    season = season or config.HIST_SEASON
    cap = credit_cap if credit_cap is not None else config.HIST_ODDS_CREDIT_CAP
    lead = lead_hours if lead_hours is not None else config.HIST_OPEN_LEAD_HOURS
    dataset = "historical_opening_lines" if line_type == "open" else "historical_closing_lines"
    prefix = "opening" if line_type == "open" else "closing"
    util.log(f"HISTORICAL ODDS: starting ({prefix} lines, season {season}, cap {cap}"
             + (f", lead {lead}h)" if line_type == "open" else ")"))
    dates = _season_dates(season)
    events = _enumerate_events(dates)
    now = datetime.now(timezone.utc)
    completed = {eid: m for eid, m in events.items()
                 if m["commence_time"] and
                 datetime.fromisoformat(m["commence_time"].replace("Z", "+00:00")) < now}
    util.log(f"  historical: {len(completed)} completed games for {prefix} lines")

    per_call = 10 * len(config.HIST_MARKETS) * len(config.ODDS_REGIONS.split(","))
    all_rows, fetched = [], 0
    for eid, meta in sorted(completed.items(), key=lambda kv: kv[1]["commence_time"]):
        st = util.credit_state()
        if fetched * per_call + per_call > cap:
            util.log(f"  historical: hit credit cap ({cap}); stopping after {fetched} games")
            break
        tip = datetime.fromisoformat(meta["commence_time"].replace("Z", "+00:00"))
        when = (tip - timedelta(hours=lead)) if line_type == "open" else tip
        date_iso = when.strftime("%Y-%m-%dT%H:%M:%SZ")
        all_rows.extend(_odds_at(eid, meta, date_iso, line_type))
        fetched += 1
        if fetched % 10 == 0:
            util.log(f"  historical: {fetched}/{len(completed)} games "
                     f"(~{fetched*per_call} cr; remaining {st.get('last_remaining')})")
    util.write_dataset(pd.DataFrame(all_rows), dataset, f"{prefix}_{season}")
    util.log(f"HISTORICAL ODDS: done. {fetched} games, {len(all_rows)} rows, "
             f"~{fetched*per_call} credits spent")


if __name__ == "__main__":
    # Usage: python -m wnba_pull.odds_historical [SEASON] [CREDIT_CAP] [open|close]
    # e.g.   python -m wnba_pull.odds_historical 2025 20000 open
    import sys
    _season = sys.argv[1] if len(sys.argv) > 1 else None
    _cap = int(sys.argv[2]) if len(sys.argv) > 2 else None
    _lt = sys.argv[3] if len(sys.argv) > 3 else "close"
    run(_season, _cap, _lt)
