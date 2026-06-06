"""Live Kalshi WNBA prediction-market snapshots (public trade-api, no auth).

Captures, per cycle:
  - market quotes: yes/no bid/ask, last price, volume, open interest, status
  - top-of-book + depth (orderbook) for active game markets
  - recent trades (prints/fills) for microstructure analysis
Prices are in cents (0-100); divide by 100 for implied probability.
"""
import pandas as pd

from wnba_pull import config, util


def _events_for_series(series: str) -> list[dict]:
    url = f"{config.KALSHI_BASE}/events"
    params = {"series_ticker": series, "with_nested_markets": "true",
              "status": "open", "limit": 200}
    data, _ = util.get_json(url, params)
    return (data or {}).get("events", []) if isinstance(data, dict) else []


def pull_markets(snap_ts: str) -> list[str]:
    """Snapshot all active game + prop markets. Returns active market tickers."""
    rows, active_tickers = [], []
    for series in config.KALSHI_GAME_SERIES + config.KALSHI_PROP_SERIES:
        for ev in _events_for_series(series):
            for m in ev.get("markets", []):
                rows.append({
                    "snapshot_ts": snap_ts,
                    "series": series,
                    "event_ticker": ev.get("event_ticker"),
                    "event_title": ev.get("title"),
                    "market_ticker": m.get("ticker"),
                    "market_subtitle": m.get("yes_sub_title") or m.get("subtitle"),
                    "status": m.get("status"),
                    "yes_bid": m.get("yes_bid"),
                    "yes_ask": m.get("yes_ask"),
                    "no_bid": m.get("no_bid"),
                    "no_ask": m.get("no_ask"),
                    "last_price": m.get("last_price"),
                    "volume": m.get("volume"),
                    "volume_24h": m.get("volume_24h"),
                    "open_interest": m.get("open_interest"),
                    "close_time": m.get("close_time"),
                })
                if m.get("status") == "active":
                    active_tickers.append(m.get("ticker"))
    util.write_dataset(pd.DataFrame(rows), "kalshi_markets", f"kalshi_{snap_ts}")
    util.log(f"  kalshi markets: {len(rows)} rows, {len(active_tickers)} active")
    return active_tickers


def pull_orderbooks(tickers: list[str], snap_ts: str) -> None:
    """Resting depth. Kalshi returns orderbook_fp.{yes,no}_dollars as
    [price_in_dollars, size] levels (price 0-1 = implied probability)."""
    rows = []
    for t in tickers:
        url = f"{config.KALSHI_BASE}/markets/{t}/orderbook"
        data, _ = util.get_json(url, {"depth": 10})
        ob = (data or {}).get("orderbook_fp", {}) if isinstance(data, dict) else {}
        for side, key in (("yes", "yes_dollars"), ("no", "no_dollars")):
            for level in (ob.get(key) or []):
                rows.append({"snapshot_ts": snap_ts, "market_ticker": t, "side": side,
                             "price_dollars": float(level[0]), "size": float(level[1])})
    util.write_dataset(pd.DataFrame(rows), "kalshi_orderbook", f"ob_{snap_ts}")
    util.log(f"  kalshi orderbook: {len(rows)} levels across {len(tickers)} markets")


def pull_trades(tickers: list[str], snap_ts: str) -> None:
    rows = []
    for t in tickers:
        url = f"{config.KALSHI_BASE}/markets/trades"
        data, _ = util.get_json(url, {"ticker": t, "limit": 100})
        for tr in (data or {}).get("trades", []) if isinstance(data, dict) else []:
            rows.append({
                "snapshot_ts": snap_ts,
                "market_ticker": t,
                "trade_id": tr.get("trade_id"),
                "created_time": tr.get("created_time"),
                "yes_price": tr.get("yes_price"),
                "no_price": tr.get("no_price"),
                "count": tr.get("count"),
                "taker_side": tr.get("taker_side"),
            })
    util.write_dataset(pd.DataFrame(rows), "kalshi_trades", f"trades_{snap_ts}")
    util.log(f"  kalshi trades: {len(rows)} prints across {len(tickers)} markets")


def pull_all(snap_ts: str) -> None:
    active = pull_markets(snap_ts)
    if active:
        pull_orderbooks(active, snap_ts)
        pull_trades(active, snap_ts)
