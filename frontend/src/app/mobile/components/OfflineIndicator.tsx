"use client";

/**
 * Offline Indicator — ImoOS Field App
 * Banner de status online/offline com badge de sync pendente
 */
import { Wifi, WifiOff, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

interface OfflineIndicatorProps {
  isOnline: boolean;
  pendingCount: number;
  onSync: () => void;
  isSyncing?: boolean;
}

export function OfflineIndicator({
  isOnline,
  pendingCount,
  onSync,
  isSyncing = false,
}: OfflineIndicatorProps) {
  // Don't show if online with no pending items
  if (isOnline && pendingCount === 0) {
    return null;
  }

  return (
    <div
      className={cn(
        "sticky top-0 z-30 px-4 py-2 text-sm font-medium",
        "flex items-center justify-between",
        !isOnline 
          ? "bg-red-500 text-white" 
          : pendingCount > 0 
            ? "bg-amber-500 text-white"
            : "bg-green-500 text-white"
      )}
    >
      {/* Status */}
      <div className="flex items-center gap-2">
        {!isOnline ? (
          <>
            <WifiOff className="w-4 h-4" />
            <span>Sem conexão</span>
          </>
        ) : pendingCount > 0 ? (
          <>
            <Wifi className="w-4 h-4" />
            <span>{pendingCount} item(s) pendente(s)</span>
          </>
        ) : (
          <>
            <Wifi className="w-4 h-4" />
            <span>Online</span>
          </>
        )}
      </div>

      {/* Sync Button (when online with pending items) */}
      {isOnline && pendingCount > 0 && (
        <button
          onClick={onSync}
          disabled={isSyncing}
          className={cn(
            "flex items-center gap-1 px-3 py-1.5 rounded-lg",
            "bg-white/20 hover:bg-white/30 active:bg-white/40",
            "transition-colors disabled:opacity-50"
          )}
        >
          <RefreshCw className={cn("w-4 h-4", isSyncing && "animate-spin")} />
          <span>Sincronizar</span>
        </button>
      )}
    </div>
  );
}
