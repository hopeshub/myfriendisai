"use client";

import { useCallback, useEffect, useState } from "react";
import type { ThemeData } from "./page";
import { type ThemeId } from "./themes";
import { useBreakpoint } from "./useBreakpoint";
import type { KeywordDetailsData } from "./TransparencyPanel";
import BottomSheet from "./BottomSheet";
import TrendAtlas from "./TrendAtlas";
import { THEMES } from "./themes";

type TimeRange = "6M" | "1Y" | "2Y" | "ALL";

type Props = { themeData: ThemeData; keywordDetails: KeywordDetailsData };

export default function TrendsExplorer({ themeData, keywordDetails }: Props) {
  const [detailPanel, setDetailPanel] = useState<ThemeId | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>("1Y");
  const { bp: rawBp, isMobileStrip: rawMobileStrip } = useBreakpoint();
  // Default to desktop during SSR/hydration to avoid layout flash
  const bp = rawBp ?? "desktop";
  const isMobileStrip = rawMobileStrip ?? false;

  const closeDetail = useCallback(() => {
    const triggerId = detailPanel;
    setDetailPanel(null);
    // Restore focus to the panel header that opened it (a11y).
    if (triggerId) {
      requestAnimationFrame(() => {
        document
          .querySelector<HTMLButtonElement>(`[data-theme-trigger="${triggerId}"]`)
          ?.focus();
      });
    }
  }, [detailPanel]);

  // Escape closes the open detail (inline expansion on desktop/tablet, bottom
  // sheet on mobile) and returns focus to the panel that opened it.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && detailPanel) closeDetail();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [detailPanel, closeDetail]);

  return (
    <>
      <div className="max-w-[1536px] mx-auto px-4 sm:px-8 py-4 sm:py-5">
        {/* Headline + measurement contract */}
        <div className="mb-4">
          <h1 className="text-[22px] sm:text-2xl lg:text-3xl font-bold text-[#F8FAFC] mb-1.5">
            How are people talking about AI companionship?
          </h1>
          <p className="text-sm sm:text-base text-[#94A3B8]">
            Six recurring themes in how people talk about AI companions on
            Reddit — romance, sex, consciousness, therapy, addiction, and loss —
            and how each has risen or fallen over time.
          </p>
          <p className="text-xs sm:text-sm text-[#64748B] mt-2">
            Each panel has its own scale (mentions per 1,000 posts) — read a
            line&apos;s <span className="text-[#94A3B8]">shape over time</span>,
            not its height against other themes.
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

        {/* Trend Atlas — small-multiples grid */}
        <figure role="img" aria-labelledby="atlas-caption" className="m-0">
          <figcaption id="atlas-caption" className="sr-only">
            A grid of six small line charts, one per theme (romance, sex/erotic
            roleplay, consciousness, therapy, addiction, rupture), showing each
            theme&apos;s rate of validated-keyword mentions per 1,000 posts over
            time across AI-companionship Reddit communities. Each panel has its
            own y-axis; line heights are not comparable between themes because
            keyword detection sensitivity differs by theme. Each panel begins at
            its own coverage-start date. Event markers note major platform
            changes. Per-theme reliability detail is on the about page.
          </figcaption>
          <TrendAtlas
            themeData={themeData}
            timeRange={timeRange}
            bp={bp}
            selected={detailPanel}
            keywordDetails={keywordDetails}
            onOpenDetail={(id) =>
              setDetailPanel((prev) =>
                prev === id ? null : (id as ThemeId),
              )
            }
          />
        </figure>

        {/* Methodology note */}
        <p
          className="text-center"
          style={{
            fontSize: isMobileStrip ? 14 : 12,
            color: "#8293A6",
            marginTop: 16,
            marginBottom: 8,
          }}
        >
          Each line is the rate of validated-keyword mentions per 1,000 posts
          (7-day smoothed, post text only). The chart uses keyword counts — no
          AI classification. Per-theme reliability varies.{" "}
          <a
            href="/about#verification"
            style={{ color: "#94A3B8", textDecoration: "underline" }}
          >
            Methodology
          </a>{" "}
          ·{" "}
          <a
            href="/about"
            style={{ color: "#94A3B8", textDecoration: "underline" }}
          >
            Theme reliability
          </a>
          .
        </p>
      </div>

      {/* Detail — on desktop/tablet the detail expands inline inside the
          atlas grid (see TrendAtlas); on mobile (single-column grid) it opens
          as a bottom sheet so the strip stays usable above it. */}
      {bp === "mobile" &&
        (() => {
          const panelTheme = detailPanel
            ? THEMES.find((t) => t.id === detailPanel)
            : null;
          const panelData = detailPanel ? keywordDetails[detailPanel] : null;
          if (!panelTheme || !panelData) return null;
          return (
            <BottomSheet
              isOpen={!!detailPanel}
              themeLabel={panelTheme.label}
              themeEmoji={panelTheme.emoji}
              themeTagline={panelTheme.tagline}
              themeColor={panelTheme.color}
              data={panelData}
              onClose={closeDetail}
            />
          );
        })()}
    </>
  );
}
