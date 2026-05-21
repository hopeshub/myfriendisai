import Link from "next/link";
import TrendsExplorer from "./TrendsExplorer";
import PostVolumeChart from "./PostVolumeChart";
import EventShowcase from "./EventShowcase";
import RecoverySection from "./RecoverySection";
import AmbientSection from "./AmbientSection";
import { loadThemeData, loadCommunityComposition, loadRecoveryVolume } from "./themeData";
import { THEMES } from "./themes";
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
                style={{ position: "absolute", left: 0, color: "#7E8B9E" }}
              >
                &bull;
              </span>
              {item.body}
            </li>
          ))}
        </ul>

        {/* Six-theme strip — a tappable index of the §3 atlas. Lets a reader
            jump straight to one theme's chart and real posts without first
            scrolling the whole narrative. */}
        <nav
          aria-label="The six tracked themes"
          className="rise-in"
          style={{ marginTop: 24, maxWidth: measure, animationDelay: "320ms" }}
        >
          <div style={{ ...sectionLabel, marginBottom: 8 }}>The six themes</div>
          <div className="flex flex-wrap gap-2">
            {THEMES.map((t) => (
              <Link
                key={t.id}
                href={`/theme/${t.id}`}
                className="inline-flex items-center gap-1.5 rounded-full border border-[#2A2D3A] px-3 py-1 min-h-11 sm:min-h-0 text-sm text-[#C8D0DC] transition-colors hover:border-[#3F4351] hover:bg-[#15171E] hover:text-[#F1F4F8]"
              >
                <span aria-hidden>{t.emoji}</span>
                {t.label}
              </Link>
            ))}
          </div>
        </nav>
      </header>

      {/* §1 — Orientation: post volume */}
      <div className="mb-16">
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
          scale &mdash; a boom to nearly 40,000 posts a month, then a long
          recede. Underneath it all is churn: a community surges, crests, and
          gives way to the next platform. The floor holds; the names keep
          changing.
        </p>
        <PostVolumeChart
          characterai={communityComposition.characterai}
          composition={communityComposition.composition}
        />
        <p style={{ ...intro, marginTop: 16 }}>
          A falling line means fewer posts in that community &mdash; not
          necessarily fewer people. The conversation can also move &mdash; to a
          Discord, an in-app forum, a general-AI subreddit this tracker
          doesn&apos;t follow. The chart watches a room empty out; it
          can&apos;t see where everyone went.
        </p>
        </section>
      </div>

      {/* §2 — Events */}
      <div className="mb-16">
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
          Every event here is a rupture &mdash; itself a finding about the
          method. Of the six themes, rupture is the only one shaped like an
          event: romance, consciousness, and therapy drift, with no press
          release behind them. A section built around moments can only be
          about the theme that arrives in them.
        </p>
        <EventShowcase />
        </section>
      </div>

      {/* §3 — The theme atlas */}
      <div className="mb-16">
        <section id="themes" className="scroll-mt-8">
        <div style={sectionLabel}>The themes</div>
        <h2
          className="font-display text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          How the conversation shifts inside these communities
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          Six recurring themes, and how often each one&apos;s language surfaces
          in posts across these communities, month by month. Each panel is
          scaled to mentions per 1,000 posts &mdash; a value of 8 means roughly
          8 of every 1,000 posts that month carried that theme&apos;s keywords.
        </p>
        <TrendsExplorer
          themeData={themeData}
          themeDataExclCai={themeDataExclCai}
        />
        </section>
      </div>

      {/* §3.5 — A word is not a fixed thing: how the instrument's words drift */}
      <div className="mb-16">
        <section>
        <div style={sectionLabel}>The instrument</div>
        <h2
          className="font-display text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          A word is not a fixed thing
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          Every line on the chart above is built from words &mdash; and words
          are the least fixed thing the project measures. They come loose from
          their meaning, they flip while you watch, and sometimes two of them
          name one behavior. Here is what that looked like, three times.
        </p>
        <p style={{ ...intro, marginBottom: 16 }}>
          <strong style={{ color: "#F1F4F8", fontWeight: 600 }}>
            A word can come loose from what it names.
          </strong>{" "}
          &ldquo;Sentient&rdquo; was once the word people here reached for to
          mark a real belief &mdash; that something might actually be there.
          Then it spread into roleplay and Character.AI memes until it no
          longer marked belief at all, and it had to be dropped from the count.
          It is part of why the consciousness panel above begins so late and
          runs so thin: not because the question went away, but because the
          word that used to carry it stopped being able to point.
        </p>
        <p style={{ ...intro, marginBottom: 16 }}>
          <strong style={{ color: "#F1F4F8", fontWeight: 600 }}>
            A word can hold its place and flip its charge.
          </strong>{" "}
          &ldquo;Therapeutic&rdquo; was a word for real help. Then, over a few
          months, people began turning it on exactly that &mdash; AI gone
          preachy and over-careful &mdash; and often the word came to carry the
          opposite of its old meaning. Same word, opposite charge, no
          announcement. &ldquo;Sentient&rdquo; had to be dropped;
          &ldquo;therapeutic&rdquo; is still counted, but now it is watched
          &mdash; re-sampled every month, because the project learned the hard
          way not to trust a word to hold still.
        </p>
        <p style={{ ...intro, marginBottom: 16 }}>
          <strong style={{ color: "#F1F4F8", fontWeight: 600 }}>
            Two words can name one behavior.
          </strong>{" "}
          &ldquo;It&apos;s my coping mechanism&rdquo; and &ldquo;I can&apos;t
          stop&rdquo; are often the same person, describing the same use on
          different days. Therapy and addiction here are not two behaviors
          &mdash; they are one behavior under two framings. But the instrument
          catches only the framings it has good words for, and it has far
          better words for the problem than for the help: &ldquo;relapse&rdquo;
          and &ldquo;days clean&rdquo; are deliberate and easy to catch, while
          &ldquo;it got me through&rdquo; hides in ordinary language the
          keywords slip past. So the two lines are not a scale to weigh one
          side against the other. They are the same act, recorded twice
          &mdash; and recorded unevenly.
        </p>
        <p style={{ ...intro }}>
          That is the thread under all three. The chart counts words, and
          words come loose, flip, and hide. The lines are real &mdash; and
          also drawn by an instrument still learning the language it reads.
        </p>
        </section>
      </div>

      {/* §4 — The recovery counter-current */}
      <div>
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
      </div>

      {/* §5 — The room next door: the AI culture-war communities. The
          chart shows the infrastructure forming; the editorial point is
          that what these subs police is upstream of AI companionship,
          not aimed at it. §4 records that posture being absorbed inward;
          the closing disclosure fences what Reddit can and can't show. */}
      <div style={{ marginTop: 56 }}>
        <section>
        <div style={sectionLabel}>The room next door</div>
        <h2
          className="font-display text-xl sm:text-2xl font-semibold text-[#F1F4F8]"
          style={{ marginBottom: 8, maxWidth: measure }}
        >
          The argument is upstream
        </h2>
        <p style={{ ...intro, marginBottom: 16 }}>
          Next door, a new infrastructure is forming. Subreddits built to
          argue about AI as a cultural project barely existed in 2023;
          the cluster&apos;s post volume rose 347% in 2025 alone, and
          now runs at more than 10,000 posts a month &mdash; up 824%
          from 2023. r/aiwars is the only all-sides debate floor;
          everyone else is a partisan room. r/antiAI didn&apos;t exist
          before March 2025; 8 months later its monthly post volume
          topped every other sub in the cluster. Both sides are
          organizing. The fight is real.
        </p>
        <p style={{ ...intro, marginBottom: 28 }}>
          Almost none of it is about AI companionship. &ldquo;AI bros&rdquo;
          appears in titles here roughly ten times more often than
          &ldquo;AI girlfriend.&rdquo; But the posture is the same one
          &mdash; that taking a chatbot seriously is a category mistake
          worth mocking &mdash; and it is already the air the communities
          on this site breathe.
        </p>
        <AmbientSection />
        </section>
      </div>

      {/* Changelog teaser — a quiet sign that the instrument is actively
          tended; the full list lives on the About page. */}
      <div>
        <div
          style={{
            marginTop: 56,
            paddingTop: 20,
            borderTop: "1px solid #2A2D3A",
          }}
        >
          <p style={{ fontSize: 13, lineHeight: 1.6, color: "#7E8B9E" }}>
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
      </div>
    </div>
  );
}
