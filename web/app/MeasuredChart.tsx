"use client";

import { useLayoutEffect, useRef, useState } from "react";

// ── MeasuredChart ────────────────────────────────────────────────────────────
// A drop-in replacement for Recharts <ResponsiveContainer>.
//
// ResponsiveContainer measures its box asynchronously, so on first mount it
// renders a 0x0 chart — logging "width(0) and height(0)" console warnings and
// leaving a blank panel until a later resize or scroll repaints it. On a page
// of lazy-loaded charts that shows up as chart boxes that stay empty until you
// scroll, which badly undercuts trust in the data.
//
// This measures the container synchronously in useLayoutEffect (after the DOM
// is committed, before the browser paints), so the chart is drawn at the
// correct size on its very first paint. A ResizeObserver keeps it in sync after
// that. The render-prop child receives the measured pixel dimensions to pass
// straight to a Recharts chart's `width`/`height`.
//
// The caller fixes the box size via `style`/`className` — Recharts needs a real
// height, and the height never depends on the chart's own content.

export default function MeasuredChart({
  className,
  style,
  role,
  ariaLabel,
  children,
}: {
  className?: string;
  style?: React.CSSProperties;
  role?: string;
  ariaLabel?: string;
  children: (dims: { width: number; height: number }) => React.ReactNode;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ width: 0, height: 0 });

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const measure = () =>
      setDims({ width: el.clientWidth, height: el.clientHeight });
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={className}
      style={style}
      role={role}
      aria-label={ariaLabel}
    >
      {dims.width > 0 && dims.height > 0 && children(dims)}
    </div>
  );
}
