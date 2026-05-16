import type { Metadata } from "next";
import { readFileSync } from "fs";
import { join } from "path";
import { THEMES } from "../themes";

export const metadata: Metadata = {
  title: "About — My Friend Is AI",
  description:
    "How this project tracks AI-companionship discourse on Reddit: the method, its honest limits, the data, and a changelog.",
  openGraph: {
    title: "About — My Friend Is AI",
    description:
      "How this project tracks AI-companionship discourse on Reddit — the method, its honest limits, and the data behind it.",
  },
};

function getPostCount(): string {
  try {
    const raw = readFileSync(join(process.cwd(), "data", "site_meta.json"), "utf-8");
    const meta = JSON.parse(raw) as { total_posts: number };
    return `~${(meta.total_posts / 1_000_000).toFixed(1)}M`;
  } catch {
    return "~4.0M";
  }
}

function getCommunityCount(): number {
  try {
    const raw = readFileSync(join(process.cwd(), "data", "subreddits.json"), "utf-8");
    const list = JSON.parse(raw) as Array<{ subreddit: string }>;
    return new Set(list.map((s) => s.subreddit)).size;
  } catch {
    return 26;
  }
}

// Changelog: a curated list of changes that affect how the chart should be
// read — not the full development history (that's the Git log).
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
      "Each theme's line now begins only once its vocabulary was common enough to measure reliably. The consciousness line starts in 2025 rather than 2023 for this reason — a flat earlier line would imply absence where I simply couldn't measure it yet.",
    ],
    recent: false,
  },
  {
    date: "March 2026",
    title: "Daily collection began",
    items: [
      "The project moved from a one-time historical backfill to collecting posts fresh from Reddit every day. Comments were collected and keyword-tagged from this point on as well, but the published chart counts post text only — so this change adds no volume to any line.",
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

const leadStyle: React.CSSProperties = { color: "#E2E8F0", fontWeight: 600 };

export default function About() {
  const stats = [
    { value: getPostCount(), label: "posts analyzed" },
    { value: String(getCommunityCount()), label: "communities tracked" },
    { value: String(THEMES.length), label: "recurring themes" },
  ];

  return (
    <div style={{ maxWidth: 720 }} className="mx-auto px-4 sm:px-6 py-10 sm:py-16">
      {/* Header */}
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
        <p style={{ fontSize: 16, color: "#94A3B8", lineHeight: 1.7 }}>
          This project follows six recurring themes in Reddit&apos;s
          AI-companion communities &mdash; romance, addiction, grief, and three
          others &mdash; and measures how often each one surfaces in posts,
          going back to 2017. What it captures is the conversation itself: when
          a line rises, people are writing about that theme more often. Whether
          the underlying experience has actually become more common is a
          separate question, and one this can&apos;t answer on its own.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-2 sm:gap-3 mb-12">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-lg"
            style={{ backgroundColor: "#1A1D27", padding: "12px 10px" }}
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
        {/* How it works */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>How it works</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              The six themes weren&apos;t decided in advance. They emerged from
              reading these communities directly and noticing which worries,
              experiences, and turns of phrase kept coming back:
            </p>
            <ul
              className="space-y-2"
              style={{ listStyleType: "none", padding: 0, margin: 0 }}
            >
              {THEMES.map((t) => (
                <li key={t.id} style={{ fontSize: 15, lineHeight: 1.6 }}>
                  <span aria-hidden>{t.emoji}</span>{" "}
                  <span style={{ color: t.color, fontWeight: 500 }}>
                    {t.label}
                  </span>
                  <span style={{ color: "#94A3B8" }}> &mdash; {t.tagline}</span>
                </li>
              ))}
            </ul>
            <p>
              Each theme is then defined by a set of keywords, and every keyword
              has to earn its place. For a candidate, I pull 100 real posts it
              matched and read them; the keyword stays only if those posts are
              genuinely about the theme. If it is matching on a coincidental
              shared word, it gets dropped. Language also drifts over time:
              &ldquo;therapeutic,&rdquo; for one, has lately been turning up as
              an insult aimed at preachy AI rather than a description of real
              support. So once a month I re-sample recent matches and re-check
              any keyword whose meaning may have moved.
            </p>
            <p>
              The chart shows how many posts use each theme&apos;s keywords,
              expressed as a rate per 1,000 posts and smoothed with a 7-day
              average. The rate matters more than a raw count would here. These
              communities have grown enormously since 2017, so a raw count would
              mostly retrace that growth; a rate sets the growth aside and shows
              how the conversation itself is shifting.
            </p>
            <p>
              There is an obvious objection here: why count keywords when a
              language model could read every post and classify it directly?
              The reason is that I wanted a measurement that stays put. A
              keyword count is fully transparent &mdash; every point on every
              line traces back to specific words in specific posts, and anyone
              can open those posts and check for themselves. It is also
              reproducible: the same posts always yield the same number, so a
              line moves when the discourse moves, not because a model was
              retrained or quietly changed its mind. For a record meant to hold
              up over years, that steadiness is worth more to me than a small
              gain in accuracy. And the gain really is small. I tested it:
              having an LLM re-check each keyword match raised precision from
              roughly 80% to 88%, while doing nothing for the posts the keywords
              never matched in the first place. So the method stays plain on
              purpose. The careful work happens earlier, in validating each
              keyword by hand before it is ever allowed to count.
            </p>
          </div>
        </section>

        {/* Reading it honestly */}
        <section id="verification" style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>How to read the lines</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              Three limits are worth holding in mind before you read too much
              into any single line.
            </p>
            <p>
              <strong style={leadStyle}>
                It counts language, not people or feelings.
              </strong>{" "}
              A rising addiction line means addiction-related language is
              showing up more often. It does not establish that more people are
              addicted, and it says nothing about whether they feel good or bad
              about their use. The site tracks how often a subject comes up, and
              only that.
            </p>
            <p>
              <strong style={leadStyle}>
                Don&apos;t compare one theme&apos;s height against another.
              </strong>{" "}
              Each theme is detected through its own vocabulary, and some
              vocabularies are simply easier to catch. Addiction has a
              distinctive recovery vocabulary &mdash; &ldquo;relapse,&rdquo;
              &ldquo;cold turkey&rdquo; &mdash; that matches cleanly. Romance
              lives in ordinary language like &ldquo;I love him&rdquo; or
              &ldquo;my boyfriend,&rdquo; nearly inseparable from everyday
              relationship talk, so only a handful of phrases survive
              validation. That asymmetry alone can lift the addiction line above
              the romance line even when romance is the larger subject. Each
              line can be trusted against its own past; the distance between two
              lines cannot.
            </p>
            <p>
              <strong style={leadStyle}>
                Each line is a floor, not a ceiling.
              </strong>{" "}
              Holding keywords to a high precision bar leaves the set
              deliberately incomplete, and I measured the cost. In a hand-coded
              sample of 400 random posts, the keywords caught somewhere between a
              few percent and about a third of the posts that genuinely
              belonged, depending on the theme. A trend&apos;s shape and timing
              can still be trusted; its absolute height cannot, and it always
              runs low. That is a trade I made on purpose: a missed post only
              weakens a line, while a false one corrupts it, so the method errs
              toward missing.
            </p>
          </div>
        </section>

        {/* Data & code */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>Data &amp; code</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              Posts from 2017 through early 2026 were backfilled from public
              Reddit archives (PullPush and Arctic Shift). From March 2026
              onward, they are collected fresh from Reddit every day. Both
              sources share the same format, so the two stretches join without a
              seam.
            </p>
            <p>
              The code, the keyword lists, and every validation record are
              public on{" "}
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className={linkClass}
              >
                GitHub
              </a>
              , along with the processed data files. The full post database
              (~24&nbsp;GB) is too large to host there, but I&apos;ll share it
              on request.
            </p>
          </div>
        </section>

        {/* Changelog */}
        <section>
          <h2 style={sectionHeaderStyle}>Changelog</h2>
          <div className="relative" style={{ paddingLeft: 24 }}>
            <div
              className="absolute top-0 bottom-0"
              style={{ left: 5, width: 1, backgroundColor: "#1E293B" }}
            />
            <div className="space-y-6">
              {CHANGELOG.map((entry, i) => (
                <div key={i} className="relative">
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
                  <div style={{ fontSize: 12, color: "#F59E0B", marginBottom: 2 }}>
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
            Changes that affect how the chart should be read. The full
            development history is in the project&apos;s{" "}
            <a
              href="https://github.com/hopeshub/myfriendisai"
              target="_blank"
              rel="noopener noreferrer"
              className={linkClass}
            >
              Git commit log
            </a>
            .
          </p>
        </section>
      </div>
    </div>
  );
}
