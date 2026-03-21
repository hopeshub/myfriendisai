import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "My Friend Is AI — Tracking AI companion discourse on Reddit";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const THEMES = [
  { emoji: "\u{1F495}", label: "Romance", color: "#FF69B4" },
  { emoji: "\u{1F51E}", label: "Sex / ERP", color: "#dc2625" },
  { emoji: "\u{1F9E0}", label: "Consciousness", color: "#A855F7" },
  { emoji: "\u{1FAC2}", label: "Therapy", color: "#3B82F6" },
  { emoji: "\u{1F48A}", label: "Addiction", color: "#fd7112" },
  { emoji: "\u{1F940}", label: "Rupture", color: "#22C55E" },
];

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: "#0F1117",
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
          <span style={{ color: "rgba(255,255,255,0.5)", fontWeight: 300 }}>
            My Friend Is
          </span>
          <span style={{ color: "#F8FAFC", fontWeight: 700, marginLeft: 8 }}>
            AI
          </span>
        </div>

        {/* Tagline */}
        <div
          style={{
            fontSize: 48,
            fontWeight: 600,
            color: "#F8FAFC",
            textAlign: "center",
            lineHeight: 1.2,
            marginBottom: 48,
          }}
        >
          How are people talking about AI companionship?
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
                backgroundColor: "#1A1D27",
                borderLeft: `3px solid ${t.color}`,
              }}
            >
              <span style={{ fontSize: 20 }}>{t.emoji}</span>
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
            color: "#94A3B8",
          }}
        >
          myfriendisai.com — ~3.8M posts from 27 Reddit communities
        </div>
      </div>
    ),
    { ...size },
  );
}
