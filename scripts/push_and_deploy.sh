#!/bin/bash
# Push updated data files to GitHub. Vercel auto-deploys on push.
#
# Failure model: commit today's data BEFORE attempting any push, so a
# transient push failure does not strand today's snapshot on a working tree
# that gets overwritten by tomorrow's export. Tomorrow's run will then push
# both commits.
#
# Exit codes:
#   0 = success, or no-op (nothing changed and nothing pending)
#   1 = pre-deploy validation failed (no commit, no push)
#   2 = git push failed (local commit may exist; next run will retry)
#   3 = unexpected internal error
#
# On any failure, a "PUSH_ERR: <message>" line is emitted so run_collect.sh
# can extract a one-liner for status.json / the stale-data banner.

cd "$(dirname "$0")/.." || { echo "PUSH_ERR: cannot cd to project"; exit 3; }

export PATH="/opt/homebrew/bin:$PATH"

# SSH-side timeouts bound any network stall to a minute or two without
# requiring an external `timeout` binary (which macOS does not ship).
export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -o ServerAliveInterval=15 -o ServerAliveCountMax=4 -o BatchMode=yes"

echo "=== Push & deploy started at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="

# Step 1: Detect whether today's run produced new data.
# status.json is intentionally excluded from this check — it changes every
# run regardless, and committing on status-only changes would push empty
# updates whenever the daily collection produced no new data.
data_changed=true
if git diff --quiet data/*.json web/data/*.json 2>/dev/null; then
    data_changed=false
fi

# Step 2: If data changed, validate and commit (BEFORE any push attempt).
if [ "$data_changed" = true ]; then
    echo "Data files changed — running pre-deploy validation..."
    if ! .venv/bin/python scripts/validate_deploy.py; then
        echo "PUSH_ERR: pre-deploy validation failed"
        echo "=== Push & deploy ABORTED (validation) ==="
        exit 1
    fi

    # web/public/dataset/ is the versioned public aggregate export (the
    # durability bundle). It is regenerated from the same JSON files, so it
    # only changes when the numbers do — but it must ride along in the same
    # commit, and `git add` on the directory picks up new files too.
    git add data/*.json web/data/*.json web/public/status.json
    if [ -d web/public/dataset ]; then
        git add web/public/dataset
    fi
    if ! git commit -m "Daily data update $(date -u '+%Y-%m-%d')"; then
        echo "PUSH_ERR: git commit failed"
        echo "=== Push & deploy ABORTED (commit) ==="
        exit 3
    fi
    echo "Committed today's data update."
else
    echo "No data file changes today."
fi

# Step 3: Push everything pending — including any commits stranded by a
# previous failed run.
UPSTREAM_AHEAD=$(git rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)
if [ "$UPSTREAM_AHEAD" -eq 0 ]; then
    echo "Nothing to push. Done."
    echo "=== Push & deploy finished (no-op) ==="
    exit 0
fi

echo "Pushing $UPSTREAM_AHEAD commit(s) to GitHub..."
push_err_file=$(mktemp -t push_and_deploy.XXXXXX)
if git push 2> >(tee "$push_err_file" >&2); then
    rm -f "$push_err_file"
    echo "=== Push & deploy finished at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="
    exit 0
fi

# Surface the last few stderr lines as a single-line PUSH_ERR.
last_lines=$(tail -n 5 "$push_err_file" 2>/dev/null | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ *//;s/ *$//')
rm -f "$push_err_file"
echo "PUSH_ERR: ${last_lines:-git push failed (no stderr)}"
echo "=== Push & deploy FAILED ==="
exit 2
