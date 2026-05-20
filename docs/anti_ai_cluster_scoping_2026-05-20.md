# Anti-AI cluster scoping — 2026-05-20 (LOCKED)

Why a new T4 "Ambient / Discourse Climate" tier exists, the criterion that gates entry, what's in it, and what would be a category error to do with it.

> **Status: LOCKED.** This criterion was derived through three iterations on 2026-05-20 — loose register → charter test → two-stage gate — plus an external-research check (Pew/Stanford HAI/Ipsos/Merchant *Blood in the Machine*/Fortune/etc.), a project-consistency check, and a synthesis pass that weighed three competing definitions. The synthesizer's standing recommendation: **do not reopen for 6 months without affirmative new evidence.** Any re-proposal must address the rejection rationales for the named subs below.

## The question

Should the tracker add the anti-AI Reddit cluster — r/antiAI and friends — to its tracked set? And if so, in what shape?

## The locked selection criterion (the two-stage gate)

> **A subreddit belongs in T4 if BOTH stages pass:**
>
> **(1) Charter test** — the sub's charter is to advocate FOR or AGAINST AI as a cultural project. A stranger reading the `public_description` and the top 50 post titles can identify the sub's side. Technical-research communities (alignment, ML engineering) fail at stage 1 even if their members are AI-skeptical in effect.
>
> **(2) Expression-not-infrastructure test** — the sub functions as a space for cultural EXPRESSION (individuals venting, grieving, arguing, advocating) rather than as movement-coordination INFRASTRUCTURE (officer roles, treaty / ballot / event organizing, recruitment for an advocacy org, named-figure intellectual lineage operating as community identity). Organized advocacy organizations fail at stage 2.
>
> The test is applied to the **community itself**, not its individual members. Individual-level distinctions dissolve (PauseAI volunteers and r/antiAI posters overlap demographically); the sub-level distinction holds because we filter at the infrastructure level.

### Why two stages (not one)

The first scoping pass used a loose "anti-AI register" criterion and admitted r/ControlProblem (alignment research, not advocacy) and r/AcceleratingAI (an arxiv paper feed). A same-day sharpening tightened to the charter test, which fixed those — but the charter test alone still admitted r/PauseAI (legitimate advocacy charter, but the sub *is* the volunteer-coordination space for an international-treaty org — infrastructure, not expression) and r/eacc / r/accelerate (the e/acc movement with named-figure intellectual lineage, not expression).

Adding stage 2 catches both kinds of mistake **symmetrically** — it disqualifies movement subs on both sides. The founder's instinct was originally phrased as "not the Yudkowsky / Berkeley Lighthaven crowd," which is the demographic gloss; the principled version is "not movement-coordination infrastructure on either side." Applied symmetrically by design.

### What T4 is not

T4 is **not** a measurement of mainstream AI cultural sentiment. The site does not claim to sample what ordinary people think about AI. T4 shows that this cluster of cultural-expression communities exists, how each is sized, and how each is moving. Read engagement, not a population estimate. This is the same May-16-retrenchment discipline applied to the secondary view.

### External evidence the criterion was checked against

The two-stage gate was pressure-tested against the AI-sentiment research literature (full sources in the synthesis-agent transcript). Key findings:
- The distinction between mainstream AI skepticism (Brian Merchant's *Blood in the Machine*; Fortune's "AI culture war" framing; the "AI slop" vocabulary) and the AI-safety / x-risk / PauseAI complex (LessWrong/MIRI/EA Forum) is real and increasingly named.
- e/acc is consistently characterized as an ideological movement with named figures (Andreessen, Beff Jezos), intellectual lineage (Nick Land/CCRU), and identity-marker behavior — not a vibe.
- No survey-research org (Pew, Stanford HAI, Ipsos, YouGov) uses our 3-bucket Anti/Pro/Debate schema; their work segments by demographics or domain. Our taxonomy is journalistic, not survey-validated — but it doesn't contradict survey work, it operates one level up (community infrastructure, not individual sentiment).
- PauseAI is the literature's "leakiest case": EA-adjacent infrastructure but everyday-citizen recruits. For a sub-level filter, the criterion holds; for an individual-level claim, it would dissolve. T4 is sub-level only.

## The three passes

## The scoping pass

A 17-agent parallel scoping pass on 2026-05-20 (15 per-sub analysts + 1 discovery agent + 1 selection-bar synthesis agent). 22 candidate subs were probed via the project's RedditClient: about-text + 50 recent posts each, dumped to `/tmp/anti_ai_scoping/`. Each per-sub agent bucketed the 50-post sample by primary discourse mode and computed companionship-discourse density (% of posts where AI companionship is the primary topic — first-person attachment OR third-person mockery / critique of AI-companion users).

