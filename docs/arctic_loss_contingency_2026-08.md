# Arctic Shift Loss Contingency

**Written 2026-08-27.** The decided position on what happens if Arctic Shift
(`arctic-shift.photon-reddit.com`) degrades or disappears.

Arctic Shift is the project's **sole** source of posts and comments. Reddit
direct access ended 2026-05-30 (global 403 on unauthenticated `.json`) and the
API-approval request was abandoned 2026-08-08 after Reddit never responded
(CLAUDE.md §6.1). Arctic-first is the permanent collection mode. That makes a
single community-run archive a single point of failure for all forward
collection, and this document records what we do about it — including the case
where the answer is "nothing, and we say so."

This is a decision record, not a proposal. It exists so that the response to an
archive outage is a lookup, not an improvisation.

---

## 1. Current dependency

Every daily run goes through `_step_collect_posts_arctic` and
`_step_collect_comments_arctic` in `scripts/collect_daily.py`, both backed by
`_fetch_window` in `scripts/backfill_arctic.py`.

| What | Endpoint | Window |
|---|---|---|
| Posts, per sub | `/api/posts/search` | `ARCTIC_WINDOW_HOURS` back from run time |
| Comments, per sub (by comment creation time) | `/api/comments/search` | same |

`ARCTIC_WINDOW_HOURS` is **7 days** (`7 * 24`, `collect_daily.py`), widened from
72h on 2026-08-27. Pagination is 100 items per request at a 2.0s delay
(`BATCH_SIZE`, `REQUEST_DELAY`); `RETRYABLE_STATUS = (422, 429, 500, 502, 503,
504)` gets 5 retries with linear backoff before a window is marked `truncated`.
Truncated windows keep their partial data and are recorded as an error in the
run summary.

**The window is the self-healing horizon.** Each run re-walks the entire window
from scratch and every insert is `INSERT OR IGNORE` on a primary key, so
re-collecting the same days is free and idempotent. Any Arctic Shift outage
shorter than the window is invisible in the corpus: the next successful run
refills it. Any outage longer than the window leaves a hole that only a manual
`scripts/backfill_arctic.py --since <date>` can fill — and only if the archive
comes back at all.

That is the whole risk model. Widening the window buys more automatic recovery;
it does not change what happens past the horizon.

Not sourced from Arctic Shift, for completeness: subreddit snapshots
(subscribers, active users). They have no archive equivalent, are frozen at
2026-06-07, and `_step_heal_snapshots` reconstructs the derived columns
(posts/day, unique authors, contributor metrics, avg comments) from our own
posts and comments tables. An Arctic outage therefore degrades the theme atlas
and the post-volume charts, not the subscriber figures — those are already
static and already labelled "(Jun 2026)" on the site.

---

## 2. Failure tiers and responses

### (a) Transient outage, shorter than the window — no action

Arctic Shift is unreachable, 5xx-ing, or timing out for less than
`ARCTIC_WINDOW_HOURS`.

**Response: none.** The next successful run re-walks the full window and the
gap closes itself. `logs/collect_daily.log` will carry `arctic_error` /
`arctic_partial` lines for the affected subs and the run may exit non-zero; the
GitHub Actions staleness alert tolerates a single failed day by design (56h
threshold, `.github/workflows/status-alert.yml`).

Do not manually backfill in this tier. A manual `--since` run during a partial
outage competes with the daily run for the same throttled archive and makes the
next automatic recovery slower, not faster.

### (b) Sustained degradation — pace down, then split the run

Arctic Shift is up but throttling hard: HTTP 422 with
`{"error": "Timeout. Maybe slow down a bit"}`, repeated across subs and days,
truncating windows on the high-volume subs (r/ChatGPT, r/ClaudeAI,
r/CharacterAI) which are walked first and are the ones whose comment-sourced
tags feed published theme counts.

**How it surfaces:**

- **Run duration.** Normal arctic runs finish in ~25 min (06:00 → ~06:25 in
  `logs/collect_daily.log`). Retry backoff is the dominant cost when the archive
  is unhappy; a run stretching past ~90 min with no corpus growth to show for it
  is the signal.
- **Arctic throttle telemetry in `status.json`.** `_fetch_window` counts
  `retryable_status`, `network_error`, and `truncated_windows` per run
  (`THROTTLE_EVENTS`, `backfill_arctic.py`); `collect_daily.py` snapshots the
  totals to `logs/last_run_stats.json` and `run_collect.sh` publishes them in
  `web/public/status.json` as **`arctic_throttle_events`**, alongside
  `run_duration_seconds`, `posts_inserted`, and `comments_collected`. A healthy
  day is at or near zero throttle events. This is the field to watch — it makes
  archive health visible from the live site rather than only from the collection
  Mac's logs.
- **`arctic_partial` / `arctic_error` entries** in the run summary, per sub.

**Mitigations, in order:**

1. **Slower pacing.** Raise `REQUEST_DELAY` in `scripts/backfill_arctic.py`
   (currently 2.0s). This is the first and usually sufficient move: 422 here
   means "you are asking too fast," not "your request is wrong." Cost is run
   duration, which we have plenty of headroom for.
