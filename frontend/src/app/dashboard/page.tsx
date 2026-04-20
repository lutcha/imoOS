"use client";

import { useState } from "react";
import { HardHat, Calendar, ArrowRight } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { useDashboardStats } from "@/hooks/useDashboardStats";
import { useConstructionAggregatedStats, useConstructionProjects } from "@/hooks/useConstructionStats";
import { 
  DashboardStatsCards, 
  ProgressChart, 
  RecentActivity, 
  SalesFunnel, 
  MaintenanceSummary,
  ObrasTable
} from "@/components/dashboard";

type Period = "7d" | "30d" | "90d";

export default function ManagerDashboardPage() {
  const [period, setPeriod] = useState<Period>("30d");

  const { data: dashboardStats, isLoading: dashboardLoading } = useDashboardStats();
  const { data: constructionStats, isLoading: constructionStatsLoading } = useConstructionAggregatedStats();
  const { data: projectsPage, isLoading: projectsLoading } = useConstructionProjects({ page_size: 10 });

  const projects = projectsPage?.results ?? [];

  const periodOptions: { value: Period; label: string }[] = [
    { value: "7d", label: "7 dias" },
    { value: "30d", label: "30 dias" },
    { value: "90d", label: "90 dias" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Dashboard de Gestão</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Visão geral de todas as obras, ativos e performance imotech.cv
          </p>
        </div>
        
        {/* Period Selector */}
        <div className="flex items-center gap-2 bg-white rounded-xl border border-border p-1">
          <Calendar className="h-4 w-4 text-muted-foreground ml-2" />
          {periodOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setPeriod(opt.value)}
              className={cn(
                "px-3 py-1.5 text-xs font-medium rounded-lg transition-all",
                period === opt.value
                  ? "bg-primary text-white shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-slate-50"
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <DashboardStatsCards
        period={period}
        stats={dashboardStats}
        constructionStats={constructionStats}
        isLoading={dashboardLoading || constructionStatsLoading}
      />

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Main Content Area (Left 3/4 on XL) */}
        <div className="xl:col-span-3 space-y-6">
          {/* Progress Chart */}
          <div className="bg-white rounded-2xl border border-border">
            <ProgressChart 
              projects={projects} 
              isLoading={projectsLoading} 
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            {/* Obras Table (3/5) */}
            <div className="lg:col-span-3 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Obras Recentes</h2>
                <Link
                  href="/construction"
                  className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                >
                  Ver todas
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
              <ObrasTable 
                projects={projects.slice(0, 5)} 
                isLoading={projectsLoading} 
              />
            </div>

            {/* Maintenance Summary (2/5) */}
            <div className="lg:col-span-2">
              <MaintenanceSummary />
            </div>
          </div>
        </div>

        {/* Sidebar Area (Right 1/4 on XL) */}
        <div className="space-y-6">
          <SalesFunnel />
          <RecentActivity activities={[]} isLoading={false} />
        </div>
      </div>
    </div>
  );
}
