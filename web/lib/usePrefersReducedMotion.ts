"use client";

import { useEffect, useState } from "react";

// ── usePrefersReducedMotion ──────────────────────────────────────────────────
// Reports whether the OS "reduce motion" setting is on. Used to gate Recharts'
// JS-driven draw-on animation, which the global CSS prefers-reduced-motion
// block cannot reach.
//
// The media query is read once in a lazy initializer, so the very first render
// already has the right answer and the effect only has to subscribe to later
// changes. Every caller is a lazily-imported client chart, so `window` exists
// by then; on the server (and in any other unresolved case) the initializer
// falls back to `true` — the calm, no-animation path.

export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(
    () =>
      typeof window === "undefined" ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  );

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  return reduced;
}
