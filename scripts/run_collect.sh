#!/bin/bash
# Wrapper script for daily collection, called by launchd.
# Activates the venv, runs collection, and logs output.

set -euo pipefail

PROJECT_DIR="/Users/walker/Projects/myfriendisai"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/collect_daily.log"

mkdir -p "$LOG_DIR"

# Rotate: keep last run's log as .prev
if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "$LOG_FILE.prev"
fi

cd "$PROJECT_DIR"

echo "=== Collection started at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ===" > "$LOG_FILE"

"$PROJECT_DIR/.venv/bin/python" scripts/collect_daily.py >> "$LOG_FILE" 2>&1
exit_code=$?

echo "=== Collection finished at $(date -u '+%Y-%m-%d %H:%M:%S UTC') (exit code: $exit_code) ===" >> "$LOG_FILE"

exit $exit_code
