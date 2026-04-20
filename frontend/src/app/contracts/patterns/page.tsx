"use client";

import { usePaymentPatterns } from "@/hooks/useContractSettings";
import { Skeleton } from "@/components/ui/Skeleton";
import { CreditCard, Plus, AlertCircle, CheckCircle2, Clock, CalendarDays, Percent } from "lucide-react";
import { formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";
import { PatternModal } from "@/components/contracts/PatternModal";
import { useState } from "react";

export default function PatternsPage() {
  const { data, isLoading, isError } = usePaymentPatterns();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPattern, setSelectedPattern] = useState<any>(null);
  
  const patterns = data?.results ?? [];

  const handleEdit = (ptn: any) => {
    setSelectedPattern(ptn);
    setIsModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedPattern(null);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-foreground">Padrões de Pagamento</h2>
        <button 
          onClick={handleCreate}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-xl font-bold text-xs shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all active:scale-95"
        >
          <Plus className="h-4 w-4" />
          Novo Padrão
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-56 w-full rounded-2xl" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-12 rounded-2xl border border-red-100 bg-red-50/50 text-center">
          <AlertCircle className="h-10 w-10 text-red-500 mx-auto mb-4" />
          <p className="text-sm font-bold text-red-600">Erro ao carregar padrões de pagamento.</p>
        </div>
      ) : patterns.length === 0 ? (
        <div className="p-20 flex flex-col items-center text-center rounded-3xl border-2 border-dashed border-slate-200 bg-slate-50/50">
          <div className="h-20 w-20 rounded-2xl bg-white shadow-sm border border-slate-200 flex items-center justify-center mb-6">
            <CreditCard className="h-10 w-10 text-primary/40" />
          </div>
          <p className="text-lg font-bold text-foreground">Ainda sem padrões configurados</p>
          <p className="text-sm text-muted-foreground mt-2 max-w-xs">
            Configure estruturas de pagamento recorrentes (ex: Sinal 20% + 24 Prestações) para poupar tempo.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {patterns.map((ptn) => (
            <div
              key={ptn.id}
              className="group relative bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-xl hover:shadow-slate-200/50 transition-all hover:-translate-y-1 overflow-hidden"
            >
              {/* Type tag background decorator */}
              <div className="absolute -right-4 -top-4 bg-primary/5 h-16 w-16 rounded-full group-hover:bg-primary/10 transition-colors" />

              <div className="flex items-start justify-between mb-4 relative z-10">
                <div className="h-12 w-12 rounded-xl bg-orange-50 flex items-center justify-center border border-orange-100 transition-colors group-hover:bg-orange-100">
                  <CreditCard className="h-6 w-6 text-orange-600" />
                </div>
                <span
                  className={cn(
                    "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider",
                    ptn.is_active
                      ? "bg-emerald-50 text-emerald-600 border border-emerald-100"
                      : "bg-slate-100 text-slate-500 border border-slate-200"
                  )}
                >
                  {ptn.is_active ? "Activo" : "Inactivo"}
                </span>
              </div>

              <h3 className="font-bold text-foreground mb-1 group-hover:text-primary transition-colors relative z-10">
                {ptn.name}
              </h3>
              <p className="text-xs text-muted-foreground line-clamp-1 mb-4">
                {ptn.description || "Estrutura personalizada."}
              </p>

              <div className="grid grid-cols-2 gap-3 mb-4 bg-slate-50/80 rounded-xl p-3 border border-slate-100">
                <div className="space-y-1">
                  <p className="text-[9px] text-muted-foreground uppercase font-bold tracking-tighter">Entrada (Sinal)</p>
                  <div className="flex items-center gap-1 text-xs font-black text-foreground">
                    <Percent className="h-3 w-3 text-primary" />
                    {ptn.down_payment_percentage}%
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-[9px] text-muted-foreground uppercase font-bold tracking-tighter">Prestações</p>
                  <div className="flex items-center gap-1 text-xs font-black text-foreground">
                    <CalendarDays className="h-3 w-3 text-primary" />
                    {ptn.installments_count}x
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-[10px] font-medium text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Atualizado {formatDate(ptn.updated_at)}
                </div>
                <button 
                    onClick={() => handleEdit(ptn)}
                    className="text-primary font-bold hover:underline"
                >
                    Configurar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <PatternModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        initialData={selectedPattern}
      />
    </div>
  );
}
