"use client";

import { useMemo } from "react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  ReferenceLine
} from "recharts";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/Skeleton";
import { BudgetStats } from "@/hooks/useBudgetStats";
import { formatCveCompact } from "@/lib/format";

interface BudgetChartProps {
  stats: BudgetStats | null;
  isLoading?: boolean;
}

export function BudgetChart({ stats, isLoading }: BudgetChartProps) {
  const data = useMemo(() => {
    if (!stats?.categories_summary) return [];
    
    return stats.categories_summary.map((cat) => ({
      name: cat.category_name.length > 15 
        ? cat.category_name.slice(0, 15) + "..." 
        : cat.category_name,
      orcado: parseFloat(cat.budgeted_cve),
      real: parseFloat(cat.actual_cve),
      variacao: cat.variance_pct,
    }));
  }, [stats]);

  const totals = useMemo(() => {
    if (!stats) return { orcado: 0, real: 0, variacao: 0 };
    return {
      orcado: parseFloat(stats.total_budgeted_cve),
      real: parseFloat(stats.total_actual_cve),
      variacao: stats.overall_variance_pct,
    };
  }, [stats]);

  const formatTooltipValue = (value: number) => formatCveCompact(value);

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
        <Skeleton className="h-6 w-48 mb-6" />
        <div className="h-64">
          <Skeleton className="h-full w-full" />
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Orçamento vs Real</h3>
        <div className="h-64 flex items-center justify-center text-muted-foreground">
          <p className="text-sm">Sem dados de orçamento disponíveis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold">Orçamento vs Real</h3>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Variação Total</p>
          <p className={cn(
            "text-sm font-bold",
            totals.variacao > 10 ? "text-red-600" : 
            totals.variacao > 5 ? "text-amber-600" : 
            totals.variacao < -5 ? "text-emerald-600" : "text-slate-600"
          )}>
            {totals.variacao > 0 ? "+" : ""}{totals.variacao.toFixed(1)}%
          </p>
        </div>
      </div>
      
      <div className="mb-4 flex items-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-blue-500" />
          <span>Orçado: {formatCveCompact(totals.orcado)}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-emerald-500" />
          <span>Real: {formatCveCompact(totals.real)}</span>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 10, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 11 }}
              stroke="#6b7280"
              interval={0}
              angle={-30}
              textAnchor="end"
              height={60}
            />
            <YAxis 
              tickFormatter={(v) => formatCveCompact(v)}
              stroke="#6b7280"
              fontSize={11}
            />
            <Tooltip
              formatter={(value: number, name: string) => [
                formatCveCompact(value),
                name === "orcado" ? "Orçado" : "Real"
              ]}
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: "12px" }}
              formatter={(value) => value === "orcado" ? "Orçado" : "Real"}
            />
            <Bar dataKey="orcado" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="real" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
