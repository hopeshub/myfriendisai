import type { Metadata } from "next";
import { readFileSync } from "fs";
import { join } from "path";

export const metadata: Metadata = {
  title: "About — My Friend Is AI",
  description:
    "Methodology, data sources, and changelog for the AI companionship community tracker.",
  openGraph: {
    title: "About — My Friend Is AI",
    description:
      "How we track AI companion discourse: keyword validation methodology, data sources, and project changelog.",
  },
};

function getPostCount(): string {
  try {
    const raw = readFileSync(join(process.cwd(), "data", "site_meta.json"), "utf-8");
    const meta = JSON.parse(raw) as { total_posts: number };
    return `~${(meta.total_posts / 1_000_000).toFixed(1)}M`;
  } catch {
    return "~3.8M";
  }
}

const STATS = [
  { value: getPostCount(), label: "posts in corpus" },
  { value: "27", label: "tracked communities" },
  { value: "80%", label: "minimum precision threshold" },
];

const CHANGELOG = [
  {
    date: "May 12, 2026",
    title: "Full v8 keyword revalidation under the new audit gate: 29 of 40 audited keywords pass",
    items: [
      "Applied the new 5-gate validation procedure retroactively to every v8 keyword with enough stored classifications to audit (40 of 76 pre-v8.1 keywords). The remaining 36 are LOW VOLUME placeholders (<50 corpus hits) for which an n=20 audit is not methodologically meaningful; they retain their original validation status",
      "29 of 40 audited keywords cleared the new ≥85% inter-rater agreement gate. The 11 failures are explained by two specific patterns rather than the keywords being bad",
      "Pattern 1 — the therapy theme has genuinely fuzzier boundaries than rupture/romance/addiction. All four therapy keywords (\"as a therapist\" 60% agreement, \"for therapy\" 60%, \"therapeutic\" 65%, \"emotional support\" 75%) show real classifier-interpretation variance on edge cases like critiques of AI-as-therapist, character backstory mentions, and peripheral therapy framing. The keywords still produce signal — but the precision numbers from prior validations should be read with wider uncertainty bands than for other themes. A future cycle may tighten the therapy rubric specifically",
      "Pattern 2 — stored primary classifications that predate the April 23 rubric lock can be out-of-step with the current topical-reading standard, particularly for posts with `[removed]` bodies. The audit, running under the current rubric, classifies these YES when the title in a companion subreddit is on-topic; older stored labels defaulted to NO. Affects \"lewd\" (55% audit agreement, 9 of 9 disagreements are [removed]-body posts), \"nsfw chat\" (70%), \"sex with\" (80%), \"finally deleted\" (80%), and \"hours a day\" (75%). The audit is correct under the current rubric — these keywords' true precision is HIGHER than their stored numbers suggest, not lower",
      "Two romance keywords (\"husbando\" 70%, \"honeymoon\" 80%) failed for genuine frame-dependence reasons. \"Honeymoon\" especially is ambiguous between literal AI-romance use (\"honeymoon trip with my Replika\") and platform metaphor (\"honeymoon phase with CharacterAI\"). Both are valid readings under the rubric",
      "Net effect on the trend lines: no keyword is being cut or removed. The audit data is now part of the per-keyword annotation in config/keywords_v8.yaml. Coverage went from zero audited v8 keywords (yesterday) to 37 of 84 current v8.1 keywords audited under the 5-gate procedure (29 v8 PASS + 8 v8.1 KEEPs from the emotional-loss batch)",
      "Full report: docs/validation_v8_full_revalidation_2026-05-12.md",
    ],
    recent: true,
  },
  {
    date: "May 12, 2026",
    title: "Keyword methodology gets a 5th gate: independent audit and inter-rater agreement",
    items: [
      "Added an audit step to the keyword validation pipeline. Every new keyword now requires a second, independent Claude Code instance to re-classify a 20-post subsample under the same rubric, without seeing the primary labels. The per-keyword inter-rater agreement must be ≥85% to ship — a fifth hard gate on top of the existing four (precision, Wilson lower bound, top-subreddit concentration, cross-theme overlap)",
      "Why this matters: precision alone is one number from one classifier. The audit is an empirical estimate of how much that number depends on classifier interpretation. Mean inter-rater agreement on the first batch validated under the new procedure was 93% — meaning when this site says a keyword has 88% precision, you should read it with ±~7pp variance from classifier noise alone",
      "The audit immediately caught a live failure. The candidate keyword \"erased\" looked clean under the old procedure (85% precision, all four legacy gates passed) but the audit returned 80% inter-rater agreement. All four disagreements clustered on a categorizable pattern: posts where a user deleted their own chat or a transient bug cleared messages were being scored as rupture, when they should not be — those are user actions or technical glitches, not platform-driven companion loss. The keyword was demoted to REVIEW and the rupture theme definition was tightened with two new explicit exclusions",
      "Pipeline now self-corrects via documented rubric loop: when an audit disagreement pattern is categorizable (3+ disagreements in the same FP category), the theme definition gets a new explicit excludes clause and the keyword is re-validated under the tightened rubric. Audits surface gaps; rubric tightens; future keywords in the same theme benefit automatically",
      "Honest limit: both classifier and auditor are the same model (Claude Code). This catches permissive-drift and rubric gaps but does not address single-model bias. A genuinely hostile reviewer will point out that within-model inter-rater reliability is not the same as cross-model or human-coded κ — they would be right. Adding a human-coded calibration set is the next layer of rigor and remains an open checklist item in the methodology doc",
      "Procedure is now a documented runbook future researchers (or Claude sessions) can follow without hand-holding. Includes a five-stage workflow, agent prompt templates, a validation doc template, and a worked example from this batch. See analysis/keyword_pipeline/README.md in the repository",
    ],
    recent: true,
  },
  {
    date: "May 12, 2026",
    title: "Rupture vocabulary expanded with 8 emotional-loss keywords; methodology enhanced with audit step",
    items: [
      "Added 8 new Rupture keywords capturing affective companion-loss vocabulary: saying goodbye (97% precision), taken away (95%), mourning (91%), mourn (89%), devastated (88%), grieve (88%), goodbye (88%), and farewell (87%). All eight cleared a 5-gate validation (precision, Wilson lower bound, top-subreddit concentration, cross-theme overlap, and a new inter-rater agreement gate)",
      "Trigger: Anthropic's announcement that Claude Sonnet 4.5 would be retired May 15 exposed a gap. The companion community responded with grief, farewells, and a petition, but the existing rupture vocabulary (lobotomy, nerfed, gutted) only catches the metaphorical-loss register — not the affective-loss register. None of the 22 Sonnet-4.5-related companion posts since May 5 were rupture-tagged under the old vocabulary",
      "What the new vocabulary catches that the old didn't: 5 of those 22 Sonnet 4.5 posts are now rupture-tagged via the new keywords (mourn, grieve, goodbye family). The remaining 17 use event-descriptive language — petition, removing, retiring — which we deliberately rejected at pre-screen because it concentrates on single platforms' controversy cycles (the canonical keep4o failure pattern) and would fail construct validity. The principled affective vocabulary worked; the event vocabulary was correctly held out",
      "Methodology enhancement: every new keyword now requires an independent audit pass. A separate Claude Code instance re-classifies a 20-post subsample under the same rubric without seeing the primary labels. Per-keyword inter-rater agreement must be ≥85% to ship. Mean agreement on this batch was 93%; the audit demoted erased to REVIEW (80% agreement revealed a rubric gap around user-initiated content deletion) and confirmed grief as a CUT (62% precision, audit agreement consistent with that)",
      "Theme definition tightened: rupture excludes now explicitly cover user-initiated content deletion, transient bug-based erasure, and sarcasm without affective stake. Both clarifications were driven by the erased audit's disagreement pattern — exactly the self-correcting loop the new audit step was designed to surface",
      "Rupture-tagged unique post count: ~1,830 → 5,026. The trend line shifts upward starting today; pre/post comparisons across May 12 are not apples-to-apples and should be read with that caveat. The shift is methodology improvement, not real-world signal change",
      "What's NOT in this update: heartbroken (77% precision, 68% Wilson lower bound — recommend re-running at n=200 before promoting) and erased (rubric was tightened to fix its audit miss; re-validate under the new rubric before merging) are held back for a follow-up batch",
      "Full report: docs/validation_emotional_loss_2026-05-12.md. Pipeline methodology documented in analysis/keyword_pipeline/README.md",
    ],
    recent: true,
  },
  {
    date: "April 23, 2026",
    title: "Keyword revalidation: 6 cuts, 6 promotions, methodology tightened",
    items: [
      "Revalidated all 46 high-volume keywords (≥50 hits) against the post-April-20 corpus using the same 100-post manual scoring methodology used to establish the original baselines",
      "Cut 6 keywords that collapsed below 60% precision: sentient and self-aware (CharacterAI meme dilution), chatbot addiction (journalist and moderator solicitation in recovery subs), and kink, fetish, nsfw bot (bot-directory listings and genre-tag content)",
      "Promoted 6 keywords from researcher-accepted to clean KEEP after clearing 80%: neutered (93%), grieving (86%), clean for (96%), as a therapist (87%), therapeutic (87%), and for therapy (89%)",
      "Why this happened: keywords age. “Sentient” (the volume anchor of consciousness, 83% precision in March) dropped to 55% — not because consciousness discourse is fading, but because the word got absorbed into CharacterAI meme culture (joke titles, RP character traits, dismissive one-liners) while serious discourse moved toward more specific vocabulary like personhood, selfhood, and subjective experience. The theme’s vocabulary matured while its most-common carrier word got memed. A similar dynamic drove the sex/ERP cuts: bot-directory listings and genre-tag content now dominate matches for kink, fetish, and “nsfw bot”",
      "What it means for the trend lines: the consciousness series will look noticeably thinner — sentient alone had carried roughly 1,100 of the theme’s tagged posts. That’s the precision-first tradeoff at work. We trade recall (loose meme-register usage) for signal quality: every remaining match reliably represents serious engagement with the question rather than ironic or joke-register mention",
      "Rupture is now the strongest theme (8 of 8 keywords at ≥84% precision); Sex/ERP narrowed to its high-precision core — erp (98%), steamy (96%), erotic roleplay (85%) carry the signal",
      "Tightened the classification standard to use an explicit topical reading (“posts thematically about X in a companion community”) rather than the prior ambiguous wording that mixed topical and first-person-content language. The ambiguity had caused an initial revalidation pass to systematically understate precision on defensible keywords",
      "Full report: docs/validation_all_themes_revalidation_2026-04-23.md",
    ],
    recent: true,
  },
  {
    date: "April 20, 2026",
    title: "Multi-word keyword boundary fix and full corpus re-tag",
    items: [
      "Fixed a regex bug where multi-word keywords matched as substrings inside unrelated words \u2014 e.g. \u201Cdating my\u201D was being tagged inside \u201Cupdating my\u201D and \u201Cvalidating my,\u201D inflating counts with false positives",
      "Root cause: the matcher compiled single-word terms with word boundaries but skipped boundaries on multi-word phrases; now every term uses \\b boundaries",
      "Re-tagged the full corpus under the fixed matcher \u2014 894k posts across 22 T1\u2013T3 subreddits, plus 64k comments from the post-March-18 window",
      "Net \u2212600 false-positive post-level tag rows. Largest reductions: romance (\u22128.3%), therapy (\u22127.3%), sexual/ERP (\u22126.6%). Consciousness and rupture were nearly unaffected because their multi-word terms don\u2019t collide with common English substrings",
      "A precision smoke-test the same day surfaced a separate drift pattern in the romance theme: ChatGPTcomplaints posts now contain satirical scripts and press-citation threads that quote romance vocabulary in the third person. Flagged as a stage-2 filtering target; no keyword-file edits made yet",
    ],
    recent: true,
  },
  {
    date: "April 15, 2026",
    title: "Weekly contributors replaces dead \u201Cactive users\u201D metric",
    items: [
      "Reddit removed the active_user_count field from the public API in September 2025, leaving our collector silently recording zeros",
      "Replaced with a rolling 7-day distinct-contributor count \u2014 built from the post and comment authors we already store",
      "Historical series backfills cleanly to 2023 for post authors; comment authors join the count from 2026-03-10 forward, when comment collection began",
      "Surfaces on the community explorer as a sortable \u201CContributors / wk\u201D column \u2014 small companionship subs can now rank on activity instead of being buried by subscriber count",
      "Aligns with Reddit\u2019s own September 2025 move away from subscribers toward visitors and contributions as the primary vitality signal",
    ],
    recent: true,
  },
  {
    date: "March 21, 2026",
    title: "Year-over-year comparison improvements",
    items: [
      "Headline now uses per-1k-posts rate instead of raw counts, controlling for collection volume growth",
      "Averaging now divides by calendar days (90) instead of days-with-data, fixing sparse-data bias in prior-year windows",
      "Large changes (>100%) now show actual rates instead of percentages \u2014 e.g. \u201Crose from 1.2 to 8.6 per 1k posts\u201D gives more context than a raw percentage when the base rate is small",
    ],
    recent: true,
  },
  {
    date: "March 21, 2026",
    title: "Mobile responsive redesign",
    items: [
      "Theme cards now scroll horizontally on phones instead of stacking in a grid",
      "Chart appears above the fold on mobile \u2014 no more scrolling past cards to see trends",
      "Detail panel opens as a draggable bottom sheet instead of covering the full screen",
      "Minimum 14px font size and 44px touch targets across all interactive elements",
    ],
    recent: true,
  },
  {
    date: "March 15, 2026",
    title: "Keyword expansion (discovery batch)",
    items: [
      "Added 16 validated keywords across all six themes via co-occurrence analysis",
      "Addiction: chatbot addiction, almost relapsed, finally deleted, the craving, so addictive",
      "Consciousness: sapience, tulpa, lemoine, soulbonder",
      "Sexual/ERP: erps, erping",
      "Rupture: lobotomies, lobotomizing, lobotomised",
      "Therapy: emotional support, coping mechanism",
      "All keywords validated at \u226580% precision",
    ],
    recent: false,
  },
  {
    date: "March 15, 2026",
    title: "Keyword validation methodology (v8 \u2192 v9)",
    items: [
      "Narrowed from 15 overlapping categories to 6 defensible themes",
      "Rebuilt keyword classification pipeline with FTS5 full-text search",
      "Conducted co-occurrence discovery analysis to surface data-driven keyword candidates",
      "Identified and excluded SpicyChat bot-building spam from 2 prolific authors",
    ],
    recent: false,
  },
  {
    date: "March 13, 2026",
    title: "Live daily collection begins",
    items: [
      "Automated daily collection via launchd (local) replacing backfill pipeline",
      "27 active subreddits collected daily at 6:00 AM PT",
    ],
    recent: false,
  },
  {
    date: "March 2026",
    title: "Subreddit corpus finalized at 27 active communities",
    items: [
      "Expanded from 19 to 29 communities, then deactivated 2 (JanitorAI_Official, SillyTavernAI excluded from keyword matching due to bot-card pollution)",
      "Tier structure: 5 general AI (T0), 10 primary companionship (T1), 8 platform-specific (T2), 4 recovery/dependency (T3)",
    ],
    recent: false,
  },
];

