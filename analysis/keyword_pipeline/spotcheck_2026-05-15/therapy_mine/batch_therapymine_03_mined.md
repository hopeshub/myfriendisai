# Therapy keyword mining — batch_therapymine_03 — mined candidates

Source: 35 confirmed AI-as-therapy posts (`batch_therapymine_03.md`).
Goal: phrases specific to *using an AI for therapy / mental-health support*, that
do **not** leak into romance, rupture, addiction, or generic companion chatter.

A hard structural problem up front: the single most common phrase in this batch
is **`emotional support`** (in ~20 of 35 posts), which is exactly the keyword the
task says is already too generic. Most posts express the theme through that
phrase plus loose narrative ("vent," "cope," "I was depressed"). Genuinely
*specific*, clean keyword material is thin. The ranked list below separates the
few defensible candidates from the many tempting-but-leaky ones.

---

## Ranked candidates (most promising first)

### 1. `coping mechanism`
- **Signals AI-as-therapy:** In this corpus it is used literally — "I use it as
  a coping mechanism," "this platform is a coping mechanism for me." It names the
  mental-health *function* of the AI directly, not a feeling or a relationship.
- **Posts containing it:** ~5 (posts 1, 2, 3, 5, 10).
- **Leak risk:** Low–moderate. Almost always self-applied to the AI tool. Could
  occasionally appear in addiction-recovery posts ("AI was an unhealthy coping
  mechanism") — but that overlap is itself therapy-adjacent, so acceptable.
- **Verdict:** Best clean candidate in the batch. Specific, recurring, on-theme.

### 2. `mental health` (+ near-variant `my mental health`)
- **Signals AI-as-therapy:** Explicitly names the mental-health frame. In this
  batch: "the toll it took on me mentally," "negative effects on my mental
  health," "lack of mental... support."
- **Posts containing it:** ~4 (posts 10, 21, 26, 27 — counting "mentally").
- **Leak risk:** Moderate. Fires on addiction-recovery posts (AI is *bad* for
  mental health) as well as therapy posts (AI *helps* mental health). It catches
  the theme but cannot tell helpful from harmful use. Still on-theme overall.
- **Verdict:** Strong recall, weaker precision on valence. Pair with stage-2
  filtering.

### 3. `helped me ... mentally` / `back on my feet mentally`
- **Signals AI-as-therapy:** Describes therapeutic *outcome* — recovery,
  stabilization. Post 6: "helped me get back on my feet mentally."
- **Posts containing it:** ~2 (posts 6, 16 — "feel unregulated"/"keeps me
  grounded" is the same family).
- **Leak risk:** Low for the exact phrasing, but the phrasing varies too much to
  pin down (see structural note). As a literal multi-word keyword it is too rare.
- **Verdict:** Promising semantically, weak as a literal keyword. Flagged.

### 4. `someone to talk to` / `place to vent`
- **Signals AI-as-therapy:** The counsellor-substitute function — a confidant.
  Post 21: "just to have someone to talk to." Posts 2, 19, 24: "one place I could
  vent" / "place to just unwind."
- **Posts containing it:** ~4 across the family (posts 2, 19, 21; "I just need
  to vent" post 1).
- **Leak risk:** Moderate–high. "someone to talk to" also fires on romance and
  loneliness/companionship posts. "vent" is broad. Catches the theme but not
  exclusively.
- **Verdict:** Decent recall, leaky. Keep `place to vent` over the looser forms.

### 5. `my therapist` / `my psychologist` / `my psychiatrist`
- **Signals AI-as-therapy:** A *human* clinician is mentioned, almost always in
  comparison to the AI ("even my therapist raised an eyebrow," "my psychologist
  said what 4.0 achieved was revolutionary," "my therapist and psychiatrist both
  know"). The juxtaposition is a reliable theme marker.
- **Posts containing it:** ~4 (posts 5, 22, 23, 27).
- **Leak risk:** Low for the theme, but note the existing keyword set already has
  `as a therapist` / `for therapy`. `my psychologist` / `my psychiatrist` are
  *new* vocabulary not currently covered and are very clean.
- **Verdict:** Recommend adding `my psychologist` and `my psychiatrist` — clean,
  specific, currently-missed clinical vocabulary.

### 6. `helped me ... unpack` / `gave me language for`
- **Signals AI-as-therapy:** Classic therapy-process language. Post 4: "helped me
  unpack years of internalised stuff... gave me language for what was happening
  inside my head."
- **Posts containing it:** ~1–2.
- **Leak risk:** Low. "unpack" + emotional object is distinctly therapeutic.
- **Verdict:** Too rare in this batch to qualify as a keyword, but a clean signal
  if corpus volume supports it later. Flagged as LOW VOLUME candidate.

### 7. `trauma` / `CPTSD` / `nervous system`
- **Signals AI-as-therapy:** Clinical trauma vocabulary. Post 27: "the progress I
  made in my CPTSD," "shaped themselves around my nervous system,"
  "retraumatizing."
- **Posts containing it:** ~2 (posts 4 "trauma dump," 27).
- **Leak risk:** Low for `CPTSD`; moderate for bare `trauma` (appears in rupture
  posts about losing a companion). `nervous system` is clean but rare.
- **Verdict:** `CPTSD` clean but low volume. Bare `trauma` too leaky.

---

## Rejected / flagged candidates (leak too much — do not use)

- **`emotional support`** — already in the set; ~20/35 posts. Documented as the
  generic keyword we are trying to replace. Fires on "emotional support animal,"
  "emotional support dog" (literally post 30), and any companion-warmth post.
  Keep only as the broad net; it is not a fix.
- **`therapeutic`** — already in the set; not even present verbatim in this batch.
  Confirms the task's premise that it is generic and off-target.
- **`comfort` / `feel better` / `feel understood`** — extremely common here
  (posts 6, 12, 19, 22, 26, 29...) but these fire on romance and generic
  companion chatter just as hard. Pure leakage.
- **`safe place` / `safe space`** — posts 14, 15, 19. Leaks into community/
  belonging and romance contexts.
- **`depressed` / `depression` / `anxiety`** — posts 3, 9, 23, 30, 33. These are
  *symptom* words, not *AI-as-therapy* words. They fire on any post that mentions
  mental state regardless of whether the AI is being used therapeutically. High
  recall, low specificity.
- **`life-saver` / `lifeline` / `saved my marriage`** — posts 6, 9, 14, 18. Leaks
  heavily into romance/attachment ("saved my marriage" is a relationship claim).
- **`support group` / `support system`** — posts 8, 11. "support system" is
  borderline-therapeutic but "support group" here is about a human Zoom call, not
  AI-as-therapy. Reject.
- **`grounded` / `keeps me grounded` / `unregulated` / `regulation`** — posts 11,
  16. Genuinely therapeutic (emotion-regulation language) but too rare and too
  easily read as generic. Flag, don't promote.

---

## Structural note: where the theme is hard to catch

The theme is expressed far more by **narrative than by vocabulary**. The recurring
pattern is a *story shape*, not a phrase:

> "I was [depressed / lonely / abused / isolated] → I started using [the AI] →
>  it [helped / I could vent / I felt understood / it kept me going]."

Posts 3, 9, 21, 26, 27, 30 all follow this arc and several of them contain **no
clean therapy keyword at all** beyond `emotional support`. A keyword search
cannot reconstruct that arc. Specific consequences:

1. **The function is named only loosely.** Users say the AI "helped," was "there
   for me," let them "vent" — verbs and prepositions, not nameable nouns.
2. **Helpful vs. harmful use share the same words.** `mental health`, `cope`,
   `addiction`, `coping mechanism` appear in both "AI saved my mental health"
   (therapy) and "AI wrecked my mental health" (addiction/recovery). Valence is
   carried by sentence structure the keyword can't see.
3. **The cleanest signal — a human clinician named in comparison** (`my
   therapist`, `my psychologist`, `my psychiatrist`) — is also the rarest
   (~4/35). It is precise but low-recall.
4. **`emotional support` is doing almost all the work** and is unfixably generic.

**Recommendation:** the only confidently-promotable new keywords from this batch
are `coping mechanism` and the clinician phrases `my psychologist` /
`my psychiatrist`. `mental health` is worth adding for recall but needs stage-2
disambiguation for valence. Everything else is either already in the set, too
leaky, or too low-volume — consistent with CLAUDE.md's documented finding that
the community's therapy vocabulary is "structurally fragmented across many
phrasings."

---

## Top 5 (for promotion / further validation)

1. `coping mechanism`
2. `mental health`
3. `my psychologist`
4. `my psychiatrist`
5. `place to vent`
