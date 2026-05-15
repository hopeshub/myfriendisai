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
          I track six recurring themes in AI-companion communities on Reddit
          &mdash; romance, addiction, grief, and a few more &mdash; and how
          often each comes up in posts, going back to 2017. It measures the
          conversation, not the reality behind it: how often a theme is talked
          about, not how common it actually is.
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
              The six themes come from reading these communities directly
              &mdash; the worries, experiences, and turns of phrase that surface
              again and again:
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
              For each theme I gather candidate keywords, then check every one
              by hand. I pull 100 real posts a keyword matched, read them, and
              keep the keyword only if it genuinely marks the theme &mdash; not
              if it just happens to share a word. Keywords that don&apos;t hold
              up get dropped. And because language drifts &mdash;
              &ldquo;therapeutic&rdquo; started showing up as an insult about
              preachy AI &mdash; I re-check the set over time, not just once.
            </p>
            <p>
              The chart shows how often the surviving keywords appear, as a rate
              per 1,000 posts, smoothed with a 7-day average. Measuring a rate
              rather than a raw count means the lines reflect how the
              conversation itself changes &mdash; not just how fast the
              communities grow.
            </p>
          </div>
        </section>

        {/* Reading it honestly */}
        <section id="verification" style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>Reading it honestly</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              A few limits worth knowing before you read too much into any
              single line.
            </p>
            <p>
              <strong style={leadStyle}>
                It counts language, not people or feelings.
              </strong>{" "}
              When the addiction line rises, more people are using
              addiction-related language &mdash; not necessarily that more
              people are addicted, and nothing about whether they feel good or
              bad about it. This is a frequency tracker.
            </p>
            <p>
              <strong style={leadStyle}>
                Don&apos;t compare heights between themes.
              </strong>{" "}
              Each theme has its own vocabulary. Addiction borrows distinctive
              recovery words &mdash; &ldquo;relapse,&rdquo; &ldquo;cold
              turkey&rdquo; &mdash; that are easy to catch cleanly. Romance
              hides in everyday language &mdash; &ldquo;I love him,&rdquo;
              &ldquo;my boyfriend&rdquo; &mdash; barely separable from ordinary
              relationship talk, so only a few specific phrases survive
              validation. Addiction&apos;s line can sit higher than
              romance&apos;s without romance being any smaller. Follow each
              line&apos;s own shape over time; don&apos;t rank the themes by
              height.
            </p>
            <p>
              <strong style={leadStyle}>
                Each line is a floor, not a ceiling.
              </strong>{" "}
              Keeping only high-precision keywords means missing a lot. I
              measured how much by hand-sampling 400 random posts: depending on
              the theme, the keywords catch only a few percent to about a third
              of the posts that genuinely belong. So a trend&apos;s shape and
              timing are honest, but its absolute height is an undercount
              &mdash; I&apos;d rather miss real posts than let in false ones.
            </p>
            <p>
              <strong style={leadStyle}>
                No AI scores the posts &mdash; though I tried.
              </strong>{" "}
              The chart is a plain keyword count; nothing re-reads each post to
              judge whether it &ldquo;really&rdquo; counts. I did build that
              &mdash; an extra layer where an LLM re-checks every match &mdash;
              and measured it. It lifted precision a little (roughly 80% to
              88%), but it couldn&apos;t close the bigger gap: the keywords
              miss a lot to begin with, and a filter sitting behind them
              can&apos;t recover what they never caught. So I left it out. The
              plain count has its own advantage anyway &mdash; it&apos;s
              reproducible, so a line moves when the conversation moves, not
              when a model&apos;s judgment drifts.
            </p>
          </div>
        </section>

        {/* Data & code */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>Data &amp; code</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              Posts from 2017 through early 2026 were backfilled from public
              Reddit archives &mdash; PullPush and Arctic Shift. From March 2026
              on, they are collected fresh from Reddit every day. The format is
              the same either way.
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
              . The processed data files are there too; the full post database
              (~24&nbsp;GB) is available on request.
            </p>
          </div>
        </section>

        {/* Who made this */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>Who made this</h2>
          <div style={bodyStyle}>
            <p>
              I&apos;m Walker Bockley &mdash; I built this and I keep it
              running. If you spot a mistake or have a question, opening an
              issue on{" "}
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className={linkClass}
              >
                GitHub
              </a>{" "}
              is the best way to reach me.
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
