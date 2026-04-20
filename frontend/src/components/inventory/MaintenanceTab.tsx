"use client";

import { useState } from "react";
import { 
  Wrench, 
  AlertTriangle, 
  CheckCircle2, 
  Plus, 
  Clock,
  ChevronRight,
  MessageSquare,
  Loader2,
  X
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useUnitOccurrences, useResolveOccurrence, UnitOccurrence } from "@/hooks/useUnits";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export function MaintenanceTab({ unitId, unitCode }: { unitId: string; unitCode: string }) {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const { data: occurrencesPage, isLoading } = useUnitOccurrences(unitId);
  const resolveMutation = useResolveOccurrence();
  
  const occurrences = occurrencesPage?.results ?? [];

  const priorityColors: Record<string, string> = {
    URGENT: "text-red-600 bg-red-50 border-red-100",
    HIGH: "text-orange-600 bg-orange-50 border-orange-100",
    NORMAL: "text-blue-600 bg-blue-50 border-blue-100",
    LOW: "text-slate-600 bg-slate-50 border-slate-100",
  };

  const handleResolve = async (id: string) => {
    try {
      await resolveMutation.mutateAsync({ occurrenceId: id, resolution_notes: "Resolvido via dashboard" });
    } catch (err) {
      console.error("Failed to resolve occurrence", err);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-20 bg-slate-50 rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">Histórico Técnico</h3>
          <p className="text-xs text-muted-foreground">Ocorrências e manutenções da unidade {unitCode}</p>
        </div>
        <Button size="sm" onClick={() => setIsFormOpen(true)} className="gap-2 h-8 px-3 text-xs">
          <Plus className="h-3.5 w-3.5" />
          Reportar Problema
        </Button>
      </div>

      {isFormOpen && (
        <div className="bg-slate-50 rounded-2xl border border-slate-200 p-4 border-dashed animate-in slide-in-from-top-2">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-xs font-bold text-slate-700">Nova Ocorrência</h4>
            <button onClick={() => setIsFormOpen(false)} className="text-slate-400 hover:text-slate-600">
              <X className="h-4 w-4" />
            </button>
          </div>
          <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); setIsFormOpen(false); }}>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Prioridade</label>
                <select className="w-full bg-white border border-slate-200 px-3 py-1.5 rounded-lg text-xs outline-none">
                  <option value="NORMAL">Normal</option>
                  <option value="HIGH">Alta</option>
                  <option value="URGENT">Urgente</option>
                  <option value="LOW">Baixa</option>
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Tipo</label>
                <select className="w-full bg-white border border-slate-200 px-3 py-1.5 rounded-lg text-xs outline-none">
                  <option>Reparação</option>
                  <option>Preventiva</option>
                  <option>Vistoria</option>
                </select>
              </div>
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase">Descrição</label>
              <textarea 
                rows={2}
                className="w-full bg-white border border-slate-200 px-3 py-2 rounded-lg text-xs outline-none resize-none"
                placeholder="Descreva o problema técnico detectado..."
              />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <Button type="button" variant="ghost" size="sm" onClick={() => setIsFormOpen(false)} className="h-8 text-xs">Cancelar</Button>
              <Button type="submit" size="sm" className="h-8 text-xs">Submeter</Button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-3">
        {occurrences.map((occurrence) => (
          <div 
            key={occurrence.id}
            className="group bg-white rounded-xl border border-slate-100 p-4 hover:border-slate-200 transition-all shadow-sm"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className={cn(
                  "mt-0.5 p-2 rounded-lg border",
                  priorityColors[occurrence.priority]
                )}>
                  <AlertTriangle className="h-4 w-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={cn(
                      "text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase",
                      occurrence.status === "RESOLVED" ? "bg-emerald-50 text-emerald-600 border-emerald-100" :
                      occurrence.status === "OPEN" ? "bg-orange-50 text-orange-600 border-orange-100" :
                      "bg-blue-50 text-blue-600 border-blue-100"
                    )}>
                      {occurrence.status === "RESOLVED" ? "Resolvido" : "Aberto"}
                    </span>
                    <span className="text-[10px] text-muted-foreground font-medium">
                      {format(new Date(occurrence.created_at), "dd 'de' MMM, HH:mm", { locale: ptBR })}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-slate-700 mb-1">{occurrence.description}</p>
                  {occurrence.resolution_notes && (
                    <div className="mt-2 p-2 bg-slate-50 rounded-lg border border-slate-100 flex items-start gap-2">
                      <CheckCircle2 className="h-3 w-3 text-emerald-500 mt-0.5 shrink-0" />
                      <p className="text-[11px] text-slate-600 italic">{occurrence.resolution_notes}</p>
                    </div>
                  )}
                </div>
              </div>
              
              {occurrence.status !== "RESOLVED" && (
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="h-8 text-[11px] font-bold text-emerald-600 border-emerald-100 hover:bg-emerald-50 shrink-0"
                  onClick={() => handleResolve(occurrence.id)}
                  disabled={resolveMutation.isPending}
                >
                  {resolveMutation.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : "Marcar como Resolvido"}
                </Button>
              )}
            </div>
          </div>
        ))}

        {occurrences.length === 0 && !isFormOpen && (
          <div className="text-center py-12 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200">
            <CheckCircle2 className="h-8 w-8 text-slate-300 mx-auto mb-2" />
            <p className="text-sm text-slate-500 font-medium">Sem histórico de manutenção</p>
            <p className="text-[10px] text-slate-400">Esta unidade encontra-se em perfeitas condições.</p>
          </div>
        )}
      </div>
    </div>
  );
}
