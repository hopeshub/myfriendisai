export type TimelineEvent = {
  date: string;
  label: string;
  emoji: string;
};

export const EVENTS: TimelineEvent[] = [
  {
    date: "2023-02-01",
    label: "Replika removes ERP",
    emoji: "💔",
  },
  {
    date: "2024-05-13",
    label: "GPT-4o launches",
    emoji: "✨",
  },
  {
    date: "2025-08-01",
    label: "First 4o retirement attempt",
    emoji: "📢",
  },
  {
    date: "2025-10-15",
    label: "MIT loneliness study",
    emoji: "📊",
  },
  {
    date: "2026-01-29",
    label: "#Keep4o movement begins",
    emoji: "🚨",
  },
  {
    date: "2026-02-13",
    label: "GPT-4o retired",
    emoji: "💔",
  },
];
