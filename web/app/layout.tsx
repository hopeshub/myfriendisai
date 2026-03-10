import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

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
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white text-zinc-900`}
      >
        <header className="border-b border-zinc-200">
          <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
            <Link
              href="/"
              className="text-lg font-semibold tracking-tight hover:opacity-75 transition-opacity"
            >
              My Friend Is AI
            </Link>
            <nav className="flex gap-6 text-sm text-zinc-500">
              <Link
                href="/communities"
                className="hover:text-zinc-900 transition-colors"
              >
                Communities
              </Link>
              <Link
                href="/about"
                className="hover:text-zinc-900 transition-colors"
              >
                About
              </Link>
            </nav>
          </div>
        </header>

        <main className="max-w-5xl mx-auto px-6 py-10">{children}</main>

        <footer className="border-t border-zinc-200 mt-20">
          <div className="max-w-5xl mx-auto px-6 py-6 text-xs text-zinc-400 flex items-center justify-between">
            <span>
              Data collected daily from Reddit&apos;s public .json endpoints.
            </span>
            <span>myfriendisai.com</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
