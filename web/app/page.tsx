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

  let raw: Record<string, Array<{ date: string; count: number; count_7d_avg?: number }>>;
  try {
    raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (e) {
    console.error("Failed to parse keyword_trends.json:", e);
    return {};
  }

  // Total posts per day for normalization
  const totalPostsByDate: Record<string, number> = {};
  for (const e of raw["_total_posts"] ?? []) {
    totalPostsByDate[e.date] = e.count;
  }

  const result: ThemeData = {};
  for (const [themeId, categories] of Object.entries(THEME_CATEGORIES)) {
    // Sum raw daily hits and 7-day averages across merged categories
    const rawByDate: Record<string, { count: number; avg: number }> = {};
    for (const cat of categories) {
      for (const e of raw[cat] ?? []) {
        if (!rawByDate[e.date]) rawByDate[e.date] = { count: 0, avg: 0 };
        rawByDate[e.date].count += e.count;
        rawByDate[e.date].avg += e.count_7d_avg ?? e.count;
      }
    }

    // Clip current partial month
    const currentMonth = new Date().toISOString().slice(0, 7); // "YYYY-MM"
    const dates = Object.keys(rawByDate).sort().filter((d) => d.slice(0, 7) < currentMonth);

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
