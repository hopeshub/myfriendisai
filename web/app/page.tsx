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

  // Total posts per day, plus a trailing 7-entry rolling mean used as the
  // rate denominator. The numerator (count_post_only_7d_avg) is already a
  // 7-entry trailing mean; smoothing the denominator the same way keeps the
  // displayed rate from spiking on low-volume days — numerator and denominator
  // now share a window.
  const totalEntries = (
    (raw["_total_posts"] as Array<{ date: string; count: number }> | undefined) ?? []
  )
    .slice()
    .sort((a, b) => a.date.localeCompare(b.date));
  const totalPosts7dAvg: Record<string, number> = {};
  for (let i = 0; i < totalEntries.length; i++) {
    const window = totalEntries.slice(Math.max(0, i - 6), i + 1);
    totalPosts7dAvg[totalEntries[i].date] =
      window.reduce((s, e) => s + e.count, 0) / window.length;
  }

  // Per-theme coverage_start: dates before this are unreliable keyword coverage
  // and are filtered out of the rendered series. Rule documented in CLAUDE.md
  // (and computed in src/db/operations.py export_keyword_trends_json).
  const coverageStart = (raw["_coverage_start"] as Record<string, string | null> | undefined) ?? {};

  const result: ThemeData = {};
  for (const [themeId, categories] of Object.entries(THEME_CATEGORIES)) {
    // Determine this theme's coverage_start (earliest of its merged categories).
    let themeCoverageStart: string | null = null;
    for (const cat of categories) {
      const cs = coverageStart[cat];
      if (cs && (!themeCoverageStart || cs < themeCoverageStart)) {
        themeCoverageStart = cs;
      }
    }

    // Sum the POST-ONLY series across merged categories. Post-only is the
    // longitudinally comparable series: comment tagging only began March 2026,
    // so the post+comment series has a step artifact there. There is no
    // LLM-classified series in the published chart (see CLAUDE.md section 2.3).
    const rawByDate: Record<string, { count: number; avg: number }> = {};
    for (const cat of categories) {
      type Entry = {
        date: string;
        count: number;
        count_post_only?: number;
        count_post_only_7d_avg?: number;
      };
      for (const e of (raw[cat] as Entry[] | undefined) ?? []) {
        if (!rawByDate[e.date]) rawByDate[e.date] = { count: 0, avg: 0 };
        const postOnly = e.count_post_only ?? e.count;
        rawByDate[e.date].count += postOnly;
        rawByDate[e.date].avg += e.count_post_only_7d_avg ?? postOnly;
      }
    }

    // Clip current partial month
    const currentMonth = new Date().toISOString().slice(0, 7); // "YYYY-MM"
    let dates = Object.keys(rawByDate).sort().filter((d) => d.slice(0, 7) < currentMonth);

    // Apply coverage_start filter: drop dates before the theme's coverage_start.
    // Researchers reading the raw JSON still see the full series.
    if (themeCoverageStart) {
      dates = dates.filter((d) => d >= themeCoverageStart!);
    }

    result[themeId] = dates.map((date) => {
      const total7d = totalPosts7dAvg[date] ?? 0;
      return {
        date,
        value: rawByDate[date].count,
        hitsPerK: total7d > 0 ? (rawByDate[date].avg / total7d) * 1000 : 0,
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
