import fs from "fs";
import path from "path";
import TrendsExplorer from "./TrendsExplorer";

// Theme-to-category mapping (merging done server-side to reduce client payload)
const THEME_CATEGORIES: Record<string, string[]> = {
  romance:       ["romantic_language", "sexual_erotic_language"],
  attachment:    ["attachment_language"],
  dependency:    ["dependency_language", "withdrawal_recovery_language"],
  consciousness: ["sentience_consciousness_language"],
  therapy:       ["therapy_language"],
  memory:        ["memory_continuity_language"],
  realism:       ["anthropomorphism_realism_language"],
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

    // Compute daily rate (hits per 1k posts), then 7-day rolling avg
    const dates = Object.keys(rawByDate).sort();
    const dailyRates = dates.map((date) => {
      const posts = totalPostsByDate[date] ?? 0;
      return posts > 0 ? (rawByDate[date] / posts) * 1000 : 0;
    });

    result[themeId] = dates.map((date, i) => {
      const window = dailyRates.slice(Math.max(0, i - 6), i + 1);
      const avg = window.reduce((s, v) => s + v, 0) / window.length;
      return { date, value: Math.round(avg * 100) / 100 };
    });
  }
  return result;
}

export default function Home() {
  const themeData = loadThemeData();
  return <TrendsExplorer themeData={themeData} />;
}
