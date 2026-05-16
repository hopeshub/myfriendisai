# Therapy keyword mining — batch batch_therapymine_05 (mined)

## Summary

This batch is a hard one for keyword mining. All 4 posts were confirmed
AI-as-therapy, but the vocabulary they actually use is **almost entirely the
generic stem `therapeutic`** — the exact word the task says is already failing
at ~64% precision. There is very little theme-specific phrasing to extract.
Post 4 in particular ("therapeutic effect") only matches the generic stem and
is otherwise about sentience/bonding. So the honest finding is: this small
sample does not yield strong new keywords. Below are the best candidates anyway,
ranked, with specificity warnings.

## Ranked candidate list (most promising first)

### 1. `therapeutic purposes`
- **Why it signals AI-as-therapy:** Two-word phrase explicitly framing app use
  as a mental-health/therapy function ("use the app for therapeutic purposes",
  "users still pay attention to the therapeutic purposes of the app"). The noun
  `purposes` ties `therapeutic` to *intent of use*, which is much harder to
  satisfy with the generic "the model's therapeutic tone" false positive.
- **Posts containing it:** 1 of 4 (post 1, twice).
- **Specificity:** Good. Unlikely to leak into romance/rupture/addiction. Main
  residual risk is meta-discussion of an app's intended purpose without a
  personal therapy claim, but that is still on-theme adjacent.

### 2. `most therapeutic thing`
- **Why it signals AI-as-therapy:** Superlative personal testimony pattern
  ("the MOST therapeutic thing I ever done in my life"). Signals a first-person
  lived therapeutic experience rather than a description of model behavior.
- **Posts containing it:** 1 of 4 (post 3).
- **Specificity:** Moderate. The phrase itself is clean, but it is essentially
  a one-off phrasing — low expected corpus volume. Likely a LOW VOLUME
  candidate; flagged as such.

### 3. `therapeutic effect`
- **Why it signals AI-as-therapy:** Names a therapy-like benefit of the AI
  ("I can imagine some therapeutic effect").
- **Posts containing it:** 1 of 4 (post 4).
- **Specificity:** WEAK — flagged. This is barely more than the bare
  `therapeutic` stem and would fire on clinical/meta discussion of AI's
  "therapeutic effect" in the abstract, including skeptical or research-framed
  posts. Not recommended as a standalone keyword; included only for
  completeness.

### 4. `therapeutic site` / `therapeutic app`
- **Why it signals AI-as-therapy:** "I NEED MY THERAPEUTIC SITE" (post 2) treats
  the platform itself as a therapy resource — strong AI-as-therapy framing when
  it fires.
- **Posts containing it:** 1 of 4 (post 2, as "therapeutic site").
- **Specificity:** Good when it fires, but **very low volume** — "therapeutic
  site/app" is idiosyncratic phrasing. Flagged LOW VOLUME; almost certainly
  below the 50-hit pre-screen floor.

### Rejected / not proposed
- **`emotional support`** — already in the keyword set and named as a generic
  precision problem; collides with "emotional support animal" and generic
  companion chatter. Not re-proposed.
- **bare `therapeutic`** — the existing failing keyword; nothing in this batch
  improves on it.
- **`emotional` / `bonding` / `emotional relationship`** (post 4) — these are
  romance/attachment vocabulary, not therapy. Would leak heavily into the
  romance theme. Not proposed.

## Hard-to-keyword phrasing patterns

This is the important finding from the batch:

1. **The theme rides almost entirely on the bare stem `therapeutic`.** 3 of 4
   posts use `therapeutic` and little else theme-specific. The construct is
   carried by a word that is generic by itself, so precision can only be
   recovered by *bigrams anchored on `therapeutic`* (`therapeutic purposes`,
   `most therapeutic thing`) — and those individually have low volume. The
   theme is structurally fragmented across many low-volume `therapeutic + noun`
   phrasings, which matches the CLAUDE.md note that therapy keyword mining
   keeps failing the volume floor.

2. **Naturalistic "talk to" / coping framing with no therapy vocabulary.**
   Post 3's actual signal ("made a mother figure to talk to", "nurturing",
   "loving experience") describes therapeutic use entirely through
   relationship/comfort language. A keyword search cannot catch this without
   firing on romance — it is genuinely indirect.

3. **Hedged / hypothetical therapy framing.** Post 4 discusses a "therapeutic
   effect" as a *possibility* alongside "danger of getting addicted" — the post
   is confirmed on-theme but reads as meta-reflection. Keywords that catch it
   would also catch skeptical and research-style posts, hurting precision.

**Recommendation:** Of these, only `therapeutic purposes` is worth carrying
forward to validation; the rest are low-volume or too generic. Consistent with
the standing guidance to defer therapy keyword mining until corpus growth lifts
candidates above the 50-hit floor.
