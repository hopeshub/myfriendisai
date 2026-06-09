# Incident: Reddit kills unauthenticated `.json` access — 12-day collection gap

**Window:** 2026-05-29 → 2026-06-09 (last good collection 2026-05-28 13:52 UTC)
**Detected:** 2026-06-09, on return from travel. Local notifications fired daily but reached nobody.

## What happened

On 2026-05-30 Reddit globally disabled unauthenticated `.json` endpoint access — no
announcement, no deprecation period. Every endpoint returns 403 (Reddit's own edge,
`server: snooserv`) for every User-Agent and IP. This was the project's primary data
source and its founding architecture assumption ("no API credentials needed").
Confirmed as a global policy change, not an IP block, via public reporting.
`.rss` endpoints still work but lack score/comments/selftext.

This is the second unannounced sourcing break (PullPush died 2025).

## Impact

- **Posts / theme trends:** 12-day gap, fully recovered same day from Arctic Shift
  (two ~7-day chunked windows, all 40 subs, `data_source='arctic_shift'`).
- **Subreddit snapshots** (subscribers/active users from `about.json`): permanent
  12-day hole — Arctic Shift has no daily snapshot equivalent. Communities-page
  sparklines carry a notch for the window.
- **Comments:** not collected for posts whose 5–6-day eligibility window fell inside
  the gap. The post+comment theme series converges to post-only for the window
  (same behavior as pre-2026-03-18 backfill data). Accepted; footnoted in site copy.
- **Scores/comment-counts on recovered posts** were captured at archive age, not our
  usual ~36h — fine for volume trends, slightly inconsistent for engagement metrics.
- **The site** stayed up throughout; data was stale, never wrong.

## Fixes shipped 2026-06-09

1. **OAuth collection** — `src/reddit_client.py` now auto-detects
   `~/.config/myfriendisai-reddit.env` (script-app `client_credentials` grant,
   `oauth.reddit.com`, 1.5s interval). No creds file → legacy unauth mode.
2. **Arctic Shift auto-fallback** — `collect_daily.py` Step 1b: if Reddit fails for
   >half the subs, pull the last 36h per sub from Arctic Shift. Theme trends can no
   longer go stale from a Reddit-side access change.
3. **Remote staleness alert** — `.github/workflows/status-alert.yml` checks the live
   `status.json` daily and fails (→ GitHub email) if no successful push for >56h.
   Failure detection existed before; *reaching a traveling owner* did not.

## Lessons

- The pipeline's failure handling worked exactly as designed for 12 days — and that
  wasn't enough, because all alerting was Mac-local. External alerting on the public
  artifact is the durable fix.
- "The chart is a floor, not a ceiling" + provenance labels absorbed the incident
  with no published claim becoming wrong.
- Treat Reddit access as revocable at any time. The fallback path, not the access
  mode, is the real architecture.
