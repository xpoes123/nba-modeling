"""Consolidate snapshots -> one parquet+csv per dataset, zip, upload to share server.

Produces:
  wnba_data/consolidated/<dataset>.parquet  (+ .csv)
  wnba_data/wnba_data.zip                    (everything Bill needs)
  uploads zip + manifest to the VPS public share dir.
"""
import subprocess
import zipfile
from pathlib import Path

import pandas as pd

from wnba_pull import config, util

# datasets that are split across many timestamped/ per-game files -> concat into one
CONSOLIDATE = [
    "schedule_results", "player_box", "pbp_raw", "pbp_events", "shots",
    "players",
    "live_game_lines", "live_props",
    "kalshi_markets", "kalshi_orderbook", "kalshi_trades",
    "historical_closing_lines", "historical_opening_lines",
]


def consolidate() -> dict[str, int]:
    out = config.OUT / "consolidated"
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for ds in CONSOLIDATE:
        d = config.OUT / ds
        if not d.exists():
            continue
        files = sorted(d.glob("*.parquet"))
        if not files:
            continue
        frames = []
        for f in files:
            try:
                frames.append(pd.read_parquet(f))
            except Exception as e:  # noqa: BLE001
                util.log(f"  consolidate {ds}: bad file {f.name}: {e}")
        if not frames:
            continue
        df = pd.concat(frames, ignore_index=True)
        df.to_parquet(out / f"{ds}.parquet", index=False)
        df.to_csv(out / f"{ds}.csv", index=False)
        counts[ds] = len(df)
        util.log(f"  consolidated {ds}: {len(df)} rows from {len(files)} files")
    return counts


def write_manifest(counts: dict[str, int]) -> Path:
    cr = util.credit_state()
    lines = ["# WNBA Data Pull - Manifest", ""]
    lines.append(f"- Seasons: {', '.join(config.SEASONS)}")
    lines.append(f"- Odds API credits remaining: {cr.get('last_remaining')}")
    lines.append("")
    lines.append("## Datasets (rows)")
    for ds, n in sorted(counts.items()):
        lines.append(f"- {ds}: {n:,}")
    p = config.OUT / "consolidated" / "MANIFEST.md"
    p.write_text("\n".join(lines))
    return p


def make_zip() -> Path:
    out = config.OUT / "consolidated"
    zpath = config.OUT / "wnba_data.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.glob("*")):
            z.write(f, arcname=f"wnba_data/{f.name}")
        readme = Path(__file__).parent / "README_FOR_BILL.md"
        if readme.exists():
            z.write(readme, arcname="wnba_data/README.md")
    util.log(f"  zip written: {zpath} ({zpath.stat().st_size/1e6:.1f} MB)")
    return zpath


def upload(zpath: Path) -> str | None:
    """scp the zip to the VPS share dir. Returns public URL or None on failure."""
    target = f"{config.VPS_USER}@{config.VPS_HOST}:{config.VPS_SHARE_DIR}/"
    try:
        subprocess.run(["ssh", f"{config.VPS_USER}@{config.VPS_HOST}",
                        f"mkdir -p {config.VPS_SHARE_DIR}"], check=True, timeout=60)
        subprocess.run(["scp", str(zpath), target], check=True, timeout=1800)
        url = f"{config.PUBLIC_BASE_URL}/wnba_data.zip"
        util.log(f"  uploaded -> {url}")
        return url
    except Exception as e:  # noqa: BLE001
        util.log(f"  UPLOAD FAILED (zip still local at {zpath}): {e}")
        return None


def run() -> str | None:
    util.log("PACKAGE: consolidating")
    counts = consolidate()
    write_manifest(counts)
    zpath = make_zip()
    return upload(zpath)


if __name__ == "__main__":
    run()
