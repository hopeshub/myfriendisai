#!/bin/bash
# launchd wrapper: monthly drift-check sample build.
#
# Runs `scripts/drift_check.py build`, which samples recent keyword matches
# from the local tracker.db and stages Markdown sample files under
# analysis/keyword_pipeline/results/. It does NOT classify them — that step
# needs Claude Code agents and happens in an interactive session.
#
# Triggered by ~/Library/LaunchAgents/com.myfriendisai.drift-check.plist on
# the 13th of each month. On completion it posts a macOS notification so the
# staged samples don't quietly sit unclassified. To finish the cycle: open
# Claude Code and ask it to run the drift check (classify → record → report).
#
# This only runs `build` because that is the deterministic, DB-dependent half.
# The classification half is judgement work and stays in a Claude Code session.

set -uo pipefail

PROJECT_DIR="/Users/walker/Projects/myfriendisai"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/drift_build.log"
RESULTS_DIR="$PROJECT_DIR/analysis/keyword_pipeline/results"

cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"

# Rotate: keep last run's log as .prev
if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "$LOG_FILE.prev"
fi

# Monthly period label, e.g. 2026-06 — drift_check.py accepts it via --quarter.
PERIOD=$(date '+%Y-%m')

echo "=== Drift build started $(date -u '+%Y-%m-%d %H:%M:%S UTC') — period $PERIOD ===" > "$LOG_FILE"

"$PROJECT_DIR/.venv/bin/python" scripts/drift_check.py build --quarter "$PERIOD" >> "$LOG_FILE" 2>&1
rc=$?

echo "=== Drift build finished $(date -u '+%Y-%m-%d %H:%M:%S UTC') — exit $rc ===" >> "$LOG_FILE"

if [ "$rc" -eq 0 ]; then
    n=$(ls "$RESULTS_DIR"/drift_"$PERIOD"_*.md 2>/dev/null | wc -l | tr -d ' ')
    msg="$n sample files staged for $PERIOD. Open Claude Code and run the drift check to classify them."
else
    msg="Drift build FAILED (exit $rc) — see logs/drift_build.log"
fi
echo "$msg" >> "$LOG_FILE"
osascript -e "display notification \"$msg\" with title \"myfriendisai · drift check\"" 2>/dev/null || true

echo "=== Done ===" >> "$LOG_FILE"
