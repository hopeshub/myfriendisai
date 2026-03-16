import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About — My Friend Is AI",
  description:
    "Methodology, data sources, and changelog for the AI companionship community tracker.",
};

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
  },
  {
    date: "March 13, 2026",
    title: "Live daily collection begins",
    items: [
      "Automated daily collection via launchd (local) replacing backfill pipeline",
      "27 active subreddits collected daily at 6:00 AM PT",
    ],
  },
  {
    date: "March 2026",
    title: "Subreddit corpus finalized at 27 active communities",
    items: [
      "Expanded from 19 to 29 communities, then deactivated 2 (JanitorAI_Official, SillyTavernAI excluded from keyword matching due to bot-card pollution)",
      "Tier structure: 4 general AI (T0), 6 primary companionship (T1), 11 platform-specific (T2), 6 recovery/dependency (T3)",
    ],
  },
];

export default function About() {
  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
      <h1 className="text-2xl sm:text-3xl font-bold text-foreground mb-8">
        About
      </h1>

      <div className="space-y-10">
        {/* How this works */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-foreground">
            How this works
          </h2>
          <p className="text-sm sm:text-base leading-relaxed text-muted">
            We track 27 Reddit communities where people discuss AI companions
            &mdash; from large platforms like r/CharacterAI and r/replika to
            recovery communities like r/ChatbotAddiction. Our corpus spans
            January 2023 to present and contains over 3.7 million posts.
          </p>
          <p className="text-sm sm:text-base leading-relaxed text-muted">
            For each of the six themes, we maintain a curated list of keywords
            and phrases &mdash; terms like &ldquo;lobotomized,&rdquo;
            &ldquo;chatbot addiction,&rdquo; &ldquo;emotional support,&rdquo;
            &ldquo;sentient.&rdquo; Every keyword went through a validation
            process: we sampled up to 100 posts matching each term, classified
            whether the match genuinely reflected the theme in context, and
            required at least 80% precision before including it. Keywords that
            didn&apos;t clear that threshold were cut, regardless of volume. The
            full keyword list and precision scores are published in our{" "}
            <a
              href="https://github.com/hopeshub/myfriendisai"
              target="_blank"
              rel="noopener noreferrer"
              className="text-foreground underline underline-offset-2 hover:text-primary transition-colors"
            >
              GitHub repository
            </a>
            .
          </p>
          <p className="text-sm sm:text-base leading-relaxed text-muted">
            The chart shows how often these validated terms appear per 1,000
            posts, using a 7-day rolling average to smooth daily noise. Because
            we normalize to post volume, the trends reflect changes in how
            people talk &mdash; not just growth in the communities themselves.
          </p>
        </section>

        {/* What this captures */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-foreground">
            What this captures and what it doesn&apos;t
          </h2>
          <p className="text-sm sm:text-base leading-relaxed text-muted">
            This is a frequency tracker, not a sentiment analyzer. When the
            addiction line rises, it means more people are using
            addiction-related language &mdash; not that more people are addicted.
            The signal is intentionally narrow: we trade coverage for precision,
            preferring to undercount rather than pollute the data. Some themes
            are measured by just a handful of highly specific terms. Every data
            point traces back to a validated keyword in a real post.
          </p>
        </section>

        {/* Data collection */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-foreground">
            Data collection
          </h2>
          <p className="text-sm sm:text-base leading-relaxed text-muted">
            Data from January 2023 through March 12, 2026 was backfilled from
            PullPush and Arctic Shift Reddit archives. Beginning March 13, 2026,
            posts are collected daily via Reddit&apos;s API. The data format and
            processing pipeline are identical regardless of source.
          </p>
        </section>

        {/* Ongoing updates */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-foreground">
            Ongoing updates
          </h2>
          <p className="text-sm sm:text-base leading-relaxed text-muted">
            This project evolves as the space does. New themes, subreddits, and
            keywords are validated and added using the same process described
            above. Every change is logged in the changelog below, and the full
            validation records, keyword lists, and decision rationale are
            available in the{" "}
            <a
              href="https://github.com/hopeshub/myfriendisai"
              target="_blank"
              rel="noopener noreferrer"
              className="text-foreground underline underline-offset-2 hover:text-primary transition-colors"
            >
              GitHub repository
            </a>
            .
          </p>
        </section>

        {/* Changelog */}
        <section>
          <h2 className="text-lg font-semibold text-foreground mb-6">
            Changelog
          </h2>
          <div className="space-y-4">
            {CHANGELOG.map((entry, i) => (
              <div
                key={i}
                className="rounded-lg pl-4 pr-4 py-4"
                style={{
                  borderLeft: "3px solid #2A2D3A",
                  backgroundColor: "#13151D",
                }}
              >
                <div className="flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-3 mb-2">
                  <span
                    className="text-xs font-medium whitespace-nowrap"
                    style={{ color: "#94A3B8" }}
                  >
                    {entry.date}
                  </span>
                  <span className="text-sm font-medium text-foreground">
                    {entry.title}
                  </span>
                </div>
                <ul className="space-y-1">
                  {entry.items.map((item, j) => (
                    <li
                      key={j}
                      className="text-xs sm:text-sm leading-relaxed text-muted pl-3"
                      style={{ listStyleType: "none" }}
                    >
                      <span style={{ color: "#2A2D3A" }} className="mr-2">
                        &bull;
                      </span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
