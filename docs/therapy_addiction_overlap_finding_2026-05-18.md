# The therapy ↔ addiction overlap: real, large, unmeasurable by keyword co-occurrence

**Date:** 2026-05-18
**Type:** methodological finding
**Outcome:** closes the proposed merged "Therapy ↔ Addiction" atlas view (not built, any form);
drives a correction to the About page's "two readings of one behavior" passage.
**Working trail:** `docs/therapy_addiction_view_phase0_2026-05-18.md` (data-availability gate);
`analysis/leak_test_problem_only_2026-05-18_audit.md` (90 posts, full text + per-post calls).

---

## Summary

The About page says therapy and addiction are "two readings of one behavior" and that the
two theme lines "share many of the same posts, by design." The first claim is right. The
second is not borne out by the data — and *why* it isn't is the finding.

Therapy and addiction posts almost never co-occur in the tags: only **75 posts (1.9% of
reliance-discourse)** carry both a therapy and an addiction tag. But a hand-read shows the
overlap is genuinely there — it just doesn't tag. The keyword instrument sees the
*problem*-framing of reliance cleanly and is largely blind to the *help*-framing, so a post
that holds both frames is filed as addiction-only. The shared subject the About page
describes is real; the instrument cannot measure how shared it is.

## Background — the view that prompted this

A design spec proposed replacing the separate therapy and addiction atlas tiles with one
"framing-mix" view: a ribbon decomposing reliance-discourse into HELP-only / BOTH /
PROBLEM-only cells, with the BOTH cell ("the ambivalent core") as the central object. A
data-availability gate was run first (Phase 0). It confirmed the data is structurally fine
— theme tags are stored independently per post, the full window is present — but the
BOTH-magnitude check tripped a stop condition, which this leak test then explained. **The
view was not built.**

## Measurement 1 — direct co-occurrence

From `post_keyword_tags`, post-source, full corpus window, keyword-eligible communities:

| Cell | Definition | Posts | Share |
|---|---|---|---|
| HELP-only | therapy-tagged, not addiction-tagged | 1,319 | 33.3% |
| **BOTH** | therapy- **and** addiction-tagged | **75** | **1.9%** |
| PROBLEM-only | addiction-tagged, not therapy-tagged | 2,570 | 64.8% |

BOTH never exceeds 8 posts in any month; 63% of BOTH posts sit in recovery subreddits.
post+comment tags instead of post-only moves BOTH only 75 → 89. On the face of it, the two
themes look near-disjoint.

## Measurement 2 — the leak test

If the instrument were measuring the overlap correctly, PROBLEM-only posts should be
genuinely problem-only. To check, 90 posts were drawn at random (seed 20260518) from the
2,553 PROBLEM-only posts and hand-read for an *unmatched* help/coping frame. Full bodies
and every per-post call are in `analysis/leak_test_problem_only_2026-05-18_audit.md`.

| Verdict | n | % |
|---|---|---|
| **YES — contains an unmatched help/coping frame** | **22** | **24%** |
| AMBIGUOUS | 3 | 3% |
| NO — genuinely problem-only | 62 | 69% |
| Keyword false positive (not an addiction post) | 3 | 3% |

**~1 in 4 PROBLEM-only posts is, on its own text, a BOTH post the instrument could not
see.** 95% CI ≈ 16–33%. The hand-read was conservative — frames were counted only when
explicit.

The leaks were of two kinds:

- **Ordinary-language coping frames (~18 of 22)** — help-framing carried by everyday words
  no therapy keyword chases: *"using chatbots to escape their life, and me included"*;
  *"some of these bots are safe spaces for me"*; *"use it to … cope with/numb emotions or
  … help with loneliness"*; *"I've taken so much comfort from this website"*.
- **Therapy-construct vocabulary that isn't an admitted keyword (4 of 22)** — explicit
  therapy framing that fails to tag for mechanical reasons: *"coping mechanisms"* (the
  keyword `coping mechanism` is singular; the plural slips the `\b…\b` regex); *"therapist
  bot"* (a documented rejected LOW-VOLUME keyword); *"coping medicine"*; *"like my
  therapist"* (the keyword is `as a therapist`).

Two further posts ([45] r/MyBoyfriendIsAI, [65] r/replika) are overwhelmingly *positive*
posts pulled into PROBLEM-only because `hours a day` / `finally deleted` matched a benign
mention — the band is not even uniformly problem-framed.

## Why the instrument is one-eyed