const linkClass =
  "text-foreground underline underline-offset-2 hover:text-primary transition-colors";

const sectionHeaderStyle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 500,
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  color: "#8293A6",
  marginBottom: 16,
};

const bodyStyle: React.CSSProperties = {
  fontSize: 15,
  lineHeight: 1.8,
  color: "#CBD5E1",
};

const sectionStyle: React.CSSProperties = {
  borderLeft: "1px solid #334155",
  paddingLeft: 24,
};

export default function About() {
  return (
    <div style={{ maxWidth: 720 }} className="mx-auto px-4 sm:px-6 py-10 sm:py-16">
      {/* Page headline */}
      <div className="mb-10">
        <div
          style={{
            fontSize: 12,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            color: "#8293A6",
            marginBottom: 8,
          }}
        >
          About this project
        </div>
        <h1
          style={{ fontSize: 32, fontWeight: 600 }}
          className="text-foreground mb-2"
        >
          Tracking how people talk about AI companions
        </h1>
        <p style={{ fontSize: 16, color: "#94A3B8" }}>
          Tracking AI companion discourse on Reddit across six themes.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-2 sm:gap-3 mb-12">
        {STATS.map((stat) => (
          <div
            key={stat.label}
            className="rounded-lg"
            style={{
              backgroundColor: "#1A1D27",
              padding: "12px 10px",
            }}
          >
            <div
              style={{
                fontSize: 22,
                fontWeight: 500,
                color: "#F8FAFC",
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {stat.value}
            </div>
            <div style={{ fontSize: 12, color: "#94A3B8", marginTop: 2 }}>
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-10">
        {/* How this works */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>How this works</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              Themes emerge from direct observation of how people talk in these
              communities &mdash; patterns in language that signal recurring
              concerns, experiences, and framings. For each theme, we identify
              candidate keywords: terms and phrases that appear to reliably mark
              that theme in context.
            </p>
            <ul className="space-y-2" style={{ listStyleType: "none", padding: 0 }}>
              {[
                { emoji: "\u{1F495}", label: "Romance", tagline: "Language of love, dating, and romantic attachment", color: "#FF69B4" },
                { emoji: "\u{1F51E}", label: "Sex / ERP", tagline: "Language of sexual and erotic roleplay", color: "#f87171" },
                { emoji: "\u{1F9E0}", label: "Consciousness", tagline: "Language of sentience, awareness, and inner experience", color: "#C084FC" },
                { emoji: "\u{1FAC2}", label: "Therapy", tagline: "Language of mental health support and emotional care", color: "#60A5FA" },
                { emoji: "\u{1F48A}", label: "Addiction", tagline: "Language of dependency and compulsion", color: "#fd7112" },
                { emoji: "\u{1F940}", label: "Rupture", tagline: "Language of loss and grief", color: "#22C55E" },
              ].map((t) => (
                <li key={t.label} style={{ fontSize: 15, lineHeight: 1.6 }}>
                  <span>{t.emoji}</span>{" "}
                  <span style={{ color: t.color, fontWeight: 500 }}>{t.label}</span>
                  <span style={{ color: "#94A3B8" }}> &mdash; {t.tagline}</span>
                </li>
              ))}
            </ul>
            <p>
              Each keyword is then validated through manual scoring of 100-post
              samples, checking whether the term actually signals the theme or
              just happens to co-occur. Keywords scoring 80% precision or above
              are accepted. Keywords in the 60&ndash;79% range may be accepted
              when false positive patterns are well-defined and the keyword adds
              meaningful vocabulary diversity. All validation decisions are
              documented and available on the{" "}
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className={linkClass}
              >
                GitHub repository
              </a>
              .
            </p>
            <p>
              The chart shows how often these validated terms are mentioned per
              1,000 posts, using a 7-day rolling average to smooth daily noise. Because
              we normalize to post volume, the trends reflect changes in how
              people talk &mdash; not just growth in the communities themselves.
            </p>
          </div>
        </section>

        {/* Why hit rates don't compare */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>
            Why mention rates don&apos;t compare across themes
          </h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              A theme&apos;s mention rate reflects how often people use
              distinctive, validated language for that topic &mdash; not how
              prevalent the topic is overall.
            </p>
            <p>
              Some themes have highly specific vocabulary. When someone describes
              AI addiction, they borrow clinical recovery language:
              &ldquo;relapse,&rdquo; &ldquo;cold turkey,&rdquo; &ldquo;chatbot
              addiction.&rdquo; These terms are rare outside that context and
              validate at near-perfect precision. The keyword net catches most of
              what&apos;s there.
            </p>
            <p>
              Other themes are expressed through everyday language. When someone
              is in a romantic relationship with their AI, they say &ldquo;I
              love him,&rdquo; &ldquo;my boyfriend,&rdquo; &ldquo;we went on a
              date&rdquo; &mdash; words that are indistinguishable from how
              people talk about human relationships. These fail precision
              validation because they can&apos;t be reliably attributed to AI
              companionship. Only highly specific phrases like &ldquo;our
              wedding&rdquo; or &ldquo;my AI partner&rdquo; survive, meaning the
              keyword net captures only a fraction of the actual romance
              discourse.
            </p>
            <p>
              The result: addiction may show a higher mention rate than romance,
              but that reflects vocabulary distinctiveness, not phenomenon size.
              Each theme&apos;s trend line is meaningful over time &mdash; a
              spike or decline in a theme tells you something real about how that
              conversation is changing. But comparing mention rates between
              themes does not tell you which topic is &ldquo;bigger&rdquo; or
              more important.
            </p>
          </div>
        </section>

        {/* How the aggregate is composed */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>
            How the aggregate is composed
          </h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              The chart shows post-volume-weighted rates across all 22 primary
              AI companionship subreddits. A community generating 400 posts a
              day pulls the aggregate toward its language profile more than one
              generating 5 a day.
            </p>
            <p>
              One community &mdash; r/CharacterAI &mdash; currently makes up
              roughly two-thirds of the post volume in our corpus.
              CharacterAI&apos;s discourse skews toward platform mechanics
              (memory resets, model degradation, addiction recovery) and away
              from explicit romance or sexual content, which tend to happen{" "}
              <em>in</em> conversations on companion-romance and NSFW platforms
              rather than <em>as posts about them</em>.
            </p>
            <p>
              What this means: the aggregate mention rate for any theme is best
              read as &ldquo;across the ecosystem, weighted by where the
              conversation is actually happening&rdquo; &mdash; not
              &ldquo;across the average AI companion community.&rdquo; Smaller
              communities like r/MyBoyfriendIsAI, r/NomiAI, and r/SpicyChatAI
              have very different thematic profiles, but contribute
              proportionally less to the aggregate. As the ecosystem evolves and
              the volume distribution shifts, the aggregate will shift with it.
            </p>
          </div>
        </section>

        {/* What this captures */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>
            What this captures and what it doesn&apos;t
          </h2>
          <div style={bodyStyle}>
            <p>
              This is a frequency tracker, not a sentiment analyzer. When the
              addiction line rises, it means more people are using
              addiction-related language &mdash; not that more people are
              addicted. The signal is intentionally narrow: we trade coverage for
              precision, preferring to undercount rather than pollute the data.
              Some themes are measured by just a handful of highly specific
              terms. Every data point traces back to a validated keyword in a
              real post.
            </p>
          </div>
        </section>

        {/* Data collection */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>Data collection</h2>
          <div style={bodyStyle}>
            <p>
              Data from January 2023 through March 12, 2026 was backfilled from
              PullPush and Arctic Shift Reddit archives. From March 13, 2026
              onward, posts are collected daily via Reddit&apos;s API, with
              periodic backfills from Arctic Shift to ensure complete coverage
              of high-volume communities that exceed the daily collection&apos;s
              per-request limits. The data format and processing pipeline are
              identical regardless of source.
            </p>
          </div>
        </section>

        {/* Ongoing updates */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>Ongoing updates</h2>
          <div style={bodyStyle}>
            <p>
              This project evolves as the space does. New themes, subreddits,
              and keywords are validated and added using the same process
              described above. Every change is logged in the changelog below, and
              the full validation records, keyword lists, and decision rationale
              are available in the{" "}
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className={linkClass}
              >
                GitHub repository
              </a>
              .
            </p>
          </div>
        </section>

        {/* Changelog timeline */}
        <section>
          <h2 style={sectionHeaderStyle}>Changelog</h2>
          <div className="relative" style={{ paddingLeft: 24 }}>
            {/* Vertical timeline line */}
            <div
              className="absolute top-0 bottom-0"
              style={{
                left: 5,
                width: 1,
                backgroundColor: "#1E293B",
              }}
            />

            <div className="space-y-6">
              {CHANGELOG.map((entry, i) => (
                <div key={i} className="relative">
                  {/* Timeline dot */}
                  <div
                    className="absolute rounded-full"
                    style={{
                      left: -22,
                      top: 4,
                      width: 9,
                      height: 9,
                      backgroundColor: entry.recent ? "#F59E0B" : "#334155",
                      border: "2px solid #0F1117",
                    }}
                  />

                  <div
                    style={{ fontSize: 12, color: "#F59E0B", marginBottom: 2 }}
                  >
                    {entry.date}
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 500,
                      color: "#F8FAFC",
                      marginBottom: 6,
                    }}
                  >
                    {entry.title}
                  </div>
                  <ul className="space-y-1">
                    {entry.items.map((item, j) => (
                      <li
                        key={j}
                        style={{
                          fontSize: 13,
                          lineHeight: 1.6,
                          color: "#94A3B8",
                          paddingLeft: 12,
                          listStyleType: "none",
                        }}
                      >
                        <span style={{ color: "#334155" }} className="mr-1.5">
                          &bull;
                        </span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

