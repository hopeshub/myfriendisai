# Therapy + consciousness quality program — 2026-05-16

Before demoting the two weak themes (therapy ~64%, consciousness ~68% — see
`docs/keyword_context_spotcheck_2026-05-15.md`), this program runs the two
*structural* improvement levers that the prior keyword-replacement work never
tried. The keyword-replacement avenue is exhausted (`docs/therapy_keyword_decision_2026-05-15.md`);
these two levers attack the method, not the word list, and both become reusable
pipeline capabilities.

## The stopping rule (set before any results)

Measured on **rebuilt-line volume-weighted topical precision**:

- **≥ 80%** → the theme graduates / stays a full peer line on the chart.
- **70–79%** → present as an explicit lower-confidence tier — an *earned,
  evidenced* tier, not a giveup.
- **< 70%** → the structural verdict stands; demote or drop.

Recall is **not** in scope of this rule — therapy recall (~14%) is untouched by
any keyword-side work and remains a permanent disclosed caveat regardless of
outcome. This program improves precision only.

Anti-over-engineering checkpoint: if a lever clears the bar, **stop** — do not
run the next lever for its own sake.

---

## Lever 1 — Census validation for low-volume clean keywords (therapy)

**Thesis.** The project's n=100 validation method has a 50-hit "volume floor":
keywords below it can't be sampled at n=100, so they were dismissed. But the
floor is a *sampling-method artifact, not a quality bar*. A keyword with 29
corpus hits is validated by reading **all 29** — a full population census, with
no sampling error. Therapy's clean vocabulary is fragmented across many rare
phrasings; census validation is the method that can admit them.

**Method.** 22 specific AI-as-therapy candidate phrasings (from the 2026-05-15
therapy mining, minus phrases subsumed by existing keywords and the 4
already-failed candidates) were pre-screened for corpus hits, then every
word-boundary match was pulled — 491 unique posts — and classified blind,
dual-rubric (topical + strict), by 13 CC agents, identical protocol to the
spot-check audit. Reproducible: `therapy_census_prescreen.py`,
`therapy_census_build.py`, `therapy_census_score.py`; batches/results under
`analysis/keyword_pipeline/therapy_census_2026-05-16/`.

**Result — 15 of 22 candidates clear the 80% topical KEEP gate:**

| Verdict | Count | Candidates |
|---|--:|---|
| KEEP (≥80% topical) | 15 | my psychiatrist, talk therapy, go to a therapist, my own therapist, better than therapy, cheaper than therapy, helped me heal, afford therapy, real therapist, someone to vent to, actual therapist, process trauma, talked me through, seeing a therapist, my psychologist |
| REVIEW (60–79%) | 6 | mental health support, therapy sessions, like a therapist, therapy session, therapy tool, see a therapist |
| CUT (<60%) | 1 | talk me down |

Clean **new** therapy volume recoverable from the 15 KEEP candidates (dedup
union, posts not already therapy-tagged): **142 posts**.

**Caveats on the KEEP set (honest reading):**
- *Census removes sampling error, not classifier error.* Still LLM-graded, no
  human gold anchor — same limitation as the parent audit.
- *Census certifies the current population, not future matches.* Eight KEEP
  keywords have ≤10 current hits (three have ≤5). 100% on n=3 is a true census
  of today's matches but a weak guarantee as the keyword accrues volume — these
  go on the drift-check watch list.
- *Soft KEEPs.* `my psychologist` (81% topical / 39% strict) and
  `seeing a therapist` (85% / 50%) pass the project's locked *topical* gate but
  have large topical–strict gaps — admitted, flagged.

### Projected rebuilt therapy line

Existing therapy keywords, production volume × confirmed topical precision
(`emotional support` 56% and `therapeutic` 55% per the n=100 confirmatory read;
others n=20 screen):

| Keyword | Vol | Topical |
|---|--:|--:|
| emotional support | 571 | 56% |
| therapeutic | 328 | 55% |
| coping mechanism | 252 | 70% |
| for therapy | 109 | 90% |
| as a therapist | 66 | 75% |
| ai therapist | 53 | 90% |
| free therapy | 29 | 90% |
| ai therapy | 24 | 65% |

Current volume-weighted topical precision ≈ **64%** (matches the audit).

**Scenario: cut `therapeutic` + `emotional support`, add the 15 KEEP census keywords.**

- Remaining 6 original keywords: ~533 tags, ~77% as a group.
- 15 census keywords: ~170 new tags, ~84% as a group.
- **Rebuilt line ≈ 79% volume-weighted topical precision at ~49% of current volume.**

Compare the handoff's option C ("cut both, keep clean core"): ~78–80% at **~37%**
volume. **Lever 1 roughly doubles the survivable volume of the precise-therapy
option** — that is the headline result. It does not, on its own, clear 80%.

### Stopping-rule checkpoint after Lever 1

