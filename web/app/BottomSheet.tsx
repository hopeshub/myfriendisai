"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  KeywordsSection,
  CommunitiesSection,
  SamplePostsSection,
  pickSamples,
} from "./TransparencyPanel";
import type { CategoryDetail } from "./TransparencyPanel";

type Props = {
  isOpen: boolean;
  themeLabel: string;
  themeEmoji: string;
  themeTagline: string;
  themeColor: string;
  data: CategoryDetail;
  onClose: () => void;
};

const SHEET_DEFAULT = 60; // % of viewport
const SHEET_EXPANDED = 90; // % of viewport
const CLOSE_THRESHOLD = 0.3; // drag 30% of sheet height to close

export default function BottomSheet({
  isOpen,
  themeLabel,
  themeEmoji,
  themeTagline,
  themeColor,
  data,
  onClose,
}: Props) {
  const [sheetHeight, setSheetHeight] = useState(SHEET_DEFAULT);
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const dragStartY = useRef(0);
  const dragStartHeight = useRef(SHEET_DEFAULT);
  const sheetRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const handleCloseRef = useRef<() => void>(() => {});

  // Reset state when opening — intentional setState-in-effect to sync
  // derived state (sheet position) with the isOpen prop.
  useEffect(() => {
    if (isOpen) {
      setSheetHeight(SHEET_DEFAULT); // eslint-disable-line react-hooks/set-state-in-effect
      setDragOffset(0);
      setIsClosing(false);
    }
  }, [isOpen]);

  // Lock body scroll when sheet is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = "";
      };
    }
  }, [isOpen]);

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") handleCloseRef.current();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [isOpen]);

  // Focus trap: cycle focus within the sheet
  useEffect(() => {
    if (!isOpen || !sheetRef.current) return;
    const sheet = sheetRef.current;
    const focusable = sheet.querySelectorAll<HTMLElement>(
      'button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable.length > 0) focusable[0].focus();

    function trapFocus(e: KeyboardEvent) {
      if (e.key !== "Tab" || focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
    document.addEventListener("keydown", trapFocus);
    return () => document.removeEventListener("keydown", trapFocus);
  }, [isOpen]);

  const handleClose = useCallback(() => {
    setIsClosing(true);
    setTimeout(() => {
      onClose();
      setIsClosing(false);
    }, 300);
  }, [onClose]);
  useEffect(() => {
    handleCloseRef.current = handleClose;
  }, [handleClose]);

  // --- Touch gesture handling on the drag handle ---
  const handleTouchStart = useCallback(
    (e: React.TouchEvent) => {
      dragStartY.current = e.touches[0].clientY;
      dragStartHeight.current = sheetHeight;
      setIsDragging(true);
    },
    [sheetHeight],
  );

  const handleTouchMove = useCallback(
    (e: React.TouchEvent) => {
      if (!isDragging) return;
      const deltaY = e.touches[0].clientY - dragStartY.current;
      setDragOffset(deltaY);
    },
    [isDragging],
  );

  const handleTouchEnd = useCallback(() => {
    if (!isDragging) return;
    setIsDragging(false);

    const sheetPx = (sheetHeight / 100) * window.innerHeight;
    const threshold = sheetPx * CLOSE_THRESHOLD;

    if (dragOffset > threshold) {
      // Dragged down past threshold → close
      handleClose();
    } else if (dragOffset < -50 && sheetHeight < SHEET_EXPANDED) {
      // Dragged up significantly → expand
      setSheetHeight(SHEET_EXPANDED);
    } else {
      // Snap back to current height
    }
    setDragOffset(0);
  }, [isDragging, dragOffset, sheetHeight, handleClose]);

  const samples = pickSamples(data.keywords);

  // Compute transform for drag feedback
  const translateY = isDragging ? Math.max(0, dragOffset) : 0;
  const shouldShow = isOpen && !isClosing;

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={handleClose}
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.4)",
          zIndex: 999,
          opacity: shouldShow ? 1 : 0,
          pointerEvents: shouldShow ? "auto" : "none",
          transition: "opacity 300ms ease-out",
        }}
      />

      {/* Sheet */}
      <div
        ref={sheetRef}
        role="dialog"
        aria-modal="true"
        aria-label={`${themeEmoji} ${themeLabel} details`}
        style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          height: `${sheetHeight}dvh`,
          maxHeight: `${SHEET_EXPANDED}dvh`,
          backgroundColor: "#1A1D27",
          borderRadius: "16px 16px 0 0",
          borderTop: `3px solid ${themeColor}`,
          transform: shouldShow
            ? `translateY(${translateY}px)`
            : "translateY(100%)",
          transition: isDragging
            ? "none"
            : "transform 300ms ease-out, height 200ms ease-out",
          zIndex: 1000,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          boxShadow: "0 -8px 24px rgba(0,0,0,0.4)",
        }}
      >
        {/* Drag handle area */}
        <div
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          style={{
            flexShrink: 0,
            padding: "12px 16px 8px",
            cursor: "grab",
            touchAction: "none",
          }}
        >
          {/* Handle bar */}
          <div
            style={{
              width: 32,
              height: 4,
              background: "rgba(255,255,255,0.3)",
              borderRadius: 2,
              margin: "0 auto 12px",
            }}
          />

          {/* Header row */}
          <div className="flex items-start justify-between">
            <div>
              <div
                className="text-[15px] font-medium"
                style={{ color: themeColor }}
              >
                {themeEmoji} {themeLabel}
              </div>
              <div
                className="text-[12px] mt-0.5"
                style={{ color: "#8293A6" }}
              >
                {themeTagline}
              </div>
            </div>
            <button
              onClick={handleClose}
              className="text-[20px] leading-none w-8 h-8 flex items-center justify-center rounded hover:text-foreground transition-colors flex-shrink-0"
              style={{ color: "#8293A6" }}
              aria-label="Close panel"
            >
              &times;
            </button>
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: "0.5px", background: "#1E293B", flexShrink: 0 }} />

        {/* Scrollable content */}
        <div
          ref={contentRef}
          style={{
            flex: 1,
            overflowY: "auto",
            WebkitOverflowScrolling: "touch",
            padding: "16px 16px 24px",
          }}
          className="space-y-5"
        >
          <KeywordsSection keywords={data.keywords} color={themeColor} />
          <CommunitiesSection subreddits={data.subreddits} color={themeColor} />
          <SamplePostsSection samples={samples} />

          {/* Footer */}
          <div
            className="text-[11px] pt-2"
            style={{ color: "#8293A6", borderTop: "0.5px solid #1E293B" }}
          >
            {data.keywords.length} keywords across{" "}
            {data.subreddits.length} communities &middot;{" "}
            {data.unique_posts.toLocaleString()} posts matched &middot; All
            keywords manually validated
          </div>
        </div>
      </div>
    </>
  );
}
