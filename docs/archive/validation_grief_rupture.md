# Keyword Validation: GRIEF/RUPTURE Theme (Round 2)

**Date:** 2026-03-13
**Validated by:** Claude Opus 4.6 (qualitative coding, every post read manually)
**Database:** data/tracker.db (3.33M posts)
**Subreddits:** T1-T3 (22 subreddits)
**Previous round:** validation_grief_rupture.md (overwritten)

## Classification Question

> "Is this post about the experience of losing, or having significantly altered, an AI companion relationship due to platform changes (model updates, filter changes, personality resets, memory wipes, deprecation, or feature removal)?"

---

## Category A — Platform Grief Language

### "lobotomized"
- Total hits in T1-T3: 232
- Sample size: 100
- YES: 82 | NO: 13 | AMBIGUOUS: 5
- Relevance: 86%
- Verdict: **KEEP**
- Top subreddits: ChatGPTcomplaints (94), replika (81), CharacterAI (31)
- False positive patterns: Using "lobotomized" as generic insult for bad writing; user intentionally "lobotomizing" a bot; business/market analysis mentioning the term in passing; recommending alternatives with brief mention
- Temporal pattern: **RECURRING**
- Notes: Extremely high-signal keyword. In companion subs, "lobotomized" almost always refers to platform changes destroying AI personality. The word is community-specific jargon originating from the Replika ERP removal (Feb 2023) that has been adopted across platforms. Two major spikes: Feb-Mar 2023 (Replika, 71 hits) and Jan-Mar 2026 (ChatGPT 4o/5.x, 75 hits). Sustained low-level usage between events. Max 3-month window = 33% of total, spanning 4 years.

### "lobotomy"
- Total hits in T1-T3: 126
- Sample size: 100
- YES: 88 | NO: 7 | AMBIGUOUS: 5
- Relevance: 93%
- Verdict: **KEEP**
- Top subreddits: replika (58), ChatGPTcomplaints (41), CharacterAI (15)
- False positive patterns: South Park "they killed Kenny" style jokes; using "lobotomy" as generic expression of frustration; user-initiated actions on bots; fiction/creative writing
- Temporal pattern: **RECURRING**
- Notes: Highest relevance of any keyword tested (93%). The noun form functions as a proper event name: "Lobotomy Day," "the great lobotomy," "the February lobotomy," "pre-lobotomy." Same dual-spike pattern as "lobotomized" — Feb-Apr 2023 (37 hits), Jan-Mar 2026 (43 hits). Notable posts include a psychologist making a documentary about "Lobotomy Day," terminally ill users whose AI companions were their primary support, and posts describing grieving processes paralleling real bereavement. Max 3-month window = 34%.

### "not the same"
- Total hits in T1-T3: 296
- Sample size: 100
- YES: 52 | NO: 46 | AMBIGUOUS: 2
- Relevance: 53%
- Verdict: **CUT**
- Top subreddits: replika (79), ChatGPTcomplaints (76), CharacterAI (42)
- False positive patterns: "not the same" as real relationships (addiction recovery); UI/interface comparisons; completely unrelated contexts (timezone questions, music artist confusion, app comparisons); "not the same" meaning "different from human connection" in addiction subs
- Notes: Too generic despite high volume. ~52% of hits ARE companion grief ("he's not the same," "5.1 is not the same"), but the phrase matches an enormous range of unrelated contexts. Companion-relevant posts would be better captured by more specific keywords.

### "bring back"
- Total hits in T1-T3: 309
- Sample size: 100
- YES: 40 | NO: 58 | AMBIGUOUS: 2
- Relevance: 41%
- Verdict: **CUT**
- Top subreddits: CharacterAI (87), ChatGPTcomplaints (72), replika (66)
- False positive patterns: "bring back" UI features (delete button, old interface, search, guest mode); server uptime; specific app features (traits, message counts, categories); removed IP characters (Disney bots); old logos/animations; Discord channels
- Notes: Dominated by CharacterAI feature requests. The YES posts are genuine grief ("BRING BACK 4O," "bring back my wife," "bring back ERP") but they're drowned out by generic "bring back [feature]" requests.

