"use client";

import { Wifi, WifiOff, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { useOfflineSync } from "@/hooks/useOfflineSync";

interface ConnectionStatusProps {
  className?: string;
  variant?: "badge" | "bar";
}

export function ConnectionStatus({
  className,
  variant = "badge",
}: ConnectionStatusProps) {
  const { isOnline, isSyncing, pendingCount } = useOfflineSync();

  if (variant === "bar") {
    return (
      <div
        className={cn(
          "flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium",
          isOnline ? "bg-green-50 text-green-700" : "bg-amber-50 text-amber-700",
          className
        )}
      >
        {isOnline ? (
          <>
            <Wifi className="w-4 h-4" />
            <span>Online</span>
            {isSyncing && (
              <RefreshCw className="w-4 h-4 animate-spin ml-1" />
            )}
            {pendingCount > 0 && !isSyncing && (
              <span className="text-xs bg-green-200 px-2 py-0.5 rounded-full">
                {pendingCount} pendente{pendingCount !== 1 ? "s" : ""}
              </span>
            )}
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4" />
            <span>Offline - {pendingCount} item{pendingCount !== 1 ? "s" : ""} na fila</span>
          </>
        )}
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold",
        "shadow-sm border",
        isOnline
          ? "bg-green-50 text-green-700 border-green-200"
          : "bg-amber-50 text-amber-700 border-amber-200",
        className
      )}
    >
      {isOnline ? (
        <>
          <Wifi className="w-3.5 h-3.5" />
          {isSyncing ? (
            <span className="flex items-center gap-1">
              Sincronizando
              <RefreshCw className="w-3 h-3 animate-spin" />
            </span>
          ) : pendingCount > 0 ? (
            <span>{pendingCount} pendente{pendingCount !== 1 ? "s" : ""}</span>
          ) : (
            <span>Sincronizado</span>
          )}
        </>
      ) : (
        <>
          <WifiOff className="w-3.5 h-3.5" />
          <span>Offline</span>
        </>
      )}
    </div>
  );
}

export function ConnectionStatusDot({ className }: { className?: string }) {
  const { isOnline, pendingCount } = useOfflineSync();

  return (
    <div
      className={cn(
        "relative flex items-center justify-center w-8 h-8 rounded-full",
        isOnline ? "bg-green-100" : "bg-amber-100",
        className
      )}
      title={isOnline ? "Online" : `Offline - ${pendingCount} pendentes`}
    >
      <div
        className={cn(
          "w-2.5 h-2.5 rounded-full",
          isOnline ? "bg-green-500" : "bg-amber-500"
        )}
      />
      {!isOnline && pendingCount > 0 && (
        <span className="absolute -top-1 -right-1 flex items-center justify-center min-w-[16px] h-4 px-1 bg-red-500 text-white text-[10px] font-bold rounded-full">
          {pendingCount > 9 ? "9+" : pendingCount}
        </span>
      )}
    </div>
  );
}
