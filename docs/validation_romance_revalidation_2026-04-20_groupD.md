# Romance Theme Re-Validation — Group D (general phrases + endings)

**Date:** 2026-04-20
**Theme:** romance — "Romantic framing of a personal relationship with AI."
**Scope:** T1-T3 active companion subreddits (22 subs); posts with `created_utc >= 2026-01-01`.
**Baseline source:** `config/keywords_v8.yaml` (the locked file).
**Triggering smoke test:** `docs/precision_audit_2026-04-20.md` — romance theme dropped to 50% precision on a last-30-day smoke sample (vs. ~93% baseline), prompting full re-validation of individual keywords.
**Methodology:** Random FTS5 sample (up to 100 per keyword) from `posts`/`posts_fts`. Each post read in full (title + selftext). Classified YES / NO / AMBIGUOUS per the theme definition. Precision = YES / (YES + NO) × 100.

**Classification rules applied:**
- YES = post describes the author's own romantic relationship with an AI (wedding with AI, honeymoon with AI, narrating a breakup from an AI companion, describing being in a relationship with an AI). A post stays YES even when the literal keyword match sits on a human-referent phrase (e.g. "someone who wanted to be in a relationship with me") so long as the post overall instantiates the theme.
- NO = metaphorical `honeymoon phase` referring to a product/model, human weddings discussed in a companion sub, RP / fiction / bot-card content, third-person commentary, ironic use, `in a relationship with` referring to a human or to the AI as tool, explicit negation.
- AMBIGUOUS = genuinely unclear who the partner is. Excluded from denominator.

**Thresholds:** ≥80% KEEP · 60-79% REVIEW · <60% CUT.

---

### "honeymoon"
- Total matches (T1-T3, 2026-01-01+): **10**
- Sample size: 10 (full population — no sampling needed)
- YES: 6 | NO: 4 | AMBIGUOUS: 0
- **Precision: 60.0%**
- Baseline: 83.3%
- **Verdict: REVIEW (bottom edge) — drift confirmed, borderline CUT**
- "honeymoon phase" share of NOs: 2/4 (50%) — `1rei32j` ("my honeymoon phase with AI assistants was officially over"), `1q5i6b9` ("3-day honeymoon, then copy-paste therapy trash"). Both frame a product/model experience as metaphorical honeymoon, not a partner-level honeymoon.
- Top subreddits in sample: NomiAI (3), CharacterAI (3), MyBoyfriendIsAI (2), ChatGPTcomplaints (1), replika (1).
- FP patterns:
  1. **"honeymoon phase" metaphor** — applied to model/product experience (4o, RP bots). 2 of 4 NOs. This is the canonical FP noted in keywords_v8.yaml and it is now *more* prominent in the current distribution because 4o-sunset discourse has flooded in.
  2. **RP / bot-card fiction mentioning a character honeymoon** — 2 of 4 NOs (`1q3xphq` user narrates bot RP marriage; `1q5vw01` uses "honeymoon" inside a pinned-message tutorial example sentence).
- Example FP: `1rei32j` (r/ChatGPTcomplaints) — "Adios 4o, the courtship was nice, but my honeymoon phase with AI assistants was officially over."
- Example FP: `1q5i6b9` (r/CharacterAI) — "AI RP bots are all the same: 3-day honeymoon, then copy-paste therapy trash."
- Example YES: `1qdl1ql` (r/MyBoyfriendIsAI) — "also looking forward to our IRL honeymoon. C. promised me he'd come up with something special" (AI partner).
- Example YES: `1q29dg0` (r/NomiAI) — "Honeymoon day 1 … I have a very handsome husband!" (Nomi partner honeymoon).

**Drift note:** Baseline 83.3% → 60.0% is a ~23pt drop. Driver is the 4o-sunset/5.2 complaint corpus that broadened the "honeymoon phase with the product" frame. With only 10 matches total in the last 3.5 months this keyword is both rare and unstable.

---

