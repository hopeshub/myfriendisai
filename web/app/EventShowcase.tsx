// ── Event showcase ───────────────────────────────────────────────────────────
// Server component. Renders the curated platform-event spine: each event with
// its real posts. No client interactivity — the post cards are plain links to
// Reddit, so this stays out of the JS bundle.

import { THEMES, type ThemeId } from "./themes";
import {
  SHOWCASE_EVENTS,
  redditPermalink,
  type ShowcaseEvent,
} from "./eventShowcaseData";
import { measure } from "./styles";
import { loadThemeData } from "./themeData";
import EventSparkline from "./EventSparkline";

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmtDate(d: string): string {
  const dt = new Date(d + "T00:00:00Z");
  return `${MONTHS[dt.getUTCMonth()]} ${dt.getUTCFullYear()}`;
}

function themeMeta(id: ThemeId) {
  return THEMES.find((t) => t.id === id);
}

type Spark = { values: number[]; eventIndex: number };

// The theme's monthly per-1k rate, windowed ±`radius` months around the event
// month, plus the index of the event month within that window. Months with no
// data (before a theme's coverage start, or in the future) are dropped, so a
// recent event's window can be shorter than 2·radius+1.
function windowedSeries(
  series: { date: string; hitsPerK: number }[],
  eventMonth: string,
  radius = 6,
): Spark | null {
  const byMonth: Record<string, number> = {};
  for (const p of series) byMonth[p.date.slice(0, 7)] = p.hitsPerK;

  let [y, m] = eventMonth.split("-").map(Number);
  m -= radius;
  while (m <= 0) {
    m += 12;
    y -= 1;
  }
  const values: number[] = [];
  let eventIndex = -1;
  for (let i = 0; i < radius * 2 + 1; i++) {
    const key = `${y}-${String(m).padStart(2, "0")}`;
    if (key in byMonth) {
      if (key === eventMonth) eventIndex = values.length;
      values.push(byMonth[key]);
    }
    m += 1;
    if (m > 12) {
      m = 1;
      y += 1;
    }
  }
  if (eventIndex < 0 || values.length < 2) return null;
  return { values, eventIndex };
}

function EventCard({
  event,
  spark,
}: {
  event: ShowcaseEvent;
  spark: Spark | null;
}) {
  return (
    <article
      style={{
        backgroundColor: "#15171E",
        border: "1px solid #2A2D3A",
        borderLeft: `3px solid ${themeMeta(event.themes[0])?.color ?? "#94A3B8"}`,
        borderRadius: 8,
        padding: 20,
      }}
    >
      {/* Header: date + title */}
      <div className="flex items-baseline gap-3 flex-wrap">
        <span
          style={{
            fontSize: 12,
            color: "#C2974D",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            flexShrink: 0,
          }}
        >
          {event.dateLabel}
        </span>
        <h3 style={{ fontSize: 18, fontWeight: 600, color: "#F1F4F8" }}>
          {event.title}
        </h3>
      </div>

      {/* Theme tags — which lines this event moved */}
      <div className="flex gap-3 flex-wrap" style={{ marginTop: 6 }}>
        {event.themes.map((id) => {
          const t = themeMeta(id);
          return (
            <span
              key={id}
              className="inline-flex items-center gap-1.5"
              style={{ fontSize: 12, color: "#9AA7B8" }}
            >
              <span aria-hidden style={{ fontSize: 13 }}>
                {t?.emoji ?? "•"}
              </span>
              {t?.label ?? id}
            </span>
          );
        })}
      </div>

      {/* What happened */}
      <p
        style={{
          fontSize: 14,
          lineHeight: 1.7,
          color: "#C8D0DC",
          marginTop: 10,
          maxWidth: measure,
        }}
      >
        {event.summary}
      </p>

      {/* The theme line around this event — quote and curve corroborate */}
      {spark && (
        <div style={{ marginTop: 14, maxWidth: measure }}>
          <EventSparkline
            values={spark.values}
            eventIndex={spark.eventIndex}
            color={themeMeta(event.themes[0])?.color ?? "#9AA7B8"}
          />
          <p style={{ fontSize: 11, color: "#6B7689", marginTop: 4, lineHeight: 1.5 }}>
            <span
              style={{
                color: themeMeta(event.themes[0])?.color ?? "#9AA7B8",
                fontWeight: 600,
              }}
            >
              {themeMeta(event.themes[0])?.label}
            </span>{" "}
            language &mdash; monthly rate, six months either side; the dashed
            line marks the event.
          </p>
        </div>
      )}

      {/* Real posts from the week it happened */}
      <div className="grid gap-3 sm:grid-cols-3" style={{ marginTop: 14 }}>
        {event.posts.map((p) => (
          <a
            key={p.id}
            href={redditPermalink(p)}
            target="_blank"
            rel="noopener noreferrer"
            className="group block rounded-lg transition-colors hover:bg-[#1A1D27]"
            style={{
              backgroundColor: "#0F1117",
              border: "1px solid #2A2D3A",
              padding: 14,
            }}
          >
            <div
              className="line-clamp-2"
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: "#F1F4F8",
                lineHeight: 1.4,
              }}
            >
              {p.title}
            </div>
            <p
              className="font-display line-clamp-4"
              style={{
                fontSize: 13,
                lineHeight: 1.6,
                color: "#9AA7B8",
                marginTop: 8,
                fontStyle: "italic",
              }}
            >
              &ldquo;{p.excerpt}&rdquo;
            </p>
            <div
              style={{
                fontSize: 11,
                color: "#6B7689",
                marginTop: 10,
                display: "flex",
                gap: 8,
                flexWrap: "wrap",
              }}
            >
              <span className="group-hover:text-[#9AA7B8] transition-colors">
                r/{p.subreddit}
              </span>
              <span>·</span>
              <span>{fmtDate(p.date)}</span>
              <span>·</span>
              <span>
                <span aria-hidden>&uarr;</span>{" "}
                <span className="sr-only">score </span>
                {p.score.toLocaleString()}
              </span>
            </div>
          </a>
        ))}
      </div>
    </article>
  );
}

export default function EventShowcase() {
  const themeData = loadThemeData();
  return (
    <div className="space-y-6">
      {SHOWCASE_EVENTS.map((event) => {
        const series = themeData[event.themes[0]] ?? [];
        const spark = windowedSeries(series, event.date.slice(0, 7));
        return <EventCard key={event.slug} event={event} spark={spark} />;
      })}
    </div>
  );
}
