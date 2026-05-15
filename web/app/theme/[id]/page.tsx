import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { THEMES, DETECTOR_LABEL } from "../../themes";
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

/** Pick up to `limit` diverse posts, one from each keyword where possible. */
function pickSamplePosts(
  keywords: CategoryDetail["keywords"],
  limit: number,
): SamplePost[] {
  const out: SamplePost[] = [];
  const seen = new Set<string>();
  for (const kw of keywords) {
    if (out.length >= limit) break;
    for (const sp of kw.sample_posts) {
      if (!seen.has(sp.title)) {
        out.push(sp);
        seen.add(sp.title);
        break;
      }
    }
  }
  if (out.length < limit) {
    for (const kw of keywords) {
      for (const sp of kw.sample_posts) {
        if (out.length >= limit) break;
        if (!seen.has(sp.title)) {
          out.push(sp);
          seen.add(sp.title);
        }
      }
      if (out.length >= limit) break;
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
  const topSubs = details
    ? details.subreddits.slice(0, 5).map((s) => s.name)
    : [];

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
      <div className="mt-5">
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
            title="How much theme-relevant discourse the keyword set catches. A narrower detector means the line is a floor — the real conversation runs higher."
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
          </span>
        </div>
      </div>

      {/* The chart */}
      <div
        className="mt-6 rounded-xl"
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
          marginTop: 26,
        }}
      >
        {theme.story}
      </p>

      {/* Most active communities — one quiet line */}
      {topSubs.length > 0 && (
        <p style={{ fontSize: 13.5, color: "#8293A6", marginTop: 16 }}>
          Most active in{" "}
          {topSubs.map((name, i) => (
            <span key={name}>
              {i > 0 && ", "}
              <Link
                href={`/communities/${name}`}
                className="hover:underline underline-offset-2"
                style={{ color: "#CBD5E1" }}
              >
                r/{name}
              </Link>
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
                <div style={{ fontSize: 11.5, color: "#8293A6", marginTop: 3 }}>
                  r/{sp.subreddit} &middot; {fmtMonthYear(sp.date)}
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
