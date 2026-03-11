export type Lens = {
  id: string;
  label: string;
  emoji: string;
  keywordCategories: string[];
};

export const LENSES: Lens[] = [
  {
    id: "growth",
    label: "Growth",
    emoji: "📈",
    keywordCategories: [],
  },
  {
    id: "romance",
    label: "Romance",
    emoji: "💕",
    keywordCategories: ["relationship_language", "attachment_language"],
  },
  {
    id: "addiction",
    label: "Addiction",
    emoji: "🔁",
    keywordCategories: ["dependency_language", "withdrawal_relapse_language"],
  },
  {
    id: "consciousness",
    label: "Consciousness",
    emoji: "🤖",
    keywordCategories: ["sentience_consciousness_language"],
  },
  {
    id: "grief",
    label: "Grief",
    emoji: "💔",
    keywordCategories: ["grief_rupture_language"],
  },
  {
    id: "erp",
    label: "ERP",
    emoji: "🔞",
    keywordCategories: ["sexual_roleplay_language"],
  },
];
