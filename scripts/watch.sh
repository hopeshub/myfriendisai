#!/usr/bin/env bash
# Live-refresh status monitor. Clears screen and re-runs status.sh
# every 30 seconds. Ctrl-C to stop.
#
# Usage:
#   bash scripts/watch.sh
#
# Or via osascript to open in a new Terminal window (see scripts/open_watch.sh).

cd "$(dirname "$0")/.."

while true; do
    clear
    bash scripts/status.sh
    echo
    echo "─────────────────────────────────────────"
    echo "  Refreshing every 30s. Press Ctrl-C to stop."
    echo "  Last update: $(date)"
    echo "─────────────────────────────────────────"
    sleep 30
done