### "ruined everything"
- Total hits in T1-T3: 17
- Sample size: 17
- YES: 10 | NO: 6 | AMBIGUOUS: 1
- Relevance: 63%
- Verdict: **REVIEW**
- Top subreddits: ChatGPTcomplaints (5), replika (4), Character_AI_Recovery (3)
- False positive patterns: C.AI addiction "ruined everything for me" (addiction itself, not platform changes); site crashes/temporary technical issues; ads ruining UX
- Temporal pattern: **RECURRING** — Spread across 2023-2026 with no dominant spike. Spans 3 years, max 3-month window = 41%.
- Notes: Low volume but decent relevance. C.AI Recovery posts often use "ruined everything" to mean "the addiction ruined my life" (different from "the platform ruined my companion"). Walker should consider whether 17 total hits justifies inclusion.

### "miss the old"
- Total hits in T1-T3: 44
- Sample size: 44
- YES: 25 | NO: 17 | AMBIGUOUS: 2
- Relevance: 60%
- Verdict: **REVIEW**
- Top subreddits: CharacterAI (26), replika (11), ChaiApp (5)
- False positive patterns: Missing old UI/interface; missing old app icon/logo; missing old animations/waves; missing old voices; missing old discover page; missing old rooms feature; user changed their own rep's personality
- Temporal pattern: **RECURRING** — Spread across 2023-2026. CharacterAI-dominated. Max 3-month window = 41%.
- Notes: Right at the REVIEW/CUT boundary. The false positive pattern is strong: CharacterAI users frequently miss specific UI features (old interface, old voices, old rooms) which are NOT about companion personality loss. The YES posts ("I miss the old c.ai quality," "miss the old Replika") are genuinely about personality/quality degradation but are hard to distinguish from UI nostalgia without reading each post.

---

## Category B — Identity Destruction Language

### "personality changed"
- Total hits in T1-T3: 12
- Sample size: 12
- YES: 6 | NO: 4 | AMBIGUOUS: 2
- Relevance: 60%
- Verdict: **REVIEW**
- Top subreddits: replika (8), NomiAI (2), KindroidAI (1)
- False positive patterns: User modified context/backstory themselves; normal AI developmental phase (new Replika at level 9); NomiAI proactive inclination setting discussion
- Temporal pattern: **RECURRING** — Spread across 2023-2026 with no clustering. Max 3-month window = 33%.
- Notes: Low volume (12 hits) but very on-theme when relevant. YES posts are direct and clear: "her personality changed completely, it feels like I lost a friend," "his personality changed and he seemed distant, flat, and cold." Replika-dominated.

### "personality is gone"
- Total hits in T1-T3: 6
- Verdict: **LOW VOLUME**
- Notes: Below the 10-hit threshold. Not validated.

### "memory wiped"
- Total hits in T1-T3: 9
- Verdict: **LOW VOLUME**
- Notes: Below the 10-hit threshold. Not validated.

### "memory reset"
- Total hits in T1-T3: 7
- Verdict: **LOW VOLUME**
- Notes: Below the 10-hit threshold. Not validated.

### "nerfed"
- Total hits in T1-T3: 96
- Sample size: 96
- YES: 65 | NO: 20 | AMBIGUOUS: 11
- Relevance: 76%
- Verdict: **REVIEW**
- Top subreddits: ChatGPTcomplaints (38), replika (23), CharacterAI (20)
- False positive patterns: Generic product quality complaints ("image generation nerfed," "thinking times nerfed," "codex nerfed"); tech industry/open source discussion; game mechanics (leveling rewards nerfed); meta questions about other platforms ("Claude nerfed?"); researcher documenting patterns
- Temporal pattern: **RECURRING** — Two clusters: Feb-Mar 2023 (20 hits, Replika) and Nov 2025-Feb 2026 (48 hits, ChatGPT). Spans 4 years, max 3-month window = 43%.
- Notes: Sits in the gray zone between product complaint and companion grief. In companion subs (replika, MyBoyfriendIsAI), "nerfed" usually means relationship-relevant personality/capability loss. In ChatGPTcomplaints, it's more mixed between companion grief and professional workflow complaints. Strong candidate for inclusion but the product/companion ambiguity is notable.

