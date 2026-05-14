#!/usr/bin/env bash
# Status check for in-flight long-running work.
# Run anytime to see if Sonnet backfill / pre-2023 backfill / etc. are
# making progress or stalled. Reads DB state (source of truth), not log
# files (which are usually empty due to tee buffering).
#
# Usage: bash scripts/status.sh

set -u
cd "$(dirname "$0")/.."

DB="data/tracker.db"
NOW=$(date -u +%s)

# Parse a timestamp string (ISO 8601 with optional T separator and Z suffix,
# or "YYYY-MM-DD HH:MM:SS") into epoch seconds. Returns 0 if unparseable.
parse_ts() {
    local s="${1:-}"
    [ -z "$s" ] && { echo 0; return; }
    # Normalize: replace T with space, drop trailing Z, drop fractional seconds
    s="${s//T/ }"
    s="${s%Z}"
    s="${s%%.*}"
    date -j -u -f "%Y-%m-%d %H:%M:%S" "$s" +%s 2>/dev/null || echo 0
}

echo "=== STATUS at $(date) ==="
echo

# ── Sonnet LLM backfill ───────────────────────────────────────────
# Count only python processes, not the zsh wrappers
SONNET_PROCS=$(ps aux | grep -E "python.*llm_verify_tags.*claude-sonnet-4-6" | grep -v grep | wc -l | tr -d ' ')
SONNET_N=$(sqlite3 "$DB" "SELECT COUNT(*) FROM llm_classifications WHERE model='claude-sonnet-4-6';" 2>/dev/null)
SONNET_LAST=$(sqlite3 "$DB" "SELECT classified_at FROM llm_classifications WHERE model='claude-sonnet-4-6' ORDER BY classified_at DESC LIMIT 1;" 2>/dev/null)
SONNET_LAST_EPOCH=$(parse_ts "$SONNET_LAST")
SONNET_AGE=$(( NOW - SONNET_LAST_EPOCH ))

echo "Sonnet LLM backfill:"
echo "  processes alive: $SONNET_PROCS"
echo "  verdicts in DB:  $SONNET_N"
echo "  last verdict:    $SONNET_LAST UTC (${SONNET_AGE}s ago)"
if [ "$SONNET_PROCS" -eq 0 ] && [ "$SONNET_N" -lt 21000 ]; then
    echo "  STATE: ⚠️  CRASHED — no processes alive, target ~21k not reached"
elif [ "$SONNET_PROCS" -gt 0 ] && [ "$SONNET_AGE" -gt 300 ]; then
    echo "  STATE: ⚠️  STALLED — processes alive but no new verdicts in last 5 min"
elif [ "$SONNET_PROCS" -gt 0 ]; then
    REMAINING=$(( 21000 - SONNET_N ))
    [ "$REMAINING" -lt 0 ] && REMAINING=0
    echo "  STATE: ✓ RUNNING — ~$REMAINING items remaining"
else
    echo "  STATE: ✓ COMPLETE"
fi
echo

# ── Pre-2023 Arctic Shift backfill ────────────────────────────────
BACKFILL_PROCS=$(ps aux | grep -E "python.*backfill_pullpush" | grep -v grep | wc -l | tr -d ' ')
PRE_2023_N=$(sqlite3 "$DB" "SELECT COUNT(*) FROM posts WHERE created_utc < strftime('%s','2023-01-01');" 2>/dev/null)
PRE_2023_LAST=$(sqlite3 "$DB" "SELECT MAX(created_at) FROM posts WHERE created_utc < strftime('%s','2023-01-01');" 2>/dev/null)
PRE_2023_LAST_EPOCH=$(parse_ts "$PRE_2023_LAST")
PRE_2023_AGE=$(( NOW - PRE_2023_LAST_EPOCH ))

echo "Pre-2023 Arctic Shift backfill:"
echo "  processes alive: $BACKFILL_PROCS"
echo "  pre-2023 posts:  $PRE_2023_N"
echo "  last insert:     $PRE_2023_LAST UTC (${PRE_2023_AGE}s ago)"
if [ "$BACKFILL_PROCS" -eq 0 ] && [ "$PRE_2023_N" -lt 100 ]; then
    echo "  STATE: ⚠️  NOT RUNNING and no/few pre-2023 posts (script crashed or not started)"
elif [ "$BACKFILL_PROCS" -gt 0 ] && [ "$PRE_2023_AGE" -gt 1800 ]; then
    echo "  STATE: ⚠️  STALLED — alive but no new pre-2023 posts in 30+ min"
elif [ "$BACKFILL_PROCS" -gt 0 ]; then
    echo "  STATE: ✓ RUNNING"
else
    echo "  STATE: ✓ COMPLETE"
fi
echo

# ── Recent log errors (any 'database is locked' or python tracebacks) ──
echo "Recent errors in logs (last 100 lines only):"
for log in /tmp/sonnet_full_backfill.log /tmp/sonnet_backfill_p2.log /tmp/sonnet_backfill_p3.log /tmp/backfill_pre2023_v2.log; do
    if [ -f "$log" ]; then
        ERR_COUNT=$(tail -100 "$log" 2>/dev/null | grep -cE "Traceback|locked|crashed" | tr -d ' \n')
        if [ "${ERR_COUNT:-0}" != "0" ]; then
            echo "  $(basename "$log"): $ERR_COUNT recent error/lock lines"
        fi
    fi
done
echo

# ── Quick health: any background python processes? ──
echo "Python background jobs:"
ps aux | grep python | grep -v grep | grep -E "llm_verify_tags|backfill_pullpush" | awk '{print "  PID="$2, "CPU="$3"%", "MEM="$4"%", "RUNTIME="$10, $11}'
echo

echo "=== END STATUS ==="
