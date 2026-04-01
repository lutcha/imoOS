"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, FileText } from "lucide-react";

const NAV_ITEMS = [
  { href: "/investor", label: "Resumo", icon: LayoutDashboard, exact: true },
  { href: "/investor/documents", label: "Documentos", icon: FileText },
];

export default function InvestorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen bg-muted/30">
      {/* Simplified sidebar for investors */}
      <aside className="fixed left-0 top-0 h-full w-56 bg-white border-r border-border flex flex-col z-40">
        <div className="px-6 py-5 border-b border-border">
          <span className="text-lg font-semibold text-primary">ImoOS</span>
          <p className="text-xs text-muted-foreground mt-0.5">Portal do Investidor</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon, exact }) => {
            const isActive = exact ? pathname === href : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 ml-56 p-8">{children}</div>
    </div>
  );
}
