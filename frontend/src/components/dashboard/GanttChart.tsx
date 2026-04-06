"use client";

import { useMemo } from "react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/Skeleton";
import { GanttItem, getStatusColor, getStatusLabel } from "@/hooks/useConstructionStats";
import { formatDate } from "@/lib/format";

interface GanttChartProps {
  items: GanttItem[];
  isLoading?: boolean;
  startDate?: string;
  endDate?: string;
}

export function GanttChart({ items, isLoading, startDate, endDate }: GanttChartProps) {
  // Calculate timeline bounds
  const timelineBounds = useMemo(() => {
    if (items.length === 0) return { start: new Date(), end: new Date(), days: 30 };
    
    const dates = items.flatMap(item => [
      new Date(item.start_date),
      new Date(item.end_date)
    ]);
    
    const start = new Date(Math.min(...dates.map(d => d.getTime())));
    const end = new Date(Math.max(...dates.map(d => d.getTime())));
    
    // Add some padding
    start.setDate(start.getDate() - 7);
    end.setDate(end.getDate() + 7);
    
    const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    
    return { start, end, days };
  }, [items]);

  // Calculate position and width for each item
  const getItemStyle = (item: GanttItem) => {
    const itemStart = new Date(item.start_date);
    const itemEnd = new Date(item.end_date);
    
    const daysFromStart = Math.ceil((itemStart.getTime() - timelineBounds.start.getTime()) / (1000 * 60 * 60 * 24));
    const duration = Math.ceil((itemEnd.getTime() - itemStart.getTime()) / (1000 * 60 * 60 * 24));
    
    const leftPercent = (daysFromStart / timelineBounds.days) * 100;
    const widthPercent = (duration / timelineBounds.days) * 100;
    
    return { left: `${leftPercent}%`, width: `${Math.max(widthPercent, 2)}%` };
  };

  // Generate month headers
  const monthHeaders = useMemo(() => {
    const headers = [];
    const current = new Date(timelineBounds.start);
    
    while (current <= timelineBounds.end) {
      headers.push({
        label: current.toLocaleDateString("pt-PT", { month: "short", year: "numeric" }),
        date: new Date(current),
      });
      current.setMonth(current.getMonth() + 1);
    }
    
    return headers;
  }, [timelineBounds]);

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
        <Skeleton className="h-6 w-32 mb-6" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Cronograma (Gantt)</h3>
        <div className="h-64 flex items-center justify-center text-muted-foreground">
          <p className="text-sm">Sem dados de cronograma disponíveis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
      <div className="p-4 border-b border-border bg-slate-50/50">
        <h3 className="text-lg font-semibold">Cronograma (Gantt)</h3>
        <p className="text-xs text-muted-foreground">
          {formatDate(timelineBounds.start.toISOString())} - {formatDate(timelineBounds.end.toISOString())}
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <div className="min-w-[600px]">
          {/* Timeline Header */}
          <div className="flex border-b border-border">
            <div className="w-48 shrink-0 p-3 text-xs font-medium text-muted-foreground bg-slate-50/30 border-r border-border">
              Atividade
            </div>
            <div className="flex-1 relative">
              <div className="flex h-10">
                {monthHeaders.map((header, i) => (
                  <div
                    key={i}
                    className="flex-1 border-r border-border px-2 py-2 text-[10px] font-medium text-muted-foreground uppercase tracking-wider"
                  >
                    {header.label}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Timeline Items */}
          <div className="divide-y divide-border">
            {items.map((item, index) => {
              const style = getItemStyle(item);
              const statusColors = getStatusColor(item.status);
              
              return (
                <div key={item.id} className="flex group hover:bg-slate-50/50">
                  {/* Item Label */}
                  <div className="w-48 shrink-0 p-3 border-r border-border">
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        "w-2 h-2 rounded-full",
                        item.type === "phase" ? "bg-blue-500" : "bg-slate-400"
                      )} />
                      <div>
                        <p className="text-xs font-medium text-foreground truncate">{item.name}</p>
                        <span className={cn(
                          "text-[10px] px-1.5 py-0.5 rounded-full",
                          statusColors.bg,
                          statusColors.text
                        )}>
                          {getStatusLabel(item.status)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Item Bar */}
                  <div className="flex-1 relative h-14">
                    <div
                      className="absolute top-3 h-8 rounded-md overflow-hidden group-hover:shadow-md transition-shadow"
                      style={style}
                    >
                      {/* Progress bar */}
                      <div className={cn(
                        "h-full relative",
                        item.type === "phase" ? "bg-blue-500" : "bg-slate-400"
                      )}>
                        {/* Progress fill */}
                        <div
                          className="h-full bg-opacity-30 bg-white"
                          style={{ width: `${100 - item.progress_pct}%`, marginLeft: "auto" }}
                        />
                        {/* Progress label */}
                        <span className="absolute inset-0 flex items-center justify-center text-[10px] font-medium text-white drop-shadow">
                          {item.progress_pct}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="px-4 py-3 border-t border-border bg-slate-50/30 flex items-center gap-4 text-xs">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-blue-500" />
          Fase
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-slate-400" />
          Tarefa
        </span>
        <span className="text-muted-foreground">
          Largura = Duração | Cor interna = Progresso
        </span>
      </div>
    </div>
  );
}
