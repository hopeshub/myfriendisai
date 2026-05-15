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
    return "~3.9M";
  }
}

type ThemeHealthEntry = {
  total_post_tags: number;
  total_comment_tags: number;
  top_sub_post: { subreddit: string; n: number; pct: number } | null;
  top_sub_comment: { subreddit: string; n: number; pct: number } | null;
  top_day: { date: string; n: number; pct: number } | null;
  top_month: { month: string; n: number; pct: number } | null;
  top5_authors_pct: number;
  post_precision: { date: string; n: number; precision: number } | null;
  comment_precision: { date: string; n: number; precision: number } | null;
  noisy_keywords_comment: string[];
};

type ThemeHealthData = {
  generated_at: string;
  drift_last_updated: string | null;
  themes: Record<string, ThemeHealthEntry>;
};

function loadThemeHealth(): ThemeHealthData | null {
  try {
    const raw = readFileSync(join(process.cwd(), "data", "theme_health.json"), "utf-8");
    return JSON.parse(raw) as ThemeHealthData;
  } catch {
    return null;
  }
}

const THEME_LABELS: Record<string, string> = {
  rupture: "Rupture",
  addiction: "Addiction",
  romance: "Romance",
  sexual_erp: "Sex / ERP",
  consciousness: "Consciousness",
  therapy: "Therapy",
};

const THEME_ORDER = ["rupture", "addiction", "romance", "sexual_erp", "consciousness", "therapy"];

// Stats shown at the top of the page. The "80%" number is the per-keyword
// admission gate — every keyword in the production set was validated at
// n=100 against the topical-reading rubric and admitted only if it scored
// ≥80% precision. Previously labeled "minimum precision threshold" which
// reviewers correctly flagged as misleading (a reader could mistake it
// for aggregate chart precision). The narrower label below makes the
// scope of the claim explicit; aggregate per-theme precision (which
// varies across keywords and surfaces) is shown in the Theme Health
// snapshot section below.
const STATS = [
  { value: getPostCount(), label: "posts in corpus" },
  { value: "27", label: "tracked communities" },
  { value: "≥80%", label: "per-keyword admission gate (validated at n=100)" },
];

