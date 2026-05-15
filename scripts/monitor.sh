#!/usr/bin/env bash
# Background monitor for the in-flight pre-2023 backfill. Polls status
# every 5 minutes. Sends a macOS notification if the job stalls or crashes.
# Writes a heartbeat to /tmp/myfriendisai_monitor.heartbeat.
#
# Usage:
#   bash scripts/monitor.sh &      # start monitoring
#   tail -f /tmp/myfriendisai_monitor.log  # follow output
#
# Stops automatically when the pre-2023 backfill is complete (or you can
# kill the process).

set -u
cd "$(dirname "$0")/.."

LOG=/tmp/myfriendisai_monitor.log
HEARTBEAT=/tmp/myfriendisai_monitor.heartbeat
DB="data/tracker.db"
INTERVAL_SEC=300  # 5 minutes
STALL_THRESHOLD_SEC=1800  # 30 minutes — no DB progress means stalled

notify() {
    local title="$1"
    local message="$2"
    # macOS notification via osascript
    osascript -e "display notification \"$message\" with title \"$title\" sound name \"Glass\"" 2>/dev/null || true
    echo "[$(date)] NOTIFY: $title — $message" >> "$LOG"
}

last_alert_backfill=""

while true; do
    NOW=$(date -u +%s)
    echo -n "$(date) " > "$HEARTBEAT"

    # ── Pre-2023 backfill status ─────────────────────────
    BACKFILL_PROCS=$(ps aux | grep -E "python.*backfill_pullpush" | grep -v grep | wc -l | tr -d ' ')
    PRE_2023_N=$(sqlite3 "$DB" "SELECT COUNT(*) FROM posts WHERE created_utc < strftime('%s','2023-01-01');" 2>/dev/null)
    PRE_2023_LAST=$(sqlite3 "$DB" "SELECT MAX(created_at) FROM posts WHERE created_utc < strftime('%s','2023-01-01');" 2>/dev/null)
    PRE_2023_LAST_TS="${PRE_2023_LAST//T/ }"
    PRE_2023_LAST_TS="${PRE_2023_LAST_TS%Z}"
    PRE_2023_LAST_TS="${PRE_2023_LAST_TS%%.*}"
    PRE_2023_EPOCH=$(date -j -u -f "%Y-%m-%d %H:%M:%S" "$PRE_2023_LAST_TS" +%s 2>/dev/null || echo 0)
    PRE_2023_AGE=$(( NOW - PRE_2023_EPOCH ))

    if [ "$BACKFILL_PROCS" -eq 0 ] && [ "$PRE_2023_N" -gt 100 ]; then
        BACKFILL_STATE="DONE"
    elif [ "$BACKFILL_PROCS" -eq 0 ]; then
        BACKFILL_STATE="CRASHED"
    elif [ "$PRE_2023_AGE" -gt "$STALL_THRESHOLD_SEC" ]; then
        BACKFILL_STATE="STALLED"
    else
        BACKFILL_STATE="RUNNING"
    fi

    # ── Log heartbeat ────────────────────────────────────
    echo "$(date) backfill=$BACKFILL_STATE($PRE_2023_N)" >> "$LOG"

    # ── Notify on state changes that warrant attention ──
    case "$BACKFILL_STATE" in
        CRASHED)
            if [ "$last_alert_backfill" != "CRASHED" ]; then
                notify "Pre-2023 backfill CRASHED" "$PRE_2023_N posts inserted. Restart needed."
                last_alert_backfill="CRASHED"
            fi
            ;;
        STALLED)
            if [ "$last_alert_backfill" != "STALLED" ]; then
                notify "Pre-2023 backfill STALLED" "$PRE_2023_N posts, no new in 30+ min."
                last_alert_backfill="STALLED"
            fi
            ;;
        DONE)
            if [ "$last_alert_backfill" != "DONE" ]; then
                notify "Pre-2023 backfill DONE" "$PRE_2023_N pre-2023 posts collected. Ready to tag."
                last_alert_backfill="DONE"
            fi
            ;;
        RUNNING)
            last_alert_backfill="RUNNING"
            ;;
    esac

    # ── Exit when the backfill is complete ───────────────
    if [ "$BACKFILL_STATE" = "DONE" ]; then
        echo "$(date) Backfill complete. Monitor exiting." >> "$LOG"
        notify "Backfill complete" "Monitor exiting. Ready for final consolidation."
        break
    fi

    sleep "$INTERVAL_SEC"
done
