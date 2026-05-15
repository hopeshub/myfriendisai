#!/usr/bin/env bash
# Polls the Anthropic API every 5 minutes with a small test call.
# When 2 consecutive test calls succeed (no 529 Overloaded), automatically
# resumes the Sonnet backfill with 2 parallel processes.
#
# Run after killing Sonnet backfill due to Anthropic overload.
#
# Usage:
#   set -a && source .env && set +a
#   bash scripts/resume_when_ready.sh &

set -u
cd "$(dirname "$0")/.."

LOG=/tmp/sonnet_resume_watch.log
POLL_INTERVAL=300  # 5 minutes
REQUIRED_SUCCESSES=2  # consecutive healthy probes before resume

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set. source .env first."
    exit 1
fi

notify() {
    local title="$1"; local message="$2"
    osascript -e "display notification \"$message\" with title \"$title\" sound name \"Glass\"" 2>/dev/null || true
    echo "[$(date)] NOTIFY: $title — $message" >> "$LOG"
}

# Cheap probe: classify a 1-line dummy with Sonnet. Returns 0 if API healthy,
# nonzero if 529 / rate limit / other failure.
probe_api() {
    .venv/bin/python -c "
import sys, os
try:
    import anthropic
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=20,
        messages=[{'role': 'user', 'content': 'Reply with the single word: ok'}],
    )
    text = resp.content[0].text if resp.content else ''
    sys.exit(0 if text else 1)
except Exception as e:
    err = str(e)
    if 'overloaded' in err.lower() or '529' in err or '429' in err:
        sys.exit(2)
    sys.exit(3)
" 2>/dev/null
    return $?
}

consecutive_successes=0
echo "[$(date)] Starting resume-when-ready watcher. Poll interval ${POLL_INTERVAL}s." >> "$LOG"
notify "Sonnet watch started" "Will resume backfill when Anthropic API stabilizes."

while true; do
    probe_api
    rc=$?
    case $rc in
        0)
            consecutive_successes=$(( consecutive_successes + 1 ))
            echo "[$(date)] probe OK ($consecutive_successes/$REQUIRED_SUCCESSES)" >> "$LOG"
            ;;
        2)
            consecutive_successes=0
            echo "[$(date)] probe: overloaded/rate-limited" >> "$LOG"
            ;;
        *)
            consecutive_successes=0
            echo "[$(date)] probe: other error rc=$rc" >> "$LOG"
            ;;
    esac

    if [ "$consecutive_successes" -ge "$REQUIRED_SUCCESSES" ]; then
        # Check Sonnet isn't already running (race-condition guard)
        running=$(ps aux | grep -E "python.*llm_verify_tags.*claude-sonnet-4-6" | grep -v grep | wc -l | tr -d ' ')
        if [ "$running" -gt 0 ]; then
            echo "[$(date)] Sonnet already has $running process(es); not relaunching." >> "$LOG"
            break
        fi

        echo "[$(date)] API healthy — resuming Sonnet backfill with 2 processes." >> "$LOG"
        notify "Sonnet API healthy" "Resuming backfill with 2 parallel processes."

        KW=$(.venv/bin/python -c "from src.config import load_keywords; print(','.join(t for cat in load_keywords() for t in cat['terms']))")
        if [ -z "$KW" ]; then
            echo "[$(date)] ERROR: keyword list empty; not launching." >> "$LOG"
            notify "Sonnet resume FAILED" "Keyword list came back empty. Manual restart needed."
            break
        fi

        # Use setsid for full process-group detachment so children survive
        # this parent shell exiting. /dev/null stdin prevents SIGTTIN.
        setsid bash -c "
            cd $(pwd)
            export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'
            .venv/bin/python scripts/llm_verify_tags.py backfill \
                --keywords '$KW' --surface both --model claude-sonnet-4-6 \
                > /tmp/sonnet_resumed_p1.log 2>&1 < /dev/null
        " &
        P1=$!
        sleep 3
        setsid bash -c "
            cd $(pwd)
            export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'
            .venv/bin/python scripts/llm_verify_tags.py backfill \
                --keywords '$KW' --surface both --model claude-sonnet-4-6 \
                > /tmp/sonnet_resumed_p2.log 2>&1 < /dev/null
        " &
        P2=$!

        # Verify children survived the parent exit-prep window
        sleep 5
        running=$(ps aux | grep -E "python.*llm_verify_tags.*claude-sonnet-4-6" | grep -v grep | wc -l | tr -d ' ')
        echo "[$(date)] Launched PIDs $P1 and $P2; verified $running running 5s later." >> "$LOG"
        if [ "$running" -lt 1 ]; then
            notify "Sonnet resume FAILED" "Processes died after launch. Check /tmp/sonnet_resumed_p*.log."
        else
            notify "Sonnet resumed" "$running process(es) alive after launch. Monitor will track."
        fi
        break
    fi

    sleep "$POLL_INTERVAL"
done
