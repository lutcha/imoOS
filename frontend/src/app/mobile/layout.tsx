"use client";

/**
 * Mobile Layout — ImoOS Field App
 * Layout otimizado para telas pequenas, sem sidebar, bottom navigation
 * Touch targets 48px+, fontes 16px+, contraste alto para sol em obra
 */
import { useEffect } from "react";
import { MobileHeader } from "./components/MobileHeader";
import { MobileBottomNav } from "./components/MobileBottomNav";
import { OfflineIndicator } from "./components/OfflineIndicator";
import { initMobileDB } from "@/lib/mobile-db";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import "./globals.css";

export default function MobileLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isOnline, pendingCount, syncNow } = useOfflineSync();

  // Initialize IndexedDB on mount
  useEffect(() => {
    initMobileDB().catch(console.error);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Status bar area para iOS */}
      <div className="h-safe-top bg-primary" />
      
      {/* Header fixo */}
      <MobileHeader />
      
      {/* Indicador de conexão */}
      <OfflineIndicator 
        isOnline={isOnline} 
        pendingCount={pendingCount}
        onSync={syncNow}
      />
      
      {/* Conteúdo principal com scroll */}
      <main className="flex-1 overflow-y-auto pb-24 pt-2">
        <div className="px-4 py-2">
          {children}
        </div>
      </main>
      
      {/* Navegação inferior */}
      <MobileBottomNav />
      
      {/* Safe area para iOS */}
      <div className="h-safe-bottom" />
    </div>
  );
}
