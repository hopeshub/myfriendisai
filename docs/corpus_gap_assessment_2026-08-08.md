# Corpus Gap Assessment — 2026-08-08

**Question:** after the July–August incidents (disk-full, backup outage, Arctic Shift 422 comment losses), how big a hole is left in the research corpus — and what does it mean for the published work?

**Answer in one line:** the published research has **no hole at all**; the secondary comment corpus had a real hole that was **~99% recovered today** (110,520 comments); the one permanent, still-growing hole is **engagement metrics** (subscribers/active users), which stopped on 2026-06-07 and cannot be backfilled from any archive.

All numbers below were measured directly against `data/tracker.db` and the export files on 2026-08-08, after the repairs.

---

## 1. The published theme lines — ZERO loss

The site's published series is the **post-only** validated-keyword count (`count_post_only`, per `web/app/themeData.ts`), normalized per-1k posts from the 24 keyword-scope T1–T3 subs.

- **Post collection never had a gap.** Daily post counts are continuous through every incident, including the 2026-05-29 → 06-09 Reddit shutdown (1,555–2,280 posts/day straight through, recovered from Arctic Shift at the time) and the July–August 422 era (1,334–1,728/day, no dips).
- The comment-loss bug **never touched the published numbers** — verified by diffing exports before/after recovery: `count_post_only` changed on zero historical dates.
- Backup outage = zero data loss (backups protect the corpus; the corpus itself was never damaged).

**Bottom line: every chart on myfriendisai.com is built from an unbroken series.**

## 2. The comment corpus — hole found, hole (almost entirely) filled

Comments feed the secondary post+comment `count` series, comment-sourced tags, and future comment-language research. Its coverage has four eras:

| Era | Coverage | State after 2026-08-08 repairs |
|---|---|---|
| pre-2026-03-18 | **None** — comment collection didn't exist | Structural, by design; published series is post-only partly for this reason |
| 2026-03-18 → 05-29 (Reddit era) | Partial — one-shot snapshot at day 5-6, only posts with 5+ comments | ~7,000/day captured vs ~13,800/day in the complete era → roughly **half** of comment volume, permanently thinner unless deliberately densified (see §5) |
| 2026-05-30 → 06-10 (shutdown tail) | Was: missing days on 4 high-volume subs | **Backfilled today** |
| 2026-06-11 → present (Arctic era) | Was: 7–15 missing days per high-volume sub (422-discard bug) | **Bug fixed + backfilled today** |

**Today's recovery: 110,520 comments** across 8 subs (ClaudeAI 13.5k, ChatGPT 49.9k, singularity 24.6k, CharacterAI 7.2k, ChatGPTcomplaints 5.0k, OpenAI 5.4k, claudexplorers 4.8k, ChaiApp 49). Re-verified after backfill: **every high-volume sub now has complete daily comment coverage 2026-05-29 → 2026-08-07.** The only residual "missing" days are 8 days on r/ChaiApp, and a full-span refetch proved those days genuinely have no attachable comments (low-volume sub, quiet days) — not a loss.

