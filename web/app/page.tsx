import fs from "fs";
import path from "path";
import TrendsExplorer from "./TrendsExplorer";

// Theme-to-category mapping (merging done server-side to reduce client payload)
const THEME_CATEGORIES: Record<string, string[]> = {
  therapy:       ["therapy"],
  consciousness: ["consciousness"],
  addiction:     ["addiction"],
  romance:       ["romance"],
  sexual_erp:    ["sexual_erp"],
  rupture:       ["rupture"],
};

export type ThemeDataPoint = { date: string; value: number };
export type ThemeData = Record<string, ThemeDataPoint[]>;

function loadThemeData(): ThemeData {
  const filePath = path.join(process.cwd(), "data", "keyword_trends.json");
  if (!fs.existsSync(filePath)) return {};

  const raw: Record<string, Array<{ date: string; count: number; count_7d_avg?: number }>> =
    JSON.parse(fs.readFileSync(filePath, "utf8"));

  // Total posts per day for normalization
  const totalPostsByDate: Record<string, number> = {};
  for (const e of raw["_total_posts"] ?? []) {
    totalPostsByDate[e.date] = e.count;
  }

  const result: ThemeData = {};
  for (const [themeId, categories] of Object.entries(THEME_CATEGORIES)) {
    // Sum raw daily hits across merged categories
    const rawByDate: Record<string, number> = {};
    for (const cat of categories) {
      for (const e of raw[cat] ?? []) {
        rawByDate[e.date] = (rawByDate[e.date] ?? 0) + e.count;
      }
    }

    // Clip current partial month
    const currentMonth = new Date().toISOString().slice(0, 7); // "YYYY-MM"
    const dates = Object.keys(rawByDate).sort().filter((d) => d.slice(0, 7) < currentMonth);

    result[themeId] = dates.map((date) => ({
      date,
      value: rawByDate[date],
    }));
  }
  return result;
}

export default function Home() {
  const themeData = loadThemeData();
  return <TrendsExplorer themeData={themeData} />;
}
