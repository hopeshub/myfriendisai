import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "My Friend Is AI",
  description:
    "Tracking the growth and cultural dynamics of AI companionship communities on Reddit.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <header className="border-b border-border">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
            <Link
              href="/"
              className="text-base font-semibold tracking-tight text-foreground hover:text-primary transition-colors"
            >
              myfriendisai.com
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
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
              >
                GitHub ↗
              </a>
            </nav>
          </div>
        </header>

        <main>{children}</main>

        <footer className="border-t border-border mt-20">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 text-xs text-muted flex items-center justify-between">
            <span>Updated daily from Reddit&apos;s public endpoints.</span>
            <span>myfriendisai.com</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