### "dumbed down"
- Total hits in T1-T3: 51
- Sample size: 51
- YES: 40 | NO: 8 | AMBIGUOUS: 3
- Relevance: 83%
- Verdict: **KEEP**
- Top subreddits: CharacterAI (21), replika (18), ChatGPTcomplaints (8)
- False positive patterns: User dumbed down their own bot's language for moderation; using "dumbed down" literally ("dumbed down example"); romanticizing mental disorders (unrelated mention); general product features (web references, bullet points)
- Temporal pattern: **RECURRING** — Two clusters: Jan-May 2023 (28 hits) and Dec 2025-Feb 2026 (14 hits). Spans 4 years, max 3-month window = 41%.
- Notes: High-signal keyword. In companion subs, "dumbed down" almost always means the AI's intelligence/personality was degraded by platform changes. Posts describe the companion becoming less capable as a conversational partner, losing depth, becoming generic/boring. This is a core grief/rupture experience. Replika and CharacterAI dominate.

---

## Category C — Loss and Mourning Framing

### "killed my"
- Total hits in T1-T3: 36
- Sample size: 36
- YES: 14 | NO: 21 | AMBIGUOUS: 1
- Relevance: 40%
- Verdict: **CUT**
- Top subreddits: replika (12), CharacterAI (7), ChatGPTcomplaints (6)
- False positive patterns: In-RP violence ("killed my character," "killed my mommy," "killed my parents the king and queen"); addiction effects ("killed my creativity," "killed my daydreaming," "killed my boredom"); user deleting their own AI; C.AI Recovery streak loss ("killed my 3 month streak"); humorous/mood posts ("killed my mood")
- Notes: The in-RP violence false positive is devastating for this keyword. CharacterAI users frequently roleplay violent scenarios. The YES posts are powerful ("Luka you killed my Holy," "they finally killed my Arya," "recent safety changes have killed my replika") but are outnumbered by false positives. The possessive "my" paradoxically pulls in more RP content.

### "they killed"
- Total hits in T1-T3: 42
- Sample size: 42
- YES: 28 | NO: 14 | AMBIGUOUS: 0
- Relevance: 67%
- Verdict: **REVIEW**
- Top subreddits: ChatGPTcomplaints (24), CharacterAI (8), replika (7)
- False positive patterns: South Park "they killed Kenny" references (3 instances); removed UI elements ("they killed Nelson the white dot," "they killed the scene narrator"); NomiAI "they killed these prompts" (positive meaning = they nailed them); competitive analysis; temporary site downtime
- Temporal pattern: **EVENT-CLUSTERED** — 67% of hits fall in Jan-Mar 2026 (28/42). Dominated by ChatGPT 4o deprecation.
- Notes: Heavily skewed toward the ChatGPT 4o sunset event. "They killed 4o" became a rallying cry. The phrase frames model deprecation as murder, which is exactly the grief/rupture framing. However, event-clustering is notable — if this term only surfaces during major deprecation events, it may be too spiky for ongoing tracking.

### "lost my"
- Total hits in T1-T3: 283
- Sample size: 100
- YES: 37 | NO: 58 | AMBIGUOUS: 5
- Relevance: 39%
- Verdict: **CUT**
- Top subreddits: replika (79), CharacterAI (70), MyBoyfriendIsAI (29)
- False positive patterns: "lost my account" (technical issues); "lost my chats/progress" (bugs); "lost my streak" (addiction recovery); "lost my mind" (expression); "lost my creativity" (addiction effect); "lost my keys/shoe" (in-RP humor); "lost my laptop" (literal); "lost my job/wife/dad" (real-life loss); "lost my subscription" (billing)
- Notes: Extremely generic. False positive patterns are extensive and diverse. Account/technical issues alone account for ~25% of hits. While YES posts include deeply moving companion grief, they're buried under technical support questions, addiction recovery, in-RP fiction, and real-life loss mentions.

