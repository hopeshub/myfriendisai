#!/bin/bash
# Push updated data files to GitHub and deploy to Vercel.
# Called by cron after collect_daily.py finishes.

set -e

cd /Users/walker/Projects/myfriendisai

export PATH="/opt/homebrew/bin:$PATH"

echo "=== Push & deploy started at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="

# Only commit if data files actually changed
if git diff --quiet data/*.json web/data/*.json 2>/dev/null; then
    echo "No data changes to commit. Skipping."
    exit 0
fi

# Run pre-deploy validation
echo "Running pre-deploy validation..."
.venv/bin/python scripts/validate_deploy.py
if [ $? -ne 0 ]; then
    echo "VALIDATION FAILED — aborting deploy. Check logs/push_deploy.log"
    exit 1
fi

# Stage and commit data files only
git add data/*.json web/data/*.json
git commit -m "Daily data update $(date -u '+%Y-%m-%d')"

# Push to GitHub
git push

# Deploy to Vercel
cd web
vercel --prod --yes 2>&1 | tail -3

echo "=== Push & deploy finished at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="
