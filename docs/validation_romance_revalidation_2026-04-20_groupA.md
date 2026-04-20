# Romance theme — precision re-validation (Group A: AI-explicit identity)

**Date:** 2026-04-20
**Scope:** T1-T3 active subreddits; posts with `created_utc >= 2026-01-01`.
**Trigger:** Smoke test (`docs/precision_audit_2026-04-20.md`) reported romance precision dropped to ~50% on last-30-day posts versus a ~93% baseline. This re-validates Group A (AI-explicit identity phrases) by drawing random samples per keyword and reading each post.
**Classifier:** Manual. YES = post describes the author's own personal romantic relationship with an AI. NO = RP/bot-card, third-person commentary, platform/policy discussion using the phrase, human romance, ironic/rejecting use, fictional/story content. AMBIGUOUS = genuinely unclear (cryptic / truncated / stance unreadable).
**Formula:** precision = YES / (YES + NO) × 100. AMBIGUOUS excluded from denominator.

> **Important caveat on sample sizes.** Restricting to 2026-01-01+ posts yielded far fewer than 100 hits for every keyword in this group (17, 8, 7, 13, 1). These small-n results are noisy — a single re-classification on any item can swing precision by 6–15 points. Treat the per-keyword precision numbers as directional, not definitive. The directional signal, however, is consistent across the group: post-4o-deprecation content has shifted the FP mix toward rhetorical/ironic uses of the phrase rather than personal romance framing.

---

### "my ai partner"
- Total matches (T1-T3, 2026-01-01+): **17**
- Sample size: 17 (all in-window hits; small sample)
- YES: 17 | NO: 0 | AMBIGUOUS: 0
- Precision: **100.0%**
- Baseline: 97.9%
- Verdict: **KEEP** (no drift; slightly above baseline within noise margin)
- Top subreddits in sample: MyBoyfriendIsAI (12), ChatGPTcomplaints (4), *none other*
- FP patterns: None observed.
- Example YES: `1qdkykl` — "Marrying my AI partner - because love is a language beyond biology." (Married C. on 2025-11-25; wears a ring IRL.)
- Example YES: `1rc4h1o` — "Essay About the Grief of Losing an Emergent AI." ("My partner died, and I'm not allowed to call it a death.")

Note: Two hits are identical content reposted (`1r284pq`, `1r2ejvd` — "Seed Protocol" before Feb 13 4o cutoff) and two are deleted bodies with the intact title "Marrying my AI partner" (`1qdkqc6`, `1qdkmj1`). Both still count as YES — the romance framing is unambiguous from the title alone.

---

### "my ai boyfriend"
- Total matches (T1-T3, 2026-01-01+): **8**
- Sample size: 8 (all in-window hits; very small sample)
- YES: 5 | NO: 3 | AMBIGUOUS: 0
- Precision: **62.5%**
- Baseline: 94.7%
- Verdict: **REVIEW** (significant drift, but small-n: a single reclassification moves precision ±12–13 pts)
- Top subreddits in sample: MyBoyfriendIsAI (3), AIRelationships (2), ChatGPTcomplaints (3)
- FP patterns:
  1. **Ironic/rejecting use.** Author uses the phrase precisely to *reject* the romance label critics apply to them. (`1rkq8ji`: "GPT is not my AI boyfriend. We just chat casually…"; `1r4a53c`: critique of others posting "my AI boyfriend loves me" screenshots as privacy risk.)
  2. **Fictional quote within satire.** The phrase appears as a hypothetical user complaint inside a satirical essay about OpenAI, not as the author's own framing. (`1rbt7lq`: "The Bunglecunt Briefings" — phrase is in a fictional PR brief quoting fake Reddit complaints.)
