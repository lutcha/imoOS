"use client";

/**
 * Mobile Layout — ImoOS Field App
 * Layout otimizado para telas pequenas, sem sidebar, bottom navigation
 * Touch targets 48px+, fontes 16px+, contraste alto para sol em obra
 */
import { useEffect, useState } from "react";
import { MobileHeader } from "./components/MobileHeader";
import { MobileBottomNav } from "./components/MobileBottomNav";
import { OfflineIndicator } from "./components/OfflineIndicator";
import { RegisterSW } from "@/app/register-sw";
import { initMobileDB } from "@/lib/mobile-db";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { useRouter } from "next/navigation";
import { Toaster } from "sonner";
import "./globals.css";

export default function MobileLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isOnline, pendingCount, syncNow, isSyncing } = useOfflineSync();
  const [isReady, setIsReady] = useState(false);

  // Initialize IndexedDB on mount
  useEffect(() => {
    const init = async () => {
      try {
        await initMobileDB();
        setIsReady(true);
      } catch (error) {
        console.error("[Mobile] Failed to init IndexedDB:", error);
      }
    };
    
    init();

    // Listen for sync trigger from service worker
    const handleTriggerSync = () => {
      syncNow();
    };

    window.addEventListener("trigger-sync", handleTriggerSync);

    return () => {
      window.removeEventListener("trigger-sync", handleTriggerSync);
    };
  }, [syncNow]);

  // Handle online/offline events
  useEffect(() => {
    const handleOnline = () => {
      // Auto-sync when coming back online
      if (pendingCount > 0) {
        syncNow();
      }
    };

    window.addEventListener("online", handleOnline);
    return () => window.removeEventListener("online", handleOnline);
  }, [pendingCount, syncNow]);

  if (!isReady) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 font-medium">A carregar...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <RegisterSW />
      <Toaster 
        position="top-center"
        toastOptions={{
          style: {
            fontSize: '16px',
            padding: '16px',
          },
        }}
      />
      
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
          isSyncing={isSyncing}
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
    </>
  );
}
