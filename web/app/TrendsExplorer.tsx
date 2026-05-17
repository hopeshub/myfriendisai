"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import type { ThemeData } from "./themeData";
import { useBreakpoint } from "./useBreakpoint";
import { measure } from "./styles";

// Lazy-loaded so Recharts is not in the homepage's initial JS bundle.
// ResponsiveContainer cannot server-render at a real width anyway, so the
// SSR'd chart is discarded and re-rendered client-side regardless.
const TrendAtlas = dynamic(() => import("./TrendAtlas"), {
  ssr: false,
  // Responsive: six theme panels — 1 column on mobile, 2 on tablet, 3 on
  // desktop — so the placeholder height must shrink as the grid widens.
  loading: () => (
    <div className="min-h-[1990px] md:min-h-[1110px] lg:min-h-[760px]" />
  ),
});

type TimeRange = "6M" | "1Y" | "2Y" | "ALL";

type Props = { themeData: ThemeData; themeDataExclCai: ThemeData };
type Scope = "all" | "excl-cai";

export default function TrendsExplorer({ themeData, themeDataExclCai }: Props) {
  const [timeRange, setTimeRange] = useState<TimeRange>("1Y");
  const [scope, setScope] = useState<Scope>("all");
  const { bp: rawBp, isMobileStrip: rawMobileStrip } = useBreakpoint();
  // Default to desktop during SSR/hydration to avoid layout flash
  const bp = rawBp ?? "desktop";
  const isMobileStrip = rawMobileStrip ?? false;

  const activeData = scope === "all" ? themeData : themeDataExclCai;

  return (
    <div>
      {/* Section header — the eyebrow, heading, and intro now live in
          page.tsx §3, matching §1/§2/§4. This component starts at the
          community-scope toggle. */}

      {/* Community-scope toggle — CharacterAI dominates the post denominator
          and swings on its own platform lifecycle, which mechanically moves
          every theme rate. Excluding it shows the rate within the dedicated
          communities. See docs/characterai_composition_fault_2026-05-16.md. */}
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <span style={{ fontSize: 12, color: "#6B7689" }}>Communities:</span>
        {(
          [
            ["all", "All tracked"],
            ["excl-cai", "Excluding r/CharacterAI"],
          ] as [Scope, string][]
        ).map(([s, label]) => (
          <button
            key={s}
            onClick={() => setScope(s)}
            aria-pressed={scope === s}
            className="h-9 sm:h-auto px-3 py-1 text-sm sm:text-xs font-medium rounded-md transition-colors"
            style={{
              backgroundColor: scope === s ? "#1A1D27" : "transparent",
              color: scope === s ? "#F1F4F8" : "#9AA7B8",
              border: `1px solid ${scope === s ? "#2A2D3A" : "transparent"}`,
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <p className="mb-3" style={{ fontSize: 12, color: "#6B7689", maxWidth: measure }}>
        {scope === "all"
          ? "r/CharacterAI is roughly three-quarters of every post counted here, and it rises and falls on its own platform lifecycle — switch it off to see each rate within the dedicated companionship communities."
          : "r/CharacterAI removed from both the keyword counts and the denominator. These are the rates within the dedicated companionship and recovery communities — the rises hold, and several are steeper here."}
      </p>

      {/* Time range selector */}
      <div className="flex gap-1 mb-3">
        {(["6M", "1Y", "2Y", "ALL"] as TimeRange[]).map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            aria-pressed={timeRange === range}
            aria-label={`Show ${range === "ALL" ? "all time" : `last ${range}`}`}
            className="flex-1 sm:flex-none h-11 sm:h-auto px-3 py-1 text-sm sm:text-xs font-medium rounded-md transition-colors"
            style={{
              backgroundColor: timeRange === range ? "#1A1D27" : "transparent",
              color: timeRange === range ? "#F1F4F8" : "#9AA7B8",
              border: `1px solid ${timeRange === range ? "#2A2D3A" : "transparent"}`,
            }}
          >
            {range}
          </button>
        ))}
      </div>

      {/* Trend Atlas — small-multiples grid. A plain section, not a
          figure/role="img": the panels are links and must stay discoverable
          in the accessibility tree (role="img" would collapse them into one
          opaque image). */}
      <section aria-label="Trend atlas: six AI-companionship themes over time">
        <p className="sr-only">
          Six small line charts, one per theme (romance, sex/erotic roleplay,
          consciousness, therapy, addiction, rupture), each showing that
          theme&apos;s rate of validated-keyword mentions per 1,000 posts over
          time across AI-companionship Reddit communities. Each panel has its
          own y-axis; line heights are not comparable between themes because
          keyword detection sensitivity differs by theme. Each panel begins at
          its own coverage-start date, and is a link to that theme&apos;s page.
        </p>
        <TrendAtlas themeData={activeData} timeRange={timeRange} bp={bp} />
      </section>

      {/* Methodology + how-to-read — a quiet caption: short prose lead-in
          followed by the three reading rules as a bullet list. */}
      <div
        style={{
          fontSize: isMobileStrip ? 14 : 12,
          color: "#6B7689",
          marginTop: 16,
          marginBottom: 8,
          maxWidth: measure,
          marginLeft: "auto",
          marginRight: "auto",
          lineHeight: 1.6,
        }}
      >
        <p>How to read the atlas:</p>
        <ul
          style={{
            listStyleType: "disc",
            paddingLeft: 18,
            marginTop: 4,
          }}
        >
          <li>
            Each panel is one theme&apos;s rate of validated-keyword mentions
            per 1,000 posts, by month &mdash; counted by keyword, no AI
            classification.
          </li>
          <li>The panels have independent scales.</li>
          <li>
            Read each line&apos;s shape and timing, not its height against
            another.
          </li>
        </ul>
        <p style={{ marginTop: 4 }}>
          <a
            href="/about#verification"
            style={{ color: "#9AA7B8", textDecoration: "underline" }}
          >
            How this works, and how to read it
          </a>
        </p>
      </div>
    </div>
  );
}
