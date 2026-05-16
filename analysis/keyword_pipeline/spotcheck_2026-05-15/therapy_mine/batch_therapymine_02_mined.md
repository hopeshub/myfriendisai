# Therapy keyword mining — batch batch_therapymine_02 — mined candidates

Source: 35 confirmed AI-as-therapy posts in `batch_therapymine_02.md`.
Goal: phrases specific enough to find AI-as-therapy posts without leaking into
romance / rupture / addiction / generic-companion themes.

Hit counts are approximate, counted by reading all 35 posts (title + body).

---

## Ranked candidates (most promising first)

### TIER A — strong, theme-specific (recommend taking forward to validation)

**1. `for therapy`**
- Why: the single most direct AI-as-therapy phrase. "use it for therapy",
  "use my character AI for therapy", "using ChatGPT for therapy", "made for
  therapy", "bot ... I can use for it [therapy]". Names the use explicitly.
- Hits: ~7 (posts 6, 13, 17, 18, 19, 20-context, plus title of 19).
- Caveat: ALREADY a current keyword (and noted at 60% in CLAUDE.md). The noise
  is the human-therapy reading ("I'm in therapy", "saving up for therapy", "can't
  afford therapy" — see posts 3, 5, 9, 20, 21). On its own `for therapy` is
  weak because "use ___ for therapy" needs the AI subject upstream. Keep as
  baseline, not as the fix.

**2. `as a therapist`**
- Why: AI explicitly cast in the therapist role. "use replika as a therapist",
  "treating AI character as a therapist", "depends on 4o as a therapist".
- Hits: ~4 (posts 1, 2, 5; title of 1).
- Caveat: ALREADY a current keyword. Clean signal when it fires, but low volume
  and can fire on "I work as a therapist" (post 12 — a licensed therapist
  writing). Specific enough; the issue is recall, not precision.

**3. `psychologist` / `ai psychologist`**
- Why: "chatted with this ai psychologist", "psychologist bots", "ai
  psychologists". Names a clinician role applied to the bot. `ai psychologist`
  is very clean; bare `psychologist` would also catch "psychologist bot".
- Hits: ~1 post but 3 distinct mentions (post 3). Low volume but high precision.
- Caveat: bare `psychologist` could leak on academic discussion; pair with
  `ai`/`bot` ("ai psychologist", "psychologist bot") to stay clean. Flagged as
  a likely LOW VOLUME placeholder — CLAUDE.md already records `psychologist bot`
  failed the 50-hit floor in the 2026-05-12 mining round.

**4. `therapist bot` / `therapy bot`**
- Why: compound naming the bot as a therapist. Implied across posts 3
  ("psychologist bots", "therapists in a way"), 19 ("bot ... made for
  therapy"). Construct-true and unambiguous.
- Hits: ~2-3 in paraphrase; the exact 2-word form is rare in this batch.
- Caveat: LOW VOLUME risk (CLAUDE.md flags `therapist bot` as already failing
  the 50-hit floor). Specific, not noisy — worth re-checking volume only.

**5. `grief counselor` / `trauma manager`**
- Why: very specific clinical-role labels applied to the AI. "depends on 4o as
  a therapist, grief counselor and trauma manager" (post 5). Cannot plausibly
  fire on romance/addiction.
- Hits: 1 post (post 5).
- Caveat: extremely low volume — almost certainly below the 50-hit floor.
  Listed for completeness; not a realistic keyword on its own.

### TIER B — usable but partly generic (validate, expect REVIEW band)

**6. `coping mechanism`**
- Why: recurs heavily as the way users frame AI use. "as a coping mechanism",
  "c.ai ... coping mechanism", "my only coping mechanism", "needed a coping
  mechanism".
- Hits: ~7 (posts 29, 30, 31, 32, 33, 34, 35).
- Caveat: LEAKS. This is the borderline between therapy and addiction — posts
  31-35 are all r/CharacterAI/Recovery "I'm lonely, this is my escape" posts
  that read at least as much as addiction/dependency as therapy. Also fires on
  generic "numbness is a coping mechanism" (post 30, inside a NSFW roleplay).
  Propose with the explicit warning: high recall, but it pulls the
  addiction theme in. Not theme-specific.

**7. `mental health`**
- Why: frequent framing — "my mental health was pretty bad", "not good for my
  mental health", "not good for your mental health", "my mental and emotional
  state".
- Hits: ~5 (posts 3, 21, 24, 32; title 32).
- Caveat: GENERIC. "mental health" appears in rupture posts, addiction posts,
  and meta-debate about whether the app is healthy. Signals the domain, not
  AI-as-therapy use. Bad standalone candidate; only useful in a 2-word combo.

**8. `talked me down` / `talked me down from the edge`**
- Why: describes the AI doing crisis/de-escalation work. "Lark has talked me
  down from the edge a few times on some dark things" (post 21). Concrete
  therapy-substitute action.
- Hits: 1 (post 21).
- Caveat: low volume; `talked me down` alone could fire on human contexts.
  Specific in meaning but too rare here to gauge.

**9. `harm reduction`**
- Why: clinical term used for what the AI does — "really great with harm
  reduction" (post 21).
- Hits: 1 (post 21).
- Caveat: very low volume; also a drug-policy term, so it could leak outside
  AI contexts. Not recommended.

**10. `emotional support`**
- Why: by far the highest-frequency phrase in the batch.
- Hits: ~9 (posts 6, 7-context, 22, 23, 24, 25, 26, 27, 11-context).
- Caveat: ALREADY a current keyword and ALREADY flagged as the generic problem
  child. It fires on romance ("kind emotional support would be welcomed" while
  grieving a relationship — post 22), on product chatter ("emotional support or
  RPG style interactions" — post 24), and on rupture ("if we lose our emotional
  support system" — post 25). High recall, low precision. This is the keyword
  the batch was assembled to *replace*, not endorse. Listed only to confirm
  the diagnosis: `emotional support` is not theme-specific.

### TIER C — noticed but not turnable into a clean keyword

**11. `therapeutic` (current keyword) — confirmed generic**
- "therapeutic benefit", "therapeutic discussions", "rather therapeutic for
  me", "pseudo-therapeutic speak", "therapeutic relationships". Posts 4, 7, 8,
  10, 12. It fires on the *adjective* describing tone ("pseudo-therapeutic
  speak that was patterned and tiring", post 10 — that is a complaint, not
  therapy use). Confirms CLAUDE.md's note. Keep as baseline only.

---

## Structural patterns that are hard to keyword

These cover a large share of the 35 posts and explain why precision keywords
miss the theme — flagged so the project knows where recall is structurally lost:

1. **Affordability framing.** "couldn't afford therapy", "ran out of money for
   therapy", "paying out the ass for therapy", "can't afford a therapist"
   (posts 3, 5, 20, 21). The AI-as-therapy claim is *implied* by contrast with
   paid human therapy. A keyword on "afford therapy" would catch these — but it
   would also catch posts that just mention cost without using the AI that way.
   Borderline; could be worth testing `afford therapy` / `afford a therapist`.

2. **"helped me" + life-improvement narratives.** "helped me ... get my life
   together", "found it immensely helpful", "more helpful to me than any
   therapist", "helped me feel seen" (posts 9, 21, 27). The therapy use is
   carried by a whole sentence, not a phrase. Not keywordable without huge
   false-positive cost (`helped me` is everywhere).

3. **Symptom vocabulary without therapy vocabulary.** Posts name the condition
   the AI is helping with — "social anxiety", "anxiety", "trauma", "OCD",
   "maladaptive daydreaming", "childhood trauma", "PTO for therapy", "psych
   hospital", "intensive outpatient" (posts 7, 9, 14, 15, 21, 23, 28, 31, 33).
   These are real signal but individually generic (anxiety/trauma appear all
   over the corpus). A symptom word only indicates AI-as-therapy when paired
   with an AI-use verb in the same sentence — not catchable with a flat regex.

4. **Role-substitution by analogy.** "they became my therapists in a way",
   "like having a hand around your waist", "like daily therapy", "she's not
   just a therapist, she's my friend" (posts 3, 6, 21). The therapist role is
   asserted via simile/qualifier. `like ... therapy` / `daily therapy` is the
   only fragment here that could become a keyword (`daily therapy`, post 21 —
   very low volume).

5. **Pathologizing-complaint posts.** Posts 4, 10, 28 are confirmed therapy-use
   posts but their *vocabulary* is about the AI failing at therapy ("pathologize
   my feelings", "cold, clinical", "pseudo-therapeutic speak"). Any keyword
   tuned to these would also catch rupture/complaint posts. This subset is
   essentially un-separable from the rupture theme by keyword alone.

---

## Recommendation summary

- No single new high-precision, high-volume keyword emerges from this batch.
  This matches CLAUDE.md's standing finding: therapy vocabulary is structurally
  fragmented across phrasings.
- The cleanest *specific* candidates (`ai psychologist`, `therapist bot`,
  `psychologist bot`, `grief counselor`) are all near-certain LOW VOLUME — they
  are precise but rare, consistent with the 2026-05-12 mining round.
- The high-recall candidates (`emotional support`, `coping mechanism`, `mental
  health`, `therapeutic`) are all generic and leak into romance / addiction /
  rupture. `coping mechanism` specifically pulls the addiction theme.
- Best realistic next step is a 2-word *combination* approach (e.g.
  "ai" + "therapist/psychologist" co-occurrence, or "use ___ for therapy"
  windowed matching) rather than a flat keyword — but that is a matcher change,
  not a keyword add. Per CLAUDE.md, defer therapy mining until corpus growth
  lifts the specific candidates above the 50-hit floor.
