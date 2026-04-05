"use client";

/**
 * Mobile Bottom Navigation — ImoOS Field App
 * Navegação inferior para fácil alcance do polegar
 * Touch targets: 48px+
 */
import { usePathname } from "next/navigation";
import { ClipboardList, CheckCircle2, Camera, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  {
    href: "/mobile/obra",
    label: "Tarefas",
    icon: ClipboardList,
  },
  {
    href: "/mobile/obra?tab=completed",
    label: "Concluídas",
    icon: CheckCircle2,
  },
  {
    href: "/mobile/photos",
    label: "Fotos",
    icon: Camera,
  },
  {
    href: "/mobile/settings",
    label: "Config",
    icon: Settings,
  },
];

export function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-border shadow-[0_-2px_10px_rgba(0,0,0,0.05)]">
      <div className="flex items-center justify-around h-16 pb-[env(safe-area-inset-bottom)]">
        {navItems.map((item) => {
          const isActive = pathname === item.href || 
            (item.href !== "/mobile/obra" && pathname.startsWith(item.href.replace("?tab=completed", "")));
          
          return (
            <a
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center justify-center flex-1 h-full min-h-[48px]",
                "gap-1 px-2 transition-colors",
                isActive 
                  ? "text-primary" 
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <item.icon className={cn(
                "w-6 h-6 transition-transform",
                isActive && "scale-110"
              )} />
              <span className="text-xs font-medium">{item.label}</span>
            </a>
          );
        })}
      </div>
    </nav>
  );
}
