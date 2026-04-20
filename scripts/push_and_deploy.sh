#!/bin/bash
# Push updated data files to GitHub and deploy to Vercel.
# Called by run_collect.sh after collection finishes, or manually.
# Vercel auto-deploys on push via GitHub integration — no CLI deploy needed.

set -e

cd /Users/walker/Projects/myfriendisai

export PATH="/opt/homebrew/bin:$PATH"

echo "=== Push & deploy started at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="

# Push any commits left unpushed by a previous failed run before deciding
# there's "nothing to do". Without this, a commit-succeeded-but-push-failed
# run would hide yesterday's data behind today's no-op diff check.
UPSTREAM_AHEAD=$(git rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)
if [ "$UPSTREAM_AHEAD" -gt 0 ]; then
    echo "Found $UPSTREAM_AHEAD unpushed commit(s) from a prior run — pushing first."
    timeout 300 git push
fi

# Only commit if data files actually changed
if git diff --quiet data/*.json web/data/*.json 2>/dev/null; then
    echo "No data changes to commit. Skipping."
    exit 0
fi

# Run pre-deploy validation
echo "Running pre-deploy validation..."
.venv/bin/python scripts/validate_deploy.py
if [ $? -ne 0 ]; then
    echo "VALIDATION FAILED — aborting deploy. Check logs"
    exit 1
fi

# Stage and commit data files + status.json
git add data/*.json web/data/*.json web/public/status.json
git commit -m "Daily data update $(date -u '+%Y-%m-%d')"

# Push to GitHub (triggers Vercel auto-deploy via GitHub integration).
# Timeout guards against launchd blocking for hours if SSH stalls.
timeout 300 git push

echo "=== Push & deploy finished at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="
