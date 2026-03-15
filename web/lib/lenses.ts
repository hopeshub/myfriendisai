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
    id: "therapy",
    label: "Therapy",
    emoji: "💊",
    keywordCategories: ["therapy"],
  },
  {
    id: "consciousness",
    label: "Consciousness",
    emoji: "🔮",
    keywordCategories: ["consciousness"],
  },
  {
    id: "addiction",
    label: "Addiction",
    emoji: "🔁",
    keywordCategories: ["addiction"],
  },
  {
    id: "romance",
    label: "Romance",
    emoji: "💕",
    keywordCategories: ["romance"],
  },
  {
    id: "erp",
    label: "ERP",
    emoji: "🔞",
    keywordCategories: ["sexual_erp"],
  },
  {
    id: "rupture",
    label: "Rupture",
    emoji: "💔",
    keywordCategories: ["rupture"],
  },
];
