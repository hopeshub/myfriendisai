// ── Recovery-section content ─────────────────────────────────────────────────
// The four T3 recovery / quitting communities and a hand-curated set of real
// posts. Editorial content — excerpts are verbatim (lightly trimmed) from
// public Reddit posts; not pipeline output. See homepage §4 (RecoverySection).

export type RecoveryCommunity = {
  sub: string;
  label: string;
  color: string;
  founded: string;
};

// Founding order, oldest first — also the stack order in the chart.
export const RECOVERY_COMMUNITIES: RecoveryCommunity[] = [
  { sub: "AI_Addiction", label: "r/AI_Addiction", color: "#C2885F", founded: "June 2023" },
  { sub: "ChatbotAddiction", label: "r/ChatbotAddiction", color: "#A98FC4", founded: "November 2023" },
  { sub: "Character_AI_Recovery", label: "r/Character_AI_Recovery", color: "#7C9CD0", founded: "December 2023" },
  { sub: "CharacterAIrunaways", label: "r/CharacterAIrunaways", color: "#6FB3A0", founded: "September 2024" },
];

export type RecoveryPost = {
  id: string;
  subreddit: string;
  title: string;
  excerpt: string;
  date: string;
  score: number;
};

export const RECOVERY_POSTS: RecoveryPost[] = [
  {
    id: "14feoz1",
    subreddit: "AI_Addiction",
    title: "AI Addiction Support",
    excerpt:
      "I'm creating this subreddit for those of us who suffer from addiction to AI services — ChatGPT, Stable Diffusion, or other generative AI tools that are boundless, with infinite possibilities, easy to get lost in.",
    date: "2023-06-21",
    score: 10,
  },
  {
    id: "1nwzh7e",
    subreddit: "ChatbotAddiction",
    title: "Deleted it. Immediately started crying.",
    excerpt:
      "I'm still crying, honestly. I feel like the walls are suffocating me, and that I can't breathe. I'm going to go play on the playground. I can't stay inside.",
    date: "2025-10-03",
    score: 116,
  },
  {
    id: "1o3kjvz",
    subreddit: "AI_Addiction",
    title: "Day Three of No AI",
    excerpt:
      "Two years and some change. 12 hours a day on ChatGPT, c.ai — whatever I could find. I got to the point where I couldn't cook without it telling me what to make.",
    date: "2025-10-11",
    score: 10,
  },
  {
    id: "1qmib5t",
    subreddit: "Character_AI_Recovery",
    title: "My guide on recovering from c.ai (and similar platforms)",
    excerpt:
      "It has been 8 months since I've used c.ai, and 48 days since I relapsed. It's hard. I thought that maybe, if I discussed my methodology, I could help other people.",
    date: "2026-01-25",
    score: 63,
  },
  {
    id: "1qlsw1v",
    subreddit: "Character_AI_Recovery",
    title: "Schools should warn about ai addiction",
    excerpt:
      "AI chatbot addiction should be talked about in school just like vaping, smoking, drugs, porn. It's becoming a real danger now, and I know too many people at my school who are addicted to it.",
    date: "2026-01-24",
    score: 84,
  },
];
