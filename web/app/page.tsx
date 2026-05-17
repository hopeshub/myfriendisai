import TrendsExplorer from "./TrendsExplorer";
import PostVolumeChart from "./PostVolumeChart";
import EventShowcase from "./EventShowcase";
import { loadThemeData, loadPostVolume } from "./themeData";

// ── Homepage ─────────────────────────────────────────────────────────────────
// One scrollable narrative, top to bottom:
//   masthead  → who this watches
//   §1 volume → how much these communities post (orientation; no caveats but
//               the pre-2023 archive seam)
//   §2 events → the platform ruptures, with real posts — the strongest content
//   §3 atlas  → how the six themes shift (direction-only; TrendsExplorer)
// Post volume comes first to orient; events get the visual weight.

const sectionLabel: React.CSSProperties = {
  fontSize: 12,
  textTransform: "uppercase",
  letterSpacing: "0.06em",
  color: "#64748B",
  marginBottom: 8,
};

const intro: React.CSSProperties = {
  fontSize: 15,
  lineHeight: 1.7,
  color: "#94A3B8",
  maxWidth: 700,
};

export default function Home() {
  const themeData = loadThemeData();
  const postVolume = loadPostVolume();

  return (
    <div className="max-w-[1080px] mx-auto px-4 sm:px-8 pt-10 sm:pt-14 pb-8">
      {/* Masthead */}
      <header className="mb-16">
        <h1
          className="text-[26px] sm:text-3xl lg:text-[34px] font-bold text-[#F8FAFC]"
          style={{ lineHeight: 1.2, marginBottom: 12 }}
        >
          How the committed core of AI companionship talks
        </h1>
        <p style={{ ...intro, fontSize: 16, color: "#94A3B8" }}>
          A live record of the Reddit communities where AI companionship is the
          central subject &mdash; from r/replika to r/MyBoyfriendIsAI to
          communities for people trying to quit. It tracks six recurring themes
          in how these communities talk, and the platform events that move
          them. Not how common AI companionship is &mdash; but how this
          conversation changes over time.
        </p>
      </header>

      {/* §1 — Orientation: post volume */}
      <section className="mb-16">
        <div style={sectionLabel}>The communities</div>
        <h2
          className="text-xl sm:text-2xl font-semibold text-[#F8FAFC]"
          style={{ marginBottom: 8 }}
        >
          How much the committed core posts
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          Every month, this many posts went up across the AI-companion
          communities tracked here. It is the plainest measure in the project
          &mdash; a count of posts, no keyword judgement involved &mdash; and it
          answers the simplest question: are these communities growing? They
          are. Read it as community activity, not a headcount of people &mdash;
          one prolific user outposts ten quiet ones. And treat the shaded years
          before 2023 as a floor, not a count: public archives captured them
          only partially, and one 2017&ndash;2019 stretch not at all.
        </p>
        <PostVolumeChart data={postVolume} />
      </section>

      {/* §2 — Events */}
      <section className="mb-16">
        <div style={sectionLabel}>What happened</div>
        <h2
          className="text-xl sm:text-2xl font-semibold text-[#F8FAFC]"
          style={{ marginBottom: 8 }}
        >
          The events that move the conversation
        </h2>
        <p style={{ ...intro, marginBottom: 24 }}>
          This is where the instrument is sharpest. When a platform changes
          underneath its users &mdash; an app removes a feature, a model is
          retired &mdash; the language in these communities changes fast and
          unmistakably. Each of these is a real event, paired with real posts
          from the week it happened.
        </p>
        <EventShowcase />
      </section>

      {/* §3 — The theme atlas */}
      <section>
        <div style={sectionLabel}>The themes</div>
        <TrendsExplorer themeData={themeData} />
      </section>
    </div>
  );
}