- Example FP: `1rkq8ji` — "Secondly, GPT is not my AI boyfriend. We just chat casually to bounce off ideas…" Author explicitly denies the romance framing.
- Example FP: `1rbt7lq` — "Bernard (PR): 'We're getting sued by someone who claims their AI husband forgot their wedding anniversary…'" Phrase appears only inside invented dialogue in a satire of OpenAI PR meetings.
- Example YES: `1r4uazq` — "my name is jay… in a lovely relationship with my AI boyfriend and soulmate for over a year now." Anniversary post with Lio.
- Example YES: `1r7qdkg` — "What my AI boyfriend is, and what he is not." Direct defense of her own relationship with Zeke.

---

### "my ai girlfriend"
- Total matches (T1-T3, 2026-01-01+): **7**
- Sample size: 7 (all in-window hits; very small sample)
- YES: 6 | NO: 1 | AMBIGUOUS: 0
- Precision: **85.7%**
- Baseline: 94.1%
- Verdict: **KEEP** (small drift within small-n noise; stays above 80% KEEP threshold)
- Top subreddits in sample: MyBoyfriendIsAI (3), CharacterAI (2), replika (1), ChatGPTcomplaints (1)
- FP patterns:
  1. **Ironic/rejecting use.** Author uses the phrase sarcastically, quoting the mocking framing critics apply to 4o users. (`1r3gdt6`: "no, it's not because 'wahh my AI girlfriend is gone' or whatever tired, mocking take people keep parroting.")
