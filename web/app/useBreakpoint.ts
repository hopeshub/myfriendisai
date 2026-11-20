"use client";

import { useEffect, useState } from "react";

/**
 * Returns whether the viewport is ≤768px (the "mobile strip" breakpoint: the
 * 14px mobile font floor, and the atlas stacking each strip's labels above
 * it). Starts as null during SSR/hydration to avoid layout flash.
 */
export function useBreakpoint(): {
  isMobileStrip: boolean | null;
} {
  const [state, setState] = useState<{ isMobileStrip: boolean | null }>({
    isMobileStrip: null,
  });

  useEffect(() => {
    function update() {
      const isMobileStrip = window.innerWidth <= 768;
      // Return the previous object when nothing changed: resize fires on every
      // pixel of a drag and (on mobile Safari) whenever the URL bar collapses
      // during scroll — a fresh object each time would re-render every chart.
      setState((prev) =>
        prev.isMobileStrip === isMobileStrip ? prev : { isMobileStrip },
      );
    }
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  return state;
}
