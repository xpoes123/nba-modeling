#!/usr/bin/env bash
# MANUAL one-time pull of 2025 WNBA closing lines. Run this yourself AFTER your
# the-odds-api monthly quota resets (billing anniversary = 17th of the month).
# It checks credits first, pulls ~8,580 credits worth of 2025 closing lines,
# then re-zips and re-uploads the public pack to share.djiang.xyz/wnba.
#
#   ./wnba_pull/pull_2025_odds.sh
#
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

KEY=$(grep -E '^ODDS_API_KEY=' .env | cut -d= -f2)
REM=$(curl -s -D - "https://api.the-odds-api.com/v4/sports/?apiKey=$KEY" -o /dev/null \
      | grep -i 'x-requests-remaining' | tr -dc '0-9')
echo "the-odds-api credits remaining: ${REM:-unknown}"
if [ "${REM:-0}" -lt 9000 ]; then
  echo "Not enough credits (${REM:-0} < 9000). Has the quota reset (17th)? Aborting."
  exit 1
fi

echo "Pulling 2025 closing lines (cap 10000 credits)..."
PYTHONPATH=. uv run python -m wnba_pull.odds_historical 2025 10000 || exit 1
echo "Repackaging + uploading the pack..."
PYTHONPATH=. uv run python -m wnba_pull.package_and_share || exit 1
echo "Done. 2025 closing lines added to https://share.djiang.xyz/wnba/wnba_data.zip"
