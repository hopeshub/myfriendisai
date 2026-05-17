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
    title: "Theme accuracy re-checked",
    items: [
      "Re-checked that keywords land on the theme they claim — about 1,800 tagged posts re-read by independent classifiers, then a sample re-coded by hand. Keywords reliably identify AI-companion discourse; sorting it into the right theme is tightest for sex/ERP and addiction, and holds up better for therapy and consciousness than a first, classifier-only pass had suggested. The re-check also confirmed that therapy and addiction are largely one subject — the same reliance on an AI, framed once as help and once as a problem. No keywords changed: the response to a fast-moving vocabulary is disclosure, not constant edits.",
    ],
    recent: true,
  },
  {
    date: "May 2026",
    title: "Post corpus extended back to 2017",
    items: [
      "The post corpus was backfilled from public archives back to 2017. In practice this moved the earliest theme lines from a 2023 start back a few months, into late 2022 — as far back as monthly volume stays reliable enough to chart. The 2017–2021 years exist in the corpus but are too sparse to draw as theme lines, so the early-Replika era is not itself visible on the chart.",
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
          Tracking how AI-companion communities talk
        </h1>
        <p style={{ fontSize: 16, color: "#94A3B8", lineHeight: 1.7 }}>
          This project follows six recurring themes in Reddit&apos;s
          AI-companion communities &mdash; romance, addiction, grief, and three
          others &mdash; and measures how often each one surfaces in posts. The
          post corpus reaches back to 2017, though the theme lines themselves
          begin in 2022&ndash;2023, where monthly volume becomes reliable enough
          to chart. What it captures is the conversation itself: when
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
              The six themes are a deliberate choice, not a neutral census of
              everything these communities discuss. They came out of reading
              the communities closely &mdash; but they reflect a particular
              focus: the parts of life with an AI companion that carry real
              weight, like intimacy, belief, dependence, and loss. There is no
              &ldquo;fun,&rdquo; &ldquo;creativity,&rdquo; or &ldquo;everyday
              utility&rdquo; theme here, and that absence is a choice, not an
              oversight. This is the lens the project looks through; the list
              below is what it was pointed at:
            </p>
            <ul
              className="space-y-2"
              style={{ listStyleType: "none", padding: 0 }}
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
              gain in accuracy.
            </p>
            <p>
              And the gain really is small. I tested it: having an LLM re-check
              each keyword match raised precision from roughly 80% to 88%, while
              doing nothing for the posts the keywords never matched in the
              first place. So the method stays plain on purpose. The careful
              work happens earlier, in validating each keyword by hand before it
              is ever allowed to count.
            </p>
          </div>
        </section>

        {/* Which communities */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>
            Which communities &mdash; and why only these
          </h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              AI companionship comes up across far more of Reddit than the
              communities tracked here. The project tracks a curated set
              anyway, because of a problem that showed up early. In a large
              general subreddit like r/ChatGPT, the keywords cannot tell two
              things apart: &ldquo;my boyfriend is using ChatGPT&rdquo; and
              &ldquo;my boyfriend <em>is</em> an AI&rdquo; are built from the
              same words. Run a romance keyword across r/ChatGPT and most of
              what it catches is ordinary human-relationship talk that merely
              mentions AI.
            </p>
            <p>
              The fix isn&apos;t a smarter keyword &mdash; it&apos;s the room.
              In a community like r/replika, &ldquo;my boyfriend&rdquo; almost
              always means the AI, because that is what the community is
              about. The subreddit does the disambiguating the keyword cannot.
              The keywords are the lens; the curated community list keeps that
              lens pointed where the words mean what they appear to mean. It is
              also why the large general-AI subreddits are tracked for size and
              activity but kept out of the theme lines.
            </p>
            <p>
              An AI model reading each post could make that call directly
              &mdash; it could tell the two boyfriends apart where a keyword
              cannot. But running one across the millions of posts in the large
              general subreddits would be expensive, and for a one-person
              project that is out of scope. So the room does that work instead.
            </p>
            <p>
              This is a real choice, and it shapes what the site can see.
              These communities &mdash; the committed core of AI companionship
              on Reddit &mdash; lean toward people for whom it is central and
              often intense, including recovery communities for people trying
              to quit. That makes the site good at catching
              that end of the spectrum and blind to casual mentions elsewhere.
              The trends describe <em>this curated set of communities</em>{" "}
              &mdash; not Reddit as a whole, and not &ldquo;people&rdquo; in
              general.
            </p>
            <p>
              Within that curated set, each theme is also concentrated. Two or
              three subreddits usually account for most of a theme&apos;s posts
              &mdash; and the sexual-content line is about half r/replika alone.
              A theme line is often, in practice, a close reading of a few
              communities rather than an even sweep across all of them.
            </p>
          </div>
        </section>

        {/* A moving target */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>A moving target</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              Most things you measure hold still while you measure them. This
              subject does not &mdash; and that churn turned out to be one of
              the project&apos;s clearest findings, not an obstacle to it.
            </p>
            <p>
              The vocabulary moves fast. &ldquo;Sentient&rdquo; was once the
              natural anchor word for the consciousness theme, until it spread
              into roleplay and Character.AI memes and stopped marking genuine
              belief, so I dropped it. &ldquo;Therapeutic&rdquo; turned, over a
              few months, from a word for real support into an insult aimed at
              preachy AI. Every model release and content-policy change sends a
              fresh wave of language through these communities &mdash; Replika
              removing erotic roleplay in 2023, OpenAI retiring its 4o model in
              2026. A keyword that reads cleanly in January can be noise by
              April. The communities move too: some are private or invite-only
              and can&apos;t be tracked at all, and the set worth watching keeps
              changing.
            </p>
            <p>
              So the instrument can&apos;t sit still either. The keyword set has
              been through several full revisions, and the monthly re-check
              exists because I learned firsthand that a validated keyword is
              only validated for now.
            </p>
            <p style={leadStyle}>
              None of this is a flaw being patched out. It is the nature of a
              fast-moving subject &mdash; and keeping the measurement honest
              means keeping it in motion.
            </p>
          </div>
        </section>

        {/* Reading it honestly */}
        <section id="verification" style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>How to read the lines</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              A line is a useful signal, but a narrow one. Four limits are
              worth holding in mind before you read too much into any single
              one.
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
                Read direction and timing, not height.
              </strong>{" "}
              Three things make the <em>height</em> of a line untrustworthy
              even where its <em>shape</em> holds. Each theme is caught through
              its own vocabulary, and some vocabularies match more easily
              &mdash; addiction&apos;s recovery words (&ldquo;relapse,&rdquo;
              &ldquo;cold turkey&rdquo;) catch cleanly, while romance lives in
              ordinary language (&ldquo;I love him,&rdquo; &ldquo;my
              boyfriend&rdquo;) that mostly slips past &mdash; so one line can
              sit above another even when the second theme is the larger one.
              The high precision bar also leaves the keyword set deliberately
              incomplete: in a hand-coded sample of 400 random posts, it caught
              between a few percent and about a third of the posts that
              genuinely belonged, depending on the theme. And it is weakest
              exactly where the subject is most itself &mdash; someone writing
              &ldquo;I love him&rdquo; about an AI in the same ordinary words
              they would use for a person is the hardest case of all to catch.
              So every line is a floor, not a ceiling: it runs low, it cannot be
              measured against its neighbours, and only its direction, timing,
              and spikes can be trusted. That incompleteness is a trade made on
              purpose &mdash; a missed post only weakens a line, while a false
              one corrupts it, so the method errs toward missing.
            </p>
            <p>
              <strong style={leadStyle}>
                Therapy and addiction are two readings of one behavior.
              </strong>{" "}
              Both lines track the same act &mdash; leaning on an AI to get
              through something hard &mdash; and what divides them is only how
              the writer frames it. &ldquo;It&apos;s my coping mechanism&rdquo;
              and &ldquo;I can&apos;t stop&rdquo; are the same use seen in two
              lights. So the two lines share many of the same posts, by design;
              a therapy post that looks like it belongs under addiction usually
              belongs under both. Read them as a linked pair, and watch which
              way the balance tips.
            </p>
            <p>
              <strong style={leadStyle}>
                The set of communities grew over time.
              </strong>{" "}
              In the early years almost every tracked community was a primary
              companionship subreddit. Platform-specific and recovery
              communities were smaller then, or did not exist yet, and have
              grown since. Each line is measured against whatever communities
              existed at the time &mdash; so part of a long climb reflects the
              tracked world widening, not only the conversation itself. Trust
              the broad direction of a line more than its exact path.
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
              onward, they are collected fresh from Reddit every day. One caveat
              comes with the older years: the further back a post goes, the more
              likely its text was removed or deleted before the archive captured
              it &mdash; so there is simply less wording for the keywords to
              match in the early years than in the recent ones. Every line
              therefore runs a little lower at its start than the discourse
              really was, which makes each rise look somewhat steeper than it
              was. The shape and the timing of events are sound; the steepness
              of the long climb is partly the instrument warming up, not only
              the subject growing.
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
              on request &mdash; reach me on X at{" "}
              <a
                href="https://x.com/hopes_revenge"
                target="_blank"
                rel="noopener noreferrer"
                className={linkClass}
              >
                @hopes_revenge
              </a>
              , the project&apos;s only point of contact.
            </p>
          </div>
        </section>

        {/* Changelog */}
        <section>
          <h2 style={{ ...sectionHeaderStyle, paddingLeft: 24 }}>Changelog</h2>
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
                        <span style={{ color: "#64748B" }} className="mr-1.5">
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
          <p
            style={{
              fontSize: 12,
              color: "#64748B",
              marginTop: 20,
              paddingLeft: 24,
            }}
          >
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
