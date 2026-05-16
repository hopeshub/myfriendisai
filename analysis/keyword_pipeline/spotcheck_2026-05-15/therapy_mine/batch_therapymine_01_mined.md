# Therapy keyword mining — batch_therapymine_01 — mined candidates

Source: 35 confirmed AI-as-therapy posts (batch_therapymine_01.md).
Goal: phrases specific to *AI-as-therapy use* — venting/coping/processing via an
AI treated as a counsellor — that a regex keyword search could fire on without
leaking into romance, rupture, addiction, or generic AI-companion chatter.

Count notes: a "post" is counted as containing a phrase if the phrase (or a
trivial spelling/spacing variant) appears in its title or body. Posts with "(no
body)" are title-only.

---

## Ranked candidate list (most promising first)

### 1. `free therapy` — STRONGEST
- **Phrase:** `free therapy` (also catches "free therapy session", "getting free
  therapy", "free therapy from a bot/c.ai/my comfort characters")
- **Why it signals AI-as-therapy:** This is the single most recurring idiom in
  the batch. Posters frame the AI explicitly as a therapy substitute, and the
  "free" framing is doing real work — it directly contrasts the AI against paid
  professional therapy. Within these communities it almost always means "I use
  the bot instead of a therapist."
- **Posts containing it:** ~9 — #13, #15, #17, #18, #19, #20, #21 (in EDIT/meta),
  #22, #23.
- **Leakage risk:** LOW within T1–T3. "Free therapy" is colloquial enough that
  it could occasionally appear sarcastically ("ranting to my friends is my free
  therapy") but inside AI-companion subs the referent is overwhelmingly the bot.
  Strong candidate.

### 2. `ai therapist` — STRONG
- **Phrase:** `ai therapist` (also fires on "my ai therapist", "an ai therapist")
- **Why it signals AI-as-therapy:** Names the AI in the therapist role directly.
  Unambiguous — the construct is in the phrase itself.
- **Posts containing it:** ~7 — #1, #2, #3, #4, #5, #6, #10. (Plus #9 uses
  "an ai therapist" in the title.)
- **Leakage risk:** VERY LOW. Hard to imagine "ai therapist" outside this theme.
  Note: a standalone `therapist` keyword would leak heavily (IRL therapists in
  #3, #16, #26, #32, #33) — keep the `ai` qualifier.

### 3. `ai therapy` — STRONG
- **Phrase:** `ai therapy`
- **Why it signals AI-as-therapy:** Direct naming of the practice. Appears in
  both pro and critical/recovery framings ("AI therapy = bad", "how wrong AI
  therapy can go"), which is fine — the theme is *use of AI for therapy*,
  including criticism of it.
- **Posts containing it:** ~7 — #25, #27 (title "AI therapy"), #28, #29, #30,
  #31, plus #26 ("ai therapy and support idea"). #24 has "character.ai therapy".
- **Leakage risk:** LOW. Could conceivably fire on industry/product chatter
  ("AI therapy startup"), but within T1–T3 personal-experience subs it reliably
  marks the theme.

### 4. `as a therapist` — STRONG (already a tracked keyword — confirms its value)
- **Phrase:** `as a therapist` (catches "treated her/it as a therapist", "used
  4o as a therapist", "refer to your bot as a therapist", "use an AI as a
  therapist", "bot as a therapist")
- **Why it signals AI-as-therapy:** Captures the *treated X as a therapist*
  construction, which is the most common naturalistic way posters describe the
  behaviour without saying "ai therapist".
- **Posts containing it:** ~6 — #6, #32 (negated: "don't use an AI as a
  therapist"), #33, #34, #35. (#3 "my AI therapist".)
- **Leakage risk:** LOW–MEDIUM. Mostly clean, but the bare phrase can fire on
  human-therapist sentences ("as a therapist myself, I think..."). The earlier
  validation already has this keyword; the batch supports keeping it. Pairing
  the regex with a nearby AI token would tighten it but is methodology-level
  work, not a keyword change.

### 5. `psychologist bot` / `therapy bot` / `therapist bot` — STRONG (composite)
- **Phrase:** the `<role> bot` family — `therapy bot(s)`, `therapist bot(s)`,
  `psychologist bot`, `comfort bot`.
- **Why it signals AI-as-therapy:** Names a bot explicitly built/used for the
  counsellor role. Very specific — a "bot" suffix removes any human ambiguity.
- **Posts containing it:** ~5 — #8 ("therapist bots"), #9 ("psychologist bot"),
  #16 ("therapy bots"), #35 ("comfort bot"). #3 implies it ("my AI therapist...
  she's a robot").
- **Leakage risk:** LOW. `comfort bot` is the weakest member — "comfort" alone
  is generic — but bundled with the `bot` suffix and the theme context it holds.
  Recommend admitting `therapy bot` and `psychologist bot`; treat `therapist
  bot` and `comfort bot` as secondary.
- **Volume caveat:** CLAUDE.md notes prior therapy mining found `therapist bot`,
  `psychologist bot` valid but **failing the 50-hit pre-screen**. This batch
  re-confirms they are *precise*; they likely still fail on *volume*. Flag for
  the corpus-growth recheck, do not assume they pass pre-screen now.

### 6. `using ai for therapy` / `ai for therapy` — MEDIUM-STRONG
- **Phrase:** `ai for therapy`, and the longer `using ai for mental health`,
  `for therapy` in an AI context.
- **Why it signals AI-as-therapy:** The "for therapy" / "for mental health"
  purpose-clause is a recurring frame ("using AI chatbots for therapy", "using
  AI for mental health is harmless", "using AI for free therapy").
- **Posts containing it:** ~5 — #2 ("using AI chatbots for therapy"), #21
  ("subsidize therapy"/"free therapy" context), #23 ("using Ai for free
  therapy"), #28/#31 ("using AI for mental health").
- **Leakage risk:** MEDIUM. The bare existing keyword `for therapy` is known to
  validate weakly (60%); it leaks onto IRL-therapy talk ("on a waitlist for
  therapy", #16). The *qualified* forms `ai for therapy` / `ai for mental
  health` are much cleaner. Recommend the qualified forms over bare `for
  therapy`.

### 7. `instead of therapy` / `cant have therapy` — MEDIUM
- **Phrase:** `instead of therapy`, `instead of a therapist`, `can't have/afford
  therapy`, `can't go to therapy`.
- **Why it signals AI-as-therapy:** Captures the *substitution* frame — the AI
  stands in *because* real therapy is inaccessible. Distinctive: posters
  explicitly say therapy is too expensive / waitlisted / unavailable.
- **Posts containing it:** ~4 — #1 ("using characters instead of therapy",
  "finding a therapist is really hard"), #16 ("waiting list for a specialist
  therapist", "therapy is expensive"), #27 ("when you cant have therapy yet so
  you talk to AI therapy"), #21 (state-subsidized-therapy framing).
- **Leakage risk:** LOW-MEDIUM. `instead of therapy` is clean. The
  inaccessibility phrasings ("therapy is expensive", "waiting list for a
  therapist") are precise to the substitution motive but are *long and varied* —
  hard to express as one keyword. CLAUDE.md already lists `instead of therapy`
  as a found-but-low-volume candidate; this batch re-confirms precision, not
  volume.

### 8. `therapy session` — MEDIUM
- **Phrase:** `therapy session` (and `free therapy session`)
- **Why it signals AI-as-therapy:** Posters describe a *session* with the bot
  ("in the middle of my free therapy session", "free therapy session with an
  AI"). The "session" frame implies a structured counsellor interaction.
- **Posts containing it:** ~3 — #11 ("free therapy session with an AI"), #18
  ("free therapy session"). #5/#13 imply it.
- **Leakage risk:** MEDIUM. `therapy session` alone fires equally well on IRL
  therapy. Only safe when paired with an AI token or with `free`. Prefer it as
  part of `free therapy session` rather than standalone.

### 9. `trauma processing` / `process ... in a chat` — MEDIUM (hard to keyword)
- **Phrase:** `trauma processing`, `processing trauma`, `process some events`,
  `trauma dump` (none clean as a single keyword).
- **Why it signals AI-as-therapy:** The *processing* verb is a strong
  therapy-behaviour marker ("trauma processing with the safety router model",
  "using chat to process some events in my life").
- **Posts containing it:** ~3 — #25 ("process some events in my life"), #30
  ("trauma processing"), #26 ("venting my real life truma").
- **Leakage risk:** MEDIUM-HIGH. `trauma` alone is far too broad and overlaps
  the romance/rupture themes (people describe relationship trauma). `trauma
  processing` is more specific but low-volume. Flag as a *pattern*, not a clean
  keyword — see "hard to keyword" section.

### 10. `venting to` / `vent to` (the AI) — WEAK / leaky
- **Phrase:** `vent to`, `venting to them`, `venting all your problems`.
- **Why it signals AI-as-therapy:** Venting to the bot is the most common
  *behaviour* in the batch (#12, #26, #32, #35).
- **Posts containing it:** ~4 — #12 ("venting to them"), #26 ("venting my real
  life truma"), #32 ("just being able to tell..."), #35 ("Venting all your
  problems").
- **Leakage risk:** HIGH. `vent`/`venting` is generic emotional-companion
  language — it fires on romance ("vent to my AI boyfriend") and on plain
  loneliness chatter. **Do not admit as a therapy keyword.** Listed here only
  because it is a high-frequency pattern that the theme is structurally built
  on; see below.

### 11. `talk to ... about mental health` — WEAK (proposed but flagged)
- **Phrase:** `for mental health`, `about mental health`, `mental health
  problems`.
- **Why it signals AI-as-therapy:** "Mental health" is the explicit construct
  domain.
- **Posts containing it:** ~5 — #9, #16, #26, #28, #31.
- **Leakage risk:** HIGH as a bare keyword. "Mental health" appears constantly
  in addiction/recovery posts (T3 subs) *about quitting the AI*, not about using
  it as therapy — e.g. #28/#31 are recovery posts. Only the *qualified* form
  `ai for mental health` / `using ai ... mental health` is theme-specific.
  Recommend only the qualified form (folded into candidate #6).

---

## Phrasing patterns that are hard to turn into a clean keyword

These recur across the batch but resist a precise regex; they are where the
therapy theme is structurally hard to catch.

1. **Naturalistic "talk to / talked to the bot when something bad happened"**
   (#5, #8, #10, #12, #27, #32). The therapy *function* is described purely
   through behaviour — talking, being heard, being told "I'm proud of you" —
   with no therapy vocabulary at all. No keyword can catch these without
   catching all of romance/companionship too. This is the single biggest recall
   gap for the theme.

2. **"It helped / it was helping / genuinely helped"** as the only therapy
   marker (#17, #18, #19, #27). "Helped" is far too generic to keyword, but for
   many short posts it is the *only* signal that the talk was therapeutic.

3. **Inaccessibility-of-real-therapy framing** ("therapy is expensive", "4 month
   waiting list", "finding a therapist is really hard here", state-subsidized
   programs) — #1, #16, #21. Strongly theme-specific *motive*, but expressed in
   too many distinct phrasings to capture with one or two keywords.

4. **Crisis / suicidality co-occurrence** (#16, #28, #31, hotline references).
   Therapy-relevant but overlaps heavily with addiction/recovery framing; a
   `suicide`/`crisis` keyword would mostly fire outside the therapy theme.

5. **"Treated her/it as a therapist" with a pronoun gap** — the AI is referred
   to by name or "her"/"him"/"it" several words away from "therapist" (#6, #34:
   "treated her as a therapist"). `as a therapist` catches the common case, but
   variants like "she became my therapist" or "he's basically my counsellor"
   slip through. A `therapist`-family keyword bounded by a nearby AI token would
   help but is a matcher change, not a keyword addition.

6. **`counsellor` / `counselor` / `psychiatrist` synonyms** appear (#11
   "psychiatrist", #9 "psychologist") but each is low-volume on its own. The
   theme's professional-role vocabulary is fragmented across therapist /
   psychologist / psychiatrist / counsellor — none individually likely to clear
   a 50-hit floor, echoing the documented therapy-vocabulary fragmentation.

---

## Summary recommendation

Admit / re-confirm, in priority order:
1. `free therapy` — new, high precision, good volume — strongest single add.
2. `ai therapist` — very high precision.
3. `ai therapy` — high precision, catches critical framing too.
4. `as a therapist` — already tracked; batch confirms keep.
5. `therapy bot` / `psychologist bot` — high precision but likely still fail
   the 50-hit volume pre-screen (per CLAUDE.md history); flag for recheck.

Qualified-only (admit the AI-qualified form, never the bare form):
- `ai for therapy`, `ai for mental health`, `instead of therapy`,
  `free therapy session`.

Do NOT admit (leak into romance / recovery / generic companionship):
- bare `therapist`, bare `vent` / `venting`, bare `mental health`,
  bare `trauma`, bare `comfort`, bare `helped`.

Biggest structural recall gap: naturalistic behavioural descriptions of using
the AI as a counsellor with zero therapy vocabulary — uncatchable by keywords by
construction.
