# Verify Unattended Collection Setup

## Task

Check that the daily Reddit collection pipeline will run reliably without any user interaction. Verify each of the following and report a pass/fail for each:

### 1. launchd job is loaded
Run `launchctl list | grep myfriendisai` — confirm the job exists and note its status.

### 2. No duplicate scheduling
Run `crontab -l` — confirm there are NO myfriendisai cron entries. Collection must only run via launchd. If cron entries exist, they will race with launchd and one will always fail on the lock file.

### 3. Plist file exists and is valid
Check that `~/Library/LaunchAgents/com.myfriendisai.collect-daily.plist` exists. Print its contents and verify:
- Schedule (should be Hour=6, Minute=0)
- Script path points to `scripts/run_collect.sh`
- Working directory is the project root
- Log paths are set

### 4. Wrapper script exists and is executable
Check that `scripts/run_collect.sh` exists, has execute permissions, and:
- Calls `collect_daily.py` for collection
- Calls `push_and_deploy.sh` after collection succeeds
- Sets PATH to include `/opt/homebrew/bin` (needed for vercel, git)
- Push failure is non-fatal (collection data is preserved)

### 5. Push script is correct
Check that `scripts/push_and_deploy.sh` exists, has execute permissions, and:
- Uses `git status --porcelain` for change detection (NOT `git diff --quiet`, which misses untracked files)
- Runs `validate_deploy.py` before committing
- Runs `vercel --prod --yes` from the project root (NOT from `web/` — Vercel project already has `web` as root directory)

### 6. SSH authentication works non-interactively
Run `env -i HOME=$HOME PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" ssh -T git@github.com` — this simulates the stripped environment that launchd/cron provides. Must authenticate successfully. If it fails, check:
- SSH key exists at `~/.ssh/id_ed25519` (no passphrase)
- GitHub host key is in `~/.ssh/known_hosts`
- Git remote is SSH not HTTPS: `git remote -v` should show `git@github.com:...`

### 7. Vercel CLI available in launchd PATH
Run `env -i HOME=$HOME PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" which vercel` — must find vercel.

### 8. Data file integrity
Check that `web/data/keywords.json` exists (it's expected by `validate_deploy.py` and the frontend). Run `validate_deploy.py` and confirm all checks pass.

### 9. Collection runs successfully
Check the most recent log at `logs/collect_daily.log`:
- Did it complete with exit code 0?
- How many subreddits and posts were collected?
- Did push & deploy succeed?
Also check `logs/failures.log` for any recent failures.

### 10. No missed days
Run: `sqlite3 data/tracker.db "SELECT snapshot_date, COUNT(*) FROM subreddit_snapshots GROUP BY snapshot_date ORDER BY snapshot_date DESC LIMIT 7;"` — should show 27 subs for each of the last 7 days with no gaps.

### 11. System energy settings
Run `pmset -g` and check:
- Is sleep set to 0 (never)?
- Is `autorestart` set to 1?

### 12. Disk space
Run `df -h /` and report free space. Flag if less than 10GB free. Also check DB size with `du -sh data/tracker.db` — flag if approaching available disk.

### 13. Auto-login check
Run `defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>/dev/null`. Must return a username. If it errors, auto-login is off — launchd user agents won't run after reboot.

### 14. Automatic updates check
Run `defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticallyInstallMacOSUpdates 2>/dev/null`. Flag if set to 1 (enabled) — auto-updates can reboot the machine mid-collection.

## Output format

Print a clear summary at the end:

```
=== UNATTENDED COLLECTION READINESS ===
 1. launchd job loaded:       ✅ / ❌
 2. No duplicate scheduling:  ✅ / ❌
 3. Plist file valid:         ✅ / ❌
 4. Wrapper script OK:        ✅ / ❌
 5. Push script OK:           ✅ / ❌
 6. SSH auth (non-interactive):✅ / ❌
 7. Vercel CLI in PATH:       ✅ / ❌
 8. Data file integrity:      ✅ / ❌
 9. Last collection run:      ✅ / ❌  (X subs, Y posts)
10. No missed days:           ✅ / ❌
11. Sleep disabled:           ✅ / ❌
    Auto-restart on power:    ✅ / ❌
12. Disk space:               ✅ / ❌  (X GB free, DB Y GB)
13. Auto-login:               ✅ / ❌
14. Auto-updates off:         ✅ / ❌

ACTION REQUIRED:
- (list anything that failed and how to fix it)
```