| Sub | Subs | Companionship density | Cadence | Verdict |
|---|---:|---:|---:|---|
| r/antiAI | 185K | 6% | ~98/d | climate context (T4) |
| r/aiwars | 144K | 2% | ~59/d | climate context (T4) |
| r/ArtistHate | 33K | 2% | ~2.6/d | climate context (T4) |
| r/BetterOffline | 40K | 4% | ~15/d | climate context (T4) |
| r/AIDangers | 39K | 6% | ~13/d | climate context (T4) |
| r/ControlProblem | 51K | 2% | ~8/d | climate context (T4) |
| r/PauseAI | 5.4K | 0% | mod | climate context (T4) |
| r/DefendingAIArt | 63K | 0% | ~51/d | climate context (T4, pro side) |
| r/accelerate | 60K | n/a | mod | climate context (T4, pro side) |
| r/AcceleratingAI | 2.5K | n/a | mod | climate context (T4, pro side) |
| r/AntiAIArt | 1.3K | 0% | ~1.5/d | reject — duplicates ArtistHate |
| r/ArtistLounge | 381K | 0% | ~19/d | reject — working-artist craft sub |
| r/AISafety | 898 | 6% | ~2/d | reject — alignment-research forum |
| r/SneerClub | 21K | 2% | 0.4/d | reject — defunct, Zizian/Yud drama |
| r/aboringdystopia | 763K | 0% | ~13/d | reject — broad dystopia |
| r/Buttcoin | 213K | 0% | ~3.5/d | reject — crypto-skeptic, rule against AI |
| r/LinkedInLunatics | 1M | 0% | ~32/d | reject — LinkedIn mockery |
| r/AIethics | 6K | ~0% | low | reject — academic podcast feed |
| r/EthicalAI | 854 | 20% | 0.12/d | reject from T4 (companionship critique, not culture-war; queued for a separate decision) |
| r/StopAI | 104 | 0% | low | reject — too small/inactive |
| r/QuitAI | — | — | — | does not exist / banned |
| r/AICompanionRecovery | — | — | — | does not exist |

## The locked decision

**Admit nine subs as Tier 4 — Ambient / Discourse Climate.** Six anti-AI cultural expression, two pro-AI cultural expression, one debate arena. Tracked as context only: they appear on `/communities` under three "Ambient" category chips with the same engagement-metrics treatment as every other tracked sub. They are excluded from the theme atlas, `keyword_trends.json`, `composition_trends.json`, the per-1k denominator, and every keyword export.

**Backfill policy (revised 2026-05-20 after homepage-framing pass):** T4 is forward-only for any **keyword-derivable** metric. Engagement metrics — particularly **monthly post volume** — *may* be backfilled via Arctic Shift for cultural-context display. The forward-only rule was conservative, not load-bearing; what's load-bearing is the keyword-pipeline gate (`exclude_from_keywords: true` + `tier in (1,2,3)` in `load_keyword_communities`). Post-volume backfill doesn't touch keyword precision and lets the §5 homepage panel actually carry a story instead of being empty for months.

**Final T4 roster:**

| Side | Sub | Subs | Stage 1 (charter) | Stage 2 (expression-not-infrastructure) |
|---|---|---:|---|---|
| Anti-AI | r/antiAI | 185K | "People who believe AI will negatively affect the human race." | Venting/grievance hub, no advocacy org behind it |
| Anti-AI | r/FuckAI | 19K | "Exposing all the bad about AI, harmful to workers/artists/writers" | Expression-mode community grievance |
| Anti-AI | r/ArtistHate | 33K | Pro-artist anti-AI advocacy ("expose increasing hate against artists") | Artist-community grievance space, not org-coordination |
| Anti-AI | r/AIDangers | 39K | Charter mocks techno-optimists; "AI risk awareness" framing | Cultural protest content (booing CEOs, butlerian-jihad memes) — not LessWrong infrastructure |
| Anti-AI | r/BetterOffline | 40K | Podcast-fan sub for Ed Zitron's anti-AI-hype podcast | Mainstream tech-journalism audience, no movement infrastructure |
| Anti-AI | r/trueantiAI | 653 | Sister of r/antiAI with stricter no-AI-content rule | Expression-mode, like r/antiAI |
| Debate Arena | r/aiwars | 144K | "Following news and developments on ALL sides of the AI art debate" | Open debate floor — explicitly not a side, not an org |
| Pro-AI | r/DefendingAIArt | 63K | "Fighting misinformation and attempts at legislation against AI artwork" | Artist-community advocacy expression (defending art, mocking "antis") — not campaign infrastructure |
| Pro-AI | r/ProAI | 662 | "For people who are Pro-AI. We exclude anyone who isn't pro-AI" | Small, charter-simple expression sub |

## Rejected entries (with locked rationale)

**Failed stage 1 — technical/non-advocacy:**

- **r/ControlProblem** (51K) — AI alignment research. The charter names a research problem and quotes Yudkowsky/Scott Alexander; top posts are fellowship applications, alignment-methodology papers, ASTRA/ERA fellowships. Member sentiment is anti-AI in effect but charter is technical. *Including this would conflate "thinks AI is dangerous" (a research position) with "opposes AI as a cultural project" (advocacy) — exactly the conflation the criterion is designed to prevent.*
- **r/AcceleratingAI** (2.5K) — charter passes the test ("celebrating the positive and transformative aspects of AI… No doom prophecies") but practice fails it. Dominant discourse is a single-author arxiv-paper firehose with near-zero comment engagement. *Charter ≠ lived activity; both must hold.*

