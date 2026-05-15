#!/usr/bin/env bash
# Online backup of the SQLite tracker.db using sqlite3 .backup.
# Unlike a raw file copy, .backup respects WAL and produces a consistent
# snapshot even while the daily collection pipeline is running.
#
# Stores the last N backups (default 7) and prunes older ones.
#
# Usage:
#   bash scripts/backup_db.sh                    # default destination + retention
#   bash scripts/backup_db.sh /path/to/dest      # custom destination dir
#
# Recommended: add to launchd or a daily cron alongside collect_daily.
# Or run manually before any risky migration / schema change.

set -euo pipefail

cd "$(dirname "$0")/.."

DB="data/tracker.db"
DEST="${1:-$HOME/Backups/myfriendisai}"
KEEP=7

if [ ! -f "$DB" ]; then
    echo "ERROR: database not found at $DB" >&2
    exit 1
fi

mkdir -p "$DEST"
ts=$(date -u +%Y%m%dT%H%M%SZ)
out="$DEST/tracker_$ts.db"

echo "[$(date)] Starting online backup → $out"
sqlite3 "$DB" ".backup '$out'"
if [ ! -f "$out" ]; then
    echo "ERROR: backup file not created" >&2
    exit 1
fi

# Verify integrity of the backup before pruning anything
echo "[$(date)] Running integrity_check on backup..."
result=$(sqlite3 "$out" "PRAGMA integrity_check;")
if [ "$result" != "ok" ]; then
    echo "ERROR: backup integrity check failed: $result" >&2
    echo "Keeping the corrupt backup at $out for inspection." >&2
    exit 1
fi

size=$(du -h "$out" | cut -f1)
echo "[$(date)] Backup complete: $out ($size, integrity ok)"

# Prune old backups, keep most recent KEEP
echo "[$(date)] Pruning old backups (keeping last $KEEP)..."
ls -1t "$DEST"/tracker_*.db 2>/dev/null | tail -n +"$((KEEP + 1))" | while read -r old; do
    echo "  Removing $old"
    rm -f "$old"
done

remaining=$(ls -1 "$DEST"/tracker_*.db 2>/dev/null | wc -l | tr -d ' ')
echo "[$(date)] Done. $remaining backups in $DEST."
