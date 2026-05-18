import type { Metadata } from "next";
import Link from "next/link";
import { readFileSync } from "fs";
import { join } from "path";
import { Inter, Newsreader } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import StaleDataBanner from "./StaleDataBanner";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const newsreader = Newsreader({
  subsets: ["latin"],
  weight: ["400", "600"],
  style: ["normal", "italic"],
  display: "swap",
  variable: "--font-newsreader",
});

export const metadata: Metadata = {
  title: "My Friend Is AI",
  description:
    "A live, transparent tracker of explicit AI-companion language in curated Reddit communities — how themes like romance, dependency, personhood, sexual roleplay, therapeutic use, and loss rise and fall over time.",
  metadataBase: new URL("https://myfriendisai.com"),
  openGraph: {
    title: "My Friend Is AI",
    description:
      "A live, transparent tracker of explicit AI-companion language in curated Reddit communities, across six themes — romance, sex/ERP, consciousness, therapy, addiction, and rupture. A precision-first discourse tracker built from validated keyword matching, not a population estimate.",
    url: "https://myfriendisai.com",
    siteName: "My Friend Is AI",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "My Friend Is AI",
    description:
      "Tracking AI companion discourse on Reddit across six themes.",
  },
  robots: {
    index: true,
    follow: true,
  },
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

  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className={`antialiased ${inter.className} ${newsreader.variable}`}>
        <a href="#main" className="skip-link">Skip to content</a>
        <StaleDataBanner />
        <header className="border-b border-border">
          <div className="max-w-[1080px] mx-auto px-4 sm:px-8 py-4 flex items-center justify-between">
            <Link
              href="/"
              className="font-display text-lg tracking-tight hover:opacity-80 transition-opacity"
            >
              <span style={{ fontWeight: 400, color: "#9AA7B8", fontStyle: "normal" }}>My Friend Is</span>
              {" "}
              <span style={{ fontWeight: 600, color: "#F8FAFC", fontStyle: "normal" }}>AI</span>
            </Link>
            <nav className="flex gap-6 text-sm text-muted">
              <Link
                href="/communities"
                className="hover:text-foreground transition-colors"
              >
                Communities
              </Link>
              <Link
                href="/about"
                className="hover:text-foreground transition-colors"
              >
                About
              </Link>
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
              >
                GitHub ↗
              </a>
            </nav>
          </div>
        </header>

        <main id="main">{children}</main>

        <footer className="border-t border-border mt-20">
          <div className="max-w-[1080px] mx-auto px-4 sm:px-8 py-8 text-sm text-muted flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-col gap-1">
              <span>An independent, one-person research project.</span>
              <span>
                Data from Reddit&apos;s public endpoints ·{" "}
                {formatPostCount(meta.total_posts)} posts · {startYear}–present ·
                updated daily
              </span>
            </div>
            <nav className="flex gap-5">
              <Link href="/about" className="hover:text-foreground transition-colors">
                About
              </Link>
              <Link
                href="/communities"
                className="hover:text-foreground transition-colors"
              >
                Communities
              </Link>
              <a
                href="https://github.com/hopeshub/myfriendisai"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
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
