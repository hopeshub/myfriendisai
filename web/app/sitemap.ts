import type { MetadataRoute } from "next";
import { getSubreddits } from "@/lib/data";
import { THEMES } from "./themes";

export default function sitemap(): MetadataRoute.Sitemap {
  const subreddits = getSubreddits();
  const now = new Date().toISOString();

  const communityPages = subreddits.map((s) => ({
    url: `https://myfriendisai.com/communities/${s.subreddit}`,
    lastModified: now,
    changeFrequency: "daily" as const,
    priority: 0.6,
  }));

  // The six theme pages — core content, second only to the homepage.
  const themePages = THEMES.map((t) => ({
    url: `https://myfriendisai.com/theme/${t.id}`,
    lastModified: now,
    changeFrequency: "daily" as const,
    priority: 0.8,
  }));

  return [
    {
      url: "https://myfriendisai.com",
      lastModified: now,
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: "https://myfriendisai.com/about",
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.8,
    },
    {
      url: "https://myfriendisai.com/communities",
      lastModified: now,
      changeFrequency: "daily",
      priority: 0.7,
    },
    ...themePages,
    ...communityPages,
  ];
}
