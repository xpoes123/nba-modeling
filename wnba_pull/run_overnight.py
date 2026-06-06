"""Overnight orchestrator for the WNBA data pull.

Runs concurrently:
  - a live polling loop (sportsbook lines + props + Kalshi) for RUN_HOURS, and
  - the one-time free stats backfill + current-season historical closing lines.

Packages + uploads after the stats backfill (so the heavy data is available by
morning even while polling continues), then again at the very end.

Launch detached so it survives the terminal/session:
    cd ~/code/nba-modeling
    setsid uv run python -m wnba_pull.run_overnight > wnba_data/run.log 2>&1 &
"""
import threading
import time

from wnba_pull import (config, util, odds_live, kalshi_live,
                       stats_backfill, odds_historical, package_and_share)


def polling_loop() -> None:
    util.log("POLL LOOP: starting")
    deadline = time.time() + config.RUN_HOURS * 3600
    cycle = 0
    while time.time() < deadline:
        cycle += 1
        snap = util.utcnow_iso()
        util.log(f"POLL cycle {cycle} @ {snap}")
        try:
            odds_live.pull_game_lines(snap)
        except Exception as e:  # noqa: BLE001
            util.log(f"  game lines EXC: {e}")
        if cycle % config.PROPS_EVERY_N_CYCLES == 1:
            try:
                odds_live.pull_props(snap)
            except Exception as e:  # noqa: BLE001
                util.log(f"  props EXC: {e}")
        try:
            kalshi_live.pull_all(snap)
        except Exception as e:  # noqa: BLE001
            util.log(f"  kalshi EXC: {e}")
        cr = util.credit_state()
        util.log(f"POLL cycle {cycle} done. odds credits remaining: {cr.get('last_remaining')}")
        # sleep in small chunks so we can exit promptly at the deadline
        slept = 0
        while slept < config.POLL_INTERVAL_SEC and time.time() < deadline:
            time.sleep(min(30, config.POLL_INTERVAL_SEC - slept))
            slept += 30
    util.log(f"POLL LOOP: finished after {cycle} cycles")


def main() -> None:
    config.OUT.mkdir(parents=True, exist_ok=True)
    util.log("=" * 60)
    util.log("WNBA OVERNIGHT PULL: START")
    cr = util.credit_state()
    util.log(f"odds credits remaining at start: {cr.get('last_remaining')}")

    poller = threading.Thread(target=polling_loop, name="poller", daemon=True)
    poller.start()

    # one-time backfills on the main thread
    try:
        stats_backfill.run()
    except Exception as e:  # noqa: BLE001
        util.log(f"STATS BACKFILL EXC: {e}")
    try:
        odds_historical.run()
    except Exception as e:  # noqa: BLE001
        util.log(f"HISTORICAL ODDS EXC: {e}")

    util.log("INTERIM PACKAGE: uploading stats + historical now")
    try:
        url = package_and_share.run()
        util.log(f"INTERIM upload url: {url}")
    except Exception as e:  # noqa: BLE001
        util.log(f"INTERIM PACKAGE EXC: {e}")

    util.log("Waiting for polling loop to finish...")
    poller.join()

    util.log("FINAL PACKAGE: consolidating everything")
    try:
        url = package_and_share.run()
        util.log(f"FINAL upload url: {url}")
    except Exception as e:  # noqa: BLE001
        util.log(f"FINAL PACKAGE EXC: {e}")

    cr = util.credit_state()
    util.log(f"odds credits remaining at end: {cr.get('last_remaining')}")
    util.log("WNBA OVERNIGHT PULL: COMPLETE")
    util.log("=" * 60)


if __name__ == "__main__":
    main()
