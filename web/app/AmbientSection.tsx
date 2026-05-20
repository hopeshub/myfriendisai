// ── Ambient / Discourse-climate section (homepage §5) ───────────────────────
// Server component. The section's eyebrow, heading, and intro live in
// page.tsx (matching §1/§2/§4); this renders the chart + the closing
// disclosure paragraph.
//
// The editorial point: the broad AI culture war is loud and growing fast,
// but its discourse barely touches AI companionship. Half a million
// subscribers arguing about AI on Reddit; almost none of them arguing about
// this. The sustained critique of AI companions on Reddit is happening in §4
// (the recovery cluster) — inside the affected communities themselves.
//
// Tracked as CONTEXT only — T4 subs are excluded from every keyword
// measurement (see the LOCKED criterion in CLAUDE.md §2.1 + the scoping
// doc). Read engagement, not opinion.

import AmbientChart from "./AmbientChart";
import { loadAmbientCohort } from "./themeData";
import { measure } from "./styles";

export default function AmbientSection() {
  const data = loadAmbientCohort();

  return (
    <div>
      <AmbientChart top={data.top} stack={data.stack} />

      <p
        style={{
          fontSize: 13,
          lineHeight: 1.7,
          color: "#9AA7B8",
          marginTop: 28,
          maxWidth: measure,
        }}
      >
        <span style={{ color: "#F1F4F8", fontWeight: 600 }}>
          What this is and isn&apos;t.
        </span>{" "}
        Engagement, not opinion &mdash; these communities take sides about AI
        as a cultural project; they are not a sample of mainstream AI
        sentiment. The pro-AI side of the cluster looks thinner because most
        pro-AI energy on Reddit lives in product communities (r/ChatGPT,
        r/ClaudeAI, r/singularity) &mdash; people using the thing, not
        arguing for it. The fight against AI companionship, as far as Reddit
        shows it, is happening in §4 above: inside the communities
        themselves.
      </p>
    </div>
  );
}
