# The CharacterAI composition fault

*Recorded 2026-05-16. A structural fault surfaced by adversarial review (several
Claude Code reviewers in succession) and verified here against `data/tracker.db`.
It affects two charts — the §1 post-volume chart and the §3 theme atlas — and it
has one cause and one fix.*

---

## The fault

r/CharacterAI dominates the tracked corpus to a degree that distorts every
volume-weighted figure on the site.

- At the 2024-06 peak, CharacterAI was **90%** of curated-set post volume
  (Herfindahl index ≈ 8,150 — "one community plus rounding error").
- By mid-year: ~76% (2023), ~90% (2024), ~67% (2025), lower through 2026.

CharacterAI is also **atypical**: a mass-market roleplay platform, not a
dedicated-companionship community in the way r/replika or r/MyBoyfriendIsAI are,
and its lifecycle — 2023–24 surge, 2024–25 contraction after the Setzer lawsuit
and content-filtering — swings independently of AI-companion discourse.

Because CharacterAI is simultaneously **huge**, **atypical**, and
**lifecycle-swinging**, it distorts two things:

### §1 — the post-volume chart

The aggregate line is 75–90% CharacterAI. Its 2024→2025 "decline" (308k → 259k
posts/yr) is **entirely** CharacterAI (−76k); the rest of the curated set *grew*
(+27k, +45%). The aggregate falls only because CharacterAI's drop outweighs
everyone else's rise.

### §3 — the theme atlas (per-1k rates)

The per-1k rate's denominator includes CharacterAI. As CharacterAI's denominator
share swung from ~90% to ~35%, the theme rates moved inversely:

| theme | Pearson r (rate vs CharacterAI denominator share) |
|---|---|
| therapy | −0.76 |
| rupture | −0.69 |
| consciousness | −0.64 |
| romance | −0.59 |
| addiction | −0.58 |
| sexual_erp | −0.21 |

Five of six themes are moderately-to-strongly inversely coupled. sexual_erp is
the exception — its shape is driven by the Feb-2023 Replika ERP event, not the
denominator dilution.

## The disentanglement — artifact, or real?

The correlation alone cannot say whether the theme rises are genuine or a
denominator artifact. But the *database* carries per-subreddit keyword tags for
every year (`post_keyword_tags.subreddit`) — only the published JSON does not.
So the rate can be recomputed **excluding CharacterAI from the denominator**:

per-1k rate at checkpoints (2023-06 → 2024-06 → 2025-06 → 2026-04):

| theme | published (all communities) | ex-CharacterAI |
|---|---|---|
| romance | 2.5 → 1.2 → 3.6 → 2.5 | 6.6 → 4.2 → 10.1 → 6.6 |
| sexual_erp | 13.4 → 1.6 → 3.4 → 2.4 | 55.0 → 12.4 → 9.7 → 5.9 |
| consciousness | 0.1 → 0.0 → 0.6 → 1.6 | 0.4 → 0.0 → 1.6 → 4.1 |
| therapy | 1.0 → 0.8 → 1.9 → 3.1 | 2.0 → 0.9 → 4.3 → 6.8 |
| addiction | 0.5 → 1.5 → 3.4 → 11.4 | 0.2 → 0.5 → 6.6 → 23.7 |
| rupture | 2.5 → 2.2 → 2.9 → 12.8 | 8.0 → 3.0 → 4.1 → 13.7 |

**Conclusion: the theme rises are real.** Excluding CharacterAI, addiction,
therapy, consciousness, and rupture all still climb — several of them *more
steeply* than the published line. romance shows no secular trend either way
(its shape is preserved); sexual_erp declines from the 2023 event (preserved).

The negative correlation is **coincidence in time**, not a single artifact:
CharacterAI's lifecycle contraction and the genuine intensification of these
themes within the dedicated communities both happened over 2024–2026. The
CharacterAI bulk was *diluting* the denominator — which made the published
chart **conservative**, not falsely alarming.

What is genuinely true: the published per-1k rate's **absolute level** is
composition-dependent — ex-CharacterAI rates run 2–3× higher. A reader cannot
take the published magnitude at face value.

## The fix — one medicine, both charts

Break CharacterAI out.

1. **§1 post-volume** — a composition chart: CharacterAI vs. the rest of the
   curated set. The ex-CharacterAI band *is* the category-growth signal.
2. **§3 theme atlas** — publish the theme rate computed over the dedicated
   communities (ex-CharacterAI), or show both lines. **Note:** changing the
   published rate's denominator is a methodology change — it needs researcher
   sign-off and a version bump, per the post-ship methodology-stability rule.

## Honest limits

- "ex-CharacterAI" is *cleaner*, not clean — the remaining set still has its
  own composition (replika-heavy in the early years).
- consciousness rests on ~13 months of data — treat its number as weak.
- This isolates the denominator confound only. It does not revalidate the
  keywords or change any keyword-level precision finding.
