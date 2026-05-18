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
# Total tracked communities — derived from config, not hardcoded, so it stays
# correct as communities are added/deactivated.
subreddits_total=$("$PROJECT_DIR/.venv/bin/python" -c "
from src.config import load_communities
print(len(load_communities()))
" 2>/dev/null || echo 0)
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
# Status carries a consecutive-failure counter and the last error line so the
# frontend stale-data banner can show *why* the site is stale, not just that
# it is. last_push_error is extracted from the PUSH_ERR sentinel emitted by
# push_and_deploy.sh.
now=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
collection_succeeded_bool=$([ $collect_exit -eq 0 ] && echo true || echo false)
last_push_error=""
if [ "$push_succeeded" = false ] && [ $collect_exit -eq 0 ]; then
    last_push_error=$(grep "^PUSH_ERR:" "$LOG_FILE" | tail -1 | sed 's/^PUSH_ERR: //' || echo "")
fi

"$PROJECT_DIR/.venv/bin/python" - "$STATUS_FILE" "$now" "$posts_collected" "$subreddits_ok" "$subreddits_total" "$collection_succeeded_bool" "$push_succeeded" "$last_push_error" <<'EOPY'
import json
import sys

status_path, now, posts, ok, total, collection_ok, push_ok, last_err = sys.argv[1:9]
collection_ok = collection_ok == "true"
push_ok = push_ok == "true"

try:
    prev = json.load(open(status_path))
except Exception:
    prev = {}

prev_consec = int(prev.get("consecutive_push_failures") or 0)
prev_last_push = prev.get("last_successful_push")

if push_ok:
    consec = 0
    last_push = now
    last_err = ""
else:
    consec = prev_consec + 1
    last_push = prev_last_push

out = {
    "last_collection": now,
    "posts_collected": int(posts),
    "subreddits_ok": int(ok),
    "subreddits_total": int(total),
    "collection_succeeded": collection_ok,
    "push_succeeded": push_ok,
    "last_successful_push": last_push,
    "consecutive_push_failures": consec,
    "last_push_error": last_err or None,
}
with open(status_path, "w") as f:
    json.dump(out, f, indent=2)
    f.write("\n")
EOPY

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
