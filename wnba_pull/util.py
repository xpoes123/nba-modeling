"""Shared helpers: HTTP with retries, parquet+csv writers, credit tracking, logging."""
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from wnba_pull import config


def utcnow_iso() -> str:
    """UTC timestamp safe for filenames, e.g. 20260606T141530Z."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def get_json(url: str, params: dict | None = None, retries: int = 4,
             timeout: int = 30) -> tuple[dict | list | None, dict]:
    """GET JSON with exponential backoff. Returns (data, response_headers)."""
    last_exc = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r.json(), dict(r.headers)
            if r.status_code in (401, 422):
                log(f"  HTTP {r.status_code} (non-retryable) {url} :: {r.text[:200]}")
                return None, dict(r.headers)
            log(f"  HTTP {r.status_code} attempt {attempt+1}/{retries} {url}")
        except Exception as e:  # noqa: BLE001 - want to retry on any network error
            last_exc = e
            log(f"  EXC attempt {attempt+1}/{retries} {url} :: {e}")
        time.sleep(2 ** attempt)
    if last_exc:
        log(f"  GIVING UP {url} :: {last_exc}")
    return None, {}


def write_dataset(df: pd.DataFrame, subdir: str, name: str) -> Path:
    """Write a timestamped parquet snapshot into OUT/<subdir>/. Returns the path."""
    if df is None or len(df) == 0:
        return None
    d = config.OUT / subdir
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


# ---- the-odds-api credit ledger (persisted so it survives across runs/processes) ----
_LEDGER = config.OUT / "_credit_ledger.json"
_LOCK = threading.Lock()


def credit_state() -> dict:
    if _LEDGER.exists():
        return json.loads(_LEDGER.read_text())
    return {"used_this_run": 0, "last_remaining": None}


def record_credits(headers: dict, cost: int) -> dict:
    """Update the credit ledger from odds-api response headers + our own cost tally."""
    with _LOCK:
        st = credit_state()
        st["used_this_run"] = st.get("used_this_run", 0) + cost
        rem = headers.get("x-requests-remaining")
        if rem is not None:
            st["last_remaining"] = int(float(rem))
        config.OUT.mkdir(parents=True, exist_ok=True)
        _LEDGER.write_text(json.dumps(st))
        return st
