"use client";

import { ArrowLeft, HardHat } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface MobileHeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  backHref?: string;
  rightAction?: React.ReactNode;
  className?: string;
}

export function MobileHeader({
  title,
  subtitle,
  showBack = false,
  backHref = "/construction/mobile",
  rightAction,
  className,
}: MobileHeaderProps) {
  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-40 bg-white border-b border-gray-200",
        "safe-area-top",
        className
      )}
    >
      <div className="flex items-center justify-between px-4 h-14">
        <div className="flex items-center gap-3">
          {showBack ? (
            <Link
              href={backHref}
              className="flex items-center justify-center w-10 h-10 -ml-2 rounded-full active:bg-gray-100 transition-colors"
              aria-label="Voltar"
            >
              <ArrowLeft className="w-6 h-6 text-gray-700" />
            </Link>
          ) : (
            <div className="flex items-center justify-center w-10 h-10 -ml-2">
              <HardHat className="w-6 h-6 text-blue-600" />
            </div>
          )}
          <div className="flex flex-col">
            <h1 className="text-lg font-bold text-gray-900 leading-tight">
              {title}
            </h1>
            {subtitle && (
              <span className="text-xs text-gray-500 leading-tight">
                {subtitle}
              </span>
            )}
          </div>
        </div>

        {rightAction && (
          <div className="flex items-center">
            {rightAction}
          </div>
        )}
      </div>
    </header>
  );
}

export function MobileLogoHeader() {
  return (
    <header className="fixed top-0 left-0 right-0 z-40 bg-blue-600 safe-area-top">
      <div className="flex items-center justify-center h-14">
        <div className="flex items-center gap-2">
          <HardHat className="w-7 h-7 text-white" />
          <span className="text-lg font-bold text-white">ImoOS Obra</span>
        </div>
      </div>
    </header>
  );
}