2. **Split collection across the day.** The window re-walk is idempotent, so
   there is nothing preventing a second launchd invocation later in the day
   picking up what the morning run truncated. The `run_collect.sh` wrapper lock
   (`data/.run_collect.lock.d`) already prevents overlap.
3. **Raise `max_retries`** (currently 5 in `_fetch_window`) before accepting a
   truncated window.

None of these require a methodology change. Collection cadence is not a
published claim; the corpus is dated by `created_utc`, not by collection time.

### (c) Permanent loss — the archive is gone

Arctic Shift shuts down, goes private, or degrades past usability with no
recovery. This is the tier that matters, because there is no technical answer to
it and pretending otherwise is how this project would start lying.

**The position: collection ends at the last good day. The corpus becomes a
completed longitudinal archive with a documented end date, and the site converts
from a live tracker to an archival artifact.**

Concretely:

1. **Stop collecting.** Unload `com.myfriendisai.collect-daily`. Leave
   `com.myfriendisai.backup-b2` running — the corpus still needs protecting.
2. **Fix the end date.** Determine the last day with complete coverage (the last
   run with no `truncated_windows`), and treat that as the corpus end. Days after
   it are partial and should be excluded from the published series rather than
   shipped as a decline that is really a collection artifact. A collection
   failure that renders as a downward trend is the single worst outcome
   available here.
3. **Convert the site.** The stale-data banner already reads `status.json` and
   already says *why* the site is stale. It escalates once, to a permanent
   "collection ended <date>" notice on the homepage and About page — stated
   plainly, with the reason (Reddit access revoked 2026-05-30; archive
   unavailable from <date>). The charts stay up. A completed 2017–<date>
   discourse series is a legitimate research artifact; a tracker quietly showing
   a frozen last month is not.
4. **Ship the durability bundle.** The versioned public export of the aggregate
   dataset (monthly per-theme counts, per-sub volumes — derived numbers only, no
   raw Reddit content) plus the schema doc and the consolidated methodology
   document (CLAUDE.md §6, "Outstanding work" item 4) is the guarantee that the
   research survives the loss of both its sources. **This is the actual
   contingency plan.** It is currently queued rather than shipped, which means
   today the project's durability depends on the collection Mac and a B2 restic
   repo. That is the gap this document is pointing at.

**No scraping workarounds.** Not on Reddit, not on third-party mirrors. Reddit
direct access is dead (global 403, all UAs and IPs; app creation approval-gated
and never granted) and that decision is closed per CLAUDE.md §6.1. Building a
scraper would trade a documented, honest end date for an undocumented,
policy-violating, silently-degrading data source — the exact opposite of the
project's stated method. The end of collection is an acceptable outcome. A
corpus of unknown provenance is not.

---

## 3. Early-warning signals

| Signal | Where it surfaces | Threshold |
|---|---|---|
| `arctic_throttle_events` (sum of `retryable_status`, `network_error`, `truncated_windows`) | `web/public/status.json`, via `logs/last_run_stats.json` | any sustained non-zero |
| `run_duration_seconds`, `posts_inserted`, `comments_collected` | same | duration climbing while inserts fall |
| `collection_succeeded` false | `status.json`; macOS notification; `logs/failures.log` | 1 day = watch, 2 days = act |
| `consecutive_push_failures` ≥ 2 | `status.json` → GHA `status-alert.yml` → email | alert fires |
| Last successful push > 56h | live `myfriendisai.com/status.json` → GHA → email | alert fires |
| Last successful backup > 72h | same workflow, second step | alert fires |
| Per-sub `arctic_partial` / `arctic_error` | `logs/collect_daily.log` run summary | high-volume subs first |
| Run duration | `logs/collect_daily.log` start/finish stamps | >90 min on an arctic day |

The GHA workflow is the only signal that reaches a person who is not sitting at
the collection Mac. That was the lesson of the 12-day May 2026 gap
(`docs/reddit_json_shutdown_2026-06-09.md`) and the 18-day backup outage of
July–August 2026: local notifications detect, they do not notify.

Note the alerts are keyed to *publishing*, not to *archive health* — a run that
collects nothing but exports and pushes successfully keeps every alert green.
The arctic telemetry fields in `status.json` are what close that blind spot, and
they are the reason to look at `status.json` rather than only at inbox alerts.

---

## 4. What not to do

- **Do not re-file or re-nudge the Reddit API access request.** Filed
  2026-06-11, never acknowledged, abandoned 2026-08-08. The procedure is kept in
  `docs/reddit_api_access_request_guide.md` as a historical record only. If
  Reddit publicly changes its access posture, that is a new decision made on new
  evidence — not a retry.
- **Do not build a scraper.** See §2(c).
- **Do not silently backfill from an unvetted mirror.** If another archive is
  ever adopted it needs the same treatment Arctic Shift got: a documented
  provenance note, a `data_source` value on every row it produces, a
  spot-comparison against the existing corpus on an overlapping window, and a
  disclosure on the About page. Mixing an unverified source into a longitudinal
  series destroys the one thing the series is for.
- **Do not paper over a collection gap.** No interpolation, no carry-forward, no
  smoothing across a hole. The corpus is already documented as a floor; a gap is
  a gap and gets stated as one. The May 2026 snapshot notch is the precedent —
  it is visible in the sparklines on purpose.
- **Do not let a partial final window become a published downward trend.**
  See §2(c) step 2.
