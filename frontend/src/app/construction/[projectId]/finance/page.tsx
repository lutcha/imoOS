"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  TrendingUp, 
  Plus, 
  FileSpreadsheet, 
  FileText,
  DollarSign,
  EuroIcon,
  Filter
} from "lucide-react";
import { useProjectFinance } from "@/hooks/useProjectFinance";
import { useConstructionProject } from "@/hooks/useConstructionStats";
import { FinancialSummaryCard } from "@/components/finance/FinancialSummaryCard";
import { BudgetVsActualChart } from "@/components/finance/BudgetVsActualChart";
import { ExpenseList } from "@/components/finance/ExpenseList";
import { Button } from "@/components/ui/button";
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatCveCompact } from "@/lib/format";

export default function ConstructionFinancePage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [currency, setCurrency] = useState<"CVE" | "EUR">("CVE");

  const { data: project, isLoading: projectLoading } = useConstructionProject(projectId);
  const { 
    summary, 
    expenses, 
    isLoading: financeLoading 
  } = useProjectFinance(projectId);

  if (projectLoading || financeLoading) {
    return <FinanceSkeleton />;
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h2 className="text-xl font-semibold">Projecto não encontrado</h2>
        <Link href="/construction" className="text-primary hover:underline mt-2">
          Voltar às obras
        </Link>
      </div>
    );
  }

  // Map summary categories to chart data
  const chartData = summary?.categories.map(cat => ({
    name: cat.name,
    budget: cat.budgeted,
    actual: cat.actual
  })) || [];

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
        <span className="text-foreground font-medium">Financeiro</span>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <Link
            href={`/construction/${projectId}`}
            className="p-2 rounded-xl border border-border hover:bg-muted transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-muted-foreground" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Módulo Financeiro Consolidado</h1>
            <p className="text-sm text-muted-foreground">Gestão de orçamentos, gastos e rentabilidade</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
           <div className="p-1 bg-muted rounded-lg flex gap-1 mr-2">
            <Button 
              variant={currency === "CVE" ? "secondary" : "ghost"} 
              size="sm" 
              className="px-3 h-8 text-xs font-bold"
              onClick={() => setCurrency("CVE")}
            >
              CVE
            </Button>
            <Button 
              variant={currency === "EUR" ? "secondary" : "ghost"} 
              size="sm" 
              className="px-3 h-8 text-xs font-bold"
              onClick={() => setCurrency("EUR")}
            >
              EUR
            </Button>
          </div>
          <Button variant="outline" size="sm" className="gap-2">
            <FileSpreadsheet className="h-4 w-4" />
            Exportar
          </Button>
          <Button size="sm" className="gap-2 shadow-sm">
            <Plus className="h-4 w-4" />
            Nova Despesa
          </Button>
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <FinancialSummaryCard 
          title="Orçamento Total" 
          amount={summary?.total_budgeted || 0}
          currency={currency}
          trend={0}
          icon={TrendingUp}
        />
        <FinancialSummaryCard 
          title="Custo Realizado" 
          amount={summary?.total_actual || 0}
          currency={currency}
          trend={summary?.performance_percentage || 0}
          isWarning={summary?.is_over_budget}
          icon={DollarSign}
        />
        <FinancialSummaryCard 
          title="Variação" 
          amount={(summary?.total_budgeted || 0) - (summary?.total_actual || 0)}
          currency={currency}
          isNegative={(summary?.total_budgeted || 0) - (summary?.total_actual || 0) < 0}
          icon={TrendingUp}
        />
         <FinancialSummaryCard 
          title="Adiantamentos" 
          amount={summary?.total_advances || 0}
          currency={currency}
          icon={EuroIcon}
        />
      </div>

      {/* Main Content */}
      <Tabs defaultValue="expenses" className="space-y-6">
        <div className="flex items-center justify-between">
          <TabsList className="bg-muted/50 border border-border">
            <TabsTrigger value="expenses">Despesas & Analítico</TabsTrigger>
            <TabsTrigger value="advances">Adiantamentos a Empreiteiros</TabsTrigger>
            <TabsTrigger value="reports">Relatórios BI</TabsTrigger>
          </TabsList>
          
          <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground">
            <Filter className="h-4 w-4" />
            Filtros
          </Button>
        </div>

        <TabsContent value="expenses" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <BudgetVsActualChart data={chartData} loading={financeLoading} />
            
            <div className="rounded-xl border border-border bg-white p-5 shadow-sm h-full">
              <h3 className="font-semibold mb-4 text-sm uppercase tracking-wider text-muted-foreground">Status de Saúde</h3>
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-100">
                  <p className="text-xs text-emerald-700 font-bold mb-1">RENTABILIDADE PREVISTA</p>
                  <p className="text-xl font-bold text-emerald-800">22.4%</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span>Execução Orçamental</span>
                    <span className="font-bold">{summary?.performance_percentage.toFixed(1)}%</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div 
                      className={cn(
                        "h-full rounded-full",
                        summary?.is_over_budget ? "bg-destructive" : "bg-primary"
                      )} 
                      style={{ width: `${Math.min(summary?.performance_percentage || 0, 100)}%` }} 
                    />
                  </div>
                </div>
                <div className="pt-4 border-t border-slate-100">
                  <p className="text-xs text-muted-foreground mb-3">CONCELHOS FINANCEIROS (AI)</p>
                  <p className="text-xs leading-relaxed italic text-slate-600">
                    "O custo de acabamentos está 12% acima do orçado. Recomenda-se revisão do contrato de fornecimento de cerâmicas para a fase 5."
                  </p>
                </div>
              </div>
            </div>
          </div>

          <ExpenseList expenses={expenses || []} loading={financeLoading} />
        </TabsContent>

        <TabsContent value="advances">
          <div className="rounded-xl border border-dashed border-border p-12 text-center text-muted-foreground">
            <EuroIcon className="h-12 w-12 mx-auto mb-4 opacity-20" />
            <h3 className="font-medium text-foreground">Gestão de Adiantamentos</h3>
            <p className="text-sm max-w-sm mx-auto mt-2">
              Acompanhe os pagamentos antecipados a subempreiteiros e a sua respectiva amortização por via de autos de medição.
            </p>
            <Button variant="outline" className="mt-6" disabled>Em desenvolvimento</Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function FinanceSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-64" />
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Skeleton className="col-span-2 h-[350px] rounded-xl" />
        <Skeleton className="h-[350px] rounded-xl" />
      </div>
      <Skeleton className="h-64 w-full rounded-xl" />
    </div>
  );
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(" ");
}
