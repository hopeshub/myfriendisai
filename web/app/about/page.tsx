import type { Metadata } from "next";
import { readFileSync } from "fs";
import { join } from "path";
import { THEMES } from "../themes";
import {
  fontSize,
  sectionEyebrow,
  sectionHeading,
  introParagraph,
  bodyParagraph,
} from "../styles";
import { CHANGELOG } from "../changelog";

const ABOUT_DESCRIPTION =
  "How this project tracks AI-companionship discourse on Reddit — the method, its honest limits, and the data behind it.";

export const metadata: Metadata = {
  title: "About",
  description:
    "How this project tracks AI-companionship discourse on Reddit: the keyword method, its honest limits, the data sources, and a changelog of method changes.",
  alternates: { canonical: "/about" },
  openGraph: {
    title: "About — My Friend Is AI",
    description: ABOUT_DESCRIPTION,
  },
  twitter: {
    title: "About — My Friend Is AI",
    description: ABOUT_DESCRIPTION,
  },
};

function getPostCount(): string {
  // If site_meta.json is unreadable, render "—" rather than a hardcoded
  // number — a stale fallback would silently misstate the corpus size,
  // and the about page is exactly where readers go to verify it.
  try {
    const raw = readFileSync(join(process.cwd(), "data", "site_meta.json"), "utf-8");
    const meta = JSON.parse(raw) as { total_posts: number };
    return `~${(meta.total_posts / 1_000_000).toFixed(1)}M`;
  } catch {
    return "—";
  }
}

function getCommunityCount(): number {
  try {
    const raw = readFileSync(join(process.cwd(), "data", "subreddits.json"), "utf-8");
    const list = JSON.parse(raw) as Array<{ subreddit: string }>;
    return new Set(list.map((s) => s.subreddit)).size;
  } catch {
    // Fallback only if subreddits.json is unreadable — keep in sync with the live count.
    return 31;
  }
}

const linkClass =
  "text-foreground underline underline-offset-2 hover:opacity-80 transition-opacity";

// Section heading + body paragraph come from the shared styles module.
const sectionHeaderStyle = sectionHeading;
const bodyStyle = bodyParagraph;

const sectionStyle: React.CSSProperties = {
  borderLeft: "1px solid #334155",
  paddingLeft: 24,
};

const leadStyle: React.CSSProperties = { color: "#F1F4F8", fontWeight: 600 };

// Understated landmark subhead — a standalone bold line, not a big heading.
const subheadStyle: React.CSSProperties = {
  fontWeight: 600,
  color: "#F1F4F8",
  fontSize: fontSize.base,
};

