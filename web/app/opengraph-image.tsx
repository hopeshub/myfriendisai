import { ImageResponse } from "next/og";
import siteMeta from "../data/site_meta.json";
import subreddits from "../data/subreddits.json";
import themeCounts from "../public/dataset/v1/monthly_theme_counts.json";
import { C, SITE_THEME } from "@/app/styles";

export const runtime = "edge";
export const alt = "My Friend Is AI — Tracking AI companion discourse on Reddit";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

// On the paper theme every theme is drawn in the one navy ink (themes.ts).
const THEMES = [
  { label: "Romance", color: "#FF69B4" },
  { label: "Sex / ERP", color: "#f87171" },
  { label: "Consciousness", color: "#C084FC" },
  { label: "Therapy", color: "#60A5FA" },
  { label: "Addiction", color: "#fd7112" },
  { label: "Rupture", color: "#22C55E" },
].map((t) => (SITE_THEME === "paper" ? { ...t, color: C.title } : t));

// Read from the build-time data export so the counts cannot go stale.
const POST_COUNT = `~${(siteMeta.total_posts / 1_000_000).toFixed(1)}M`;
const COMMUNITY_COUNT = new Set(
  (subreddits as Array<{ subreddit: string }>).map((s) => s.subreddit),
).size;

// Paper theme: the card is a miniature of the homepage atlas — six labelled
// channels on salmon recorder rules, one red event mark across them — set in
// IBM Plex Sans Condensed. (Satori cannot read woff2, so the two weights it
// needs ship as .woff beside the site's woff2 files.)
const CHANNELS: [string, string][] = [
  ["romance", "Romance"], ["sexual_erp", "Sex / ERP"], ["consciousness", "Consciousness"],
  ["therapy", "Therapy"], ["addiction", "Addiction"], ["rupture", "Rupture"],
];
// The last 12 complete months of each theme's published rate, from the public
// dataset (the same numbers the atlas draws), and the event to mark across them.
type Row = { theme: string; month: string; rate_per_1k: number | null };
const ROWS = (themeCounts as unknown as { rows: Row[] }).rows;
const LAST_MONTHS = Array.from(new Set(ROWS.map((r) => r.month))).sort().slice(-12);
const EVENT_MONTH = "2026-02"; // 4o retired
function series(theme: string): number[] {
  const byMonth = new Map(ROWS.filter((r) => r.theme === theme).map((r) => [r.month, r.rate_per_1k ?? 0]));
  return LAST_MONTHS.map((m) => byMonth.get(m) ?? 0);
}

async function paperCard() {
  const [regular, semibold] = await Promise.all([
    fetch(new URL("./fonts/ibm-plex-sans-condensed-latin-400-normal.woff", import.meta.url)).then((r) => r.arrayBuffer()),
    fetch(new URL("./fonts/ibm-plex-sans-condensed-latin-600-normal.woff", import.meta.url)).then((r) => r.arrayBuffer()),
  ]);
  const ROW = 46;
  const LABEL_W = 190;
  const TRACE_W = 800;
  return new ImageResponse(
    (
      <div
        style={{
          background: C.bg,
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          padding: "56px 72px 44px",
          fontFamily: "Plex",
          color: C.title,
        }}
      >
        <div style={{ display: "flex", fontSize: 28 }}>
          <span style={{ color: C.lead, fontWeight: 400 }}>My Friend Is</span>
          <span style={{ fontWeight: 600, marginLeft: 8 }}>AI</span>
        </div>
        <div style={{ display: "flex", fontSize: 56, fontWeight: 600, lineHeight: 1.08, marginTop: 18, letterSpacing: "-0.01em" }}>
          When the AI is the relationship, not the tool
        </div>
        <div style={{ display: "flex", flexDirection: "column", marginTop: 36, position: "relative" }}>
          {CHANNELS.map(([id, name]) => {
            const v = series(id);
            const max = Math.max(...v, 0.001);
            const pts = v
              .map((y, i) => `${(i / (v.length - 1)) * TRACE_W},${ROW - 5 - (y / max) * (ROW - 10)}`)
              .join(" ");
            return (
              <div key={id} style={{ display: "flex", height: ROW, alignItems: "center", borderTop: `1px solid ${C.grid}` }}>
                <span style={{ width: LABEL_W, fontSize: 19, fontWeight: 600 }}>{name}</span>
                <svg width={TRACE_W} height={ROW} viewBox={`0 0 ${TRACE_W} ${ROW}`}>
                  <polyline points={pts} fill="none" stroke={C.title} strokeWidth={2} strokeLinejoin="round" />
                </svg>
                <span style={{ marginLeft: 16, fontSize: 19, color: C.title }}>{v[v.length - 1].toFixed(1)}</span>
              </div>
            );
          })}
          <div style={{ display: "flex", height: 0, borderTop: `1px solid ${C.grid}` }} />
          <div
            style={{
              position: "absolute",
              left: LABEL_W + (LAST_MONTHS.indexOf(EVENT_MONTH) / (LAST_MONTHS.length - 1)) * TRACE_W,
              top: 0,
              width: 0,
              height: ROW * CHANNELS.length,
              borderLeft: `2px dashed ${C.event}`,
            }}
          />
        </div>
        <div style={{ display: "flex", marginTop: "auto", fontSize: 19, color: C.lead }}>
          {`myfriendisai.com — ${POST_COUNT} posts collected from ${COMMUNITY_COUNT} Reddit communities`}
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [
        { name: "Plex", data: regular, weight: 400, style: "normal" },
        { name: "Plex", data: semibold, weight: 600, style: "normal" },
      ],
    },
  );
}

export default async function Image() {
  if (SITE_THEME === "paper") return paperCard();
  return new ImageResponse(
    (
      <div
        style={{
          background: C.bg,
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "60px 80px",
        }}
      >
        {/* Site name */}
        <div
          style={{
            display: "flex",
            fontSize: 32,
            letterSpacing: "-0.02em",
            marginBottom: 24,
          }}
        >
          <span style={{ color: C.ogMuted, fontWeight: 300 }}>
            My Friend Is
          </span>
          <span style={{ color: C.title, fontWeight: 700, marginLeft: 8 }}>
            AI
          </span>
        </div>

        {/* Tagline */}
        <div
          style={{
            fontSize: 48,
            fontWeight: 600,
            color: C.title,
            textAlign: "center",
            lineHeight: 1.2,
            marginBottom: 48,
          }}
        >
          When the AI is the relationship, not the tool
        </div>

        {/* Theme pills */}
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", justifyContent: "center" }}>
          {THEMES.map((t) => (
            <div
              key={t.label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "10px 20px",
                borderRadius: 8,
                backgroundColor: C.surface2,
                borderLeft: `3px solid ${t.color}`,
              }}
            >
              <span style={{ fontSize: 18, color: t.color, fontWeight: 500 }}>
                {t.label}
              </span>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div
          style={{
            position: "absolute",
            bottom: 40,
            fontSize: 18,
            color: C.leadAlt,
          }}
        >
          {`myfriendisai.com — ${POST_COUNT} posts collected · ${COMMUNITY_COUNT} Reddit communities tracked`}
        </div>
      </div>
    ),
    { ...size },
  );
}
