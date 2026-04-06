"use client";

import { 
  HardHat, 
  TrendingUp, 
  ClipboardList, 
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatCveCompact } from "@/lib/format";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  icon: React.ElementType;
  color: "blue" | "emerald" | "amber" | "purple" | "red";
  isLoading?: boolean;
}

const colorConfig = {
  blue: { bg: "bg-blue-50", text: "text-blue-700", icon: "text-blue-600" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-700", icon: "text-emerald-600" },
  amber: { bg: "bg-amber-50", text: "text-amber-700", icon: "text-amber-600" },
  purple: { bg: "bg-purple-50", text: "text-purple-700", icon: "text-purple-600" },
  red: { bg: "bg-red-50", text: "text-red-700", icon: "text-red-600" },
};

function StatCard({ 
  title, 
  value, 
  subtitle, 
  trend, 
  trendValue, 
  icon: Icon, 
  color,
  isLoading 
}: StatCardProps) {
  const colors = colorConfig[color];
  
  const TrendIcon = trend === "up" ? ArrowUpRight : trend === "down" ? ArrowDownRight : Minus;
  const trendColor = trend === "up" ? "text-emerald-600" : trend === "down" ? "text-red-600" : "text-slate-400";

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <Skeleton className="h-11 w-11 rounded-xl" />
          <Skeleton className="h-5 w-12 rounded-full" />
        </div>
        <div className="mt-4 space-y-2">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-9 w-20" />
          <Skeleton className="h-3 w-32" />
        </div>
      </div>
    );
  }

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-border bg-white p-6 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
      <div className="flex items-center justify-between">
        <div className={cn("rounded-xl p-2.5", colors.bg)}>
          <Icon className={cn("h-6 w-6", colors.icon)} />
        </div>
        {trend && (
          <div className={cn("flex items-center gap-0.5 text-xs font-medium", trendColor)}>
            <TrendIcon className="h-3.5 w-3.5" />
            <span>{trendValue}</span>
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <p className={cn("mt-1 text-2xl font-bold tracking-tight", colors.text)}>{value}</p>
        {subtitle && (
          <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
        )}
      </div>
    </div>
  );
}

interface ConstructionStatsCardsProps {
  stats: {
    active_projects: number;
    average_progress: number;
    pending_tasks: number;
    total_budget_cve: string;
  } | null;
  isLoading?: boolean;
}

export function ConstructionStatsCards({ stats, isLoading }: ConstructionStatsCardsProps) {
  const cards = [
    {
      title: "Obras Ativas",
      value: stats?.active_projects ?? 0,
      subtitle: "Projetos em construção",
      trend: "up" as const,
      trendValue: "+2",
      icon: HardHat,
      color: "blue" as const,
    },
    {
      title: "Progresso Médio",
      value: `${Math.round(stats?.average_progress ?? 0)}%`,
      subtitle: "Média de todas as obras",
      trend: "up" as const,
      trendValue: "+5%",
      icon: TrendingUp,
      color: "emerald" as const,
    },
    {
      title: "Tarefas Pendentes",
      value: stats?.pending_tasks ?? 0,
      subtitle: "Ações a completar",
      trend: "neutral" as const,
      trendValue: "—",
      icon: ClipboardList,
      color: "amber" as const,
    },
    {
      title: "Orçamento Total",
      value: formatCveCompact(parseFloat(stats?.total_budget_cve ?? "0")),
      subtitle: "Valor orçado em todas as obras",
      icon: Wallet,
      color: "purple" as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => (
        <StatCard
          key={index}
          {...card}
          isLoading={isLoading}
        />
      ))}
    </div>
  );
}

interface DashboardStatsCardsProps {
  period: "7d" | "30d" | "90d";
  stats: {
    inventory: { available: number; total: number };
    revenue_cve: string;
    pipeline: Record<string, number>;
    contracts: Record<string, number>;
  } | null;
  constructionStats: {
    active_projects: number;
    average_progress: number;
    pending_tasks: number;
  } | null;
  isLoading?: boolean;
}

export function DashboardStatsCards({ 
  period, 
  stats, 
  constructionStats,
  isLoading 
}: DashboardStatsCardsProps) {
  const periodLabel = period === "7d" ? "últimos 7 dias" : period === "30d" ? "últimos 30 dias" : "últimos 90 dias";

  const cards = [
    {
      title: "Obras Ativas",
      value: constructionStats?.active_projects ?? 0,
      subtitle: `Em construção (${periodLabel})`,
      icon: HardHat,
      color: "blue" as const,
    },
    {
      title: "Progresso Médio",
      value: `${Math.round(constructionStats?.average_progress ?? 0)}%`,
      subtitle: "Média de todas as obras",
      icon: TrendingUp,
      color: "emerald" as const,
    },
    {
      title: "Tarefas Pendentes",
      value: constructionStats?.pending_tasks ?? 0,
      subtitle: "Ações prioritárias",
      icon: ClipboardList,
      color: "amber" as const,
    },
    {
      title: "Receita Total",
      value: formatCveCompact(parseFloat(stats?.revenue_cve ?? "0")),
      subtitle: `Confirmada (${periodLabel})`,
      icon: Wallet,
      color: "purple" as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => (
        <StatCard
          key={index}
          {...card}
          isLoading={isLoading}
        />
      ))}
    </div>
  );
}
