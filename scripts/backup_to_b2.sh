#!/usr/bin/env bash
# Off-site backup of tracker.db (plus CLAUDE.md and docs/archive/) to
# Backblaze B2 via restic.
#
# Self-contained — no external drive involved. Steps:
#   1. WAL-safe staging copy of the DB on the internal disk
#   2. integrity check on that copy
#   3. restic backup of the copy + CLAUDE.md + docs/archive/ to the B2 repo
#   4. prune old B2 snapshots (keep 7 daily / 5 weekly / 12 monthly)
#   5. delete the staging copy
#
# Credentials (B2 keys + restic repo password) come from
# ~/.config/myfriendisai-backup.env (chmod 600, never committed).
#
# Scheduled daily via launchd (com.myfriendisai.backup-b2). Safe to run
# while the collection pipeline is active — sqlite3 .backup is WAL-safe
# and restic locks its own repo.

set -euo pipefail
cd "$(dirname "$0")/.."

# launchd gives a minimal PATH; restic is Homebrew, sqlite3 is system.
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

CRED="$HOME/.config/myfriendisai-backup.env"
DB="data/tracker.db"
STAGING="data/tracker-staging.db"   # data/*.db is gitignored
LOG="logs/backup_b2.log"

mkdir -p logs
[ -f "$LOG" ] && mv "$LOG" "$LOG.prev"
exec >> "$LOG" 2>&1

# Always remove the staging copy on exit — success, failure, or interrupt.
trap 'rm -f "$STAGING" "$STAGING-shm" "$STAGING-wal" "$STAGING-journal"' EXIT

fail() {
    echo "BACKUP_B2_ERR: $1"
    osascript -e "display notification \"$1\" with title \"myfriendisai B2 backup FAILED\"" 2>/dev/null || true
    exit 1
}

echo "[$(date)] ===== B2 backup start ====="

[ -f "$CRED" ] || fail "credentials file missing: $CRED"
# shellcheck disable=SC1090
source "$CRED"
[ -n "${RESTIC_REPOSITORY:-}" ] || fail "RESTIC_REPOSITORY not set (bad credentials file)"
[ -f "$DB" ] || fail "database not found: $DB"

# 0. Disk-space precheck. Staging writes a full copy of the DB, and restic
#    needs scratch space for temp pack files on top of that. Checking up front
#    turns a silent mid-run "no space left on device" (which cost 18 days of
#    backups in Aug 2026) into an obvious, actionable failure before any
#    25 GB copy is attempted.
#
#    Fallback (2026-08-08): the DB has outgrown the internal disk — a same-
#    volume staging copy needs 2x the DB size free and that headroom no longer
#    exists, so the internal path fails every day until the DB-slimming
#    migration (CLAUDE.md §6) lands. When internal space is short AND the T9
#    external drive is mounted, stage there instead. This is a fallback, not
#    the primary path: the original "no external drive" design intent stands,
#    and if T9 is absent we still fail loudly rather than silently skipping.
SCRATCH_GIB=3
T9_STAGING_DIR="/Volumes/T9/myfriendisai-safety"
db_bytes=$(stat -f%z "$DB")
need_bytes=$(( db_bytes + SCRATCH_GIB * 1024 * 1024 * 1024 ))
free_bytes=$(( $(df -k . | awk 'NR==2 {print $4}') * 1024 ))
if [ "$free_bytes" -lt "$need_bytes" ]; then
    # Internal disk can't hold the staging copy — try the T9 fallback.
    # restic temp packs still use the internal disk, so require SCRATCH_GIB
    # free there and DB-size + margin free on T9.
    t9_free_bytes=$(( $(df -k "$T9_STAGING_DIR" 2>/dev/null | awk 'NR==2 {print $4}' || echo 0) * 1024 ))
    if [ -d "$T9_STAGING_DIR" ] \
        && [ "$t9_free_bytes" -gt $(( db_bytes + 2 * 1024 * 1024 * 1024 )) ] \
        && [ "$free_bytes" -gt $(( SCRATCH_GIB * 1024 * 1024 * 1024 )) ]; then
        STAGING="$T9_STAGING_DIR/tracker-staging.db"
        echo "[$(date)] Internal disk short (need $(( need_bytes / 1024**3 )) GiB, have $(( free_bytes / 1024**3 )) GiB) — staging on T9 instead"
    else
        fail "insufficient disk: need $(( need_bytes / 1024**3 )) GiB (DB $(( db_bytes / 1024**3 )) GiB + ${SCRATCH_GIB} GiB restic scratch), have $(( free_bytes / 1024**3 )) GiB free, and T9 fallback unavailable"
    fi
else
    echo "[$(date)] Disk precheck OK — need $(( need_bytes / 1024**3 )) GiB, have $(( free_bytes / 1024**3 )) GiB free"
fi

# 1. WAL-safe staging copy on the internal disk. sqlite3 .backup produces a
#    consistent snapshot even while the collector is writing to the live DB.
echo "[$(date)] WAL-safe staging copy -> $STAGING"
rm -f "$STAGING" "$STAGING-shm" "$STAGING-wal" "$STAGING-journal"
sqlite3 "$DB" ".backup '$STAGING'" || fail "sqlite3 .backup failed"
[ -f "$STAGING" ] || fail "staging copy was not created"

# 2. Integrity-check the copy before trusting it.
echo "[$(date)] Verifying staging copy (quick_check) ..."
qc=$(sqlite3 "$STAGING" "PRAGMA quick_check;" 2>&1)
[ "$qc" = "ok" ] || fail "staging copy failed quick_check: $qc"

# 3. restic backup the copy to the encrypted B2 repo. CLAUDE.md and
#    docs/archive/ ride along in the same snapshot — they are gitignored
#    (public repo, internal notes), so this backup is their only off-site copy.
echo "[$(date)] restic backup -> $RESTIC_REPOSITORY"
restic backup "$STAGING" CLAUDE.md docs/archive --tag tracker-db --host myfriendisai-collector \
    || fail "restic backup failed"

# 4. Retention. group-by host,tags (NOT the default host,paths) so every
#    daily snapshot counts as one series for the keep-policy.
echo "[$(date)] Pruning B2 snapshots (keep 7 daily / 5 weekly / 12 monthly) ..."
restic forget --tag tracker-db --group-by host,tags \
    --keep-daily 7 --keep-weekly 5 --keep-monthly 12 \
    --prune || fail "restic forget/prune failed"

# 5. Record success so the daily pipeline can publish backup freshness in
#    status.json, which the GitHub Actions alert reads. Without this the only
#    failure signal is a local notification — which is how an 18-day backup
#    outage went unnoticed in Jul-Aug 2026. logs/ is gitignored, so this is
#    local state, not committed data.
date -u '+%Y-%m-%dT%H:%M:%SZ' > logs/last_backup_success

# 6. staging copy removed by the EXIT trap.
echo "[$(date)] ===== B2 backup done ====="
restic snapshots --tag tracker-db --compact --group-by host,tags 2>/dev/null | tail -8 || true
