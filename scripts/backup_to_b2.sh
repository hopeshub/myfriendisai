#!/usr/bin/env bash
# Two-tier backup of tracker.db:
#   Tier 1 (local):    backup_db.sh -> WAL-safe timestamped snapshot on T9 (keeps 7)
#   Tier 2 (off-site): restic -> encrypted, deduplicated repo in Backblaze B2
#
# Credentials (B2 keys + restic repo password) are sourced from
# ~/.config/myfriendisai-backup.env (chmod 600, never committed).
#
# Scheduled daily via launchd (com.myfriendisai.backup-b2); can also be run
# manually. Safe to run while the collection pipeline is active — sqlite3
# .backup is WAL-safe and restic locks its own repo.

set -euo pipefail
cd "$(dirname "$0")/.."

# launchd gives a minimal PATH; restic is Homebrew, sqlite3 is system.
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

CRED="$HOME/.config/myfriendisai-backup.env"
T9_DIR="/Volumes/T9/myfriendisai-backup/db"
LOG="logs/backup_b2.log"

mkdir -p logs
[ -f "$LOG" ] && mv "$LOG" "$LOG.prev"
exec >> "$LOG" 2>&1

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
[ -d "/Volumes/T9" ] || fail "T9 drive not mounted — cannot stage snapshot"

# ── Tier 1: local WAL-safe snapshot to T9 (timestamped, keeps last 7) ──
echo "[$(date)] Tier 1: local snapshot via backup_db.sh ..."
bash scripts/backup_db.sh "$T9_DIR" || fail "backup_db.sh (local snapshot) failed"

# ── Tier 2: restic the newest snapshot to the encrypted B2 repo ──
LATEST=$(ls -t "$T9_DIR"/tracker_*.db 2>/dev/null | head -1)
[ -n "$LATEST" ] || fail "no T9 snapshot found to upload"
echo "[$(date)] Tier 2: restic backup -> $RESTIC_REPOSITORY"
echo "[$(date)]   source: $LATEST"
restic backup "$LATEST" --tag tracker-db --host myfriendisai-collector \
    || fail "restic backup failed"

# ── Retention: prune old B2 snapshots ──
# group-by host,tags (NOT the default host,paths): the source filename is
# timestamped, so path-grouping would put every day in its own group and the
# keep-policy would never prune. Tag-grouping treats all daily snapshots as
# one series.
echo "[$(date)] Pruning B2 snapshots (keep 7 daily / 5 weekly / 12 monthly) ..."
restic forget --tag tracker-db --group-by host,tags \
    --keep-daily 7 --keep-weekly 5 --keep-monthly 12 \
    --prune || fail "restic forget/prune failed"

echo "[$(date)] ===== B2 backup done ====="
restic snapshots --tag tracker-db --compact --group-by host,tags 2>/dev/null | tail -8 || true
