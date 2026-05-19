import type { MetadataRoute } from "next";
import { readFileSync } from "fs";
import { join } from "path";
import { getSubreddits } from "@/lib/data";
import { THEMES } from "./themes";

// Data-driven pages genuinely refresh when the daily export lands — anchor
// their lastModified to the data's currency date, not the build clock, so a
// no-op rebuild doesn't churn every timestamp and erode the sitemap's signal.
function getDataDate(): string {
  try {
    const raw = readFileSync(join(process.cwd(), "data", "site_meta.json"), "utf-8");
    return (JSON.parse(raw) as { date_end: string }).date_end;
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
}

export default function sitemap(): MetadataRoute.Sitemap {
  const subreddits = getSubreddits();
  const dataDate = getDataDate();

  const communityPages = subreddits.map((s) => ({
    url: `https://myfriendisai.com/communities/${s.subreddit}`,
    lastModified: dataDate,
    changeFrequency: "daily" as const,
    priority: 0.6,
  }));

  // The six theme pages — core content, second only to the homepage.
  const themePages = THEMES.map((t) => ({
    url: `https://myfriendisai.com/theme/${t.id}`,
    lastModified: dataDate,
    changeFrequency: "daily" as const,
    priority: 0.8,
  }));

  return [
    {
      url: "https://myfriendisai.com",
      lastModified: dataDate,
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: "https://myfriendisai.com/about",
      lastModified: dataDate,
      changeFrequency: "weekly",
      priority: 0.8,
    },
    {
      url: "https://myfriendisai.com/communities",
      lastModified: dataDate,
      changeFrequency: "daily",
      priority: 0.7,
    },
    ...themePages,
    ...communityPages,
  ];
}