**Failed stage 2 — movement-coordination infrastructure:**

- **r/PauseAI** (5.4K) — charter is to coordinate volunteers for an international AI-pause treaty. The literature ("AI Safety Community Exists, But Its Impact Is Uncertain", TechPolicy.Press; PauseAI's own growth-strategy doc) confirms PauseAI is an EA-adjacent advocacy organization with officers, recruitment funnels, ballot-measure campaigns, and treaty work. *That is movement infrastructure, not cultural expression. Excluded for the same reason any future ballot-campaign or lobbying sub would be excluded on either side.*
- **r/eacc** (2.1K) — the reddit home of e/acc (effective accelerationism). The movement has named figures (Andreessen, Beff Jezos), intellectual lineage (Nick Land/CCRU), and identity-marker behavior (profile tags, jargon). *Named-figure intellectual lineage operating as community identity is the textbook stage-2 failure mode on the pro side.*
- **r/accelerate** (60K) — "AI-Positive Techno-Accelerationist High-Fidelity Epistemic Enclave." The "epistemic enclave" language is e/acc identity-marker behavior; positioning itself as the partisan alternative to r/singularity / r/futurology / r/artificial / r/technology is movement coordination, not individual cultural expression. *Keeping it would owe a written reason that doesn't also re-admit r/eacc; no such reason exists.*

## Pro-AI asymmetry is honest, not artifact

Reddit has more anti-AI advocacy *expression* than pro-AI. Pro-AI energy on Reddit mostly lives in T0 product subs (r/ChatGPT, r/ClaudeAI, r/singularity) — pro-AI by member self-selection but charter is product/tool, not advocacy. Folding those into T4 would recreate the r/AcceleratingAI mistake (charter ≠ practice) and inflate the pro side dishonestly. Document the asymmetry on the About page; don't paper over it.

The exclusion is double-gated:
1. Every T4 entry carries `exclude_from_keywords: true`.
2. `load_keyword_communities()` was tightened from `tier >= 1` to `tier in (1, 2, 3)` — defense in depth, so an accidentally-unflagged T4 sub still can't slip in.

Frontend boundary: `loadCommunityComposition()` in `web/app/themeData.ts` now joins against `subreddits.json` tier and explicitly excludes T4 subs from the homepage "Other" companion-volume band. Without this, ambient sub volume would silently pollute the §1 composition chart.

## Why no anti-AI sub enters the theme atlas

Even r/antiAI at 6% companionship density would be a category error to keyword-tag. The 6 themes (romance, sex/ERP, consciousness, therapy, addiction, rupture) were validated on **first-person companion talk**. Applied to third-person outside-looking-in critique they fire on different referents:

- "addiction" picks up concern-trolling about other people's chatbot use, not first-person dependency.
- "consciousness" picks up AI-doom philosophy posts about sentience-as-x-risk, not user attribution of inner experience.
- "rupture" doesn't fire at all — no relationship to lose.

A counter-discourse panel measuring outside-looking-in critique is a legitimate research question, but it needs its own validated keyword set, its own 100-post-per-keyword qualitative coding pass, and its own panel — not a merge into the existing theme atlas. T4 leaves that door open without committing to it.

## Why T3 was the wrong tier for these subs

T3 is *inside-looking-out*: ex-users of AI companions doing peer support / AA-NA framing. The anti-AI subs are *outside-looking-in*: people who never used AI companions, often hostile to those who do. Different epistemic position, different vocabulary, different valence. Forcing them into T3 would have mixed two distinct discourse modes under one tier label.

## What this is not

- **Not a measurement of "the AI culture war."** The site does not claim to measure pro-vs-anti AI sentiment. The T4 view shows that the cluster exists and how active each community is. Read the engagement, not a balance score.
- **Not a backfill.** Forward-only, like the May 18 coverage refresh. T4 sparklines start from collection onward.
- **Not a homepage panel.** T4 lives on `/communities` as a category chip, behind a click. The locked homepage frame (the four-section companionship narrative) is unchanged.

## r/EthicalAI — a separate decision, not bundled

r/EthicalAI was the only sub in the entire scoping pass with non-trivial companionship-discourse density (20%, ~45 posts/year). The discourse is a real mix of outside-looking-in companion-platform critique (Nomi self-harm, Glimpse manipulation, "The Illusion of AI Companionship") and first-person relational framing. It's structurally interesting but does not belong in T4 — it's not culture-war discourse. If ever tracked it would be either T3-adjacent or its own tier, and would need the same exclude-from-keywords treatment for the same category-error reason. Deferred.

## Related artifacts

- `config/communities.yaml` — T4 section
- `src/config.py` — tier-4 validation + tightened `load_keyword_communities`
- `web/app/themeData.ts` — T4 exclusion from composition band
- `web/app/communities/CommunitiesTable.tsx` — T4 badge styling
- `web/app/communities/[subreddit]/page.tsx` — T4 tier label
- `CLAUDE.md` §1, §2.1, §2.3 — scope statement updates
