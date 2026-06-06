"""Live sportsbook odds snapshots from the-odds-api (game lines + player props).

Each call is flattened to tidy long-format rows so Bill can pivot/merge easily:
one row per (game, bookmaker, market, outcome) with a snapshot timestamp.
"""
import pandas as pd

from wnba_pull import config, util


def _flatten_event(ev: dict, snap_ts: str) -> list[dict]:
    rows = []
    for bm in ev.get("bookmakers", []):
        for mk in bm.get("markets", []):
            for oc in mk.get("outcomes", []):
                rows.append({
                    "snapshot_ts": snap_ts,
                    "event_id": ev.get("id"),
                    "commence_time": ev.get("commence_time"),
                    "home_team": ev.get("home_team"),
                    "away_team": ev.get("away_team"),
                    "bookmaker": bm.get("key"),
                    "bookmaker_title": bm.get("title"),
                    "market": mk.get("key"),
                    "last_update": mk.get("last_update") or bm.get("last_update"),
                    "outcome_name": oc.get("name"),
                    "outcome_desc": oc.get("description"),   # player name for props
                    "price": oc.get("price"),
                    "point": oc.get("point"),
                })
    return rows


def pull_game_lines(snap_ts: str) -> int:
    """One call: h2h+spreads+totals for all WNBA games. Returns credits spent."""
    url = f"https://api.the-odds-api.com/v4/sports/{config.ODDS_SPORT}/odds"
    params = {
        "apiKey": config.ODDS_API_KEY,
        "regions": config.ODDS_REGIONS,
        "markets": ",".join(config.ODDS_GAME_MARKETS),
        "oddsFormat": config.ODDS_BOOKMAKER_FORMAT,
    }
    data, headers = util.get_json(url, params)
    cost = len(config.ODDS_GAME_MARKETS) * len(config.ODDS_REGIONS.split(","))
    util.record_credits(headers, cost)
    if not data:
        util.log("  game lines: no data")
        return cost
    rows = []
    for ev in data:
        rows.extend(_flatten_event(ev, snap_ts))
    util.write_dataset(pd.DataFrame(rows), "live_game_lines", f"lines_{snap_ts}")
    util.log(f"  game lines: {len(data)} games, {len(rows)} rows  (cost {cost} cr)")
    return cost


def pull_props(snap_ts: str) -> int:
    """Per-event prop calls. Returns credits spent."""
    ev_url = f"https://api.the-odds-api.com/v4/sports/{config.ODDS_SPORT}/events"
    events, _ = util.get_json(ev_url, {"apiKey": config.ODDS_API_KEY})  # events endpoint = free
    if not events:
        util.log("  props: no upcoming events")
        return 0
    rows, cost = [], 0
    per_event = len(config.ODDS_PROP_MARKETS) * len(config.ODDS_REGIONS.split(","))
    for ev in events:
        url = (f"https://api.the-odds-api.com/v4/sports/{config.ODDS_SPORT}"
               f"/events/{ev['id']}/odds")
        params = {
            "apiKey": config.ODDS_API_KEY,
            "regions": config.ODDS_REGIONS,
            "markets": ",".join(config.ODDS_PROP_MARKETS),
            "oddsFormat": config.ODDS_BOOKMAKER_FORMAT,
        }
        data, headers = util.get_json(url, params)
        cost += per_event
        util.record_credits(headers, per_event)
        if data:
            rows.extend(_flatten_event(data, snap_ts))
    util.write_dataset(pd.DataFrame(rows), "live_props", f"props_{snap_ts}")
    util.log(f"  props: {len(events)} events, {len(rows)} rows  (cost {cost} cr)")
    return cost
