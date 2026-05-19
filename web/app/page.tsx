import Link from "next/link";
import Reveal from "./Reveal";
import TrendsExplorer from "./TrendsExplorer";
import PostVolumeChart from "./PostVolumeChart";
import EventShowcase from "./EventShowcase";
import RecoverySection from "./RecoverySection";
import { loadThemeData, loadCommunityComposition, loadRecoveryVolume } from "./themeData";
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
  const communityComposition = loadCommunityComposition();
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
          How the communities turned over
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          Add up the posts across these communities and the floor holds steady
          &mdash; a few thousand a month, spiking only when a platform breaks.
          What doesn&apos;t hold is the cast. In 2023, AI-companion Reddit was,
          basically, r/replika. Replika then emptied out &mdash; from 38,000
          posts a year to under 5,000 &mdash; and a new generation rose to take
          its place, post for post: r/NomiAI, r/KindroidAI, r/ChaiApp, a
          born-in-2024 r/MyBoyfriendIsAI.
        </p>
        <p style={{ ...intro, marginBottom: 16 }}>
          r/CharacterAI, the mass-market giant, ran the same arc at far larger
          scale &mdash; a boom past 40,000 posts a month, then a long recede.
          The pattern under all of it is churn: a community surges, crests, and
          gives way to the next platform. The floor holds; the names keep
          changing. Below, r/CharacterAI sits on its own scale, with every
          other community stacked beneath it &mdash; so the handover is visible.
        </p>
        <PostVolumeChart
          characterai={communityComposition.characterai}
          composition={communityComposition.composition}
        />
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
        <p style={{ ...intro, marginBottom: 16 }}>
          Every event here is a rupture &mdash; and that is itself a finding
          about the method. Rupture isn&apos;t the most important of the six
          themes; it is the only one shaped like an event. Romance,
          consciousness, therapy drift &mdash; no press release moves them, no
          single day a platform pulled access. Rupture has those days. So an
          event-driven section can only ever be rupture: a tracker built around
          moments sees, most sharply, the discourse that arrives in moments.
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
