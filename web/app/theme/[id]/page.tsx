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
import { fontSize, sectionEyebrow } from "../../styles";

// ── Per-theme page ───────────────────────────────────────────────────────────
// The deeper "what is this and why" for one theme: a full-size chart, a plain-
// language story anchored to the events, and a few real posts. Reached by
// clicking a panel on the homepage atlas. Each theme page also shows its own
// keyword set with per-keyword precision, so a reader can see exactly which
// validated terms define the theme and how clean each one tested.

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
    const free = kw.sample_posts.find((sp) => !seen.has(sp.id));
    if (free) {
      out.push({ ...free, matchedTerm: kw.term });
      seen.add(free.id);
    }
  }
  if (out.length < limit) {
    for (const kw of keywords) {
      for (const sp of kw.sample_posts) {
        if (out.length >= limit) break;
        if (!seen.has(sp.id)) {
          out.push({ ...sp, matchedTerm: kw.term });
          seen.add(sp.id);
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
    // tagline, not story — story is a full paragraph that truncates
    // mid-sentence in search results and social cards.
    description: theme.tagline,
    openGraph: {
      title: `${theme.label} — My Friend Is AI`,
      description: theme.tagline,
    },
  };
}

// Section eyebrow comes from the shared styles module.
const SECTION_LABEL = sectionEyebrow;

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
        style={{ color: "#9AA7B8" }}
      >
        &larr; All themes
      </Link>

      {/* Header */}
      <div className="mt-4">
        <h1
          className="font-display font-semibold flex items-center gap-2.5"
          style={{ fontSize: fontSize.xxxl, color: theme.color }}
        >
          <span aria-hidden style={{ fontSize: fontSize.xxl }}>
            {theme.emoji}
          </span>
          {theme.label}
        </h1>
        <p style={{ fontSize: fontSize.base, color: "#9AA7B8", marginTop: 6 }}>
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
          fontSize: fontSize.md,
          lineHeight: 1.7,
          color: "#C8D0DC",
          marginTop: 18,
        }}
      >
        {theme.story}
      </p>

      {/* Most active communities — one quiet line */}
      {topSubs.length > 0 && (
        <p style={{ fontSize: fontSize.base, color: "#9AA7B8", marginTop: 16 }}>
          Most of this theme&apos;s posts come from a few communities &mdash;{" "}
          {topSubs.map((s, i) => (
            <span key={s.name}>
              {i > 0 && ", "}
              <Link
                href={`/communities/${s.name}`}
                className="underline underline-offset-2"
                style={{ color: "#C8D0DC" }}
              >
                r/{s.name}
              </Link>
              <span style={{ color: "#7E8B9E" }}> {s.pct}%</span>
            </span>
          ))}
          {" "}&mdash; so this line is a close reading of those rooms, not an
          even sweep across Reddit.
        </p>
      )}

      {/* The keywords that define this theme */}
      {details && details.keywords.length > 0 && (
        <div style={{ marginTop: 30 }}>
          <div style={SECTION_LABEL}>The keywords</div>
          <p
            style={{
              fontSize: fontSize.sm,
              color: "#7E8B9E",
              marginTop: 6,
              lineHeight: 1.6,
            }}
          >
            This theme is defined by these {details.keywords.length} validated
            keywords &mdash; a post counts when its text matches one of them,
            with no AI classifier. The percentage is the share of a
            keyword&apos;s matches that were on-theme when hand-checked.
          </p>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 6,
              marginTop: 12,
            }}
          >
            {[...details.keywords]
              .sort((a, b) => b.hits - a.hits)
              .map((kw) => (
                <span
                  key={kw.term}
                  style={{
                    display: "inline-flex",
                    alignItems: "baseline",
                    gap: 6,
                    backgroundColor: "#1A1D27",
                    border: "1px solid #2A2D3A",
                    borderRadius: 6,
                    padding: "3px 9px",
                    fontSize: fontSize.sm,
                  }}
                >
                  <span style={{ color: "#C8D0DC" }}>{kw.term}</span>
                  {kw.precision != null && (
                    <span style={{ color: "#7E8B9E" }}>
                      {Math.round(kw.precision)}%
                    </span>
                  )}
                  {kw.status && (
                    <span
                      style={{
                        color: "#8A93A3",
                        fontStyle: "italic",
                        fontSize: fontSize.xs,
                      }}
                    >
                      {kw.status === "audit-gate-fail"
                        ? "· contested"
                        : kw.status === "researcher-accepted"
                        ? "· judgment call"
                        : "· low volume"}
                    </span>
                  )}
                </span>
              ))}
          </div>
          {details.keywords.some((kw) => kw.status) && (
            <p
              style={{
                fontSize: fontSize.xs,
                color: "#7E8B9E",
                marginTop: 10,
                lineHeight: 1.6,
              }}
            >
              A few keywords carry a note.{" "}
              <em style={{ color: "#9AA7B8" }}>contested</em> &mdash; an
              independent re-read didn&apos;t consistently agree its matches
              were on-theme, so its precision is less settled than the figure
              suggests. <em style={{ color: "#9AA7B8" }}>judgment call</em>{" "}
              &mdash; kept despite a score below the usual bar because its
              false matches are few and predictable.{" "}
              <em style={{ color: "#9AA7B8" }}>low volume</em> &mdash; too few
              matches to score precisely.
            </p>
          )}
          <p
            style={{
              fontSize: fontSize.xs,
              color: "#7E8B9E",
              marginTop: 12,
              lineHeight: 1.6,
            }}
          >
            These keywords are precision-first: when one matches, the post is
            usually on-theme &mdash; but they also miss a lot. A hand-coded
            audit found keyword matching catches only a minority of genuinely
            on-theme posts &mdash; a few percent to about a third, depending on
            the theme. Read the line as a floor, not a full count.{" "}
            <a
              href="/about#verification"
              style={{ color: "#9AA7B8", textDecoration: "underline" }}
            >
              How this is measured &rarr;
            </a>
          </p>
        </div>
      )}

      {/* Example posts */}
      <div style={{ marginTop: 30 }}>
        <div style={SECTION_LABEL}>Matched posts</div>
        <p
          style={{
            fontSize: fontSize.sm,
            color: "#7E8B9E",
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
              const displayTitle = truncate(sp.title, 120);
              // Test the *truncated* title — if truncation dropped the matched
              // term, fall through to the excerpt so the post still shows its
              // highlighted keyword rather than rendering with none.
              const inTitle = displayTitle
                .toLowerCase()
                .includes(sp.matchedTerm.toLowerCase());
              return (
                <div
                  key={sp.id}
                  style={{
                    padding: "12px 0",
                    borderTop: i > 0 ? "1px solid #1E293B" : undefined,
                  }}
                >
                  <a
                    href={`https://www.reddit.com/comments/${sp.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline underline-offset-2 transition-colors"
                    style={{ fontSize: fontSize.base, color: "#C8D0DC" }}
                  >
                    {inTitle
                      ? highlight(displayTitle, sp.matchedTerm, theme.color)
                      : displayTitle}
                  </a>
                  {!inTitle && sp.excerpt && (
                    <div
                      style={{
                        fontSize: fontSize.sm,
                        lineHeight: 1.55,
                        color: "#9AA7B8",
                        marginTop: 5,
                        borderLeft: "2px solid #2A2D3A",
                        paddingLeft: 10,
                      }}
                    >
                      {highlight(sp.excerpt, sp.matchedTerm, theme.color)}
                    </div>
                  )}
                  <div
                    style={{ fontSize: fontSize.micro, color: "#7E8B9E", marginTop: 5 }}
                  >
                    r/{sp.subreddit} &middot; {fmtMonthYear(sp.date)}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p style={{ fontSize: fontSize.base, color: "#7E8B9E", marginTop: 6 }}>
            No example posts available yet.
          </p>
        )}
        <p
          style={{
            fontSize: fontSize.xs,
            color: "#7E8B9E",
            marginTop: 14,
            lineHeight: 1.6,
          }}
        >
          Snippets are shortened and usernames aren&apos;t shown; each link
          opens the original public Reddit post.{" "}
          <a
            href="/about#verification"
            style={{ color: "#9AA7B8", textDecoration: "underline" }}
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
          borderTop: "1px solid #1E293B",
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
                fontSize: fontSize.base,
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
                fontSize: fontSize.base,
                color: "#9AA7B8",
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
