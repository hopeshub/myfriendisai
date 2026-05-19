import fs from "fs";
import path from "path";

// Server-side loaders for the keyword trend data. Shared by the homepage
// (app/page.tsx) and the per-theme pages (app/theme/[id]/page.tsx) so the
// loading logic lives in exactly one place.

// ── Shapes of data/keyword_details.json ──────────────────────────────────────
export type SamplePost = {
  title: string;
  subreddit: string;
  date: string;
  id: string;
  // A short body excerpt around the matched keyword, or null when the keyword
  // matched the title instead (export_keyword_details.py).
  excerpt: string | null;
};
export type KeywordEntry = {
  term: string;
  hits: number;
  precision: number | null;
  // Display status from the keyword's YAML annotation: "audit-gate-fail",
  // "researcher-accepted", "low-volume", or null for a clean keyword.
  status: string | null;
  sample_posts: SamplePost[];
};
export type SubredditEntry = { name: string; hits: number; pct: number };
export type CategoryDetail = {
  keywords: KeywordEntry[];
  subreddits: SubredditEntry[];
  total_hits: number;
  unique_posts: number;
};
export type KeywordDetailsData = Record<string, CategoryDetail>;

// Theme-to-category mapping (merging done server-side to reduce client payload)
const THEME_CATEGORIES: Record<string, string[]> = {
  therapy:       ["therapy"],
  consciousness: ["consciousness"],
  addiction:     ["addiction"],
  romance:       ["romance"],
  sexual_erp:    ["sexual_erp"],
  rupture:       ["rupture"],
};

// One point per MONTH (date is "YYYY-MM-01"). The charts only ever render the
// monthly mean of the per-1k rate, so loadThemeData aggregates daily → monthly
// server-side rather than shipping ~5,600 daily points per theme to the client.
export type ThemeDataPoint = { date: string; value: number; hitsPerK: number };
export type ThemeData = Record<string, ThemeDataPoint[]>;

// `filename` selects the source: "keyword_trends.json" (all communities, the
// published default) or "composition_trends.json" (the ex-CharacterAI view —
// see docs/characterai_composition_fault_2026-05-16.md). Both files share an
// identical schema, so the same loader serves both.
export function loadThemeData(filename: string = "keyword_trends.json"): ThemeData {
  const filePath = path.join(process.cwd(), "data", filename);
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
  // and are filtered out of the rendered series. Rule computed in
  // src/db/operations.py export_keyword_trends_json.
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
    // LLM-classified series in the published chart.
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

    // Aggregate daily → monthly. The atlas and the per-theme chart both render
    // the monthly mean of the daily per-1k rate (their monthlySeries() helper),
    // so doing it here ships ~36 points per theme instead of ~5,600 — the chart
    // is pixel-identical (monthlySeries on already-monthly data is a no-op).
    const monthly: Record<
      string,
      { rateSum: number; n: number; count: number }
    > = {};
    for (const date of dates) {
      const total7d = totalPosts7dAvg[date] ?? 0;
      const hitsPerK = total7d > 0 ? (rawByDate[date].avg / total7d) * 1000 : 0;
      const m = date.slice(0, 7) + "-01";
      if (!monthly[m]) monthly[m] = { rateSum: 0, n: 0, count: 0 };
      monthly[m].rateSum += hitsPerK;
      monthly[m].n += 1;
      monthly[m].count += rawByDate[date].count;
    }
    result[themeId] = Object.keys(monthly)
      .sort()
      .map((m) => ({
        date: m,
        value: monthly[m].count,
        hitsPerK: monthly[m].rateSum / monthly[m].n,
      }));
  }
  return result;
}

export function loadKeywordDetails(): KeywordDetailsData {
  const filePath = path.join(process.cwd(), "data", "keyword_details.json");
  if (!fs.existsSync(filePath)) return {};
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (e) {
    console.error("Failed to parse keyword_details.json:", e);
    return {};
  }
}

// ── Community composition over time ──────────────────────────────────────────
// Per-community monthly post volume, from community_activity.json. §1 shows
// r/CharacterAI on its own (60-90% of all volume — it would crush a shared
// scale) and every other companionship community as a stacked area, so the
// field's turnover is visible: r/replika's 2023 dominance collapsing while a
// new generation rises to fill a roughly flat total.

