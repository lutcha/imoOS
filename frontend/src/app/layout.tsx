import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { Providers } from "@/providers/Providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ImoOS — Sistema de Gestão Imobiliária",
  description: "Plataforma completa para promotoras e construtoras imobiliárias.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        <Providers>
          <Sidebar />
          <div className="flex flex-col min-h-screen bg-muted/30 ml-64">
            <Topbar />
            <main className="flex-1 mt-16 p-8">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}

