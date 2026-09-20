import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "Vault — File workspace", description: "Manage your files in one place." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ja"><body>{children}</body></html>;
}
