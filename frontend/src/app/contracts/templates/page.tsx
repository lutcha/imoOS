"use client";

import { useContractTemplates } from "@/hooks/useContractSettings";
import { Skeleton } from "@/components/ui/Skeleton";
import { FileCode2, Plus, AlertCircle, CheckCircle2, Clock } from "lucide-react";
import { formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";

export default function TemplatesPage() {
  const { data, isLoading, isError } = useContractTemplates();
  const templates = data?.results ?? [];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-foreground">Templates de Documentos</h2>
        <button className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-xl font-bold text-xs shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all active:scale-95">
          <Plus className="h-4 w-4" />
          Novo Template
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-2xl" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-12 rounded-2xl border border-red-100 bg-red-50/50 text-center">
          <AlertCircle className="h-10 w-10 text-red-500 mx-auto mb-4" />
          <p className="text-sm font-bold text-red-600">Erro ao carregar templates.</p>
        </div>
      ) : templates.length === 0 ? (
        <div className="p-20 flex flex-col items-center text-center rounded-3xl border-2 border-dashed border-slate-200 bg-slate-50/50">
          <div className="h-20 w-20 rounded-2xl bg-white shadow-sm border border-slate-200 flex items-center justify-center mb-6">
            <FileCode2 className="h-10 w-10 text-primary/40" />
          </div>
          <p className="text-lg font-bold text-foreground">Sem templates criados</p>
          <p className="text-sm text-muted-foreground mt-2 max-w-xs">
            Crie templates HTML com variáveis dinâmicas para automatizar a geração de contratos.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((tpl) => (
            <div
              key={tpl.id}
              className="group relative bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-xl hover:shadow-slate-200/50 transition-all hover:-translate-y-1"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="h-12 w-12 rounded-xl bg-primary/5 flex items-center justify-center border border-primary/10 transition-colors group-hover:bg-primary/10">
                  <FileCode2 className="h-6 w-6 text-primary" />
                </div>
                <span
                  className={cn(
                    "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider",
                    tpl.is_active
                      ? "bg-emerald-50 text-emerald-600 border border-emerald-100"
                      : "bg-slate-100 text-slate-500 border border-slate-200"
                  )}
                >
                  {tpl.is_active ? (
                    <>
                      <CheckCircle2 className="h-3 w-3" /> Activo
                    </>
                  ) : (
                    "Inactivo"
                  )}
                </span>
              </div>

              <h3 className="font-bold text-foreground mb-1 group-hover:text-primary transition-colors">
                {tpl.name}
              </h3>
              <p className="text-xs text-muted-foreground line-clamp-2 mb-4 h-8">
                {tpl.description || "Sem descrição disponível."}
              </p>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-[10px] font-medium text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Actualizado em {formatDate(tpl.updated_at)}
                </div>
                <button className="text-primary font-bold hover:underline">Editar</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
