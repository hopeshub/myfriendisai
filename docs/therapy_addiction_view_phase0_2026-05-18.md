# Phase 0 — Data-availability gate: Therapy ↔ Addiction view

**Date:** 2026-05-18
**Status:** ⛔ HALTED at Check 4 — stop-and-talk condition triggered. No view code written.
**Decision required from a human before Phase 1 begins.**

Per the spec's §8, Phase 0 runs four checks then stops. All four ran. Checks 1–3 pass
cleanly. **Check 4 (BOTH-magnitude) triggers the spec's explicit STOP condition.**

---

## Check 1 — Schema check → GOOD case

Theme tags are stored as **independent per-theme, per-keyword, per-source rows**, not a
single winning theme per post. Table `post_keyword_tags`:

```
post_id | subreddit | category | matched_term | post_date | source
UNIQUE(post_id, category, matched_term, source)
```

A post freely carries tags for multiple themes. The full window (2017-08-25 → 2026-05-18)
is present in this one table.

**→ BOTH is a direct query. No backfill, no re-match, no RECOVERABLE/BAD branch.**

## Check 2 — Raw-text retention → PASS

`posts`: 4,049,302 rows, 2017-01-01 → 2026-05-18. `selftext` NULL on 0 posts; empty on
824,930 (link/image posts — titles present; only 4 posts have no title). Full text is
retained for the entire window. (Not needed given Check 1 is GOOD, but confirmed.)

## Check 3 — Reproduction check → PASS (within tolerance)

`post_keyword_tags` (post-source, distinct posts, monthly) reproduces
`keyword_trends.json` `count_post_only` within 1–4 posts/month for both themes
(e.g. addiction 2026-03: 213 = 213; therapy 2026-01: 63 vs 59). The small residual is
consistent with the export applying the `exclude_from_keywords` filter (r/AIGirlfriend,
r/SpicyChatAI, r/ChatGPTNSFW) that the raw table query does not. The instrument is
stable — no pipeline/keyword-file drift alarm.

## Check 4 — BOTH-magnitude → ⛔ STOP CONDITION TRIGGERED

Cells over the full measurable window, **post-source only** (the chosen definition):

| Cell | Posts | Share of reliance-discourse |
|---|---|---|
| HELP-only (therapy, not addiction) | 1,319 | 33.3% |
| **BOTH (therapy AND addiction)** | **75** | **1.9%** |
| PROBLEM-only (addiction, not therapy) | 2,570 | 64.8% |
| **Total reliance-discourse** | **3,964** | 100% |

post+comment instead of post-only moves BOTH only 75 → 89. It does not rescue the cell.

**BOTH per month** (2025 onward) never exceeds 8 posts; BOTH share never exceeds ~6% and
is 0–3% in most months. BOTH by year: 2022:1, 2023:1, 2024:4, 2025:42, 2026:27.

**BOTH is concentrated, not distributed.** Of 75 BOTH posts: recovery subs
(Character_AI_Recovery 34, ChatbotAddiction 11, +2) = 47 (63%); r/CharacterAI 14;
r/ChatGPTcomplaints 6. The long-lived **primary companionship "stable cohort"** the spec's
§3 robustness toggle depends on holds only ~6 BOTH posts across the entire window.

**Hand-read of 22 BOTH posts:** the posts are *genuinely* ambivalent — the spec's
post-level thesis holds where BOTH exists. Examples: "I don't think I can quit"
(`emotional support` + `clean for`/`hours a day`); "Bedridden, nothing to do but mourn my
coping mechanism" (`coping mechanism` + `cold turkey`); "4o was a REVOLUTIONARY tool for
mental health" (`emotional support`/`therapeutic` + `hours a day`). The dominant pattern
is the therapy keyword **`coping mechanism`** co-occurring with addiction recovery
vocabulary inside recovery subs.

---

## What this means

The data **does not contradict the about page.** The about page claims therapy and
addiction are one *subject/behavior* split by the *valence of the writer's framing*. That
is exactly what the cells show: 98.1% of reliance-discourse posts commit to a single
valence (HELP-only or PROBLEM-only). "One behavior, two framings" is intact.

The data **does contradict the spec.** The spec infers from "one behavior, two framings"
that a large share of individual posts hold *both* frames at once, and builds Panel B
around that "ambivalent core" as the central, brightest, first-class object. The keyword
instrument measures co-occurrence of help-vocabulary and problem-vocabulary in one post —
and that is ~2%. BOTH *is* a residual. It cannot carry the center of the chart.

Recall asymmetry (spec §4) does push BOTH down — help-framing in ordinary language slips
past keywords — but it would need to be wrong by ~10–20× to make BOTH "central," which is
not plausible. And the stable-cohort toggle (§3), the spec's single most important
control, would render the BOTH band essentially empty (~6 posts).

A secondary finding worth noting: the help:problem mix itself is ~33:65 — but §4's recall
asymmetry biases *exactly* toward over-counting PROBLEM-only, so even the headline mix is
a soft number, not a hard one.

## Options for the human decision

1. **Build the view, demote BOTH.** Keep the two-panel design and the genuine findings —
   the help/problem mix, its drift, its deformation at events, the stable-cohort test —
   but drop BOTH as the central object. Render it as a thin, explicitly-labeled seam
   between the two bands, or omit it and state in the caption that doubly-framed posts are
   ~2% (a real finding: posts overwhelmingly pick one valence). This keeps every §1
   question answerable *except* "how large is the ambivalent core" — whose honest answer
   is "small."
2. **Reframe the view around the actual finding.** The headline becomes "therapy and
   addiction are near-disjoint partitions of one subject — readers commit to one valence,"
   which is itself a clean, defensible, anti-hype result. The chart shows the mix and the
   event response; the ~2% BOTH is presented as the finding, not designed around.
3. **Do not merge; keep two tiles.** Fall back to status quo if neither reframing is
   wanted.

My recommendation: **Option 1 or 2.** The view is still worth building — the
event-deformation question and the stable-cohort test are real and unique to this view —
but Panel B as specified (BOTH central and brightest) must change, and the framing copy
in §6 must change with it. This is a copy/design decision, not a data failure.

**Spec compliance note:** §8 Check 4 says BOTH-near-empty is "a stop-and-talk moment, not
a build-through moment. Report it and wait." Halting here accordingly.