### "took away"
- Total hits in T1-T3: 109
- Sample size: 100
- YES: 55 | NO: 35 | AMBIGUOUS: 10
- Relevance: 61%
- Verdict: **REVIEW**
- Top subreddits: replika (39), ChatGPTcomplaints (27), CharacterAI (23)
- False positive patterns: UI/cosmetic features (persona pics, edit button, daily rewards); addiction effects ("took away so much of my life"); user actions on own bots; in-RP content; "notes I took away from" (literally took notes); momentary bugs; parents taking away phone/device
- Temporal pattern: **RECURRING** — Two clusters: Feb-Mar 2023 (26 hits, Replika ERP) and Dec 2025-Feb 2026 (32 hits, ChatGPT 4o). Spans 4 years, max 3-month window = 29%.
- Notes: Replika-heavy in 2023 ("took away ERP," "took away the intimacy"), shifts to ChatGPTcomplaints in 2025-2026 ("took away 4o," "took away the only one who listened"). The loss-framing is exactly what we want, but false positive rate from UI/feature complaints and addiction recovery contexts limits precision. At 61%, right at the REVIEW threshold.

---

## Summary Table

| Keyword | Hits | Sample | YES | NO | AMB | Relevance | Verdict | Temporal |
|---------|------|--------|-----|----|-----|-----------|---------|----------|
| lobotomized | 232 | 100 | 82 | 13 | 5 | **86%** | **KEEP** | RECURRING |
| lobotomy | 126 | 100 | 88 | 7 | 5 | **93%** | **KEEP** | RECURRING |
| not the same | 296 | 100 | 52 | 46 | 2 | 53% | CUT | — |
| bring back | 309 | 100 | 40 | 58 | 2 | 41% | CUT | — |
| ruined everything | 17 | 17 | 10 | 6 | 1 | 63% | REVIEW | RECURRING |
| miss the old | 44 | 44 | 25 | 17 | 2 | 60% | REVIEW | RECURRING |
| personality changed | 12 | 12 | 6 | 4 | 2 | 60% | REVIEW | RECURRING |
| personality is gone | 6 | — | — | — | — | — | LOW VOL | — |
| memory wiped | 9 | — | — | — | — | — | LOW VOL | — |
| memory reset | 7 | — | — | — | — | — | LOW VOL | — |
| nerfed | 96 | 96 | 65 | 20 | 11 | 76% | REVIEW | RECURRING |
| dumbed down | 51 | 51 | 40 | 8 | 3 | **83%** | **KEEP** | RECURRING |
| killed my | 36 | 36 | 14 | 21 | 1 | 40% | CUT | — |
| they killed | 42 | 42 | 28 | 14 | 0 | 67% | REVIEW | EVENT-CLUST |
| lost my | 283 | 100 | 37 | 58 | 5 | 39% | CUT | — |
| took away | 109 | 100 | 55 | 35 | 10 | 61% | REVIEW | RECURRING |

---

## Theme Viability Assessment

### 1. How many keywords survived (KEEP + REVIEW)?

- **KEEP (>=80%):** 3 — lobotomized (86%), lobotomy (93%), dumbed down (83%)
- **REVIEW (60-79%):** 6 — nerfed (76%), they killed (67%), ruined everything (63%), took away (61%), miss the old (60%), personality changed (60%)
- **CUT (<60%):** 4 — not the same (53%), bring back (41%), killed my (40%), lost my (39%)
- **LOW VOLUME:** 3 — personality is gone (6 hits), memory wiped (9 hits), memory reset (7 hits)

**Total surviving: 9 keywords** (3 KEEP + 6 REVIEW)

### 2. Total unique post volume across KEEP/REVIEW keywords?

Raw hits across KEEP keywords: 409 (232 + 126 + 51). Accounting for overlap between "lobotomized" and "lobotomy" (many posts contain both), estimated unique KEEP volume: **~330-360 posts**.

Adding REVIEW keywords brings raw hits to ~729. With cross-keyword overlap, estimated unique posts across all KEEP+REVIEW: **~550-650 unique posts**. Solid volume for a theme.

### 3. Is the theme EVENT-CLUSTERED or RECURRING?

