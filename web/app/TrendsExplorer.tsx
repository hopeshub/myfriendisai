"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import type { ThemeData } from "./themeData";
import { useBreakpoint } from "./useBreakpoint";
import { measure } from "./styles";

// Lazy-loaded so the atlas is not in the homepage's initial JS bundle.
// The chart measures its container width on the client and cannot
// server-render at a real width anyway, so ssr:false loses nothing.
const TrendAtlas = dynamic(() => import("./TrendAtlas"), {
  ssr: false,
  // Holds the space of the default view (1Y, three events) so nothing below
  // jumps when the chunk lands: six strips + marker band + axis, with the
  // event legend above the stack on desktop and below it at ≤768px. Heights
  // measured from the rendered atlas: the legend wraps an extra line below
  // 360px and between 769 and 800px.
  loading: () => (
    <div className="min-h-[815px] min-[360px]:min-h-[773px] min-[540px]:min-h-[725px] min-[769px]:min-h-[580px] min-[801px]:min-h-[563.5px]" />
  ),
});

type TimeRange = "6M" | "1Y" | "2Y" | "ALL";

type Props = { themeData: ThemeData; themeDataExclCai: ThemeData };
type Scope = "all" | "excl-cai";

export default function TrendsExplorer({ themeData, themeDataExclCai }: Props) {
  const [timeRange, setTimeRange] = useState<TimeRange>("1Y");
  const [scope, setScope] = useState<Scope>("all");
  const { isMobileStrip: rawMobileStrip } = useBreakpoint();
  // Default to desktop during SSR/hydration to avoid layout flash
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
      {/* Community scope — a segmented control, deliberately styled as a
          mode switch (not a loose filter like the time range below it):
          toggling r/CharacterAI is a core methodological choice, not a
          cosmetic option. */}
      <div className="flex items-center gap-2.5 mb-2 flex-wrap">
        <span style={{ fontSize: isMobileStrip ? 14 : 12, color: "#7E8B9E" }}>
          Communities:
        </span>
        <div
          role="group"
          aria-label="Community scope"
          style={{
            display: "inline-flex",
            padding: 2,
            borderRadius: 8,
            border: "1px solid #2A2D3A",
            backgroundColor: "#13151C",
          }}
        >
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
              className="min-h-11 md:min-h-0 px-3 py-1.5 text-sm md:text-xs font-medium rounded-md transition-colors"
              style={{
                backgroundColor: scope === s ? "#252834" : "transparent",
                color: scope === s ? "#F1F4F8" : "#9AA7B8",
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      <p
        className="mb-3"
        style={{ fontSize: isMobileStrip ? 14 : 12, color: "#7E8B9E", maxWidth: measure }}
      >
        {scope === "all"
          ? "r/CharacterAI is the largest community in this set — 70–85% of every post counted here through most of 2025, and under half today — and it rises and falls on its own platform lifecycle. Switch it off to see each rate within the dedicated companionship communities."
          : "r/CharacterAI removed from both the keyword counts and the denominator. These are the rates within the dedicated companionship and recovery communities — most of the rises hold. With fewer posts to count, the therapy and addiction lines start later in this view: the earlier months exist but are too thin to chart."}
      </p>

      {/* Time range selector */}
      <div className="flex gap-1 mb-3">
        {(["6M", "1Y", "2Y", "ALL"] as TimeRange[]).map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            aria-pressed={timeRange === range}
            aria-label={`Show ${range === "ALL" ? "all time" : `last ${range}`}`}
            className="flex-1 sm:flex-none h-11 md:h-auto px-3 py-1 text-sm md:text-xs font-medium rounded-md transition-colors"
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

      {/* Trend Atlas — six channels on one time axis. A plain section, not
          a figure/role="img": the strips are links and must stay
          discoverable in the accessibility tree (role="img" would collapse
          them into one opaque image). */}
      <section aria-label="Trend atlas: six AI-companionship themes over time">
        <p className="sr-only">
          Six line charts stacked on one shared time axis, one strip per theme
          (romance, sex/erotic roleplay, consciousness, therapy, addiction,
          rupture), each showing that theme&apos;s rate of validated-keyword
          mentions per 1,000 posts by month across AI-companionship Reddit
          communities. Each strip is scaled to its own range; line heights are
          not comparable between themes because keyword detection sensitivity
          differs by theme. Each strip begins at its own coverage-start date,
          and is a link to that theme&apos;s page.
        </p>
        <TrendAtlas
          themeData={activeData}
          timeRange={timeRange}
          isMobileStrip={isMobileStrip}
        />
      </section>

      {/* Methodology + how-to-read — a quiet caption: short prose lead-in
          followed by the three reading rules as a bullet list. */}
      <div
        style={{
          fontSize: isMobileStrip ? 14 : 12,
          color: "#7E8B9E",
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
            Each strip is one theme&apos;s rate of validated-keyword mentions
            per 1,000 posts, by month &mdash; counted by keyword, no AI
            classification.
          </li>
          <li>
            Each strip is scaled to itself, like the gain on a recorder: read
            a line against its own past, never its height against another
            strip.
          </li>
          <li>
            Every line is a floor. The keywords are precision-first &mdash;
            they miss far more theme-relevant posts than they catch.
          </li>
          <li>
            The consciousness and therapy strips count only a few dozen posts a
            month, so a single month&apos;s rise or fall there is usually
            noise &mdash; read those two over half a year or more.
          </li>
          <li>
            Platform events are marked across all six strips as a shared
            time reference &mdash; watch which lines move with them and which
            don&apos;t. Only rupture reliably does.
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
