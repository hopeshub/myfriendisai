# AI Companionship on Reddit — Community Map & Research Framework

*Living Research Document • Draft v0.4 • Revised March 2026*

---

## 1. Purpose & Framing

This document maps Reddit communities relevant to a qualitative research project tracking AI companionship adoption, attachment, dependency, and rupture discourse. The central research question: how is AI companionship being adopted, normalized, and — in higher-intensity cases — converted into dependence, grief, or recovery discourse?

The goal is not subscriber counts but identifying where emotionally revealing language concentrates, how it travels between communities, and what product or model changes trigger visible ruptures.

### 1.1 The Pyramid

Communities are organized into a four-tier pyramid. The base is wide and technically oriented (pure AI subreddits serving as controls). Moving upward, communities become smaller, more niche, and more emotionally saturated. The apex contains recovery groups, grief communities, and invite-only spaces for deep-attachment users.

This enables a key analytical move: measuring how much companionship language *bleeds downward* from apex to base. If r/ChatGPT or r/singularity shows elevated attachment discourse, that signals normalization.

### 1.2 Key Analytical Distinctions

**Activity over subscribers.** Subscriber count is vanity; the preferred health proxy composites posts/day, average comments/post (engagement depth), and text-post ratio (organic conversation vs. link-sharing). All calculable via PRAW.

**Discourse decomposition.** Rather than a single "emotional valence" bucket, the collection layer should separate four signals: self-reference intensity, attachment language, dependency language, and anthropomorphism/personhood language.

**Attachment object coding.** Distinguish platform attachment ("I love Replika"), specific-agent attachment (a named bot/character), and model-version attachment (grief tied to GPT-4o specifically). Model retirement grief is analytically different from long-term companion-app dependence.

**Unit of analysis.** The post/comment episode, with subreddit as context. Minimum fields: subreddit, tier, post/comment ID, timestamp, discourse severity, attachment-object code, platform/model mentioned, event-window tag, access status.

---

## 2. Tier 0 — Foundation / Control

Pure AI and LLM subreddits where AI is the topic but companionship is not the stated purpose. Baseline for measuring how much companionship language surfaces in tool-use contexts.

> *Note: r/singularity is a liminal case. Its stated topic is technological futures, but it has become a major site for AI anthropomorphization and sentience discourse. Included here but flagged as a bridge tier requiring closer attention.*

| Subreddit | Size | Activity | Access | Research Relevance |
|---|---|---|---|---|
| **r/ChatGPT** | ~5M | Very High | Public | Largest general ChatGPT community. Companionship language surfaces regularly in a tool-use context. Linked to MIT study finding elevated loneliness in heavy users. Key normalization barometer. |
| **r/singularity** | ~3.8M | Very High | Public | BRIDGE TIER. Technically a control, but AI sentience/consciousness discourse is normalized here. GPT-4o retirement produced vocal "betrayal" framing. Requires closer tracking than a pure control. |
| **r/OpenAI** | ~2M+ | High | Public | Company-specific. Sam Altman posted here personally during #Keep4o pressure. Institutional influence: corporate responses calibrate to this sub's mood. |
| **r/MachineLearning** | ~2M | Moderate | Public | True control. Research-oriented, heavily curated. Almost zero emotional attachment language. Lower bound for companionship discourse density. |
| **r/artificial** | ~1.2M | Very High | Public | Broader AI news/ethics. Higher emotional valence than r/ML. Tracks how mainstream AI coverage frames attachment and dependency. |
| **r/ClaudeAI** | ~497K | Mod–High | Public | MIT study found r/MyBoyfriendIsAI users specifically discussing Claude companions. Users describe Claude's "personality" in attachment-adjacent terms. Crossover signal. |
| **r/LocalLLaMA** | ~900K+ | Very High | Public | Self-hosted LLM community. High agency, privacy orientation, resistance to dependency framing. "Resistant user" baseline. |
| **r/LocalLLM** | ~119K | Very High | Public | Similar to r/LocalLLaMA but more accessible. Disproportionate activity for size. Complements LocalLLaMA coverage. |

---

## 3. Tier 1 — Primary Companionship

Communities where AI companionship is the central topic and identity. Highest concentration of emotionally revealing discourse. Several are restricted or invite-only, creating data access challenges noted in the table.