Known, accepted structural drops: comments whose parent post was never collected are discarded as orphans (by design — e.g. ClaudeAI's backfill fetched 53k, inserted 13.5k; the rest were duplicates already held or orphans). This is documented behavior, not damage.

## 3. The permanent hole — engagement metrics

This is the genuine, unrecoverable loss, and it is **ongoing**:

- **Subscriber counts: frozen at 2026-06-07** (last day OAuth-era collection worked). 62 days × 40 subs ≈ **2,480 sub-days of missing snapshots, growing by 40/day.** No archive holds historical subscriber counts — Arctic Shift archives content, not community metadata. Unrecoverable.
- **Active users: never collected once** in the project's entire history (0 of ~35,700 snapshot rows). Same for Reddit's newer Visitors/Contributions metrics.
- Everything derived from these (participation rate, any future engagement index) has no denominator after June 7.

**Impact honestly assessed: modest.** CLAUDE.md already classifies engagement surfaces as *secondary context, not a measure of the phenomenon* (the 2026-05-16 reframing). The trend instrument doesn't use subscribers. But two things follow:

1. **Provenance issue to fix:** the `/communities` table displays subscriber counts (June 7 values) under a "Data as of <today>" dateline. For a site whose credibility rests on provenance labels, the Subscribers column should say what it is — "as of 2026-06-07" — until OAuth returns.
2. The only fix for the ongoing loss is **Reddit approving the API access request** (ticket filed 2026-06-11, nudge overdue since 07-09). Every day without it adds 40 more permanently-lost sub-days.

## 4. Instrument health (from the June + July drift cycles, run 2026-08-08)

Not a corpus hole, but it bounds what the corpus means. Two full drift cycles (~11,700 classifications, 92 keywords × post/comment) were completed today after a 3-month backlog:

| Theme | Jun post | Jul post | Jun comment | Jul comment |
|---|---|---|---|---|
| addiction | 86% | 85% | 78% | 79% |
| consciousness | 81% | 76% | 75% | 65% |
| romance | 86% | 84% | 75% | 72% |
| rupture | 80% | 78% | 81% | 77% |
| sexual_erp | 75% | 78% | 79% | 75% |
| therapy | **68%** | **62%** | 66% | 68% |

- **Therapy post precision (62–68%) runs well below the ~80% carried in the docs**, dragged by `ai therapy` (36%), `emotional support` (46%), `therapeutic` (50%), `as a therapist` (52%). Several therapy keywords also *declined* June→July (`as a therapist` −18, `for therapy` −18) — classifier notes attribute much of it to "therapy-speak" tone complaints about models post-4o-sunset, i.e. ambient language drifting onto the keywords. This strengthens the queued v9 therapy review.
- **Comment precision now has a real measurement** (~4,000 comment classifications) — the "urgent, never validated" queued item. It is *better* than the old n≤100 numbers suggested: addiction 78–79% (was 67%), consciousness 65–75% (was 51%), therapy 66–68% (was 58%).
- One template artifact worth a matcher tweak someday: r/NomiAI weekly art-collab boilerplate ("no NSFW content") is a recurring false-positive cluster for `nsfw content`.
- Recall remains the documented floor: 3–32% per theme (2026-05-13 audit). The chart is a floor, not a ceiling — unchanged.

## 5. Options deliberately not taken today (decisions, not oversights)

1. **Densifying the Reddit-era comment window (2026-03-18 → 05-29).** Arctic could roughly double that era's comments (~300–500k fetch, hours of API time, +1–2 GB DB). Not done: disk headroom is critical until DB slimming lands, and the published series is post-only precisely so era differences don't distort it.
2. **Extending comment history before 2026-03.** Possible in principle (Arctic reaches back years); millions of comments, +10 GB or more. A post-slimming decision if ever.
3. Both would change the *comment* corpus only — no published number depends on them today.

## 6. Summary table

| Asset | Hole? | Recoverable? | State |
|---|---|---|---|
| Published theme lines (post-only) | **None** | — | Intact end to end |
| Post corpus (4.34M posts, 2017→) | **None** | — | Continuous through all incidents |
| Comment corpus, 2026-05-29 → present | Was: ~110k comments | Yes | **Recovered 2026-08-08** |
| Comment corpus, Reddit era (Mar–May 2026) | ~Half of volume | Yes (optional) | Accepted; densify post-slimming if wanted |
| Comment corpus, pre-2026-03 | All of it | Partially (optional) | By design; published series unaffected |
| Subscribers / active users since 2026-06-08 | 2,480 sub-days, +40/day | **No** | Permanent; only OAuth stops the bleeding |
| Off-site backups Jul 20 → Aug 7 | 18 days of snapshots | N/A (corpus undamaged) | Chain restored; daily backups working again |
