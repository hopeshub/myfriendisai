"use client";

import { useState } from "react";
import type { ThemeData } from "./themeData";
import { useBreakpoint } from "./useBreakpoint";
import TrendAtlas from "./TrendAtlas";
import { measure } from "./styles";

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
      {/* Section header — the page masthead lives in page.tsx; this is §3. */}
      <div className="mb-4">
        <h2
          className="text-xl sm:text-2xl font-semibold text-[#F8FAFC] mb-2"
          style={{ maxWidth: measure }}
        >
          How the conversation shifts inside them
        </h2>
        <p
          className="text-sm sm:text-base text-[#94A3B8]"
          style={{ maxWidth: measure }}
        >
          Six recurring themes, and how often each one&apos;s language surfaces
          in posts across these communities, month by month.
        </p>
      </div>

      {/* Community-scope toggle — CharacterAI dominates the post denominator
          and swings on its own platform lifecycle, which mechanically moves
          every theme rate. Excluding it shows the rate within the dedicated
          communities. See docs/characterai_composition_fault_2026-05-16.md. */}
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <span style={{ fontSize: 12, color: "#64748B" }}>Communities:</span>
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
              color: scope === s ? "#F8FAFC" : "#94A3B8",
              border: `1px solid ${scope === s ? "#2A2D3A" : "transparent"}`,
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <p className="mb-3" style={{ fontSize: 12, color: "#64748B", maxWidth: measure }}>
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
              color: timeRange === range ? "#F8FAFC" : "#94A3B8",
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

      {/* Methodology + how-to-read — consolidated into one note, said once. */}
      <p
        className="text-center"
        style={{
          fontSize: isMobileStrip ? 14 : 12,
          color: "#8293A6",
          marginTop: 16,
          marginBottom: 8,
          maxWidth: measure,
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        Each panel is one theme&apos;s rate of validated-keyword mentions per
        1,000 posts, by month &mdash; counted by keyword, no AI classification.
        The panels have independent scales: read each line&apos;s shape and
        timing, not its height against another.{" "}
        <a
          href="/about#verification"
          style={{ color: "#94A3B8", textDecoration: "underline" }}
        >
          How this works, and how to read it
        </a>
        .
      </p>
    </div>
  );
}
