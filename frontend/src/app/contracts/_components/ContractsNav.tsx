"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { FileText, FileCode2, CreditCard } from "lucide-react";

export function ContractsNav() {
  const pathname = usePathname();

  const tabs = [
    {
      name: "Contratos",
      href: "/contracts",
      icon: FileText,
      active: pathname === "/contracts" || pathname.startsWith("/contracts/details"),
    },
    {
      name: "Templates",
      href: "/contracts/templates",
      icon: FileCode2,
      active: pathname.startsWith("/contracts/templates"),
    },
    {
      name: "Padrões de Pagamento",
      href: "/contracts/patterns",
      icon: CreditCard,
      active: pathname.startsWith("/contracts/patterns"),
    },
  ];

  return (
    <div className="flex items-center gap-1.5 p-1 bg-slate-100/50 rounded-xl w-fit border border-slate-200/60 mb-6">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={cn(
              "flex items-center gap-2 px-4 py-2 text-xs font-bold transition-all rounded-lg",
              tab.active
                ? "bg-white text-primary shadow-sm ring-1 ring-slate-200"
                : "text-muted-foreground hover:text-foreground hover:bg-white/50"
            )}
          >
            <Icon className={cn("h-4 w-4", tab.active ? "text-primary" : "text-muted-foreground")} />
            {tab.name}
          </Link>
        );
      })}
    </div>
  );
}
