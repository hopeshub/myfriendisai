import TrendsExplorer from "./TrendsExplorer";
import PostVolumeChart from "./PostVolumeChart";
import EventShowcase from "./EventShowcase";
import RecoverySection from "./RecoverySection";
import { loadThemeData, loadPostVolumeSplit, loadRecoveryVolume } from "./themeData";
import { sectionEyebrow, introParagraph, measure } from "./styles";

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
      {/* Masthead */}
      <header className="mb-16">
        <h1
          className="text-[26px] sm:text-3xl lg:text-[32px] font-bold text-[#F8FAFC]"
          style={{ lineHeight: 1.2, marginBottom: 12, maxWidth: measure }}
        >
          How the committed core of AI companionship talks
        </h1>
        <p style={{ ...intro, fontSize: 16, color: "#9AA7B8" }}>
          A live record of the Reddit communities where AI companionship is the
          central subject &mdash; from r/replika to r/MyBoyfriendIsAI to
          communities for people trying to quit.
        </p>
        <p style={{ ...intro, fontSize: 16, color: "#9AA7B8", marginTop: 12 }}>
          It tracks six recurring themes in how these communities talk, and the
          platform events that move them.
        </p>
        <p
          style={{
            ...intro,
            fontSize: 16,
            color: "#9AA7B8",
            fontWeight: 500,
            marginTop: 12,
          }}
        >
          Not how common AI companionship is &mdash; but how this conversation
          changes over time.
        </p>
      </header>

      {/* §1 — Orientation: post volume */}
      <section className="mb-16">
        <div style={sectionLabel}>The communities</div>
        <h2
          className="text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
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

      {/* §2 — Events */}
      <section className="mb-16">
        <div style={sectionLabel}>What happened</div>
        <h2
          className="text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          The events that move the conversation
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          This is where the instrument is sharpest. When a platform changes
          underneath its users &mdash; an app removes a feature, a model is
          retired &mdash; the language in these communities changes fast and
          unmistakably. Each of these is a real event, paired with real posts
          from the week it happened.
        </p>
        <EventShowcase />
      </section>

      {/* §3 — The theme atlas */}
      <section className="mb-16">
        <div style={sectionLabel}>The themes</div>
        <h2
          className="text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          How the conversation shifts inside them
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

      {/* §4 — The recovery counter-current */}
      <section>
        <div style={sectionLabel}>A counter-current</div>
        <h2
          className="text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
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
    </div>
  );
}