export default function About() {
  const stats = [
    { value: getPostCount(), label: "posts collected" },
    { value: String(getCommunityCount()), label: "communities tracked" },
    { value: String(THEMES.length), label: "recurring themes" },
  ];

  return (
    <div style={{ maxWidth: 720 }} className="mx-auto px-4 sm:px-6 py-10 sm:py-16">
      {/* Header */}
      <div className="mb-10">
        <div style={sectionEyebrow}>About this project</div>
        <h1
          style={{ fontSize: fontSize.xxxl, fontWeight: 600 }}
          className="font-display text-foreground mb-2"
        >
          Tracking how AI-companion communities talk
        </h1>
        <p style={{ ...introParagraph, color: "#9AA7B8" }}>
          This project follows six recurring themes in Reddit&apos;s
          AI-companion communities &mdash; romance, addiction, grief, and three
          others &mdash; and measures how often each one surfaces in posts. The
          post corpus reaches back to 2017, though the theme lines themselves
          begin later, as each theme&apos;s vocabulary becomes common enough to
          chart &mdash; mostly across 2022&ndash;2023, and not until 2025 for
          consciousness. What it captures is the conversation itself: when
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
                fontSize: fontSize.xl,
                fontWeight: 500,
                color: "#F8FAFC",
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {stat.value}
            </div>
            <div style={{ fontSize: fontSize.xs, color: "#9AA7B8", marginTop: 2 }}>
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-10">
        {/* Who makes this */}
        <section style={sectionStyle}>
          <h2 style={sectionHeaderStyle}>Who makes this</h2>
          <div className="space-y-4" style={bodyStyle}>
            <p>
              This is an independent project, built and maintained by one
              person. It is not academic, institutional, or peer-reviewed work
              &mdash; there is no lab or organization behind it.
            </p>
            <p>
              It started from a plain wish: a record of how these communities
              actually talk, one that anyone can check for themselves, instead
              of another round of hype or alarm. The method below is what keeps
              that record honest.
            </p>
          </div>
        </section>

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
              utility&rdquo; theme here &mdash; and everyday practical talk (bug
              reports, tips, which app to use) is, in fact, most of what these
              communities post. This is the lens the project looks through; the
              list below is what it was pointed at:
            </p>
            <ul
              className="space-y-2"
              style={{ listStyleType: "none", padding: 0 }}
            >
              {THEMES.map((t) => (
                <li key={t.id} style={{ fontSize: fontSize.base, lineHeight: 1.6 }}>
                  <span aria-hidden>{t.emoji}</span>{" "}
                  <span style={{ color: t.color, fontWeight: 500 }}>
                    {t.label}
                  </span>
                  <span style={{ color: "#9AA7B8" }}> &mdash; {t.tagline}</span>
                </li>
              ))}
            </ul>
            <p style={subheadStyle}>Validating the keywords</p>
            <p>
              Each theme is then defined by a set of keywords, and every keyword
              has to earn its place. For a candidate, I pull 100 real posts it
              matched and read them; the keyword stays only if those posts are
              genuinely about the theme. If it is matching on a coincidental
              shared word, it gets dropped. Language also drifts over time, so
              once a month I re-sample recent matches and re-check any keyword
              whose meaning may have moved.
            </p>
            <p>
              The chart shows how many posts use each theme&apos;s keywords,
              expressed as a rate per 1,000 posts and smoothed with a 7-day
              average. The rate matters more than a raw count would here. These
              communities have grown enormously since 2017, so a raw count would
              mostly retrace that growth; a rate sets the growth aside and shows
              how the conversation itself is shifting.
            </p>
            <p style={subheadStyle}>Why not just use an LLM?</p>
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
              each keyword match raised precision — the share of matched posts
              that genuinely belong to the theme — from roughly 80% to 88%,
              while doing nothing for the posts the keywords never matched in
              the first place. So the method stays plain on purpose. The careful
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
              This is a real choice, and it shapes what the site can see.
              These communities &mdash; where the AI is the relationship, not
              the tool &mdash; lean toward people for whom it is central and
              often intense, including recovery communities for people trying
              to quit. That makes the site good at catching
              that end of the spectrum and blind to casual mentions elsewhere.
              The trends describe <em>this curated set of communities</em>{" "}
              &mdash; not Reddit as a whole, and not &ldquo;people&rdquo; in
              general. And the list holds still while the platforms keep
              moving: a theme that fades here may have moved rather than
              ended &mdash; to a newer app, a Discord, a general-AI subreddit
              outside this set &mdash; and the site cannot tell those apart.
            </p>
            <p>
              One name on the list might look out of place: r/ChatGPTcomplaints.
              It is tracked as a companion community because of what its members
              write, not what it&apos;s called &mdash; it was the organizing hub
              for the #Keep4o protests when OpenAI retired GPT-4o, and a large
              share of its posts read like rupture-grief for a model people
              had built a relationship with.
            </p>
            <p>
              Within that curated set, each theme is also concentrated. Two or
              three subreddits usually account for most of a theme&apos;s posts
              &mdash; and the sexual-content line is well over half r/replika
              alone.
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
              belief, so I dropped it. &ldquo;Therapeutic&rdquo; began to turn,
              over a few months, from a word for real support into an insult
              aimed at preachy AI. Every model release and content-policy change sends a
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
              Three things make the <em>height</em> of a line untrustworthy,
              even where its <em>shape</em> holds:
            </p>
            <ul className="space-y-2" style={{ listStyleType: "none", padding: 0 }}>
              {[
                <>
                  <span style={leadStyle}>Vocabularies catch unevenly</span>
                  {" "}&mdash; addiction&apos;s recovery words
                  (&ldquo;relapse,&rdquo; &ldquo;cold turkey&rdquo;) match
                  cleanly; romance lives in ordinary language (&ldquo;I love
                  him,&rdquo; &ldquo;my boyfriend&rdquo;) that mostly slips
                  past, so one line can sit above another even when the second
                  theme is the larger one &mdash; and this runs one way: a
                  theme written in blunt, deliberate words reads higher than
                  one written in ordinary language, whatever the truth beneath.
                </>,
                <>
                  <span style={leadStyle}>
                    The keyword set is deliberately incomplete
                  </span>
                  {" "}&mdash; in a hand-coded sample of 400 random posts, it
                  caught between a few percent and about a third of the posts
                  that genuinely belonged.
                </>,
              ].map((item, i) => (
                <li
                  key={i}
                  style={{
                    fontSize: fontSize.base,
                    lineHeight: 1.7,
                    paddingLeft: 12,
                    listStyleType: "none",
                  }}
                >
                  <span style={{ color: "#7E8B9E" }} className="mr-1.5">
                    &bull;
                  </span>
                  {item}
                </li>
              ))}
            </ul>
            <p>
              So every line is a floor, not a ceiling: it runs low, it cannot be
              measured against its neighbours, and only its direction, timing,
              and spikes can be trusted &mdash; a missed post only weakens a
              line, while a false one corrupts it, so the method errs toward
              missing.
            </p>
            <p>
              <strong style={leadStyle}>
                Therapy and addiction are two readings of one behavior.
              </strong>{" "}
              Both lines track the same act &mdash; leaning on an AI to get
              through something hard &mdash; and what divides them is only how
              the writer frames it. &ldquo;It&apos;s my coping mechanism&rdquo;
              and &ldquo;I can&apos;t stop&rdquo; are the same use seen in two
              lights.
            </p>
            <p>
              You might expect the two lines to share many posts, then. They
              barely do &mdash; fewer than 1 in 50 posts is tagged on both
              &mdash; and that is a limit of the instrument, not a fact about
              the behavior. Addiction announces itself: &ldquo;relapse,&rdquo;
              &ldquo;days clean,&rdquo; &ldquo;withdrawals&rdquo; are deliberate
              words, and they match cleanly. Help-framing hides in ordinary
              language &mdash; &ldquo;it got me through,&rdquo; &ldquo;a safe
              space&rdquo; &mdash; and in a scattered vocabulary no keyword list
              captures whole. So a post that holds both frames usually tags only
              as addiction. We checked: hand-reading 90 posts the keywords had
              filed as addiction-only, about a quarter visibly carried a help
              frame the keywords missed. The overlap between these two themes is
              real and large; this method cannot measure it. Read each line on
              its own direction and timing, and do not read the gap between them
              as a help-versus-problem balance &mdash; that balance exists, but
              it is one these keywords are not equipped to weigh.
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
              One known seam in the recent data: Reddit ended unauthenticated
              data access without notice on May 30, 2026, which paused daily
              collection from May 29 to June 9, 2026. Posts for those days were
              recovered from the Arctic Shift archive, so post volume and theme
              trends are complete &mdash; but per-day subscriber and
              active-user figures for that window could not be reconstructed,
              and comments on posts from those days were not collected (the
              theme lines lean on post text alone there, as they do for all
              pre-March-2026 data).
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
              (~25&nbsp;GB) is too large to host there, but I&apos;ll share it
              on request &mdash; reach me on X at{" "}
              <a
                href="https://x.com/hopes_revenge"
                target="_blank"
                rel="noopener noreferrer"
                className={linkClass}
              >
                @hopes_revenge
              </a>
              .
            </p>
            <p>
              The site uses Vercel&apos;s privacy-friendly analytics for
              aggregate page-view counts &mdash; it sets no cookies, collects no
              personal data, and does no cross-site tracking.
            </p>
          </div>
        </section>

        {/* Changelog */}
        <section id="changelog" style={{ scrollMarginTop: 24 }}>
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
                  <div style={{ fontSize: fontSize.xs, color: "#F59E0B", marginBottom: 2 }}>
                    {entry.date}
                  </div>
                  <div
                    style={{
                      fontSize: fontSize.base,
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
                          fontSize: fontSize.sm,
                          lineHeight: 1.6,
                          color: "#9AA7B8",
                          paddingLeft: 12,
                          listStyleType: "none",
                        }}
                      >
                        <span style={{ color: "#7E8B9E" }} className="mr-1.5">
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
              fontSize: fontSize.xs,
              color: "#7E8B9E",
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