export type CaiPoint = { month: string; value: number };
export type CompositionPoint = {
  month: string;
  replika: number;
  chai: number;
  nomi: number;
  kindroid: number;
  chatgptcomplaints: number;
  myboyfriendisai: number;
  other: number;
};
export type CommunityComposition = {
  characterai: CaiPoint[];
  composition: CompositionPoint[];
};

export function loadCommunityComposition(): CommunityComposition {
  const filePath = path.join(process.cwd(), "data", "community_activity.json");
  if (!fs.existsSync(filePath)) return { characterai: [], composition: [] };
  let raw: { months: string[]; activity: Record<string, number[]> };
  try {
    raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (e) {
    console.error("Failed to parse community_activity.json:", e);
    return { characterai: [], composition: [] };
  }
  const months = raw.months ?? [];
  const activity = raw.activity ?? {};
  if (months.length === 0) return { characterai: [], composition: [] };

  const at = (sub: string, i: number) => activity[sub]?.[i] ?? 0;

  // "Other" = every community in the file that is not r/CharacterAI (its own
  // panel), not one of the six named bands, not an NSFW sub dropped from
  // keyword tracking, and not a T0 general-AI sub. New keyword communities
  // therefore fold into "Other" automatically.
  const namedOrExcluded = new Set([
    "CharacterAI", "replika", "ChaiApp", "NomiAI", "KindroidAI",
    "ChatGPTcomplaints", "MyBoyfriendIsAI",
    "AIGirlfriend", "ChatGPTNSFW", "SpicyChatAI",
    "ChatGPT", "OpenAI", "ClaudeAI", "claudexplorers", "singularity",
  ]);
  const otherSubs = Object.keys(activity).filter((s) => !namedOrExcluded.has(s));

  const characterai: CaiPoint[] = months.map((m, i) => ({
    month: m,
    value: at("CharacterAI", i),
  }));
  const composition: CompositionPoint[] = months.map((m, i) => ({
    month: m,
    replika: at("replika", i),
    chai: at("ChaiApp", i),
    nomi: at("NomiAI", i),
    kindroid: at("KindroidAI", i),
    chatgptcomplaints: at("ChatGPTcomplaints", i),
    myboyfriendisai: at("MyBoyfriendIsAI", i),
    other: otherSubs.reduce((s, sub) => s + at(sub, i), 0),
  }));
  return { characterai, composition };
}

// ── Recovery-community volume ────────────────────────────────────────────────
// Monthly post volume for the four T3 recovery / quitting communities, read
// from snapshots.json (posts_today, recomputed from the posts table). These
// communities are the counter-current to AI companionship: organized quitting
// and peer support. See the recovery section on the homepage.
// The two genuine recovery communities. r/AI_Addiction (too small) and
// r/CharacterAIrunaways (migration, not recovery) are deliberately excluded —
// see recoveryData.ts.
export const RECOVERY_SUBS = [
  "ChatbotAddiction",
  "Character_AI_Recovery",
] as const;

export type RecoveryVolumePoint = { month: string; [sub: string]: string | number };

export function loadRecoveryVolume(): RecoveryVolumePoint[] {
  const filePath = path.join(process.cwd(), "data", "snapshots.json");
  if (!fs.existsSync(filePath)) return [];
  let snaps: Array<{
    subreddit: string;
    snapshot_date: string;
    posts_today: number | null;
  }>;
  try {
    snaps = JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (e) {
    console.error("Failed to parse snapshots.json:", e);
    return [];
  }

  const recovery = new Set<string>(RECOVERY_SUBS);
  const byMonth: Record<string, Record<string, number>> = {};
  for (const s of snaps) {
    if (!recovery.has(s.subreddit)) continue;
    const m = s.snapshot_date.slice(0, 7);
    if (!byMonth[m]) byMonth[m] = {};
    byMonth[m][s.subreddit] =
      (byMonth[m][s.subreddit] ?? 0) + (s.posts_today ?? 0);
  }

  const currentMonth = new Date().toISOString().slice(0, 7);
  return Object.keys(byMonth)
    .sort()
    .filter((m) => m < currentMonth)
    .map((m) => {
      const row: RecoveryVolumePoint = { month: m };
      for (const sub of RECOVERY_SUBS) row[sub] = byMonth[m][sub] ?? 0;
      return row;
    });
}
