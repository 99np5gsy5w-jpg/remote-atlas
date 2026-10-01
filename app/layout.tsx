import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Remote Atlas · Worldwide remote jobs",
  description: "Remote jobs from employer careers sites, with private document matching.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