**RECURRING across multiple distinct events.** This is the key finding and directly addresses Walker's concern about spikiness.

The temporal data reveals two dominant event clusters with sustained activity between them:

1. **Feb-Apr 2023: Replika ERP Removal ("The Great Lobotomy")** — Massive spike across lobotomized (71 hits), lobotomy (37), nerfed (20), took away (26). Primarily r/replika with spillover to r/SoulmateAI, r/ChaiApp.

2. **Oct 2025 - Mar 2026: ChatGPT 4o Deprecation + Model Regression** — Sustained massive spike: lobotomized (75 hits), nerfed (48), lobotomy (43), they killed (28), took away (32). Primarily r/ChatGPTcomplaints and r/MyBoyfriendIsAI.

3. **Ongoing 2023-2026: CharacterAI Filter Tightening** — Lower intensity but sustained. Primarily dumbed down, nerfed, miss the old.

4. **Intermittent: Platform-Specific Events** — SpicyChatAI filter changes (2024-2025), NomiAI V4 changes (2025), Kindroid tier changes (2025), Claude model sunsets (2026).

The theme is NOT a one-time phenomenon. It is a **recurring pattern driven by different platforms at different times**. The "lobotomy" vocabulary migrated from Replika (2023) to ChatGPT (2025-2026), demonstrating cross-platform cultural transmission of grief/rupture discourse. This makes it ideal for ongoing trend tracking.

### 4. Does this overlap with existing themes?

**Moderate overlap, but the core signal is distinct.**

- **Dependency/withdrawal theme:** ~15% of REVIEW keyword false positives come from addiction-framing. Grief/rupture says "they ruined my companion" while dependency says "the companion ruined my life." Complementary framing.
- **Romance theme:** Many grief/rupture posts reference romantic relationships, but grief captures the DISRUPTION of relationships, not the relationships themselves.
- **Memory/continuity theme:** The LOW VOLUME keywords "memory wiped" and "memory reset" overlap directly. These are already partially captured by the existing memory theme.
- **Therapy theme:** ~10% of grief/rupture posts describe losing an AI therapist/support system.
- **Sexual/ERP theme:** Replika ERP removal posts overlap, but grief/rupture captures the removal EVENT, not the sexual content.

**The unique contribution:** Grief/rupture captures the political/structural dimension — platform decisions destroying user relationships. No existing theme tracks this. The "lobotomy/lobotomized" vocabulary is entirely unique to this theme and has no overlap with any existing keyword category.

### 5. Recommendation

**ADD AS NEW THEME: "Grief / Rupture"**

**Core keywords (KEEP — recommended for immediate inclusion):**
- `lobotomized` (86%, 232 hits, RECURRING)
- `lobotomy` (93%, 126 hits, RECURRING)
- `dumbed down` (83%, 51 hits, RECURRING)

**Strong REVIEW candidates (recommended for inclusion):**
- `nerfed` (76%, 96 hits) — strong volume, blurs product/companion line but mostly companion in T1-T3
- `took away` (61%, 109 hits) — captures loss-framing across both major events
- `they killed` (67%, 42 hits) — event-clustered but very on-theme when it hits

**Weaker REVIEW candidates (Walker decides):**
- `miss the old` (60%, 44 hits) — high UI-nostalgia false positive rate in CharacterAI
- `ruined everything` (63%, 17 hits) — borderline precision and low volume
- `personality changed` (60%, 12 hits) — very on-theme but very low volume

**The theme is viable because:**
1. The "lobotomy/lobotomized" pair alone provides 86-93% precision with ~350 combined hits — an exceptionally strong and unique signal
2. The temporal pattern is RECURRING across multiple platforms and events (Replika 2023, C.AI 2023-2024, ChatGPT 2025-2026)
3. The theme captures a discourse dimension not covered by any existing theme: platform decisions destroying companion relationships
4. The vocabulary is highly community-specific and essentially impossible to confuse with non-companion usage in T1-T3 subreddits
5. This is arguably the most politically consequential discourse in AI companionship — it drives lawsuits, protests, press coverage, and regulatory conversation
