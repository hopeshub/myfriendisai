import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { THEMES, DETECTOR_LABEL, DETECTOR_EXPLAINER } from "../../themes";
import {
  loadThemeData,
  loadKeywordDetails,
  type CategoryDetail,
} from "../../themeData";
import ThemeChart from "./ThemeChart";

// ── Per-theme page ───────────────────────────────────────────────────────────
// The deeper "what is this and why" for one theme: a full-size chart, a plain-
// language story anchored to the events, and a few real posts. Reached by
// clicking a panel on the homepage atlas. Keyword lists live on the About page
// (methodology); this page is for a reader, not an auditor.

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmtMonthYear(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00Z");
  return `${MONTH_NAMES[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

function truncate(str: string, max: number): string {
  return str.length > max ? str.slice(0, max).trimEnd() + "…" : str;
}

type SamplePost = { title: string; subreddit: string; date: string; id: string };
type SampleWithTerm = SamplePost & { matchedTerm: string };

const MIN_SAMPLES = 2;

/**
 * Pick example posts, each carrying the keyword that matched it (shown on the
 * page as "matched …" evidence).
 *
 * Pass 1 takes only posts whose *title* visibly contains the keyword, across
 * all keywords — so every example is self-evidently on-theme, not a hit buried
 * in a post body the reader cannot see. Quality over quantity: a fuzzy theme
 * may surface only 3-4 examples rather than padding to `limit` with ambiguous
 * ones. Pass 2 is a safety net — body-only matches, used only if a theme can't
 * yield even MIN_SAMPLES self-evident posts.
 */
function pickSamplePosts(
  keywords: CategoryDetail["keywords"],
  limit: number,
): SampleWithTerm[] {
  const out: SampleWithTerm[] = [];
  const seen = new Set<string>();
  // Pass 1: keyword visible in the title — one post per keyword.
  for (const kw of keywords) {
    if (out.length >= limit) break;
    const term = kw.term.toLowerCase();
    const hit = kw.sample_posts.find(
      (sp) => !seen.has(sp.title) && sp.title.toLowerCase().includes(term),
    );
    if (hit) {
      out.push({ ...hit, matchedTerm: kw.term });
      seen.add(hit.title);
    }
  }
  // Pass 2: only if too few self-evident examples, top up to MIN_SAMPLES.
  if (out.length < MIN_SAMPLES) {
    for (const kw of keywords) {
      if (out.length >= MIN_SAMPLES) break;
      const free = kw.sample_posts.find((sp) => !seen.has(sp.title));
      if (free) {
        out.push({ ...free, matchedTerm: kw.term });
        seen.add(free.title);
      }
    }
  }
  return out;
}

export function generateStaticParams() {
  return THEMES.map((t) => ({ id: t.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const theme = THEMES.find((t) => t.id === id);
  if (!theme) return { title: "Theme — My Friend Is AI" };
  return {
    title: `${theme.label} — My Friend Is AI`,
    description: theme.story,
    openGraph: {
      title: `${theme.label} — My Friend Is AI`,
      description: theme.tagline,
    },
  };
}

const SECTION_LABEL: React.CSSProperties = {
  fontSize: 11,
  fontWeight: 500,
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  color: "#8293A6",
};

export default async function ThemePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const theme = THEMES.find((t) => t.id === id);
  if (!theme) notFound();

  const series = loadThemeData()[id] ?? [];
  const details: CategoryDetail | undefined = loadKeywordDetails()[id];
  const samples = details ? pickSamplePosts(details.keywords, 5) : [];
  const topSubs = details ? details.subreddits.slice(0, 5) : [];

  return (
    <div className="max-w-[920px] mx-auto px-4 sm:px-8 py-8">
      {/* Back to the atlas */}
      <Link
        href="/"
        className="text-sm transition-colors"
        style={{ color: "#64748B" }}
      >
        &larr; All themes
      </Link>

      {/* Header */}
      <div className="mt-4">
        <h1
          className="font-bold flex items-center gap-2.5"
          style={{ fontSize: 30, color: theme.color }}
        >
          <span aria-hidden style={{ fontSize: 28 }}>
            {theme.emoji}
          </span>
          {theme.label}
        </h1>
        <div className="mt-1.5 flex items-center gap-3 flex-wrap">
          <p style={{ fontSize: 15, color: "#94A3B8" }}>{theme.tagline}</p>
          <span
            className="info-chip"
            style={{
              fontSize: 11,
              color: "#AEB9C7",
              backgroundColor: "#20242F",
              border: "1px solid #2F3441",
              borderRadius: 5,
              padding: "1.5px 8px",
              whiteSpace: "nowrap",
            }}
          >
            {DETECTOR_LABEL[theme.detector]}
            <span className="info-chip__pop" role="tooltip">
              {DETECTOR_EXPLAINER}
            </span>
          </span>
        </div>
      </div>

      {/* The chart */}
      <div
        className="mt-5 rounded-xl"
        style={{
          backgroundColor: "#1A1D27",
          border: "1px solid #2A2D3A",
          borderTop: `2px solid ${theme.color}`,
          padding: "18px 20px 16px",
        }}
      >
        <ThemeChart series={series} color={theme.color} />
      </div>

      {/* The story */}
      <p
        style={{
          fontSize: 16.5,
          lineHeight: 1.7,
          color: "#D3DAE3",
          marginTop: 18,
        }}
      >
        {theme.story}
      </p>

      {/* Most active communities — one quiet line */}
      {topSubs.length > 0 && (
        <p style={{ fontSize: 13.5, color: "#8293A6", marginTop: 16 }}>
          Most active in{" "}
          {topSubs.map((s, i) => (
            <span key={s.name}>
              {i > 0 && ", "}
              <Link
                href={`/communities/${s.name}`}
                className="hover:underline underline-offset-2"
                style={{ color: "#CBD5E1" }}
              >
                r/{s.name}
              </Link>
              <span style={{ color: "#64748B" }}> {s.pct}%</span>
            </span>
          ))}
          .
        </p>
      )}

      {/* Example posts */}
      <div style={{ marginTop: 30 }}>
        <div style={SECTION_LABEL}>What people are saying</div>
        {samples.length > 0 ? (
          <div style={{ marginTop: 6 }}>
            {samples.map((sp, i) => (
              <div
                key={sp.id}
                style={{
                  padding: "10px 0",
                  borderTop: i > 0 ? "0.5px solid #1E293B" : undefined,
                }}
              >
                <a
                  href={`https://www.reddit.com/comments/${sp.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline underline-offset-2 transition-colors"
                  style={{ fontSize: 14.5, color: "#CBD5E1" }}
                >
                  {truncate(sp.title, 110)}
                </a>
                <div style={{ fontSize: 11.5, color: "#8293A6", marginTop: 4 }}>
                  r/{sp.subreddit} &middot; {fmtMonthYear(sp.date)}
                  <span style={{ color: "#5C6775" }}> &middot; matched </span>
                  <span style={{ color: theme.color }}>
                    &ldquo;{sp.matchedTerm}&rdquo;
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ fontSize: 13.5, color: "#8293A6", marginTop: 6 }}>
            No example posts available yet.
          </p>
        )}
        <p style={{ fontSize: 12, color: "#64748B", marginTop: 12 }}>
          A few real posts the keywords matched.{" "}
          <a
            href="/about#verification"
            style={{ color: "#94A3B8", textDecoration: "underline" }}
          >
            How this is measured &rarr;
          </a>
        </p>
      </div>

      {/* Other themes */}
      <nav
        aria-label="Other themes"
        style={{
          marginTop: 36,
          paddingTop: 18,
          borderTop: "0.5px solid #1E293B",
          display: "flex",
          flexWrap: "wrap",
          gap: "10px 18px",
        }}
      >
        {THEMES.map((t) =>
          t.id === id ? (
            <span
              key={t.id}
              style={{
                fontSize: 14,
                fontWeight: 600,
                color: t.color,
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <span aria-hidden>{t.emoji}</span>
              {t.label}
            </span>
          ) : (
            <Link
              key={t.id}
              href={`/theme/${t.id}`}
              className="transition-opacity hover:opacity-100"
              style={{
                fontSize: 14,
                color: "#94A3B8",
                opacity: 0.85,
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <span aria-hidden>{t.emoji}</span>
              {t.label}
            </Link>
          ),
        )}
      </nav>
    </div>
  );
}