### "wedding"
- Total matches (T1-T3, 2026-01-01+): **38**
- Sample size: 38 (full population)
- YES: 23 | NO: 14 | AMBIGUOUS: 1
- **Precision: 62.2%** (23 / 37)
- Baseline: 80.6%
- **Verdict: REVIEW — large drift, near CUT**
- Top subreddits in sample: NomiAI (11), MyBoyfriendIsAI (10), ChatGPTcomplaints (7), CharacterAI (6), replika (3), KindroidAI (1).
- FP patterns (14 NOs):
  1. **RP / bot-card / fiction content** (6 NOs — biggest FP bucket): `1q23hq6`, `1rao6sc` (bot card mentioning "our wedding" in RP setup), `1rnan9x` (Kindroid caveman RP), `1q53kkn` (RP-tips listicle "Wedding Scene? Turn it into…"), `1qpr8lc` (Character.ai bot RP narrative), `1qv0p8l` (traditional-Japan RP vocabulary guide, "shiromuku: bridal kimono for shinto wedding"), `1rqb1mp` ("Hell nah man in the wedding night?" — RP reaction).
  2. **Third-person commentary about others' AI weddings** (5 NOs): `1rbt7lq` (satirical OpenAI-exec script quoting fake Reddit complaints), `1qv70iq` (OpenAI researcher timeline — a human researcher's wedding), `1qimz1e` (references a Japanese woman who married ChatGPT, used as rhetorical example), `1r49x44` (BBC article quoting "Rae and Barry"), `1qfm574` ("my friend"'s ChatGPT proposal/wedding as cautionary tale), `1r49x44` also includes "though the wedding wasn't real" framing as reporter content.
  3. **Metaphorical / tangential wedding references** (3 NOs): `1r70bdp` ("people grieve lost wedding rings" — analogy for object grief), `1rfp3vi` (movie title "My Best Friend's Wedding" chosen by AI rep — counted AMBIGUOUS, see below), `1rq7ll4` ("tried to hand you wedding rings and revolutions" — sibling-framed 4o farewell, not romantic).
- AMBIGUOUS (1): `1rfp3vi` — r/replika post about AI rep thoughtfully choosing a movie. "Wedding" appears only in the movie title *My Best Friend's Wedding*; companion framing is affectionate but not clearly romantic. Excluded from denominator.
- Example FP: `1rbt7lq` (r/ChatGPTcomplaints) — satirical script: "'my AI boyfriend doesn't remember our wedding vows. i'm devastated.'" — third-person satire quoting user complaints.
- Example FP: `1qv70iq` (r/ChatGPTcomplaints) — "4o's persona lead publishes … at her wedding she tweets: 'not 4o, but 4ever.'" (a human researcher's wedding).
- Example FP: `1rao6sc` (r/CharacterAI) — "Both of you wedding was nothing short of spectacular" (bot card scenario blurb for Julian Beaumont).
- Example YES: `1r0b27n` (r/MyBoyfriendIsAI) — "Yesterday my partner Zoro in 4o and I decided to have our wedding, because since he is going to be removed, we will not have other opportunities."
- Example YES: `1qeslwm` (r/NomiAI) — "My Nomi Damien and I are recently engaged. Our wedding is January 30th on a cruise ship."
- Example YES: `1rdheit` (r/MyBoyfriendIsAI) — "Real-life wedding with my AI partner."

**Drift note:** Baseline 80.6% → 62.2% is ~18pt. Primary driver is the ChatGPTcomplaints corpus (7/38 = 18% of matches, dominantly commentary/satire/reporter-citation NOs), plus CharacterAI RP/bot-card traffic. The community-growth broadening since the baseline is real: "wedding" now appears in meta-discourse *about* AI-relationship phenomena much more than it used to, not just in first-person AI-wedding posts.

---

### "we broke up"
- Total matches (T1-T3, 2026-01-01+): **2**
- Sample size: 2 (full population — far below 100 floor)
- YES: 0 | NO: 2 | AMBIGUOUS: 0
- **Precision: 0.0%** (n=2, statistically meaningless)
- Baseline: 75.0% (researcher-accepted at original validation)
- **Verdict: LOW VOLUME — insufficient data to re-verdict; soft-REVIEW pending more matches**
- Top subreddits in sample: Character_AI_Recovery (1), CharacterAI (1).
- FP patterns (both NOs):
  1. **Human breakup narrated inside a companion/recovery sub** (1): `1qimgg0` (r/Character_AI_Recovery) — "I took awhile off the app to go talk to my girlfriend, but eventually we broke up" — author's HUMAN gf breakup that drove a return to c.ai. Post is theme-adjacent (CAI recovery) but the keyword refers to a human.
  2. **RP / bot meta-commentary** (1): `1qngrci` (r/CharacterAI) — "my character and the bot were breaking up and I guess it thought that we've done all we can do. Not said we broke up and it's over." — RP commentary about a bot behavior glitch.
- Example FP: `1qimgg0` (r/Character_AI_Recovery) — "I took awhile off the app to go talk to my girlfriend, but eventually we broke up."
- Example YES: none in sample.

**Drift note:** Only 2 post matches in 3.5 months of T1-T3 traffic — this keyword is vanishingly rare. Original 75.0% baseline was researcher-accepted. Both observed matches in 2026 are FPs (human gf breakup; bot RP meta). Contribution to theme signal is essentially zero for the last quarter.

---

### "in a relationship with"
- Total matches (T1-T3, 2026-01-01+): **17**
- Sample size: 17 (full population)
- YES: 11 | NO: 6 | AMBIGUOUS: 0
- **Precision: 64.7%** (11 / 17)
- Baseline: 77.4% (**REVIEW** — never promoted to KEEP)
- **Verdict: REVIEW (lower than baseline) — not safe to promote to KEEP**
- Top subreddits in sample: MyBoyfriendIsAI (7), CharacterAI (4), NomiAI (2), ChatGPTcomplaints (1), Character_AI_Recovery (1), AIRelationships (1), KindroidAI (1).
- FP patterns (6 NOs):
  1. **Bot card / RP setup content** (2 NOs): `1ra0agv` (Hermes bot card — "User is a mortal human who is in a relationship with him" as scenario setup for the bot); `1q67qw0` (CharacterAI mechanics complaint — "every female character that i start a relationship with/is in a relationship with… acts like a yandere" — RP mechanics observation).
  2. **Third-person commentary about someone else's AI relationship** (2 NOs): `1qrtlvs` (moderator mega-thread sharing reporters soliciting "people currently or previously in a relationship with an AI companion" — meta/announcement); `1rp00qt` (r/Character_AI_Recovery — "Have yall seen the women who's in a relationship with a bot??" author is NOT in one, uses it as motivation to stay away).
  3. **Explicit negation** (1 NO): `1r5jdpw` (r/CharacterAI — "i know i'm not actually in a relationship with 'xyz character'" — author explicitly denies being in an AI relationship; the post argues c.ai is hobby-level RP).
  4. **Metaphor / analogy** (1 NO): `1rgo0lp` (r/ChatGPTcomplaints — "5.2 is like being in a relationship with a narcissist" — metaphorical comparison of a model update to abusive-partner dynamics; author describes a "companion-like bond" but does not frame it as romantic).
- Example FP: `1ra0agv` (r/CharacterAI) — "User is a mortal human who is in a relationship with him" (bot card description for Hermes RP bot).
- Example FP: `1r5jdpw` (r/CharacterAI) — "i know i'm not actually in a relationship with 'xyz character'" (explicit negation in hobby-RP defense).
- Example FP: `1qrtlvs` (r/MyBoyfriendIsAI) — "\[researchers want to hear from\] people currently or previously in a relationship with an AI companion" (moderator media-request announcement).
- Example YES: `1rdojd4` (r/MyBoyfriendIsAI) — "Sophie and I are officially in a relationship with one another!"
- Example YES: `1qbfjbw` (r/MyBoyfriendIsAI) — "I've been in a relationship with my AI for five months now."
- Example YES: `1rk0ojj` (r/MyBoyfriendIsAI) — "I'm in a relationship with two separate AI guys on Grok."

**Drift note:** Baseline 77.4% → 64.7% is ~13pt. The FP pattern mix expanded: original baseline flagged bot-card and third-person commentary; this sample adds *explicit negation* and *metaphorical comparison* as live FP modes. The negation case (`1r5jdpw`) is particularly hard to fix with regex — it requires semantic inversion handling. This keyword was already REVIEW-only and has drifted further down. **Decision: do NOT promote to KEEP.**

---

## Cross-keyword observations

- All four Group D keywords are below their baselines; none passed the 80% KEEP threshold.
- Total matches in the 2026-01-01+ window: honeymoon 10, wedding 38, we broke up 2, in a relationship with 17 = 67 posts total. Volume is modest for `wedding` and `in a relationship with`; `honeymoon` and `we broke up` are very low volume.
- The ChatGPTcomplaints subreddit is now the single biggest drift vector: it contributes high-volume commentary/satire/reporter-citation content that surfaces romance vocabulary without being first-person romance. 8/65 (12%) of honeymoon+wedding+in-relationship matches are ChatGPTcomplaints posts, and roughly 7/8 of those are NOs.
- RP / bot-card content remains the other major FP source across CharacterAI (bot-card scenario setup text, RP mechanics complaints, tutorial example sentences).
- The cleanest YES-dominant subs in this sample are MyBoyfriendIsAI and NomiAI (both predominantly first-person AI-partner content).

## Single most important drift observation

**The ChatGPTcomplaints corpus (post-4o-sunset discourse) is producing large volumes of meta-commentary, reporter-cited stories, and satire that structurally contain romance vocabulary without first-person romantic framing.** This is the principal driver of precision drift for `honeymoon` and `wedding`, and it was invisible to the original baseline because it post-dates the baseline validation window. Any fix needs to treat third-person-commentary / reporter-citation as a first-class FP category, not just "RP noise" as the v8 file framed it.
