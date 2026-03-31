# Add Health Monitoring to Collection Pipeline

## Context

The daily collection pipeline (launchd → run_collect.sh → collect + push) recently had a silent failure: git push broke on March 20 and nobody noticed for 2 days. We need the pipeline to report its own health so failures are caught immediately.

## Task

Add a health check step to the end of the daily pipeline that:

1. Checks whether collection succeeded (posts were stored)
2. Checks whether git push succeeded (exit code 0)
3. Writes a simple JSON status file that gets deployed to the live site
4. If anything failed, sends a notification

## Implementation

### 1. Health status JSON file

After collection and push, write a file to the web/public directory (so it deploys with the site):

```json
{
  "last_collection": "2026-03-22T06:00:00",
  "posts_collected": 621,
  "subreddits_ok": 27,
  "subreddits_total": 27,
  "push_succeeded": true,
  "last_successful_push": "2026-03-22T06:05:00"
}
```

This file should be accessible at myfriendisai.com/status.json — so anyone (including Walker) can check if the pipeline is healthy just by hitting that URL.

### 2. Add health check to run_collect.sh

At the end of run_collect.sh (after collection AND after the push/deploy step), add a section that:

- Checks the exit code of the collection script
- Checks the exit code of the git push
- Writes the status JSON file with results
- If EITHER step failed, triggers a notification

### 3. Notification on failure

Use a simple approach that doesn't require external services. Pick ONE of these (whichever is easiest to wire up):

**Option A (preferred): macOS native notification**
```bash
osascript -e 'display notification "Collection pipeline failed — check logs" with title "myfriendisai"'
```
This will show a macOS notification banner. Only works if logged in, but that's fine since we have auto-login.

**Option B: Write to a failure log that's easy to check**
Append to a file like `~/projects/myfriendisai/logs/failures.log` with timestamp and what failed. Less proactive but simple.

**Do both** — the macOS notification for immediate visibility, and the failure log for history.

### 4. Update the push step

Make sure the push/deploy step (from push_and_deploy.sh or wherever it lives) is integrated into the same pipeline as collection, so the health check can see both results. Right now collection runs via launchd at 6am and push runs via cron at 8am — these should be unified into one sequential pipeline:

1. Collect posts
2. Export JSON
3. Git add, commit, push
4. Health check + write status.json
5. Notify on failure

All in run_collect.sh (or a new wrapper that calls both). Remove any separate cron entry for push_and_deploy.sh.

## What NOT to change
- The collection logic itself
- The database schema
- The frontend code (except adding status.json to public/)
- The launchd schedule (keep 6am)

## How to verify
1. Run the full pipeline manually
2. Check that status.json appears in web/public/
3. Check myfriendisai.com/status.json after deploy
4. Intentionally break something (e.g., wrong git remote) and verify the notification fires
