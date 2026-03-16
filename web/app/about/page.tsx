import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About — My Friend Is AI",
  description:
    "Methodology, data sources, and changelog for the AI companionship community tracker.",
};

const STATS = [
  { value: "3.7M", label: "posts in corpus" },
  { value: "27", label: "tracked communities" },
  { value: "80%", label: "minimum precision threshold" },
];

const CHANGELOG = [
  {
    date: "March 15, 2026",
    title: "Keyword expansion (discovery batch)",
    items: [
      "Added 16 validated keywords across all 6 themes via co-occurrence analysis",
      "Addiction: chatbot addiction, almost relapsed, finally deleted, the craving, so addictive",
      "Consciousness: sapience, tulpa, lemoine, soulbonder",
      "Sexual/ERP: erps, erping",
      "Rupture: lobotomies, lobotomizing, lobotomised",
      "Therapy: emotional support, coping mechanism",
      "All keywords validated at \u226580% precision",
    ],
    recent: true,
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
    recent: true,
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
      "Tier structure: 4 general AI (T0), 6 primary companionship (T1), 11 platform-specific (T2), 6 recovery/dependency (T3)",
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
  color: "#64748B",
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
            color: "#64748B",
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
          A longitudinal research tracker documenting AI companionship discourse
          on Reddit.
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
              We track 27 Reddit communities where people discuss AI companions
              &mdash; from large platforms like r/CharacterAI and r/replika to
              recovery communities like r/ChatbotAddiction. Our corpus spans
              January 2023 to present and contains over 3.7 million posts.
            </p>
            <p>
              For each of the six themes, we maintain a curated list of keywords
              and phrases &mdash; terms like &ldquo;lobotomized,&rdquo;
              &ldquo;chatbot addiction,&rdquo; &ldquo;emotional support,&rdquo;
              &ldquo;sentient.&rdquo; Every keyword went through a validation
              process: we sampled up to 100 posts matching each term, classified
              whether the match genuinely reflected the theme in context, and
              required at least 80% precision before including it. Keywords that
              didn&apos;t clear that threshold were cut, regardless of volume.
              The full keyword list and precision scores are published in our{" "}
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
              The chart shows how often these validated terms appear per 1,000
              posts, using a 7-day rolling average to smooth daily noise. Because
              we normalize to post volume, the trends reflect changes in how
              people talk &mdash; not just growth in the communities themselves.
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
