import fs from "fs";
import path from "path";
import TrendsExplorer from "./TrendsExplorer";
import type { KeywordDetailsData } from "./TransparencyPanel";

// Theme-to-category mapping (merging done server-side to reduce client payload)
const THEME_CATEGORIES: Record<string, string[]> = {
  therapy:       ["therapy"],
  consciousness: ["consciousness"],
  addiction:     ["addiction"],
  romance:       ["romance"],
  sexual_erp:    ["sexual_erp"],
  rupture:       ["rupture"],
};

export type ThemeDataPoint = { date: string; value: number; hitsPerK: number };
export type ThemeData = Record<string, ThemeDataPoint[]>;

// Default chart series. Flip to "count_llm_verified" after LLM calibration
// passes (see scripts/llm_calibration_check.py). The LLM-verified series
// gracefully degrades to count_post_only on dates with no LLM verdicts, so
// historical data is preserved when the flip happens.
const DEFAULT_SERIES: "count" | "count_llm_verified" = "count";

function loadThemeData(): ThemeData {
  const filePath = path.join(process.cwd(), "data", "keyword_trends.json");
  if (!fs.existsSync(filePath)) return {};

  let raw: Record<string, unknown>;
  try {
    raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (e) {
    console.error("Failed to parse keyword_trends.json:", e);
    return {};
  }

  // Total posts per day for normalization
  const totalPostsByDate: Record<string, number> = {};
  for (const e of (raw["_total_posts"] as Array<{ date: string; count: number }> | undefined) ?? []) {
    totalPostsByDate[e.date] = e.count;
  }

  // Per-theme coverage_start: dates before this are unreliable keyword coverage
  // and are filtered out of the rendered series. Rule documented in CLAUDE.md
  // (and computed in src/db/operations.py export_keyword_trends_json).
  const coverageStart = (raw["_coverage_start"] as Record<string, string | null> | undefined) ?? {};

  const result: ThemeData = {};
  for (const [themeId, categories] of Object.entries(THEME_CATEGORIES)) {
    // Determine this theme's coverage_start (earliest of its merged categories).
    // Themes currently map 1:1 to categories, but if that changes the earliest
    // coverage gives the most data while still respecting each category's floor.
    let themeCoverageStart: string | null = null;
    for (const cat of categories) {
      const cs = coverageStart[cat];
      if (cs && (!themeCoverageStart || cs < themeCoverageStart)) {
        themeCoverageStart = cs;
      }
    }

    // Sum raw daily hits and 7-day averages across merged categories.
    // DEFAULT_SERIES controls whether we use raw keyword counts or the
    // LLM-verified subset (where the LLM was run; gracefully falls back
    // to count_post_only on dates with no LLM verdicts).
    const countKey = DEFAULT_SERIES;
    const avgKey =
      DEFAULT_SERIES === "count_llm_verified"
        ? "count_llm_verified_7d_avg"
        : "count_7d_avg";
    const rawByDate: Record<string, { count: number; avg: number }> = {};
    for (const cat of categories) {
      type Entry = {
        date: string;
        count: number;
        count_7d_avg?: number;
        count_llm_verified?: number;
        count_llm_verified_7d_avg?: number;
      };
      for (const e of (raw[cat] as Entry[] | undefined) ?? []) {
        if (!rawByDate[e.date]) rawByDate[e.date] = { count: 0, avg: 0 };
        rawByDate[e.date].count += (e[countKey] ?? e.count) as number;
        rawByDate[e.date].avg += (e[avgKey] ?? e.count_7d_avg ?? e.count) as number;
      }
    }

    // Clip current partial month
    const currentMonth = new Date().toISOString().slice(0, 7); // "YYYY-MM"
    let dates = Object.keys(rawByDate).sort().filter((d) => d.slice(0, 7) < currentMonth);

    // Apply coverage_start filter: drop dates before the theme's coverage_start.
    // Researchers reading the raw JSON still see the full series; only the
    // rendered chart respects this filter.
    if (themeCoverageStart) {
      dates = dates.filter((d) => d >= themeCoverageStart!);
    }

    result[themeId] = dates.map((date) => {
      const total = totalPostsByDate[date] ?? 0;
      return {
        date,
        value: rawByDate[date].count,
        hitsPerK: total > 0 ? (rawByDate[date].avg / total) * 1000 : 0,
      };
    });
  }
  return result;
}

function loadKeywordDetails(): KeywordDetailsData {
  const filePath = path.join(process.cwd(), "data", "keyword_details.json");
  if (!fs.existsSync(filePath)) return {};
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (e) {
    console.error("Failed to parse keyword_details.json:", e);
    return {};
  }
}

export default function Home() {
  const themeData = loadThemeData();
  const keywordDetails = loadKeywordDetails();
  return (
    <TrendsExplorer themeData={themeData} keywordDetails={keywordDetails} />
  );
}