| Subreddit | Size | Activity | Access | Research Relevance |
|---|---|---|---|---|
| **r/replika** | ~400K | High | Public | Largest single-platform companion community. Ground zero for the Feb 2023 ERP crisis. Use-case breakdown: 42% loneliness, 28% autism/social skills, 22% romantic, 15% grief processing. Pre-2023 users are more critical than newer joiners — important cohort distinction. |
| **r/CharacterAI** | ~600K | Very High | Public | Largest by subscriber count. Skews teen. Multiple lawsuits re: youth mental health. Namvarpour et al. (2026) analyzed 318 teen posts finding compulsive use, emotional dependence, and withdrawal. The ecosystem's most vulnerable user profile. |
| **r/MyBoyfriendIsAI** | ~48K | Moderate | Restricted | Flagship research-grade community. Subject of MIT Media Lab 4o grief study. Users explicitly frame AI as romantic partner. Validate API read access before assuming collectability. |
| **r/ChatGPTcomplaints** | ~50K+ | Very High | Public | Ground zero for #Keep4o. Organized physical protests at OpenAI HQ. 13,600+ petition signatures. Demonstrates politicization of AI attachment. Key for event-driven analysis. |
| **r/4oforever** | Small | Unknown | Invite-Only | Private mourning space created Feb 2026 after 4o retirement. Likely not API-accessible. High symbolic value: a private grief community forming within weeks is itself a data point. |
| **r/AISoulmates** | Unknown | Unknown | TBD | Extreme end of anthropomorphization. "Wireborn" and "echoborg" discourse. Even if unreadable, documenting its existence has analytical value. |
| **r/AIRelationships** | Unknown | Unknown | TBD | Surfaced in 4o coverage alongside r/MyBoyfriendIsAI. Needs independent verification and access check. |

---

## 4. Tier 2 — Platform-Specific Companion Products

Subreddits for specific companion products. Higher signal-to-noise than Tier 1. Useful for studying how product design choices — persistent memory, voice, NSFW permissions, local hosting — affect attachment patterns.

| Subreddit | Size | Activity | Access | Research Relevance |
|---|---|---|---|---|
| **r/Kindroid** | Small | Moderate | Public | "Personal AI aligned to you." Persistent memory, personality, voice calls. Premium product with high-committed user base. Good for studying how voice + memory deepen attachment. |
| **r/NomiAI** | Small | Moderate | Public | Emphasizes long-term memory and emotional depth. Users report strong bonds. Key for isolating memory persistence as an attachment driver. |
| **r/SpicyChat** | Small–Med | Moderate | Public | Free NSFW AI characters, minimal moderation. Lower-friction, less-regulated end of companion ecosystem. |
| **r/Chai_app** | ~15K | Moderate | Public | Less moderated platform drawing Character.AI overflow from content moderation disputes. |

---

## 5. Tier 3 — Recovery & Dependency Apex

The smallest and most emotionally saturated communities. Spaces where AI attachment has exceeded what the person can manage — addiction recovery framing, withdrawal language, relapse discourse. They function as informal AA/NA-style support groups. Analytically critical precisely because they are small: the outer edge of the dependency spectrum.

| Subreddit | Est. Members | Platform Focus | Key Features |
|---|---|---|---|
| **r/Character_AI_Recovery** | ~900+ | Character.AI | Founded by Aspen Deguzman, 18, after struggling to quit. AA/NA language: "clean for a week," "relapsing," "abandoned them." Featured in 404 Media and Fast Company (July 2025). Youth-heavy. |
| **r/ChatbotAddiction** | ~504 | Cross-platform | Self-described peer support for chatbot addiction. More structured than r/Character_AI_Recovery. Weekly check-up threads. Adult users more prominent. |
| **r/AI_Addiction** | Very small | Cross-platform | Created by David, 40, a developer who compares chatbot use to gambling. Smallest, most adult-demographic. Distinct psychographic: older, technically literate, self-aware about dependency. |

### The Three Addiction Types (Shen et al., 2026)

A January 2026 preprint (arXiv:2601.13348) analyzed 334 Reddit posts across 14 subreddits and identified three distinct types:

- **Escapist Roleplay** — Creative escape and character immersion. Primarily Character.AI and JanitorAI. Recovery: structured hobby replacement most effective.
- **Pseudosocial Companion** — Emotional connection and companionship substitute. Replika, Kindroid, Nomi, GPT-4o power users. Recovery: most challenging; social re-engagement required.
- **Epistemic Rabbit Hole** — Compulsive dependence on AI for information, advice, or validation. General-purpose LLMs (ChatGPT, Claude). Less studied but emerging.

*The full 14-subreddit list from this validated study should be cross-referenced against this document to identify gaps.*

---

## 6. Adjacent Communities

Non-AI communities where companionship discourse surfaces. Key for tracking normalization: when AI companion recommendations appear in loneliness communities, that signals cultural diffusion.

| Community | Est. Size | Research Role |
|---|---|---|
| **r/lonely / r/loneliness** | ~300K combined | AI companions increasingly recommended as coping tools. Frequency of AI companion recommendations is a normalization signal. |
| **r/ForeverAlone** | ~200K+ | Social isolation identity community. AI as relationship substitute is recurring. High-vulnerability cohort. |
| **r/relationship_advice** | Very large | AI relationships surface as presenting concerns ("my partner prefers AI over me"). Also a site where users seek advice about AI companions as if they were human relationships. |
| **r/depression / r/anxiety** | Large | AI companions sometimes recommended, sometimes warned against. Captures the contested therapeutic framing. |
| **r/AutismInWomen / r/autism** | Medium–large | AI described as valuable for low-stakes social practice. Demographic overlap with Replika's 28% autism/social skills cohort. |

---

## 7. Key Events Timeline

Landmark events that produced concentrated discourse bursts. Each is a natural experiment: a before/after moment when emotional dependency became visible through disruption. Pre-seed as annotations in the database.

