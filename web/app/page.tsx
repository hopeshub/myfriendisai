import Link from "next/link";
import Reveal from "./Reveal";
import TrendsExplorer from "./TrendsExplorer";
import PostVolumeChart from "./PostVolumeChart";
import EventShowcase from "./EventShowcase";
import RecoverySection from "./RecoverySection";
import { loadThemeData, loadPostVolumeSplit, loadRecoveryVolume } from "./themeData";
import { sectionEyebrow, introParagraph, measure } from "./styles";
import { CHANGELOG } from "./changelog";

// ── Homepage ─────────────────────────────────────────────────────────────────
// One scrollable narrative, top to bottom:
//   masthead  → who this watches
//   §1 volume → how much these communities post (orientation; no caveats but
//               the pre-2023 archive seam)
//   §2 events → the platform ruptures, with real posts — the strongest content
//   §3 atlas  → how the six themes shift (direction-only; TrendsExplorer)
// Post volume comes first to orient; events get the visual weight.

// Section eyebrow + intro paragraph come from the shared styles module.
const sectionLabel = sectionEyebrow;
const intro = introParagraph;

export default function Home() {
  const themeData = loadThemeData();
  const themeDataExclCai = loadThemeData("composition_trends.json");
  const postVolume = loadPostVolumeSplit();
  const recoveryVolume = loadRecoveryVolume();

  return (
    <div className="max-w-[1080px] mx-auto px-4 sm:px-8 pt-10 sm:pt-14 pb-8">
      {/* Masthead — one-time fade + rise, staggered ~80ms across the four
          elements. Each element's resting CSS is its natural visible state,
          so reduced-motion (duration→0) lands visible. */}
      <header className="mb-16">
        <h1
          className="font-display text-[26px] sm:text-3xl lg:text-[32px] font-semibold text-[#F8FAFC] rise-in"
          style={{
            lineHeight: 1.2,
            marginBottom: 12,
            maxWidth: measure,
            animationDelay: "0ms",
          }}
        >
          When the AI is the relationship, not the tool
        </h1>
        <ul style={{ listStyleType: "none", padding: 0, margin: 0, maxWidth: measure }}>
          {[
            {
              delay: "80ms",
              fontWeight: 400,
              body: (
                <>
                  A live record of the Reddit communities where AI
                  companionship is the central subject &mdash; from r/replika
                  to r/MyBoyfriendIsAI to communities for people trying to
                  quit.
                </>
              ),
            },
            {
              delay: "160ms",
              fontWeight: 400,
              body: (
                <>
                  It tracks six recurring themes in how these communities talk,
                  and the platform events that move them.
                </>
              ),
            },
            {
              delay: "240ms",
              fontWeight: 500,
              body: (
                <>
                  It can&apos;t tell you how common AI companionship is. It can
                  show you, month by month, how the conversation about it
                  changes.
                </>
              ),
            },
          ].map((item, i) => (
            <li
              key={i}
              className="rise-in"
              style={{
                ...intro,
                fontSize: 16,
                color: "#9AA7B8",
                fontWeight: item.fontWeight,
                marginTop: i === 0 ? 0 : 12,
                paddingLeft: 18,
                position: "relative",
                animationDelay: item.delay,
              }}
            >
              <span
                aria-hidden
                style={{ position: "absolute", left: 0, color: "#6B7689" }}
              >
                &bull;
              </span>
              {item.body}
            </li>
          ))}
        </ul>
      </header>

      {/* §1 — Orientation: post volume */}
      <Reveal className="mb-16">
        <section>
        <div style={sectionLabel}>The communities</div>
        <h2
          className="font-display text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          How active these communities are
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          Two views of the same months, each on its own scale. r/CharacterAI
          &mdash; a mass-market roleplay platform that for years was
          75&ndash;90% of every post counted here &mdash; surged and then
          contracted on its own platform lifecycle: a lawsuit, new content
          filters, users leaving.
        </p>
        <p style={{ ...intro, marginBottom: 16 }}>
          Every other tracked community did something different &mdash; it held
          roughly steady, drifting mildly upward, with spikes at the big
          platform events. That contrast is the point: the steep fall in the
          raw totals is one platform&apos;s story, not the category&apos;s.
        </p>
        <PostVolumeChart data={postVolume} />
        </section>
      </Reveal>

      {/* §2 — Events */}
      <Reveal className="mb-16">
        <section>
        <div style={sectionLabel}>What happened</div>
        <h2
          className="font-display text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          The events that move the conversation
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          When a platform changes underneath its users &mdash; an app drops a
          feature, a model is retired &mdash; the language in these communities
          shifts within days. This is where the tracker sees most clearly: each
          event below is real, paired with the posts people wrote the week it
          happened.
        </p>
        <EventShowcase />
        </section>
      </Reveal>

      {/* §3 — The theme atlas */}
      <Reveal className="mb-16">
        <section>
        <div style={sectionLabel}>The themes</div>
        <h2
          className="font-display text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          How the conversation shifts inside these communities
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          Six recurring themes, and how often each one&apos;s language surfaces
          in posts across these communities, month by month.
        </p>
        <TrendsExplorer
          themeData={themeData}
          themeDataExclCai={themeDataExclCai}
        />
        </section>
      </Reveal>

      {/* §3.5 — A word is not a fixed thing: three promoted observations */}
      <Reveal className="mb-16">
        <section>
        <h2
          className="font-display text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 16, maxWidth: measure }}
        >
          A word is not a fixed thing
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          &ldquo;Sentient&rdquo; used to be the word people here reached for to
          mark a real belief &mdash; that something might actually be there.
          Then it spread into roleplay and memes until it no longer marked
          belief at all, and it had to be dropped from the count. The
          consciousness line is thinner afterward not because the question went
          away, but because the word stopped being able to point at it.
        </p>
        <p style={{ ...intro, marginBottom: 16 }}>
          The same word can change what it means while you watch.
          &ldquo;Therapeutic&rdquo; was a word for real help &mdash; until, over
          a few months, it turned into an insult thrown at preachy AI. Same
          word, opposite charge, no announcement.
        </p>
        <p style={{ ...intro }}>
          &ldquo;It&apos;s my coping mechanism&rdquo; and &ldquo;I can&apos;t
          stop&rdquo; are often the same person, describing the same use, on
          different days. Therapy and addiction here are not two behaviors
          &mdash; they are one behavior under two framings. Which way a writer
          tilts is itself the thing being recorded.
        </p>
        </section>
      </Reveal>

      {/* §4 — The recovery counter-current */}
      <Reveal>
        <section>
        <div style={sectionLabel}>A counter-current</div>
        <h2
          className="font-display text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          Calling it an addiction
        </h2>
        <p style={{ ...intro, marginBottom: 28 }}>
          As AI companionship grew, so did unease about it. A growing number of
          people describe their own AI use as an addiction, and have built
          communities to quit it &mdash; borrowing the language of substance
          recovery: relapse, cold turkey, &ldquo;X days clean.&rdquo;
        </p>
        <RecoverySection data={recoveryVolume} />
        </section>
      </Reveal>

      {/* Changelog teaser — a quiet sign that the instrument is actively
          tended; the full list lives on the About page. */}
      <Reveal>
        <div
          style={{
            marginTop: 56,
            paddingTop: 20,
            borderTop: "1px solid #2A2D3A",
          }}
        >
          <p style={{ fontSize: 13, lineHeight: 1.6, color: "#6B7689" }}>
            Updated daily. Most recent change &mdash; {CHANGELOG[0].title} (
            {CHANGELOG[0].date}).{" "}
            <Link
              href="/about#changelog"
              style={{ color: "#9AA7B8", textDecoration: "underline" }}
            >
              See what&apos;s changed
            </Link>
          </p>
        </div>
      </Reveal>
    </div>
  );
}
