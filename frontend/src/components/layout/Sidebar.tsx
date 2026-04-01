"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useQuery } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/api-client";
import {
    LayoutDashboard,
    Building2,
    FolderKanban,
    Users,
    FileText,
    HardHat,
    Wallet,
    Settings,
    LogOut,
    ChevronRight,
    AlertTriangle,
    Store,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface UsageData {
  plan: string;
  projects: { pct_used: number };
  units: { pct_used: number };
  users: { pct_used: number };
}

const menuItems = [
    { icon: LayoutDashboard, label: "Dashboard",    href: "/" },
    { icon: FolderKanban,    label: "Projectos",    href: "/projects" },
    { icon: Building2,       label: "Inventário",   href: "/inventory" },
    { icon: Users,           label: "CRM",          href: "/crm" },
    { icon: HardHat,         label: "Obra",         href: "/construction" },
    { icon: FileText,        label: "Contratos",    href: "/contracts" },
    { icon: Wallet,          label: "Financeiro",   href: "/finance" },
    { icon: Store,           label: "Marketplace",  href: "/marketplace" },
    { icon: Settings,        label: "Configurações", href: "/settings" },
];

export function Sidebar() {
    const pathname = usePathname();
    const { logout, isAuthenticated } = useAuth();

    const { data: usage } = useQuery<UsageData>({
        queryKey: ["tenant-usage"],
        queryFn: () => {
            const token = getAccessToken();
            return fetch("/api/v1/tenant/usage/", {
                headers: { Authorization: `Bearer ${token}` },
            }).then((r) => r.json());
        },
        enabled: isAuthenticated,
        staleTime: 5 * 60 * 1000, // refresh every 5 min
    });

    const nearLimit =
        usage &&
        [usage.projects.pct_used, usage.units.pct_used, usage.users.pct_used].some(
            (p) => p >= 80
        );
    // Active match: exact for "/", prefix for everything else
    const isActive = (href: string) =>
        href === "/" ? pathname === "/" : pathname.startsWith(href);

    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-white transition-transform">
            <div className="flex h-full flex-col px-3 py-4">
                <div className="mb-10 flex items-center px-4 py-2">
                    <span className="text-2xl font-bold tracking-tight text-primary">ImoOS</span>
                </div>

                <nav className="flex-1 space-y-1">
                    {menuItems.map((item) => {
                        const active = isActive(item.href);
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "group flex items-center rounded-lg px-4 py-3 text-sm font-medium transition-all duration-200",
                                    active
                                        ? "bg-primary text-white shadow-lg shadow-primary/20"
                                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                )}
                            >
                                <item.icon className={cn("mr-3 h-5 w-5", active ? "text-white" : "text-muted-foreground")} />
                                <span className="flex-1">{item.label}</span>
                                {active && <ChevronRight className="h-4 w-4 opacity-70" />}
                            </Link>
                        );
                    })}
                </nav>

                <div className="mt-auto space-y-2">
                    {nearLimit && (
                        <Link
                            href="/settings/billing"
                            className="flex items-center gap-2 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2.5 text-xs font-medium text-amber-800 hover:bg-amber-100 transition-colors"
                        >
                            <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600" />
                            <span>Limite próximo — Upgrade</span>
                        </Link>
                    )}

                    <div className="border-t border-border pt-3">
                        <button
                            onClick={logout}
                            className="group flex w-full items-center rounded-lg px-4 py-3 text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
                        >
                            <LogOut className="mr-3 h-5 w-5" />
                            Sair
                        </button>
                    </div>
                </div>
            </div>
        </aside>
    );
}
