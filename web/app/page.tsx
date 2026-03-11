import fs from "fs";
import path from "path";
import TrendsExplorer from "./TrendsExplorer";

// Theme-to-category mapping (merging done server-side to reduce client payload)
const THEME_CATEGORIES: Record<string, string[]> = {
  romance:       ["romantic_language", "sexual_erotic_language"],
  attachment:    ["attachment_language"],
  dependency:    ["dependency_language", "withdrawal_recovery_language"],
  consciousness: ["sentience_consciousness_language"],
  substitution:  ["substitution_language"],
  therapy:       ["therapy_language"],
  memory:        ["memory_continuity_language"],
  realism:       ["anthropomorphism_realism_language"],
};

export type ThemeDataPoint = { date: string; value: number };
export type ThemeData = Record<string, ThemeDataPoint[]>;

function loadThemeData(): ThemeData {
  const filePath = path.join(process.cwd(), "data", "keyword_trends.json");
  if (!fs.existsSync(filePath)) return {};

  const raw: Record<string, Array<{ date: string; count: number; count_7d_avg: number }>> =
    JSON.parse(fs.readFileSync(filePath, "utf8"));

  const result: ThemeData = {};
  for (const [themeId, categories] of Object.entries(THEME_CATEGORIES)) {
    const byDate: Record<string, number> = {};
    for (const cat of categories) {
      for (const e of raw[cat] ?? []) {
        byDate[e.date] = (byDate[e.date] ?? 0) + e.count_7d_avg;
      }
    }
    result[themeId] = Object.entries(byDate)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, value]) => ({ date, value: Math.round(value * 10) / 10 }));
  }
  return result;
}

export default function Home() {
  const themeData = loadThemeData();
  return <TrendsExplorer themeData={themeData} />;
}
