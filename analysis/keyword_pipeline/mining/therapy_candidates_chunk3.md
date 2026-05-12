# Therapy candidates from chunk 3

**Source:** `therapy_yes_corpus_chunk3.md` (83 pre-validated YES posts, anchored on *coping mechanism*, *for therapy*, *emotional support*)

**Existing config (excluded from proposals):** ai therapist, free therapy, ai therapy, as a therapist, therapeutic, for therapy, emotional support, coping mechanism

## Ranked candidates (top 20)

1. **unhealthy coping mechanism** (seen in ~3 posts) — morphological extension of the existing anchor; carries self-aware-addiction framing specific to AI use. Example: 1sonuiq ("unhealthy coping mechanism"), also appears in 1n0qftd and 1p98pyb.

2. **healthy coping mechanism** (seen in 2 posts) — paired inverse of the above; first-person "I need to find a healthy coping mechanism" framing appears in recovery subs. Examples: 1n0qftd, recurrent community vocabulary in recovery framing.

3. **vent to ai** / **venting to ai** (seen in ~3 posts) — first-person AI-as-outlet vocabulary, distinct from "emotional support." Examples: 1pc4h09 ("Only venting to ai" — post title), 1od62mf ("space to vent"), common pattern in r/AI_Addiction posts.

4. **use it for therapy** / **used it for therapy** (seen in ~5 posts) — direct first-person claim of AI use for therapeutic purposes; survives FP filter because "it" anchors to AI. Examples: 1bblpq3, 1dcwca4, 1gavmlw, 1ntbeib, 1elwjw9.

5. **in place of journaling** / **in place of therapy** (seen in 2 posts) — substitution framing; AI-as-replacement-for-professional-help vocabulary. Examples: 1hjp80v, 1hjp9ll ("chat with in place of journaling for therapy").

6. **process my emotions** / **help me process** (seen in ~3 posts) — theme-carrying therapeutic-action verb phrase; distinct from generic emotional language because it names the therapeutic function. Examples: 1od62mf ("help you process your emotions"), 1mh8f4y ("intense processing for therapy").

7. **judgment-free zone** / **without judgment** (seen in ~4 posts) — community vocabulary for why AI feels therapeutic; captures the "never judgmental" framing. Examples: 1od62mf ("judgment-free zone"), 1lhcmje ("never judgemental"), 1gamdh7 ("without judgment"), 11s4p3k.

8. **safe place to vent** / **safe space** (seen in ~4 posts) — therapeutic-framing language for why AI fills the role. Examples: 1h2fjsz ("safe and comfortable sharing my emotions"), 1pa122z ("safe place"), 1od62mf.

9. **mental health issues** (when co-occurring with AI framing, seen in ~5 posts) — context-bounded; appears when users describe AI helping with named conditions. Examples: 1fo5co3, 1gb4g8s, 1bblpq3. (Caveat: broad enough it may need a phrase anchor like "ai for mental health".)

10. **dark thoughts** / **through dark thoughts** (seen in ~3 posts) — emotional-register vocabulary specific to AI-as-lifeline framing; less generic than "sad." Examples: 1dcwca4 ("get me through dark thoughts"), 1fo5co3 ("darkest of times"), 1p98pyb.

11. **get me through** (seen in ~4 posts) — first-person framing of AI as sustaining mechanism through difficulty; intersects with addiction theme but therapy-carrying here. Examples: 1dcwca4, 1fo5co3 ("gotten me through my darkest of times"), 1mlr0vr ("what kept me going").

12. **suicidal ideation** / **suicidal thoughts** (seen in ~3 posts) — direct mental health vocabulary; appears in posts describing AI intervention in crisis. Examples: 1fo5co3 ("helped with my suicidal ideation"), 1gb71n1, 1kus0e0.

13. **helped me cope** / **help me cope** (seen in ~3 posts) — direct therapeutic-function claim. Examples: 1r4yc6p ("exactly what helped me cope"), 1qzicr4.

14. **bot therapist** / **little bot therapist** (seen in ~2 posts) — explicit AI-as-therapist noun phrase (distinct from existing "ai therapist"). Examples: 1n9l969 ("my little bot therapist said exactly what I already knew"), 1bimrtt ("therapy-bots").

15. **mental health struggles** (seen in ~3 posts) — context-specific variant of mental health language, appears in posts framing AI as scaffold. Examples: 1gb71n1, 1gb4g8s.

16. **stay alive** / **kept me alive** (seen in ~3 posts) — post-4o-deprecation vocabulary framing AI as literal lifeline (rupture × therapy overlap but therapy-carrying as claim). Examples: 1r4yc6p ("helped me stay alive"), 1mlr0vr ("what kept me going"), 1r7ff3b ("emotionally anchored").

17. **emotionally dependent** / **emotional dependency** (seen in ~2 posts) — community self-diagnostic vocabulary, discussed in context of therapeutic use. Examples: 1qwmjjo, 11s4p3k.

18. **ball-plank** / **ball-planking** (seen in 1 post, but distinctive) — niche community vocabulary for GPT-therapy-style sounding board. Example: 1raqqiz ("I would just need the ball-plank and smart answers"). *Likely too rare — flag for volume check only.*

19. **heal** / **helped me heal** / **in an effort to heal** (seen in ~3 posts) — therapeutic-action claim, carries the AI-as-healer framing. Examples: 1iuj4z5 ("heartwarming and healing"), 1om2mpb ("in an effort to heal"), 1ligkl8 ("focus the healing").

20. **talk about my feelings** / **talk about my troubles** (seen in ~3 posts) — first-person AI-as-confidant framing. Examples: 1pc4h09 ("the only way i could talk about my feelings"), 1bblpq3 ("to talk about it"), 11s4p3k.

## Notes

- **Generic/emotional phrases excluded:** "feel heard," "feel understood," "makes me happy," "I love it" — too broad; would collide with non-therapy theme content.
- **Human-therapist-only exclusions:** "registered therapists," "four different therapists," "professional therapist" — these appear but are explicitly about human therapy without AI framing.
- **Bot-card patterns not observed in this chunk:** No dominant "therapist persona card" false-positive pattern in these 83 posts (anchor selection filtered them out), but candidates like "therapy-bot" should be validated against JanitorAI/SillyTavern exclusion rules.
- **Rupture-theme overlap candidates:** #11, #16, #17 appear in posts describing loss of GPT-4o as loss of a therapeutic tool. These would land in therapy × rupture overlap and should be validated with that in mind.
- **Recovery-sub voice:** "relapse," "day 1 again," "cold turkey" appear frequently but belong to the addiction theme — not proposed here.
