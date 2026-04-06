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
  Cell
} from "recharts";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/Skeleton";
import { ConstructionProject } from "@/hooks/useConstructionStats";

interface ProgressChartProps {
  projects: ConstructionProject[];
  isLoading?: boolean;
  maxItems?: number;
}

export function ProgressChart({ projects, isLoading, maxItems = 8 }: ProgressChartProps) {
  const data = useMemo(() => {
    return projects
      .slice(0, maxItems)
      .map((p) => ({
        name: p.name.length > 20 ? p.name.slice(0, 20) + "..." : p.name,
        progress: Math.round(p.overall_progress_pct),
        status: p.status,
      }))
      .sort((a, b) => b.progress - a.progress);
  }, [projects, maxItems]);

  const getBarColor = (progress: number, status: string) => {
    if (status === "COMPLETED") return "#10b981"; // emerald-500
    if (progress >= 75) return "#3b82f6"; // blue-500
    if (progress >= 50) return "#8b5cf6"; // violet-500
    if (progress >= 25) return "#f59e0b"; // amber-500
    return "#6b7280"; // gray-500
  };

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
        <h3 className="text-lg font-semibold mb-4">Progresso por Obra</h3>
        <div className="h-64 flex items-center justify-center text-muted-foreground">
          <p className="text-sm">Sem dados de obras disponíveis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Progresso por Obra</h3>
        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            Concluído
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            &gt;75%
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            &lt;50%
          </span>
        </div>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e5e7eb" />
            <XAxis 
              type="number" 
              domain={[0, 100]} 
              tickFormatter={(v) => `${v}%`}
              stroke="#6b7280"
              fontSize={12}
            />
            <YAxis 
              type="category" 
              dataKey="name" 
              width={120}
              tick={{ fontSize: 11 }}
              stroke="#6b7280"
            />
            <Tooltip
              formatter={(value: number) => [`${value}%`, "Progresso"]}
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            />
            <Bar dataKey="progress" radius={[0, 4, 4, 0]} barSize={20}>
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={getBarColor(entry.progress, entry.status)} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
