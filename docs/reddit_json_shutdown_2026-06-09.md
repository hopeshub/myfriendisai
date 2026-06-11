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

## Update 2026-06-11 — OAuth blocked by new approval gate

The planned script-app registration (`docs/oauth_setup_guide.md`) is not currently
possible: Reddit retired self-serve app creation (~March 2026). `prefs/apps`
redirects to the Responsible Builder Policy, whose first rule is "Approval is
required" — access must be requested via a support ticket and explicitly granted
before any API use. The academic Reddit-for-Researchers track is ineligible for
this project (university affiliation + IRB required; data-retention rules
incompatible with a longitudinal tracker), so the request goes through the
non-commercial developer track. Ticket text + full procedure:
`docs/reddit_api_access_request_guide.md`. Until approval, the pipeline stays on
the Arctic Shift fallback (theme trends current; snapshots + comments paused) —
exactly the failure mode the fallback was built for.

Same-day follow-up (request ticket filed; pipeline upgraded): the fallback was
promoted to a first-class **arctic-first mode** —

1. **No more doomed Reddit requests.** With no OAuth creds, `collect_daily.py`
   skips Step 1's Reddit pass entirely and goes straight to Arctic Shift
   (`arctic_mode = not client.is_authenticated`). Installing the creds file
   flips it back to Reddit-primary automatically, with the majority-failure
   fallback unchanged.
2. **Comments are no longer lost in arctic mode.** Arctic Shift archives
   comments within seconds of creation, so `_step_collect_comments_arctic`
   pulls each sub's comments *created* in the last 72h and attaches them to
   posts already in the DB (orphans dropped; bot/deleted filtering mirrors the
   Reddit path). Methodology note: this collects continuously by creation
   window, vs. the Reddit path's one-shot snapshot at post-age 5-6 days — it
   captures strictly more of each thread (late comments included), which is
   floor-consistent. Arctic-sourced posts carry `num_comments` from archive
   time (~0), so the old "5+ comments" eligibility filter is unusable in this
   mode; the creation-window design replaces it.
3. **The comment gap (since 2026-05-24, last Reddit comment run 2026-05-28) was
   backfilled** via `scripts/backfill_arctic.py --comments --since 2026-05-24`,
   then tagged + propagated. The post+comment theme series no longer converges
   to post-only for the outage window.
