import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { THEMES } from "../../themes";
import {
  loadThemeData,
  loadKeywordDetails,
  type CategoryDetail,
  type SamplePost,
} from "../../themeData";
import ThemeChart from "./ThemeChart";
import ThemeBackdrop from "./ThemeBackdrop";

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

type SampleWithTerm = SamplePost & { matchedTerm: string };

/**
 * Pick example posts across the theme's keywords — one per keyword first (for
 * vocabulary diversity), then filling with more. Each carries the keyword that
 * matched it; the page highlights that keyword in the post title or in a body
 * excerpt, so every example visibly shows why it was tagged. The export
 * already restricts these to post-sourced matches (keyword in the post, not a
 * comment), so an excerpt or a title hit is always available.
 */
function pickSamplePosts(
  keywords: CategoryDetail["keywords"],
  limit: number,
): SampleWithTerm[] {
  const out: SampleWithTerm[] = [];
  const seen = new Set<string>();
  for (const kw of keywords) {
    if (out.length >= limit) break;
    const free = kw.sample_posts.find((sp) => !seen.has(sp.title));
    if (free) {
      out.push({ ...free, matchedTerm: kw.term });
      seen.add(free.title);
    }
  }
  if (out.length < limit) {
    for (const kw of keywords) {
      for (const sp of kw.sample_posts) {
        if (out.length >= limit) break;
        if (!seen.has(sp.title)) {
          out.push({ ...sp, matchedTerm: kw.term });
          seen.add(sp.title);
        }
      }
      if (out.length >= limit) break;
    }
  }
  return out;
}

/** Wrap the first occurrence of `term` in `text` in the theme colour. */
function highlight(
  text: string,
  term: string,
  color: string,
): React.ReactNode {
  const i = text.toLowerCase().indexOf(term.toLowerCase());
  if (i < 0) return text;
  return (
    <>
      {text.slice(0, i)}
      <span style={{ color, fontWeight: 600 }}>
        {text.slice(i, i + term.length)}
      </span>
      {text.slice(i + term.length)}
    </>
  );
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
  const samples = details ? pickSamplePosts(details.keywords, 12) : [];
  const topSubs = details ? details.subreddits.slice(0, 5) : [];

  return (
    <ThemeBackdrop>
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
        <p style={{ fontSize: 15, color: "#94A3B8", marginTop: 6 }}>
          {theme.tagline}
        </p>
      </div>

      {/* The chart — breaks out wider than the text column on desktop */}
      <div
        className="mt-5 rounded-xl theme-chart-breakout"
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
        <div style={SECTION_LABEL}>Matched posts</div>
        <p
          style={{
            fontSize: 13,
            color: "#8293A6",
            marginTop: 6,
            lineHeight: 1.6,
          }}
        >
          A sample of real posts a keyword matched, with the matched term
          highlighted.
        </p>
        {samples.length > 0 ? (
          <div style={{ marginTop: 6 }}>
            {samples.map((sp, i) => {
              const inTitle = sp.title
                .toLowerCase()
                .includes(sp.matchedTerm.toLowerCase());
              const displayTitle = truncate(sp.title, 120);
              return (
                <div
                  key={sp.id}
                  style={{
                    padding: "12px 0",
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
                    {inTitle
                      ? highlight(displayTitle, sp.matchedTerm, theme.color)
                      : displayTitle}
                  </a>
                  {!inTitle && sp.excerpt && (
                    <div
                      style={{
                        fontSize: 13,
                        lineHeight: 1.55,
                        color: "#94A3B8",
                        marginTop: 5,
                        borderLeft: "2px solid #2A2D3A",
                        paddingLeft: 10,
                      }}
                    >
                      {highlight(sp.excerpt, sp.matchedTerm, theme.color)}
                    </div>
                  )}
                  <div
                    style={{ fontSize: 11.5, color: "#8293A6", marginTop: 5 }}
                  >
                    r/{sp.subreddit} &middot; {fmtMonthYear(sp.date)}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p style={{ fontSize: 13.5, color: "#8293A6", marginTop: 6 }}>
            No example posts available yet.
          </p>
        )}
        <p
          style={{
            fontSize: 12,
            color: "#64748B",
            marginTop: 14,
            lineHeight: 1.6,
          }}
        >
          Snippets are shortened and usernames aren&apos;t shown; each link
          opens the original public Reddit post.{" "}
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
    </ThemeBackdrop>
  );
}
