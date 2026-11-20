import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { readFileSync } from "fs";
import { join } from "path";
import localFont from "next/font/local";
import { Analytics } from "@vercel/analytics/next";
import StaleDataBanner from "./StaleDataBanner";
import "./globals.css";
import { C, SITE_THEME, paletteCssVars } from "@/app/styles";

// Fonts are self-hosted (app/fonts/, latin subset, from the @fontsource npm
// packages; OFL texts alongside) so the build makes no network request. The
// old next/font/google fetch could fail the pre-deploy build on a flaky
// morning. Same families, weights and styles as before.
const inter = localFont({
  // Variable file; the 400–700 range matches the four weights requested from
  // Google before, so weights outside it still snap to 400 or 700.
  src: [{ path: "./fonts/inter-latin-wght-normal.woff2", weight: "400 700", style: "normal" }],
  display: "swap",
});

const newsreader = localFont({
  src: [
    { path: "./fonts/newsreader-latin-400-normal.woff2", weight: "400", style: "normal" },
    { path: "./fonts/newsreader-latin-400-italic.woff2", weight: "400", style: "italic" },
    { path: "./fonts/newsreader-latin-600-normal.woff2", weight: "600", style: "normal" },
    { path: "./fonts/newsreader-latin-600-italic.woff2", weight: "600", style: "italic" },
  ],
  display: "swap",
  variable: "--font-newsreader",
  // A serif fallback, as next/font/google generated for Newsreader.
  adjustFontFallback: "Times New Roman",
});

// Paper theme (design step 3c): IBM Plex Sans Condensed for headings, labels,
// navigation and chart text; Literata for running prose. Same self-hosting.
const plexCondensed = localFont({
  src: [
    { path: "./fonts/ibm-plex-sans-condensed-latin-400-normal.woff2", weight: "400", style: "normal" },
    { path: "./fonts/ibm-plex-sans-condensed-latin-400-italic.woff2", weight: "400", style: "italic" },
    { path: "./fonts/ibm-plex-sans-condensed-latin-600-normal.woff2", weight: "600", style: "normal" },
  ],
  display: "swap",
  variable: "--font-plex-condensed",
  adjustFontFallback: "Arial",
});

const literata = localFont({
  src: [
    { path: "./fonts/literata-latin-wght-normal.woff2", weight: "200 900", style: "normal" },
    { path: "./fonts/literata-latin-wght-italic.woff2", weight: "200 900", style: "italic" },
  ],
  display: "swap",
  variable: "--font-literata",
  adjustFontFallback: "Times New Roman",
});

const fontClasses =
  SITE_THEME === "paper"
    ? `${plexCondensed.variable} ${literata.variable}`
    : `${inter.className} ${newsreader.variable}`;

export const metadata: Metadata = {
  // `default` shows on the homepage (template is not applied to it); every
  // other page passes a bare segment and the template adds the suffix.
  title: {
    default: "My Friend Is AI — Tracking AI Companion Discourse on Reddit",
    template: "%s — My Friend Is AI",
  },
  description:
    "A live tracker of how AI-companion Reddit communities talk — six recurring themes, from romance to dependence to loss, charted month by month across years of posts.",
  metadataBase: new URL("https://myfriendisai.com"),
  applicationName: "My Friend Is AI",
  authors: [{ name: "My Friend Is AI" }],
  creator: "My Friend Is AI",
  publisher: "My Friend Is AI",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "My Friend Is AI",
    // Kept under ~200 chars so the "discourse tracker, not a population
    // estimate" caveat survives X's card-description truncation.
    description:
      "How AI-companion Reddit communities talk: six themes — romance, sex, consciousness, therapy, addiction, rupture — charted month by month. A discourse tracker, not a population estimate.",
    url: "https://myfriendisai.com",
    siteName: "My Friend Is AI",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "My Friend Is AI",
    description:
      "How AI-companion Reddit communities talk: six themes charted month by month. A discourse tracker, not a population estimate.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: C.bg,
  colorScheme: SITE_THEME === "paper" ? "light" : "dark",
  width: "device-width",
  initialScale: 1,
};

