"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { 
  HardHat, 
  ArrowLeft, 
  TrendingUp,
  AlertTriangle,
  Download,
  FileSpreadsheet,
  FileText,
  Plus,
  Search,
  ChevronDown,
  ChevronUp,
  Info
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useConstructionProject } from "@/hooks/useConstructionStats";
import { useBudgets, useBudgetStats, formatBudgetVariance, BudgetItem } from "@/hooks/useBudgetStats";
import { BudgetChart } from "@/components/dashboard";
import { Skeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/button";
import { formatCve, formatCveCompact } from "@/lib/format";

export default function BudgetPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [search, setSearch] = useState("");
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  const { data: project, isLoading: projectLoading } = useConstructionProject(projectId);
  const { data: budgetsPage, isLoading: budgetsLoading } = useBudgets({ project: projectId });
  const { data: budgetStats, isLoading: statsLoading } = useBudgetStats(projectId);

  const budgets = budgetsPage?.results ?? [];
  const activeBudget = budgets.find(b => b.status === "APPROVED") || budgets[0];

  // Group items by category
  const groupedItems = activeBudget?.items?.reduce((acc, item) => {
    const category = item.category_name || "Sem Categoria";
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {} as Record<string, BudgetItem[]>) ?? {};

  const toggleCategory = (category: string) => {
    const newSet = new Set(expandedCategories);
    if (newSet.has(category)) {
      newSet.delete(category);
    } else {
      newSet.add(category);
    }
    setExpandedCategories(newSet);
  };

  if (projectLoading) {
    return <BudgetSkeleton />;
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Info className="h-12 w-12 text-red-500 mb-4" />
        <h2 className="text-lg font-semibold">Obra não encontrada</h2>
        <Link href="/construction" className="text-primary hover:underline mt-2">
          Voltar às obras
        </Link>
      </div>
    );
  }

  const totalBudgeted = parseFloat(project.budget_cve || "0");
  const totalActual = parseFloat(project.actual_cost_cve || "0");
  const variance = totalBudgeted > 0 ? ((totalActual - totalBudgeted) / totalBudgeted) * 100 : 0;
  const varianceInfo = formatBudgetVariance(variance);

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/construction" className="hover:text-foreground transition-colors">
          Obras
        </Link>
        <span>/</span>
        <Link href={`/construction/${projectId}`} className="hover:text-foreground transition-colors">
          {project.name}
        </Link>
        <span>/</span>
        <span className="text-foreground">Orçamento</span>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <Link
            href={`/construction/${projectId}`}
            className="p-2 rounded-xl border border-border hover:bg-slate-50 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-muted-foreground" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-emerald-50 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Orçamento</h1>
                <p className="text-sm text-muted-foreground">{project.name}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <FileSpreadsheet className="h-4 w-4" />
            Excel
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            <FileText className="h-4 w-4" />
            PDF
          </Button>
          <Button size="sm" className="gap-2">
            <Plus className="h-4 w-4" />
            Novo Item
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border bg-white p-5 shadow-sm">
          <p className="text-xs text-muted-foreground mb-1">Total Orçado</p>
          <p className="text-2xl font-bold text-blue-600">{formatCveCompact(totalBudgeted)}</p>
          <p className="text-xs text-muted-foreground mt-1">
            {activeBudget?.version ? `Versão ${activeBudget.version}` : "Sem orçamento"}
          </p>
        </div>

        <div className="rounded-xl border border-border bg-white p-5 shadow-sm">
          <p className="text-xs text-muted-foreground mb-1">Custo Real</p>
          <p className={cn("text-2xl font-bold", totalActual > totalBudgeted ? "text-red-600" : "text-emerald-600")}>
            {formatCveCompact(totalActual)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {totalActual > 0 ? `${((totalActual / totalBudgeted) * 100).toFixed(0)}% executado` : "—"}
          </p>
        </div>

        <div className="rounded-xl border border-border bg-white p-5 shadow-sm">
          <p className="text-xs text-muted-foreground mb-1">Variação</p>
          <p className={cn("text-2xl font-bold", varianceInfo.color)}>
            {varianceInfo.label}
          </p>
          {varianceInfo.isAlert && (
            <p className="text-xs text-red-600 mt-1 flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" />
              Acima do previsto
            </p>
          )}
        </div>

        <div className="rounded-xl border border-border bg-white p-5 shadow-sm">
          <p className="text-xs text-muted-foreground mb-1">Saldo</p>
          <p className={cn(
            "text-2xl font-bold",
            totalBudgeted - totalActual < 0 ? "text-red-600" : "text-emerald-600"
          )}>
            {formatCveCompact(totalBudgeted - totalActual)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {totalBudgeted > 0 ? `${((totalBudgeted - totalActual) / totalBudgeted * 100).toFixed(1)}% disponível` : "—"}
          </p>
        </div>
      </div>

      {/* Budget Chart */}
      <BudgetChart stats={budgetStats} isLoading={statsLoading} />

      {/* Budget Items Table */}
      <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
        <div className="p-4 border-b border-border bg-slate-50/50">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Detalhamento do Orçamento</h3>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Pesquisar itens..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 pr-4 py-2 rounded-lg border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 w-64"
              />
            </div>
          </div>
        </div>

        <div className="divide-y divide-border">
          {budgetsLoading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="p-4">
                <Skeleton className="h-8 w-full" />
              </div>
            ))
          ) : !activeBudget?.items ? (
            <div className="p-8 text-center text-muted-foreground">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Sem itens de orçamento definidos</p>
            </div>
          ) : (
            Object.entries(groupedItems).map(([category, items]) => {
              const categoryTotal = items.reduce((sum, item) => sum + parseFloat(item.total_price_cve), 0);
              const categoryActual = items.reduce((sum, item) => sum + parseFloat(item.actual_cost_cve || "0"), 0);
              const isExpanded = expandedCategories.has(category);

              return (
                <div key={category} className="bg-white">
                  {/* Category Header */}
                  <button
                    onClick={() => toggleCategory(category)}
                    className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronUp className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className="font-medium text-foreground">{category}</span>
                      <span className="text-xs text-muted-foreground">({items.length} itens)</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="text-right">
                        <p className="font-medium">{formatCveCompact(categoryTotal)}</p>
                        <p className="text-xs text-muted-foreground">orçado</p>
                      </div>
                      {categoryActual > 0 && (
                        <div className="text-right">
                          <p className={cn(
                            "font-medium",
                            categoryActual > categoryTotal ? "text-red-600" : "text-emerald-600"
                          )}>
                            {formatCveCompact(categoryActual)}
                          </p>
                          <p className="text-xs text-muted-foreground">real</p>
                        </div>
                      )}
                    </div>
                  </button>

                  {/* Items */}
                  {isExpanded && (
                    <div className="border-t border-border">
                      {items.map((item) => {
                        const itemActual = parseFloat(item.actual_cost_cve || "0");
                        const itemVariance = formatBudgetVariance(item.variance_pct);

                        return (
                          <div 
                            key={item.id} 
                            className="px-4 py-3 pl-10 flex items-center justify-between hover:bg-slate-50/50 transition-colors"
                          >
                            <div className="flex-1">
                              <p className="text-sm font-medium text-foreground">{item.description}</p>
                              <p className="text-xs text-muted-foreground">
                                {item.quantity} {item.unit} × {formatCve(parseFloat(item.unit_price_cve))}
                              </p>
                            </div>
                            <div className="flex items-center gap-4">
                              <div className="text-right">
                                <p className="text-sm font-medium">{formatCveCompact(parseFloat(item.total_price_cve))}</p>
                              </div>
                              {itemActual > 0 && (
                                <div className="text-right w-24">
                                  <p className={cn("text-sm font-medium", itemVariance.color)}>
                                    {formatCveCompact(itemActual)}
                                  </p>
                                  {item.variance_pct !== null && (
                                    <p className={cn("text-xs", itemVariance.color)}>
                                      {itemVariance.label}
                                    </p>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

function BudgetSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10 rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-64 rounded-2xl" />
    </div>
  );
}
