# Therapy keyword discovery + decision — 2026-05-15

Follow-up to the spot-check audit (`docs/keyword_context_spotcheck_2026-05-15.md`),
which found the therapy theme weakest (~64% volume-weighted topical precision,
its two biggest keywords `emotional support` and `therapeutic` ~55%). The
researcher asked: *maybe we just don't have the right keywords — try before
cutting.* This documents that attempt and its result.

## What was tried

A full discovery cycle, the project's validated anchor-mining method:

1. **Anchor set** — 144 posts independently confirmed (blind, dual-rubric) as
   real AI-as-therapy discourse, drawn from the audit + confirmatory reads.
2. **Mining** — 5 parallel CC agents read the anchor set and extracted candidate
   keyword vocabulary, ranked by specificity, leakage flagged.
3. **Volume pre-screen** — corpus-hit counts for every candidate.
4. **Validation** — n=100 dual-rubric classification for every candidate that
   cleared the volume floor (450 posts, 14 agents).

## Result: no candidate cleared the bar

**Pre-screen.** Only 5 of ~20 mined candidates cleared the 50-hit volume floor.
The precise, clean-looking ones — `free therapy` (29), `my psychologist` (29),
`ai for therapy` (16), `my psychiatrist` (10) — are still sub-floor *even after
the corpus nearly doubled* with the 2017+ backfill. Therapy's precise vocabulary
is genuinely too fragmented to keyword.

**Validation** (n=100 each, topical / strict precision):

| Candidate | Topical | Strict | Verdict |
|---|--:|--:|---|
| `vent to` | 78% | 41% | Borderline — below the 80% KEEP gate |
| `psychologist bot` | 75% | 43% | Fail — catches the named C.AI "Psychologist" character in non-therapy roleplay |
| `therapy bot` | 73% | 25% | Fail — Replika jargon for a *degraded* companion (rupture, not therapy) |
| `therapist bot` | 61% | 32% | Fail — same "therapist bot syndrome" rupture jargon |
| `comfort character` | 33% | 17% | Fail — parasocial/fandom label, not therapeutic use |

**Not one candidate reached the 80% KEEP threshold.** The closest, `vent to`
(78%), only qualifies as researcher-accepted at best.

## Why therapy resists keywords — confirmed, not assumed

Two independent failure modes, both now evidenced fresh:

1. **Fragmentation.** The clean, specific phrasings (`my ai therapist`,
   `instead of therapy`, `my psychologist`) are each individually too rare to
   pass a volume floor. The community's therapy vocabulary is spread across
   dozens of low-frequency phrasings.
2. **Polysemy / repurposing.** The phrasings that *are* high-volume get
   repurposed by the communities. `therapy bot` / `therapist bot` look maximally
   specific — yet in r/replika they are an *insult* for a companion gone cold
   and scripted after an update (a rupture complaint). This is the exact failure
   that turned `therapeutic` into an insult. The vocabulary doesn't hold still.

The mining agents also documented the structural recall gap: most real
AI-as-therapy posts describe the behaviour naturalistically ("I talked to it
when things got bad and it helped") with *no* therapy vocabulary at all — they
cannot be caught by any keyword without also catching all of romance and
companionship.

**Conclusion: this is not a keyword-selection failure that better keywords fix.
It is a property of the construct in this corpus.** The "try before you cut"
test was run in full, and it came back negative.

## Decision options

There is no move that makes therapy both clean and full-volume. The realistic
options, with quantified effect on the therapy line's volume-weighted topical
precision (currently ~64%):

| Option | Precision | Volume | Notes |
|---|--:|--:|---|
| **A. Status quo + disclosure** | ~64% | 100% | Keep all keywords; lean on the About-page caveat already drafted. Keeps `therapeutic`, which has *documented time-varying drift* (insult-use spikes with model releases) — so the therapy *trend*, not just its level, stays partly corrupted. |
| **B. Cut `therapeutic`, add `vent to`** | ~69% | ~95% | Removes the one keyword with documented trend-corrupting drift; adds the one borderline-decent candidate the discovery produced. Modest precision gain, small volume loss. Versioned v9 change. |
| **C. Cut `therapeutic` + `emotional support`, keep clean core + `vent to`** | ~78–80% | ~37% | Therapy becomes a small, genuinely precise line built on `coping mechanism`, `ai therapist`, `ai therapy`, `vent to`. Honest, but the theme nearly two-thirds shrinks. |

Any of B or C is a versioned methodology change: re-tag history, changelog
entry, and a methodology marker if the line visibly moves.

## Recommendation

**Option B.** It is the evidence-based middle: the discovery cycle proved no
keyword fix exists, so continuing to carry `therapeutic` — a ~55%-precision
keyword with a *documented, model-release-driven false-positive surge* — is
carrying a known instrument fault. Cutting it removes the part that corrupts
the trend shape; adding `vent to` (researcher-accepted, 78%) is the one genuine
gain the mining produced. Therapy stays a real line, slightly cleaner, with the
honest About-page caveat doing the rest. Option C is available if you would
rather have a small truthful line than a medium caveated one.

This needs the researcher's sign-off before `keywords_v8.yaml` is touched.
