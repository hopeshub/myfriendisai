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
                { emoji: "\u{1F51E}", label: "Sex / ERP", tagline: "Language of sexual and erotic roleplay", color: "#dc2625" },
                { emoji: "\u{1F9E0}", label: "Consciousness", tagline: "Language of sentience, awareness, and inner experience", color: "#A855F7" },
                { emoji: "\u{1FAC2}", label: "Therapy", tagline: "Language of mental health support and emotional care", color: "#3B82F6" },
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
              PullPush and Arctic Shift Reddit archives. Beginning March 13,
              2026, posts are collected daily via Reddit&apos;s API. The data
              format and processing pipeline are identical regardless of source.
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