~79% sits exactly on the 70–79% / ≥80% boundary → at this point an *earned
low-confidence tier*, not yet a clean peer line. The single biggest apparent
drag is `coping mechanism`: 252 tags (the largest remaining keyword) at the
audit's 70%. The stopping rule says continue to Lever 2.

> **Correction (after Lever 2's census, below):** the ~79% here is wrong — it
> uses `coping mechanism` at the n=20 audit screen value of 70%. A full census
> measured it at **92%**. The corrected post-Lever-1 rebuilt line is **~87%**,
> not ~79%. The 70% was screen error; see Lever 2.

Note the cut is a real shrinkage: the clean therapy line drops from ~913 real
posts to ~555 — a ~40% lower line on the chart. That is the precision/recall
tradeoff made explicit, and it makes this a versioned **v9** methodology change:
historical re-tag, changelog entry, methodology marker on the chart.

---

## Lever 2 — Co-occurrence context gating: NOT NEEDED

Lever 2 was going to gate the weak high-volume keywords. Before designing any
gate, every post matched by a gate-candidate keyword has to be labelled — so
the gated-in subset's precision can be measured. That labelling step is a full
**census** of each candidate keyword. And the census answered the question
before any gate was built.

**Gate-candidate keywords, n=20 audit screen vs. full census topical precision:**

| Keyword | Theme | n=20 screen | **Census** | n |
|---|---|--:|--:|--:|
| coping mechanism | therapy | 70% | **92%** | 253 |
| personhood | consciousness | 68% | **95%** | 124 |
| selfhood | consciousness | 85% | **93%** | 96 |
| subjective experience | consciousness | 75% | **92%** | 72 |
| inner life | consciousness | 70% | **84%** | 40 |
| has a soul | consciousness | 75% | **89%** | 37 |
| more than code | consciousness | 45% | **87%** | 34 |
| tulpa | consciousness | 45% | **64%** | 29 |
| lemoine | consciousness | 68% | **89%** | 19 |
| not just an ai | consciousness | 24% | **47%** | 17 |
| sapience | consciousness | 64% | **79%** | 14 |
| soulbonder | consciousness | 50% | **62%** | 14 |

**Every single keyword's census came in higher than its n=20 screen** — by an
average of ~+20 points. This is the `goodbye` correction (55%→81%) reproduced
across an entire theme. The weak keywords the gates were meant to fix were not
weak; they were **mis-measured**.

This is not census leniency. The same census protocol returned 55–56% for
`emotional support` and `therapeutic` (the original audit's n=100 confirmatory
reads). The method discriminates — it produces low numbers for genuinely weak
keywords. The n=20 per-keyword screens simply have ±10–25-point error, exactly
as the spot-check audit itself warned, and that error ran systematically low.

**Consequence — no keyword needs a gate.** The keywords flagged for gating are
87–95% precise. The only genuinely weak keywords left (`emotional support` 56%,
`therapeutic` 55%, `not just an ai` 47%, `soulbonder` 62%, `tulpa` 64%) are best
*cut*, not gated. Building co-occurrence-gating machinery would be solving a
problem that does not exist — over-engineering of exactly the kind the project's
own history warns against. **Lever 2 is dropped.**

Census artifacts: `gate_census_build.py` / `gate_census_score.py` /
`gate_census_2026-05-16/`, `consc_remainder_build.py` /
`consc_census_2026-05-16/`, recompute in `theme_census_recompute.py`.

---

## Final result — both themes clear the bar; the stopping rule fires

| Theme | Audit said | Census says | Action |
|---|--:|--:|---|
| **consciousness** | ~68% | **~87%** (all 11 keywords, full census) | Already a peer line. The "weakness" was n=20 screen error. Cut `not just an ai` (47%) → ~88%. Optionally cut `soulbonder`/`tulpa`. |
| **therapy** | ~64% | ~68% as-is; **~87% rebuilt** | Cut `emotional support` (56%) + `therapeutic` (55%); add the 15 Lever-1 census keywords. Rebuilt line ≈ **87%** topical at ~49% of current volume. |

Both rebuilt/recomputed lines clear the **≥80%** threshold → **both stay full
peer lines on the chart.** No demotion, no confidence tier, no LLM, no gating.

**The stopping rule fires: stop here.** The bar is cleared; running further
levers would be over-engineering.

### What this changes about the handoff's decision

The handoff's §4 decision (therapy options A/B/C/D, all ≤~64% or LLM) and §5
("demote therapy / consciousness to a low-confidence tier") were both reasoned
on the audit's volume-weighted theme numbers — which were computed from n=20
per-keyword screens that systematically understated. With census measurement:

- **Therapy is defensible as a peer line** — at ~87%, rebuilt — *better* than
  handoff option C (~78–80% at 37% volume), because Lever-1 census recovery
  roughly doubled the survivable volume.
- **Consciousness was never weak.** ~87% censused. No action needed beyond
  cutting one dead keyword.

### Honest caveats that still stand

1. **Recall is unchanged.** Therapy keyword recall ≈14%; the chart is still a
   precision-first *floor*. This program improved precision only. Permanent
   disclosed caveat.
2. **The therapy cut is a real ~40%-shorter line.** Cutting `emotional support`
   + `therapeutic` removes ~358 genuine therapy posts too; Lever 1 adds ~142
   back. Net the clean line is smaller — the precision/recall tradeoff made
   explicit. This is a versioned **v9** change: re-tag history, changelog,
   methodology marker on the chart.
3. **Topical rubric.** ~87% is the project's locked topical standard; the strict
   floor is ~70% for both themes. Band ≈ 70–87%.
4. **Still LLM-graded** — no human gold anchor, same limitation as the parent
   audit. The 72-post human anchor remains worth coding once.
5. **Small KEEP keywords** (8 of the Lever-1 KEEPs have ≤10 hits) go on the
   drift-check watch list — a census certifies today's matches, not future ones.

### Recommended follow-up (not done here — would itself need a checkpoint)

The audit's per-keyword n=20 screens understated **every** keyword they were
checked against here. That means the audit's theme numbers for the *other four*
themes (romance ~75%, rupture ~78%, etc.) are also built on noisy screens and
are probably understated too. Census validation is now built and cheap
(`*_census_build.py` + `*_census_score.py`). Re-censusing the full 92-keyword
set would replace the entire audit's screen layer with population measurements
— worth doing once, as a separate task, before any About-page precision numbers
are published.

### Nothing committed

`config/keywords_v8.yaml` is unchanged. The therapy keyword changes (cut 2, add
15) and `not just an ai` cut are a v9 methodology change and need researcher
sign-off + historical re-tag before anything ships. This document is analysis.

---

## Addendum — human gold-anchor calibration (2026-05-16, same day)

The numbers above are LLM-graded. To break the tie between the two LLM rounds
(my census round vs. the 2026-05-15 audit round, which disagreed ~11 pts), a
72-post human gold anchor was coded by the researcher — blind, dual-rubric-free,
one verdict per post. 3 posts were dropped as title-only/un-codeable; 69 coded.
Reproducible: `gold_anchor_build.py` / `gold_anchor_score.py`,
`analysis/keyword_pipeline/gold_anchor_2026-05-16/`.

| Sample | Human | My census round | Original audit round |
|---|--:|--:|--:|
| All (n=69) | 86.8% | 83.3% (−3.4) | — |
| Therapy (n=34) | 79.4% | 81.2% (+1.8) | — |
| Consciousness (n=35) | 94.1% | 85.3% (−8.8) | — |
| Audit overlap (n=16) | 93.8% | — | 78.6% (−15.2) |

**This corrects an error earlier in this program.** The mid-cycle "re-read"
concluded my census round was ~11 pts too lenient and that its numbers should
be discounted by ~11 pts. The human anchor shows the opposite: my census round
is well-calibrated — it runs *slightly strict* (−3.4 overall, dead-on for
therapy, and it under-counts consciousness). It was the **original 2026-05-15
audit round** that was off, running ~10–15 pts below human truth (n=16, so treat
the magnitude loosely). The census numbers in this document need **no downward
discount**; if anything they are mild underestimates. Therapy and consciousness
clearing ~80%+ stands.

Caveats: one human coder, coding generously (topical "when in doubt YES"); small
n per theme; the audit-round calibration is only 16 overlapping posts.

### The real finding — therapy and addiction are one behavior

Coding the anchor surfaced something more important than the precision numbers:
**the therapy and addiction themes are not cleanly separable, by construction.**
Both track the same underlying behavior — emotional reliance on an AI — and the
only thing dividing them is the writer's *valence*: neutral/positive framing
("it's my coping mechanism", "it helps me cope") reads as therapy; negative
framing ("I'm addicted", "I can't stop", "I need to quit") reads as addiction.
They are two overlapping circles with a large shared middle (posts that are
genuinely both) and small exclusive regions at each end (intentional healthy
support with no compulsion; pure compulsion/quitting with no therapeutic
framing).

Consequences:
- The therapy line's measured "noise" is substantially this overlap. A
  therapy-tagged post that looks like it belongs under addiction usually belongs
  under **both** — that is correct dual-tagging under the project's overlap
  policy, not a false positive. Much of the 2026-05-15 audit's "theme-mismatch"
  count for therapy was this legitimate linkage scored as error.
- The two lines are **not independent signals**; they share posts on purpose.
- The genuinely interesting derived signal is the *balance* between them over
  time — whether AI-reliance discourse is tilting from "this helps" toward
  "I can't stop".

**Decision (researcher, 2026-05-16):** keep both themes; let them overlap
freely; document the linkage rather than wall them off. The fix is presentation,
not keywords. Applied: the About page's "How to read the lines" section now
carries a limit, "Therapy and addiction are two readings of one behavior," and a
changelog entry records the re-check and the linkage. `CLAUDE.md` updated
(therapy-noise note + overlap policy). No keyword or methodology change.
