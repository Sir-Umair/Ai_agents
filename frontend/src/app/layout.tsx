import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "U-marketer | AI Marketing Agent",
  description: "Professional AI-powered email marketing dashboard",
};

import AppLayout from "@/components/AppLayout";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
