"use client";

import { useState } from "react";
import { usePaymentPatterns, useApplyPaymentPattern } from "@/hooks/useContractSettings";
import { Skeleton } from "@/components/ui/Skeleton";
import { CreditCard, Check, ChevronRight, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface PatternSelectorProps {
  contractId: string;
  onSuccess?: () => void;
}

export function PatternSelector({ contractId, onSuccess }: PatternSelectorProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const { data, isLoading, isError } = usePaymentPatterns();
  const applyPattern = useApplyPaymentPattern();

  const patterns = data?.results ?? [];

  const handleApply = () => {
    if (!selectedId) return;
    applyPattern.mutate(
      { contractId, patternId: selectedId },
      {
        onSuccess: () => {
          setSelectedId(null);
          onSuccess?.();
        },
      }
    );
  };

  if (isLoading) return <Skeleton className="h-40 w-full rounded-2xl" />;
  if (isError) return <div className="text-xs text-red-500">Erro ao carregar padrões.</div>;

  return (
    <div className="space-y-4 p-4 bg-slate-50 rounded-2xl border border-slate-200/60">
      <div className="flex items-center gap-2 mb-2">
        <CreditCard className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-bold text-foreground">Seleccionar Padrão de Pagamento</h3>
      </div>

      <div className="grid grid-cols-1 gap-2">
        {patterns.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-4">
            Nenhum padrão activo encontrado.
          </p>
        ) : (
          patterns.map((ptn) => (
            <button
              key={ptn.id}
              onClick={() => setSelectedId(ptn.id)}
              className={cn(
                "flex items-center justify-between p-3 rounded-xl border text-left transition-all group",
                selectedId === ptn.id
                  ? "bg-white border-primary shadow-sm ring-1 ring-primary/20"
                  : "bg-white/50 border-slate-200 hover:border-primary/40 hover:bg-white"
              )}
            >
              <div>
                <p className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">
                  {ptn.name}
                </p>
                <p className="text-[10px] text-muted-foreground mt-0.5">
                  {ptn.down_payment_percentage}% Sinal + {ptn.installments_count} Prestações
                </p>
              </div>
              {selectedId === ptn.id ? (
                <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center">
                  <Check className="h-3 w-3 text-white" />
                </div>
              ) : (
                <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-primary transition-colors" />
              )}
            </button>
          ))
        )}
      </div>

      <button
        onClick={handleApply}
        disabled={!selectedId || applyPattern.isPending}
        className="w-full mt-2 py-2.5 bg-primary text-white text-xs font-bold rounded-xl shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all disabled:opacity-50 disabled:shadow-none"
      >
        {applyPattern.isPending ? "A aplicar…" : "Aplicar Estrutura de Pagamentos"}
      </button>

      {applyPattern.isError && (
        <div className="flex items-center gap-1.5 text-[10px] font-bold text-red-600 bg-red-50 p-2 rounded-lg border border-red-100">
          <AlertCircle className="h-3.5 w-3.5" />
          Erro ao aplicar padrão.
        </div>
      )}
    </div>
  );
}