function getSiteMeta() {
  try {
    const raw = readFileSync(join(process.cwd(), "data", "site_meta.json"), "utf-8");
    return JSON.parse(raw) as { total_posts: number; date_start: string; date_end: string };
  } catch (e) {
    // Fallback is deliberately conservative — if you see this in prod, site_meta.json
    // is missing or malformed and the daily export pipeline needs investigation.
    console.error("Failed to load site_meta.json, using fallback:", e);
    return { total_posts: 0, date_start: "2017-01-01", date_end: "" };
  }
}

function formatPostCount(n: number): string {
  return `~${(n / 1_000_000).toFixed(1)}M`;
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const meta = getSiteMeta();
  const startYear = meta.date_start.slice(0, 4);
  // "2017–Sep 2026" rather than "2017–present": the end date is the last
  // collected day, which is the honest thing to print on every page.
  const endLabel = meta.date_end
    ? new Date(meta.date_end + "T00:00:00Z").toLocaleDateString("en-US", {
        month: "short",
        year: "numeric",
        timeZone: "UTC",
      })
    : "present";

  return (
    <html lang="en" data-theme={SITE_THEME} style={paletteCssVars as React.CSSProperties}>
      <body className={`antialiased ${fontClasses}`}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@graph": [
                {
                  "@type": "WebSite",
                  "@id": "https://myfriendisai.com/#website",
                  url: "https://myfriendisai.com",
                  name: "My Friend Is AI",
                  description:
                    "A tracker of how AI-companion Reddit communities talk — six recurring themes charted month by month.",
                  publisher: { "@id": "https://myfriendisai.com/#org" },
                  inLanguage: "en-US",
                },
                {
                  "@type": "Organization",
                  "@id": "https://myfriendisai.com/#org",
                  name: "My Friend Is AI",
                  url: "https://myfriendisai.com",
                  description:
                    "An independent, one-person research project tracking AI-companionship discourse on Reddit.",
                },
              ],
            }),
          }}
        />
        <a href="#main" className="skip-link">Skip to content</a>
        <StaleDataBanner />
        <header className="border-b border-border">
          <div className="max-w-[1080px] mx-auto px-4 sm:px-8 py-4 flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-0">
            <Link
              href="/"
              className="font-display text-lg tracking-tight whitespace-nowrap hover:opacity-80 transition-opacity"
            >
              <span style={{ fontWeight: 400, color: C.lead, fontStyle: "normal" }}>My Friend Is</span>
              {" "}
              <span style={{ fontWeight: 600, color: C.title, fontStyle: "normal" }}>AI</span>
            </Link>
            <nav aria-label="Primary" className="flex gap-6 text-sm text-muted">
              <Link
                href="/#themes"
                className="inline-flex items-center min-h-11 md:min-h-0 hover:text-foreground transition-colors"
              >
                Themes
              </Link>
              <Link
                href="/communities"
                className="inline-flex items-center min-h-11 md:min-h-0 hover:text-foreground transition-colors"
              >
                Communities
              </Link>
              <Link
                href="/about"
                className="inline-flex items-center min-h-11 md:min-h-0 hover:text-foreground transition-colors"
              >
                About
              </Link>
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center min-h-11 md:min-h-0 whitespace-nowrap hover:text-foreground transition-colors"
              >
                GitHub ↗
              </a>
            </nav>
          </div>
        </header>

        <main id="main" tabIndex={-1}>{children}</main>

        <footer className="border-t border-border mt-20">
          <div className="max-w-[1080px] mx-auto px-4 sm:px-8 py-8 text-sm text-muted flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-col gap-1">
              <span>An independent, one-person research project.</span>
              <span>
                Data from public Reddit archives ·{" "}
                {formatPostCount(meta.total_posts)} posts collected · {startYear}–{endLabel} ·
                updated daily
              </span>
            </div>
            <nav aria-label="Footer" className="flex gap-5">
              <Link href="/about" className="inline-flex items-center min-h-11 md:min-h-0 hover:text-foreground transition-colors">
                About
              </Link>
              <Link
                href="/communities"
                className="inline-flex items-center min-h-11 md:min-h-0 hover:text-foreground transition-colors"
              >
                Communities
              </Link>
              <a href="/dataset/v1" className="inline-flex items-center min-h-11 md:min-h-0 hover:text-foreground transition-colors">
                Data
              </a>
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center min-h-11 md:min-h-0 hover:text-foreground transition-colors"
              >
                GitHub
              </a>
            </nav>
          </div>
        </footer>
        <Analytics />
      </body>
    </html>
  );
}
