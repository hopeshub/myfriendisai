# Verify Unattended Collection Setup

## Task

Check that the daily Reddit collection pipeline will run reliably without any user interaction. Verify each of the following and report a pass/fail for each:

### 1. launchd job is loaded
Run `launchctl list | grep myfriendisai` — confirm the job exists and note its status.

### 2. Plist file exists and is valid
Check that `~/Library/LaunchAgents/com.myfriendisai.collect-daily.plist` exists. Print its contents so we can verify the schedule, script path, and working directory are correct.

### 3. Wrapper script exists and is executable
Check that the script referenced in the plist (likely `scripts/run_collect.sh`) exists and has execute permissions. Print its contents so we can verify the venv path and Python script path.

### 4. Collection script runs successfully
Do a dry run: execute the collection script manually and confirm it completes without errors. Report how many subreddits collected and how many posts stored.

### 5. System energy settings
Run `pmset -g` and check:
- Is sleep set to 0 (never)? If not, flag it.
- Is `autorestart` set to 1? If not, flag it — this controls whether the Mac restarts after a power failure.
Report what the current settings are and flag anything that needs to change.

### 6. Disk space
Run `df -h /` and report free space on the boot drive. Flag if less than 10GB free.

### 7. Auto-login check
Check if auto-login is enabled by running `defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>/dev/null`. If it returns a username, auto-login is on. If it errors, auto-login is off — flag this as something that needs to be enabled manually.

### 8. Automatic updates check
Run `defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload 2>/dev/null` and `defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticallyInstallMacOSUpdates 2>/dev/null`. Flag if automatic macOS updates are enabled.

## Output format

Print a clear summary at the end:

```
=== UNATTENDED COLLECTION READINESS ===
1. launchd job loaded:        ✅ / ❌
2. Plist file valid:          ✅ / ❌
3. Wrapper script OK:         ✅ / ❌
4. Collection test run:       ✅ / ❌  (X subs, Y posts)
5. Sleep disabled:            ✅ / ❌
6. Auto-restart on power:     ✅ / ❌
7. Disk space:                ✅ / ❌  (X GB free)
8. Auto-login:                ✅ / ❌
9. Auto-updates off:          ✅ / ❌

ACTION REQUIRED:
- (list anything that failed and how to fix it)
```
