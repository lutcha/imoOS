"use client";

/**
 * SyncBadge — ImoOS Field App
 * Badge "Pendente sincronizar" para items offline
 */
import { Cloud, CloudOff, Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface SyncBadgeProps {
  isSynced: boolean;
  isSyncing?: boolean;
  size?: "sm" | "md";
  showLabel?: boolean;
}

export function SyncBadge({
  isSynced,
  isSyncing = false,
  size = "md",
  showLabel = true,
}: SyncBadgeProps) {
  const sizeClasses = {
    sm: "px-1.5 py-0.5 text-xs gap-1",
    md: "px-2.5 py-1 text-sm gap-1.5",
  };

  const iconSizes = {
    sm: "w-3 h-3",
    md: "w-4 h-4",
  };

  if (isSyncing) {
    return (
      <span
        className={cn(
          "inline-flex items-center rounded-full font-medium",
          "bg-blue-100 text-blue-700",
          sizeClasses[size]
        )}
      >
        <Loader2 className={cn(iconSizes[size], "animate-spin")} />
        {showLabel && <span>A sincronizar...</span>}
      </span>
    );
  }

  if (isSynced) {
    return (
      <span
        className={cn(
          "inline-flex items-center rounded-full font-medium",
          "bg-green-100 text-green-700",
          sizeClasses[size]
        )}
      >
        <Check className={iconSizes[size]} />
        {showLabel && <span>Sincronizado</span>}
      </span>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full font-medium",
        "bg-amber-100 text-amber-700",
        sizeClasses[size]
      )}
    >
      <CloudOff className={iconSizes[size]} />
      {showLabel && <span>Pendente</span>}
    </span>
  );
}

// Compact icon-only version
export function SyncIcon({
  isSynced,
  isSyncing = false,
  className,
}: {
  isSynced: boolean;
  isSyncing?: boolean;
  className?: string;
}) {
  if (isSyncing) {
    return <Loader2 className={cn("w-4 h-4 animate-spin text-blue-500", className)} />;
  }
  
  if (isSynced) {
    return <Cloud className={cn("w-4 h-4 text-green-500", className)} />;
  }

  return <CloudOff className={cn("w-4 h-4 text-amber-500", className)} />;
}
