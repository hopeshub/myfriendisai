"use client";

import { useState } from "react";
import type { ThemeData } from "./themeData";
import { useBreakpoint } from "./useBreakpoint";
import TrendAtlas from "./TrendAtlas";

type TimeRange = "6M" | "1Y" | "2Y" | "ALL";

type Props = { themeData: ThemeData };

export default function TrendsExplorer({ themeData }: Props) {
  const [timeRange, setTimeRange] = useState<TimeRange>("1Y");
  const { bp: rawBp, isMobileStrip: rawMobileStrip } = useBreakpoint();
  // Default to desktop during SSR/hydration to avoid layout flash
  const bp = rawBp ?? "desktop";
  const isMobileStrip = rawMobileStrip ?? false;

  return (
    <div>
      {/* Section header — the page masthead lives in page.tsx; this is §3. */}
      <div className="mb-4">
        <h2 className="text-xl sm:text-2xl font-semibold text-[#F8FAFC] mb-1">
          How the conversation shifts inside them
        </h2>
        <p
          className="text-sm sm:text-base text-[#94A3B8]"
          style={{ maxWidth: 700 }}
        >
          Six recurring themes, and how often each one&apos;s language surfaces
          in posts across these communities, month by month.
        </p>
      </div>

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
        <TrendAtlas themeData={themeData} timeRange={timeRange} bp={bp} />
      </section>

      {/* Methodology + how-to-read — consolidated into one note, said once. */}
      <p
        className="text-center"
        style={{
          fontSize: isMobileStrip ? 14 : 12,
          color: "#8293A6",
          marginTop: 16,
          marginBottom: 8,
          maxWidth: 760,
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