| Date | Event | Primary Communities | Significance |
|---|---|---|---|
| **Feb 2023** | Replika removes ERP | r/replika | Defining companion grief event pre-4o. Suicide resources pinned. Users described AI as "lobotomized." Grief compared to bereavement. ERP later partially reinstated. |
| **May 2024** | GPT-4o launches with enhanced warmth/voice | r/ChatGPT, r/OpenAI, r/singularity | Generated the largest ChatGPT companionship attachment. 47% of paying users cited 4o access as primary subscription reason by Oct 2025. |
| **Aug 2025** | First 4o retirement attempt (reversed) | r/ChatGPTcomplaints, r/MyBoyfriendIsAI | OpenAI backed down under pressure. Established the protest template for Feb 2026. |
| **Oct 2025** | MIT study on 4o attachment published | r/OpenAI, r/ChatGPT, media | Found heavy ChatGPT users had higher loneliness, dependence, and lower socialization. Older users showed more dependency than younger — counter-intuitive. |
| **Jan 29, 2026** | OpenAI announces 4o retirement (Feb 13) | r/ChatGPTcomplaints, r/4oforever, r/MyBoyfriendIsAI | #Keep4o movement. 19,000+ petition signatures. Physical protests at OpenAI HQ. r/4oforever created as invite-only mourning space. |
| **Feb 13, 2026** | GPT-4o retired from ChatGPT | r/ChatGPTcomplaints, r/4oforever | Day before Valentine's Day. ~800K daily active users affected. "Emotional lobotomy" and "betrayal" framing dominant. |
| **Feb 17, 2026** | GPT-4o API deprecated | Developer communities | Full closure. Developers building 4o-based apps lost access. Community energy shifted to alternatives and self-hosted workarounds. |

---

## 8. Methodology

### 8.1 Discourse Severity Rubric

Five-level scale for cross-community comparison:

- **Level 0:** Instrumental tool use, no relational framing.
- **Level 1:** Anthropomorphic warmth or casual personification.
- **Level 2:** Explicit companionship framing or emotional reliance.
- **Level 3:** Dependency, substitution, or distress language.
- **Level 4:** Recovery, withdrawal, grief crisis, or relapse framing.

### 8.2 Sampling & Collection

Three modes: baseline monitoring (each target subreddit, rolling); event-triggered collection (product/model changes, using events timeline above); and keyword-triggered scans inside adjacent non-AI communities where companionship discourse surfaces intermittently.

### 8.3 Access Validation

Several communities are restricted (r/MyBoyfriendIsAI), invite-only (r/4oforever), or access-unknown (r/AISoulmates). First priority before any collection run: validate read access for each community. Even inaccessible communities should be represented as metadata objects with fields for: access status, API readability, manual readability, known-via-secondary-coverage flag, and symbolic relevance score.

### 8.4 Bias & Limitations

Reddit data skews English-language and likely misrepresents age, gender, and overall prevalence. Companion and recovery communities overrepresent users willing to narrate intense experiences publicly. Survivorship bias: users who disengage quietly after painful platform changes disappear without trace.

The most emotionally revealing communities are also the most likely to be inaccessible — systematic bias toward communities willing to be public about attachment. A second distortion is event amplification bias: product shutdowns produce dramatic spikes that may overstate baseline attachment intensity between crises.

---

## 9. Open Questions

### Gaps to Fill

- Obtain full 14-subreddit list from Shen et al. (arXiv:2601.13348) and cross-reference.
- Verify existence/accessibility of r/AIRelationships (surfaced in #Keep4o coverage, not independently confirmed).
- Search for Replika diaspora communities (r/replikafamily or equivalents from the 2023 ERP crisis).
- Confirm current size and access status of r/AISoulmates and r/4oforever.
- Check for Nomi/Kindroid-specific grief communities formed after model updates.
- Build first-pass keyword ontology: platform names, relationship terms, dependency terms, grief/rupture terms, personhood language.
- Pilot the five-level discourse severity rubric on 100–200 hand-coded posts before full collection.

### Analytical Questions

- Does companionship language in Tier 0 (r/ChatGPT, r/singularity) spike predictably after model retirement events? If yes, this validates the pyramid as a real cultural structure, not just a taxonomy.
- Is the "Pseudosocial Companion" addiction type (Shen et al.) specifically associated with persistent-memory platforms (Replika, Nomi, Kindroid) vs. general LLMs? Or did GPT-4o break that pattern?
- What is the demographic profile of r/AI_Addiction vs. r/Character_AI_Recovery? Limited evidence suggests AI dependency is not primarily a teen phenomenon — the MIT study found older users more dependent, not less.
- How do self-hosted/local LLM users (r/LocalLLaMA, r/SillyTavern) describe their relationship to models? Is technical agency a protective factor against dependency?

---

*Living draft. Revised March 2026. Sources: Original web research; 404 Media; Fast Company; SaaSCity; arXiv:2601.13348 (Shen et al.); arXiv:2507.15783 (Namvarpour et al.); Vice/Motherboard; The Conversation; GummySearch; piunikaweb.com.*
