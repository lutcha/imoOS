"use client";

import { useUnitOccurrences, UnitOccurrence } from "@/hooks/useUnits";
import { cn } from "@/lib/utils";
import { Wrench, AlertTriangle, CheckCircle2, Clock, ArrowRight } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export function MaintenanceSummary() {
  const { data: occurrencesPage, isLoading } = useUnitOccurrences();
  const occurrences = occurrencesPage?.results ?? [];

  const openCount = occurrences.filter(o => o.status !== "RESOLVED" && o.status !== "CANCELLED").length;
  const resolvedCount = occurrences.filter(o => o.status === "RESOLVED").length;

  const priorityColors: Record<string, string> = {
    URGENT: "text-red-600 bg-red-50 border-red-100",
    HIGH: "text-orange-600 bg-orange-50 border-orange-100",
    NORMAL: "text-blue-600 bg-blue-50 border-blue-100",
    LOW: "text-slate-600 bg-slate-50 border-slate-100",
  };

  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-2xl border border-border animate-pulse h-full">
        <div className="h-6 w-48 bg-slate-100 rounded mb-8" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-slate-50 rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-2xl border border-border shadow-sm flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Wrench className="h-5 w-5 text-primary" />
            Manutenção e Ativos
          </h3>
          <p className="text-xs text-muted-foreground">Estado técnico das unidades</p>
        </div>
        <Link 
          href="/inventory?tab=maintenance" 
          className="p-2 hover:bg-slate-50 rounded-full transition-colors"
        >
          <ArrowRight className="h-4 w-4 text-muted-foreground" />
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-4 bg-orange-50/50 rounded-xl border border-orange-100 flex flex-col items-center justify-center text-center">
          <AlertTriangle className="h-5 w-5 text-orange-500 mb-1" />
          <p className="text-2xl font-bold text-orange-700">{openCount}</p>
          <p className="text-[10px] uppercase font-bold text-orange-600 tracking-wider">Abertas</p>
        </div>
        <div className="p-4 bg-emerald-50/50 rounded-xl border border-emerald-100 flex flex-col items-center justify-center text-center">
          <CheckCircle2 className="h-5 w-5 text-emerald-500 mb-1" />
          <p className="text-2xl font-bold text-emerald-700">{resolvedCount}</p>
          <p className="text-[10px] uppercase font-bold text-emerald-600 tracking-wider">Resolvidas</p>
        </div>
      </div>

      <div className="flex-1 space-y-3">
        <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-2">Últimas Ocorrências</p>
        {occurrences.slice(0, 4).map((occurrence) => (
          <div 
            key={occurrence.id} 
            className="flex items-start gap-3 p-3 rounded-xl border border-slate-50 hover:border-slate-100 hover:bg-slate-50/50 transition-all cursor-default group"
          >
            <div className={cn(
              "mt-0.5 p-1.5 rounded-lg border",
              priorityColors[occurrence.priority] || priorityColors.NORMAL
            )}>
              <Clock className="h-3.5 w-3.5" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-bold truncate">Unid. {occurrence.unit_code}</span>
                <span className="text-[10px] text-muted-foreground">
                  {format(new Date(occurrence.created_at), "dd MMM", { locale: ptBR })}
                </span>
              </div>
              <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                {occurrence.description}
              </p>
            </div>
          </div>
        ))}

        {occurrences.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 text-center bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
            <CheckCircle2 className="h-8 w-8 text-slate-300 mb-2" />
            <p className="text-sm text-slate-500">Nenhuma ocorrência pendente</p>
          </div>
        )}
      </div>
    </div>
  );
}
