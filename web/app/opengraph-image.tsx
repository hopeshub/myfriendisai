import { ImageResponse } from "next/og";
import siteMeta from "../data/site_meta.json";
import subreddits from "../data/subreddits.json";
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

export default async function Image() {
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