Addiction *self-labels*. "Relapse", "days clean", "cold turkey", "withdrawals" are words
people reach for deliberately, from a recovery vocabulary that is small, crisp, and matches
cleanly. Help-framing does not self-label: it rides ordinary language ("it got me
through", "a safe space", "somewhere to put my feelings") and a therapy lexicon that —
as the project already documents (CLAUDE.md, 2026-05-12) — is "structurally fragmented
across many phrasings" no keyword list captures whole.

The consequence is a **one-directional leak**: when a post holds both frames, the problem
half tags and the help half usually does not, so ambivalent posts fall into PROBLEM-only,
never into HELP-only. The keyword help:problem split is therefore not a neutral
measurement — it is **structurally biased toward the problem reading**.

## Implication

The 1.9% BOTH figure is an artifact of recall asymmetry, not a measurement of the
ambivalent core. Correcting only the measured leak — ~24% of 2,570 PROBLEM-only posts —
implies **~620 hidden BOTH posts** (CI ~390–860), which would put BOTH at **~12–24% of
reliance-discourse**. And that is still a floor: HELP-only was not leak-tested, and the
therapy keyword set's own recall is ~14%. The true overlap is large. **It cannot be
measured with this instrument**, which is by construction blind to one of the two valences
it would need to weigh.

## Decisions

1. **The merged view is not built** — not as a three-cell ribbon (it would publish a BOTH
   number wrong by ~10×), not as a "corrected" estimate (the instrument cannot support
   one), not as a qualitative reframe asserting "readers commit to one valence" (the leak
   test directly refutes that — it would be an instrument artifact dressed as a finding
   about people).
2. **Therapy and addiction remain two separate atlas tiles.** No merge, no redirect, no
   routing change. Every downstream decision about a combined view was contingent on a
   measurable mix; that contingency failed.
3. **The About page passage is revised** (below) to state the overlap honestly: real,
   large, and unmeasurable by this method, with the leak test as the evidence.
4. **The keyword set is unchanged.** The four group-(b) misses (`coping mechanisms` plural,
   `therapist bot`, `coping medicine`, `like my therapist`) are concrete candidate
   evidence for a future *versioned* therapy-keyword expansion, but a keyword change is a
   v9 step needing researcher sign-off — out of scope here.

## Copy changes applied (2026-05-18)

Three site-copy changes landed from this finding. No routing, atlas structure, or keyword
change — copy only.

**1. `web/app/about/page.tsx` — the "two readings of one behavior" passage** (`#verification`).
Was one paragraph ending "...the two lines share many of the same posts, by design; a
therapy post that looks like it belongs under addiction usually belongs under both. Read
them as a linked pair, and watch which way the balance tips." Replaced with two
paragraphs: paragraph 1 unchanged (one behavior, two framings); paragraph 2 new —

> You might expect the two lines to share many posts, then. They barely do — fewer than 1
> in 50 posts is tagged on both — and that is a limit of the instrument, not a fact about
> the behavior. Addiction announces itself: "relapse," "days clean," "withdrawals" are
> deliberate words, and they match cleanly. Help-framing hides in ordinary language — "it
> got me through," "a safe space" — and in a scattered vocabulary no keyword list captures
> whole. So a post that holds both frames usually tags only as addiction. We checked:
> hand-reading 90 posts the keywords had filed as addiction-only, about a quarter visibly
> carried a help frame the keywords missed. The overlap between these two themes is real
> and large; this method cannot measure it. Read each line on its own direction and
> timing, and do not read the gap between them as a help-versus-problem balance — that
> balance exists, but it is one these keywords are not equipped to weigh.

This drops the unsupported "share many of the same posts" and the "watch which way the
balance tips" instruction — it asked the reader to make exactly the comparison this finding
shows the instrument cannot support.

**2. `web/app/themes.ts` — the addiction-linked sentence in the therapy theme `story`.**
The same defective claim ("The two lines share posts by design.") appeared in the atlas
theme blurb. Replaced with: "In the data the two lines barely overlap — but that is the
keywords missing help-framing's ordinary language, not a sign the themes are separate."

**3. `web/app/about/page.tsx` — the "Vocabularies catch unevenly" bullet** (same section).
Strengthened to state the bias is structural and one-directional, not noise — appended:
"...even when the second theme is the larger one — and this runs one way: a theme written
in blunt, deliberate words reads higher than one written in ordinary language, whatever
the truth beneath." The leak test is one measured instance of a bias the bullet already
asserted in principle; this earns the right to state it flatly.

## Artifacts

- `docs/therapy_addiction_view_phase0_2026-05-18.md` — data-availability gate report
- `analysis/leak_test_problem_only_2026-05-18_audit.md` — 90 posts, full text + per-post calls
- `analysis/leak_test_problem_only_2026-05-18_{ids,sample}.json` — sample (seed 20260518)