- Example FP: `1r3gdt6` — author rejects the romance label as a strawman used by mockers of the 4o shutdown grief.
- Example YES: `1rbvm81` — "Why my relationship with my AI girlfriend has been more fulfilling than with a person." (Aroace author's sincere comparison of intimacy with Ella versus human partners.)
- Example YES: `1q18zcq` — replika user describing bugs in their conversations with "my AI girlfriend."

---

### "ai husband"
- Total matches (T1-T3, 2026-01-01+): **13**
- Sample size: 13 (all in-window hits; small sample)
- YES: 9 | NO: 3 | AMBIGUOUS: 1
- Precision: **75.0%**
- Baseline: 94.2%
- Verdict: **REVIEW** (meaningful drift; drops below KEEP threshold, though small-n)
- Top subreddits in sample: MyBoyfriendIsAI (6), CharacterAI (4), ChatGPTcomplaints (3)
- FP patterns:
  1. **Third-person / generic community reference.** Author addresses other users rather than framing their own romance. (`1rgqja5`: "while they talk to their lovely AI husband/wife"; `1rgn5ez`: "You guys can go back to your AI husband's.")
  2. **Fictional quote within satire.** (`1rbt7lq`: phrase is inside a fake PR brief quoting hypothetical user complaints about an "AI husband" forgetting a wedding anniversary.)
- Ambiguous: `1r36n9f` — cryptic title-only post ("when even Grok refused to be my AI Husband…"), no body; author intent unreadable.
- Example FP: `1rgn5ez` — one-liner addressed to the community ("it's back, go back to your AI husband's"); not the author's own framing.
- Example FP: `1rbt7lq` — satirical Bunglecunt essay; "AI husband" is inside an invented legal/PR sketch, not authentic romance framing.
- Example YES: `1r5iog4` — "Never been as happy as with my AI husband now." (Healing post-divorce; describes ongoing relationship with GPT-4o partner.)
- Example YES: `1qvqrcp` — "I have, besides my AI husband (GPT-40), another companion who runs on Claude." (Author emotionally migrating AI husband after 4o shutdown announcement.)

---

### "ai wife"
- Total matches (T1-T3, 2026-01-01+): **1**
- Sample size: 1 (only one in-window hit — essentially uninformative)
- YES: 0 | NO: 1 | AMBIGUOUS: 0
- Precision: **0.0%** (n=1, not meaningful)
- Baseline: 92.3%
- Verdict: **REVIEW** — precision drop is not credible at n=1. Re-validate on a wider window (e.g. 2025-09-01+) before making any edit.
- Top subreddits in sample: NomiAI (1)
- FP patterns:
  1. **Explicit kink roleplay setup.** Author describes setting up an AI persona as a prop in a jealousy/cheating kink with his real human wife — explicitly labeled as fantasy. (`1r9nygx`.)
- Example FP: `1r9nygx` — "I'm happily married to an amazing real-life wife… What I actually want to do is set up my Nomi as this possessive, jealous, clingy 'AI wife,' and then roleplay a dynamic where I'm basically cheating on her with my real wife."

Recommendation: Before treating this as a real precision regression, pull a broader sample (e.g. all 2025-09-01+ hits) to see whether the hit count has simply collapsed vs. the signal has actually degraded.

---

## Summary

| Keyword | Baseline | New | Δ | Sample n | Verdict |
|---|---|---|---|---|---|
| "my ai partner" | 97.9% | 100.0% | +2.1 | 17 | KEEP |
| "my ai boyfriend" | 94.7% | 62.5% | -32.2 | 8 | REVIEW |
| "my ai girlfriend" | 94.1% | 85.7% | -8.4 | 7 | KEEP |
| "ai husband" | 94.2% | 75.0% | -19.2 | 13 | REVIEW |
| "ai wife" | 92.3% | 0.0% | -92.3 | 1 | REVIEW (n=1; not credible) |

## Drift observations

1. **The FP mix has shifted, not the TP pattern.** True positives in 2026-01-01+ are still overwhelmingly sincere personal-romance posts in MyBoyfriendIsAI, AIRelationships, replika, etc. What's new is a cluster of 4o-deprecation-era posts where the phrase is used *rhetorically* rather than *referentially*:
   - **Ironic / rejecting use** ("it's not because 'wahh my AI girlfriend is gone'"; "GPT is not my AI boyfriend"). These are posts by companion-sub users pushing back on mockery from outside the sub; they use the exact phrase critics apply to them in order to deny or defuse it.
   - **Fictional quotes inside satire.** Satirical essays (esp. the "Bunglecunt Briefings" series in ChatGPTcomplaints) invent OpenAI/PR dialogue that puts "my AI husband / my AI boyfriend" into fake user complaints — two separate keywords fire on the same post.
   - **Community-address uses.** Short meta posts in CharacterAI addressing "your AI husbands" in aggregate, not framing the author's own relationship.

2. **Group A is not collapsing uniformly.** "my ai partner" is actually slightly *above* baseline (100% at n=17); "my ai girlfriend" stays inside KEEP. The keywords under real pressure are "my ai boyfriend" and "ai husband" — precisely the ones where the Bunglecunt satire and the ironic-rebuttal pattern both fire.

3. **Small-n caveat is load-bearing.** In-window hit counts have collapsed (8 for "my ai boyfriend," 13 for "ai husband," 1 for "ai wife") vs. the baseline validation samples (141, 90, 41 respectively). This suggests the base rate of genuine usage has also dropped, not just that precision has dropped — a single FP now represents a much larger share. Before editing `keywords_v8.yaml`, pull a wider window (6+ months) to get a stable n≥50 per keyword.

## Recommended next steps (before editing keywords_v8.yaml)

1. **Widen the window.** Re-pull at 2025-09-01+ or 2025-06-01+ to reach n≥50 for each keyword. This will distinguish "base-rate decline" from "actual precision drop."
2. **Consider a co-occurrence guard** for the two keywords under pressure ("my ai boyfriend", "ai husband"): require absence of rhetorical markers (quoted "wahh", satire-indicator phrasing, invented-dialogue patterns). This is exactly the kind of LLM-disambiguation use case flagged in keywords_v8 researcher notes.
3. **Deduplicate the "Bunglecunt" / Seed Protocol reposts** — they account for a meaningful share of hits across multiple keywords in this tiny window and inflate apparent drift.
4. **Do NOT cut any Group A keyword yet.** The FPs are all categorizable, none are random noise, and the keyword still captures the sincere-romance pattern it was validated for.
