#!/bin/bash
# Wrapper script for daily pipeline, called by launchd.
# Runs collection, then pushes data to GitHub and deploys to Vercel.
# Writes health status to web/public/status.json and notifies on failure.

set -uo pipefail

PROJECT_DIR="/Users/walker/Projects/myfriendisai"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/collect_daily.log"
FAILURE_LOG="$LOG_DIR/failures.log"
STATUS_FILE="$PROJECT_DIR/web/public/status.json"

export PATH="/opt/homebrew/bin:$PATH"

# Prevent macOS from sleeping during the pipeline (can take 3-5 hours).
# -s = prevent sleep even on AC power; -w $$ = release when this script exits.
caffeinate -s -w $$ &

mkdir -p "$LOG_DIR"

# Rotate: keep last run's log as .prev
if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "$LOG_FILE.prev"
fi

cd "$PROJECT_DIR"

echo "=== Collection started at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ===" > "$LOG_FILE"

# ── Step 1: Collect ──
"$PROJECT_DIR/.venv/bin/python" scripts/collect_daily.py >> "$LOG_FILE" 2>&1
collect_exit=$?

echo "=== Collection finished at $(date -u '+%Y-%m-%d %H:%M:%S UTC') (exit code: $collect_exit) ===" >> "$LOG_FILE"

# Get collection stats from the database
posts_collected=0
subreddits_ok=0
subreddits_total=27
if [ $collect_exit -eq 0 ]; then
    posts_collected=$("$PROJECT_DIR/.venv/bin/python" -c "
import sqlite3
conn = sqlite3.connect('data/tracker.db')
today = conn.execute(\"SELECT COUNT(*) FROM posts WHERE date(created_utc, 'unixepoch') = date('now')\").fetchone()[0]
print(today)
conn.close()
" 2>/dev/null || echo 0)
    subreddits_ok=$("$PROJECT_DIR/.venv/bin/python" -c "
import sqlite3
conn = sqlite3.connect('data/tracker.db')
latest = conn.execute(\"SELECT MAX(snapshot_date) FROM subreddit_snapshots\").fetchone()[0]
count = conn.execute(\"SELECT COUNT(DISTINCT subreddit) FROM subreddit_snapshots WHERE snapshot_date = ?\", (latest,)).fetchone()[0]
print(count)
conn.close()
" 2>/dev/null || echo 0)
fi

# ── Step 2: Push & deploy ──
push_succeeded=false
if [ $collect_exit -ne 0 ]; then
    echo "Collection failed — skipping push & deploy." >> "$LOG_FILE"
else
    echo "" >> "$LOG_FILE"
    if "$PROJECT_DIR/scripts/push_and_deploy.sh" >> "$LOG_FILE" 2>&1; then
        echo "=== Push & deploy succeeded ===" >> "$LOG_FILE"
        push_succeeded=true
    else
        echo "=== Push & deploy FAILED (exit code: $?) — data is safe, will retry next run ===" >> "$LOG_FILE"
    fi
fi

# ── Step 3: Write health status ──
now=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
last_push="null"
if [ "$push_succeeded" = true ]; then
    last_push="\"$now\""
elif [ -f "$STATUS_FILE" ]; then
    # Preserve previous last_successful_push
    prev=$("$PROJECT_DIR/.venv/bin/python" -c "
import json
try:
    d = json.load(open('$STATUS_FILE'))
    print(d.get('last_successful_push', 'null'))
except: print('null')
" 2>/dev/null || echo "null")
    if [ "$prev" != "null" ]; then
        last_push="\"$prev\""
    fi
fi

cat > "$STATUS_FILE" <<EOJSON
{
  "last_collection": "$now",
  "posts_collected": $posts_collected,
  "subreddits_ok": $subreddits_ok,
  "subreddits_total": $subreddits_total,
  "collection_succeeded": $([ $collect_exit -eq 0 ] && echo true || echo false),
  "push_succeeded": $push_succeeded,
  "last_successful_push": $last_push
}
EOJSON

echo "Wrote status to $STATUS_FILE" >> "$LOG_FILE"

# ── Step 4: Notify on failure ──
if [ $collect_exit -ne 0 ] || [ "$push_succeeded" = false ]; then
    failure_msg=""
    if [ $collect_exit -ne 0 ]; then
        failure_msg="Collection failed (exit $collect_exit)"
    else
        failure_msg="Push/deploy failed"
    fi

    # macOS notification
    osascript -e "display notification \"$failure_msg — check logs\" with title \"myfriendisai\"" 2>/dev/null || true

    # Failure log
    echo "$(date -u '+%Y-%m-%d %H:%M:%S UTC') — $failure_msg" >> "$FAILURE_LOG"

    echo "FAILURE NOTIFIED: $failure_msg" >> "$LOG_FILE"
fi

echo "=== Pipeline complete ===" >> "$LOG_FILE"
