"use client";

import { useEffect, useState } from "react";

// ── usePrefersReducedMotion ──────────────────────────────────────────────────
// Reports whether the OS "reduce motion" setting is on. Used to gate Recharts'
// JS-driven draw-on animation, which the global CSS prefers-reduced-motion
// block cannot reach.
//
// Starts `true` (motion-reduced) so the first client render is the calm,
// no-animation path. After mount we read the real media query: if the user
// does NOT prefer reduced motion, `false` is committed before the chart's
// first paint of its data, so the draw-on animation still plays once on mount.
// This conservative default means an unresolved query never animates.

export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(true);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  return reduced;
}