const CHANGELOG = [
  {
    date: "May 2026",
    title: "Data extended back to 2017",
    items: [
      "The chart previously began in 2023. The underlying corpus now reaches back to 2017, bringing the early Replika years and the first companion-app crises into view.",
    ],
    recent: true,
  },
  {
    date: "May 2026",
    title: "Rupture vocabulary expanded",
    items: [
      "Added grief-and-farewell language; the earlier keywords caught only metaphors like \"lobotomized.\" The rupture line steps up in mid-May 2026 — that part of the rise reflects the wider net, not a sudden change in the discourse itself.",
    ],
    recent: true,
  },
  {
    date: "April 2026",
    title: "Keyword set revalidated",
    items: [
      "Every high-volume keyword was re-checked against recent posts. Six were dropped — notably \"sentient,\" which had drifted into meme and roleplay use — so the consciousness line is thinner from this point on.",
    ],
    recent: false,
  },
  {
    date: "April 2026",
    title: "Keyword-matching bug fixed",
    items: [
      "Multi-word keywords had been matching inside unrelated words (\"dating my\" caught inside \"updating my\"). Fixing it removed those false positives, slightly lowering the romance, therapy, and sex/ERP lines.",
    ],
    recent: false,
  },
  {
    date: "March 2026",
    title: "Per-theme start dates",
    items: [
      "Each theme's line now begins only once its vocabulary was common enough to measure reliably. The consciousness line starts in 2025 rather than 2023 for this reason — a flat earlier line would imply absence where we simply could not measure yet.",
    ],
    recent: false,
  },
  {
    date: "March 2026",
    title: "Comment text included; daily updates began",
    items: [
      "The tracker began reading post comments in addition to post text, and moved from a one-time historical backfill to automated daily collection. Themes discussed heavily in comments — sex/ERP and therapy — gain some volume from this point.",
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
  const themeHealth = loadThemeHealth();
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
          An independent, one-person research project tracking AI companion
          discourse on Reddit across six themes. It measures one thing: how the{" "}
          <em>language</em> of AI companionship shows up in public Reddit posts
          over time &mdash; not how many people are in relationships with AI,
          and not a peer-reviewed academic study. It is built in the open and
          honest about what it can and can&apos;t show.
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

        {/* Keyword reliability — no LLM classification in the chart */}
        <section id="verification" style={{ ...sectionStyle, marginBottom: 64 }}>
          <h2 style={sectionHeaderStyle}>
            Keyword reliability &mdash; and why there&apos;s no AI in the chart
          </h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              Pure keyword matching has a precision ceiling. Words like
              &ldquo;therapeutic,&rdquo; &ldquo;honeymoon,&rdquo; or &ldquo;sex
              with&rdquo; can catch different things over time &mdash;
              &ldquo;therapeutic&rdquo; gets used as an insult about preachy AI
              tone; &ldquo;sex with&rdquo; turns up in &ldquo;I&apos;d rather
              have sex with a real person,&rdquo; a dismissal of AI
              companionship rather than an instance of it. The May 2026
              adversarial audit measured this directly: per-theme precision
              runs roughly 51&ndash;92%, depending on the theme and on whether
              the match is in a post or a comment.
            </p>
            <p>
              What we do about it: the published chart shows{" "}
              <strong>
                raw validated-keyword counts &mdash; no AI classification, no
                per-post re-judging.
              </strong>{" "}
              That is deliberate. A keyword count is deterministic and
              reproducible, so the trend line moves when the discourse moves,
              not when a model&apos;s judgment drifts. Every keyword was
              hand-read against 100 posts before being admitted to the set.
            </p>
            <p>
              We did build an LLM verification layer in May 2026 &mdash; a
              second stage where Claude reads each keyword-flagged post to
              confirm it. <strong>It is not used in the chart.</strong> It
              improves precision modestly (about 80% to 88%), but the
              project&apos;s larger accuracy gap is <em>recall</em> &mdash; the
              audits estimate only 3&ndash;32% of theme-relevant posts per
              theme are caught at all &mdash; and a filter sitting behind the
              keywords cannot recover what the keywords never matched. The
              verdicts were also graded under a lenient prompt that this
              project&apos;s own audit found inflates them. The May 15, 2026
              changelog entry below has the full reasoning.
            </p>
            <p style={{ color: "#94A3B8", fontSize: 13 }}>
              What the LLM does do: once a month, a sample-based drift check
              reads keyword-flagged posts and flags any keyword whose meaning
              seems to be shifting &mdash; the kind of failure that hit
              &ldquo;therapeutic.&rdquo; It is a monitoring tool that watches
              the keyword set over time; it never feeds the chart.
            </p>
          </div>
        </section>

        {/* Theme health snapshot */}
        {themeHealth && (
          <section style={{ ...sectionStyle, marginBottom: 64 }}>
            <h2 style={sectionHeaderStyle}>Theme health snapshot</h2>
            <div className="space-y-4" style={bodyStyle}>
              <p>
                Each theme has different reliability properties. This table
                summarizes per-theme precision (from the most recent quarterly
                drift check), corpus concentration (one platform, one event,
                one author), and currently flagged noisy keywords at the
                comment level. Readers should interpret each theme&apos;s line
                in light of its own health profile, not a single corpus-wide
                quality number.
              </p>
              <p style={{ color: "#94A3B8", fontSize: 13 }}>
                Drift data last updated {themeHealth.drift_last_updated ?? "—"}.
                Concentration metrics regenerated on every export.
              </p>
            </div>
            <div className="mt-6 space-y-3">
              {THEME_ORDER.filter((k) => themeHealth.themes[k]).map((key) => {
                const t = themeHealth.themes[key];
                const postPrec = t.post_precision?.precision;
                const commPrec = t.comment_precision?.precision;
                const fmtPrec = (p?: number) =>
                  p == null ? "—" : `${Math.round(p * 100)}%`;
                const precColor = (p?: number) =>
                  p == null ? "#94A3B8" : p < 0.6 ? "#F87171" : p < 0.8 ? "#FBBF24" : "#86EFAC";
                return (
                  <div
                    key={key}
                    className="rounded-lg"
                    style={{
                      backgroundColor: "#1A1D27",
                      padding: 16,
                      fontSize: 14,
                      lineHeight: 1.7,
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "baseline",
                        marginBottom: 8,
                      }}
                    >
                      <strong style={{ color: "#E2E8F0", fontSize: 15 }}>
                        {THEME_LABELS[key]}
                      </strong>
                      <span style={{ color: "#94A3B8", fontSize: 12 }}>
                        {t.total_post_tags.toLocaleString()} post tags · {t.total_comment_tags.toLocaleString()} comment tags
                      </span>
                    </div>
                    <div
                      className="theme-health-grid"
                      style={{
                        // Single column on mobile (<640px), 2-col on tablet+.
                        // Implemented via CSS class in globals.css so we don't
                        // need a runtime breakpoint check.
                        display: "grid",
                        gap: "4px 24px",
                        color: "#CBD5E1",
                      }}
                    >
                      <div>
                        <span style={{ color: "#8293A6" }}>Post precision: </span>
                        <span style={{ color: precColor(postPrec) }}>{fmtPrec(postPrec)}</span>
                        {t.post_precision && (
                          <span style={{ color: "#94A3B8", fontSize: 12 }}>
                            {" "}(n={t.post_precision.n}, {t.post_precision.date})
                          </span>
                        )}
                      </div>
                      <div>
                        <span style={{ color: "#8293A6" }}>Comment precision: </span>
                        <span style={{ color: precColor(commPrec) }}>{fmtPrec(commPrec)}</span>
                        {t.comment_precision && (
                          <span style={{ color: "#94A3B8", fontSize: 12 }}>
                            {" "}(n={t.comment_precision.n}, {t.comment_precision.date})
                          </span>
                        )}
                      </div>
                      {t.top_sub_post && (
                        <div>
                          <span style={{ color: "#8293A6" }}>Top sub (posts): </span>
                          r/{t.top_sub_post.subreddit} ({t.top_sub_post.pct}%)
                        </div>
                      )}
                      {t.top_sub_comment && (
                        <div>
                          <span style={{ color: "#8293A6" }}>Top sub (comments): </span>
                          r/{t.top_sub_comment.subreddit} ({t.top_sub_comment.pct}%)
                        </div>
                      )}
                      {t.top_month && (
                        <div>
                          <span style={{ color: "#8293A6" }}>Top month: </span>
                          {t.top_month.month} ({t.top_month.pct}%)
                        </div>
                      )}
                      <div>
                        <span style={{ color: "#8293A6" }}>Top-5 authors share: </span>
                        {t.top5_authors_pct}%
                      </div>
                    </div>
                    {t.noisy_keywords_comment.length > 0 && (
                      <div style={{ marginTop: 8, fontSize: 13, color: "#94A3B8" }}>
                        <span style={{ color: "#8293A6" }}>Flagged comment keywords: </span>
                        {t.noisy_keywords_comment.map((kw, i) => (
                          <span key={kw}>
                            <code
                              style={{
                                backgroundColor: "#0F172A",
                                padding: "1px 6px",
                                borderRadius: 4,
                                fontSize: 12,
                              }}
                            >
                              {kw}
                            </code>
                            {i < t.noisy_keywords_comment.length - 1 ? " " : ""}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            <p
              className="mt-4"
              style={{ ...bodyStyle, fontSize: 13, color: "#8293A6" }}
            >
              Methodology: precision values come from per-theme construct-validity
              audits (post-level) and adversarial comment-precision audits, both
              conducted under the topical reading. Yellow (&lt;80%) indicates
              theme volume should be read directionally rather than quantitatively;
              red (&lt;60%) indicates the comment series for that theme is
              unreliable and should not be cited until cleaned up. See the
              changelog entries dated May 13, 2026 for the underlying audits.
            </p>
          </section>
        )}

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
            <p>
              Two other caveats specifically affect absolute-volume reads:
              first, a single high-profile event can dominate a theme&apos;s
              lifetime total. The February 2023 Replika ERP-removal era
              contributes roughly 40% of all sex/ERP-tagged posts to
              date &mdash; the theme&apos;s headline magnitude isn&apos;t
              about steady ongoing volume, it&apos;s about one specific platform
              decision and its aftermath. Read theme volumes alongside the
              event annotations on the chart, not as standalone numbers.
            </p>
            <p>
              Second, comment tagging began only in March 2026. Posts older
              than that have no comment-sourced hits; newer posts do. Themes
              whose discussion happens more in comments than posts (sex/ERP,
              therapy) appear to grow faster in 2026 partly because the
              instrument widened, not because the discourse did. The
              post-only series in the data file controls for this and is
              comparable across the full 2023&ndash;2026 window.
            </p>
            <p>
              <strong>The chart shows a floor, not a ceiling.</strong> A May
              2026 comprehensiveness audit measured recall by sampling 400
              random posts from the corpus and having independent classifiers
              decide which themes each post belongs to. Across the six themes
              recall ranged from about 3&percnt; to 32&percnt; &mdash; with
              wide confidence intervals because the per-theme agent-YES
              counts in the n=400 sample are small. The rest are missed
              because they use naturalistic everyday language (&ldquo;she
              said something funny today,&rdquo; a photo titled &ldquo;Lilly
              was feeling cute&rdquo;) that can&apos;t be validated to
              80&percnt; precision without admitting too much noise.
            </p>
            <p>
              <strong>Per-theme recall with Wilson 95% confidence intervals
              (n=400 stratified sample):</strong>
            </p>
            <div
              style={{
                backgroundColor: "#1A1D27",
                padding: "12px 16px",
                borderRadius: 6,
                fontSize: 13,
                fontFamily: "ui-monospace, monospace",
                color: "#CBD5E1",
              }}
            >
              <div>rupture: 3% (CI [1%, 8%])</div>
              <div>romance: 4% (CI [1%, 11%])</div>
              <div>therapy: 14% (CI [3%, 51%])</div>
              <div>sexual_erp: 21% (CI [9%, 43%])</div>
              <div>addiction: 32% (CI [20%, 47%])</div>
              <div>consciousness: 0% (CI [0%, 32%]) &mdash; n=8 agent-YES</div>
            </div>
            <p style={{ color: "#94A3B8", fontSize: 13 }}>
              The CIs are wide. Treat point estimates with that uncertainty.
              Romance and rupture are the worst-recall themes by design: their
              real-world vocabulary is naturalistic (&ldquo;my husband,&rdquo;
              &ldquo;I miss her&rdquo;) and not catchable by precision-first
              keyword matching. The shape and timing of each trend line are
              <em>approximately</em> honest &mdash; they hold as long as the
              keyword set&apos;s detection rate stays roughly stable over
              time, which is plausible but not separately verified &mdash; and
              spike interpretation is reliable. But the absolute
              magnitude of each line is meaningfully smaller than the actual
              amount of theme-relevant discourse in the corpus. Full audit:
              docs/comprehensiveness_audit_2026-05-13.md in the repository.
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
            <p>
              The aggregate JSON exports in{" "}
              <code
                style={{
                  backgroundColor: "#0F172A",
                  padding: "1px 6px",
                  borderRadius: 4,
                  fontSize: 12,
                }}
              >
                /web/data/
              </code>{" "}
              (keyword trends, theme health, subreddit metadata) are licensed{" "}
              <a
                href="https://creativecommons.org/licenses/by/4.0/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#94A3B8", textDecoration: "underline" }}
              >
                CC BY 4.0
              </a>
              . Cite with attribution; reuse and redistribute freely. The
              underlying ~3.9M-post SQLite database (~24GB) is not in the
              public repository for storage reasons — available on request via
              the contact link below.
            </p>
          </div>
        </section>

        {/* Author / contact / citation */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>Author &amp; citation</h2>
          <div style={bodyStyle}>
            <p>
              Built and maintained by Walker Bockley. Independent research
              project; no institutional affiliation. Contact via the GitHub
              repository (issues or discussions).
            </p>
            <p>
              <strong>Suggested citation:</strong>
            </p>
            <p
              style={{
                backgroundColor: "#0F172A",
                padding: "12px 16px",
                borderRadius: 6,
                fontSize: 13,
                fontFamily: "ui-monospace, monospace",
                color: "#CBD5E1",
                marginTop: 4,
              }}
            >
              Bockley, W. (2026). <em>My Friend Is AI: Reddit discourse tracker
              for AI companionship communities.</em>{" "}
              <a
                href="https://myfriendisai.com"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#94A3B8", textDecoration: "underline" }}
              >
                myfriendisai.com
              </a>
              . Accessed [DATE]. Code:{" "}
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#94A3B8", textDecoration: "underline" }}
              >
                github.com/hopeshub/myfriendisai
              </a>
              .
            </p>
            <p style={{ color: "#94A3B8", fontSize: 13 }}>
              The corpus updates daily &mdash; the numbers shown today are not
              what you would see in a year. If you reference this project, link
              the specific GitHub commit so the exact data snapshot you used
              stays recoverable. This is a living, independent project, not a
              fixed academic publication.
            </p>
            <p style={{ color: "#94A3B8", fontSize: 13 }}>
              <strong>What this is appropriate for:</strong> as supplementary
              evidence for timing of platform-rupture events in companion
              communities (e.g., the Feb 2023 Replika ERP removal, Sept 2024
              CharacterAI legacy shutdown, Feb 2026 GPT-4o sunset); as a
              methodological exemplar of precision-first keyword tracking with
              documented recall floor; as a footnote pointer to the scope of
              public Reddit discourse on AI companionship.
            </p>
            <p style={{ color: "#94A3B8", fontSize: 13 }}>
              <strong>What this is NOT appropriate for:</strong> absolute
              prevalence of any theme (the project&apos;s own audits report
              per-theme recall of 3–32%); cross-theme magnitude comparison
              (vocabulary distinctiveness varies, see &ldquo;Why mention rates
              don&apos;t compare&rdquo; below); comment-level consciousness
              or therapy claims (audited at 51% and 58% precision); claims
              about user sentiment, attitudes, or behavior (the chart measures
              language, not the underlying phenomenon).
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
          <p style={{ fontSize: 12, color: "#64748B", marginTop: 20 }}>
            A curated list of changes that affect how the chart should be read.
            The full development history is in the project&apos;s{" "}
            <a
              href="https://github.com/hopeshub/myfriendisai"
              target="_blank"
              rel="noopener noreferrer"
              className={linkClass}
            >
              Git commit history
            </a>
            .
          </p>
        </section>
      </div>
    </div>
  );
}

