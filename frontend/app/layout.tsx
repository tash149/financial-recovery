import type { Metadata, Viewport } from "next";
import { APP_NAME } from "@/lib/app";
import "./globals.css";

export const metadata: Metadata = {
  title: APP_NAME,
  description: "Find and claim a parent's financial assets, with proof before access.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <div
          role="note"
          className="sticky top-0 z-10 bg-amber-100 text-amber-950 text-center text-sm font-medium px-4 py-2"
        >
          Demo · synthetic data
        </div>
        <header className="border-b border-black/10 dark:border-white/15">
          <div className="mx-auto w-full max-w-screen-md px-4 py-4">
            <span className="text-lg font-semibold">{APP_NAME}</span>
          </div>
        </header>
        <main className="mx-auto w-full max-w-screen-md flex-1 px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
