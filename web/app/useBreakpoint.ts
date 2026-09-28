"use client";

import { useEffect, useState } from "react";

export type Breakpoint = "mobile" | "tablet" | "desktop";

/**
 * Returns the current breakpoint and whether the viewport is ≤768px (mobile strip).
 * Both values start as null during SSR/hydration to avoid layout flash.
 */
export function useBreakpoint(): {
  bp: Breakpoint | null;
  isMobileStrip: boolean | null;
} {
  const [state, setState] = useState<{
    bp: Breakpoint | null;
    isMobileStrip: boolean | null;
  }>({ bp: null, isMobileStrip: null });

  useEffect(() => {
    function update() {
      const w = window.innerWidth;
      const bp: Breakpoint = w < 640 ? "mobile" : w < 1024 ? "tablet" : "desktop";
      const isMobileStrip = w <= 768;
      // Return the previous object when nothing changed: resize fires on every
      // pixel of a drag and (on mobile Safari) whenever the URL bar collapses
      // during scroll — a fresh object each time would re-render every chart.
      setState((prev) =>
        prev.bp === bp && prev.isMobileStrip === isMobileStrip
          ? prev
          : { bp, isMobileStrip },
      );
    }
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  return state;
}
