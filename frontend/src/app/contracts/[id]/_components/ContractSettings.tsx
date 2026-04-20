"use client";

import { useState } from "react";
import { useContractTemplates } from "@/hooks/useContractSettings";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";
import { FileCode2, Settings, Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ContractSettingsProps {
  contractId: string;
  currentTemplateId?: string | null;
}

export function ContractSettings({ contractId, currentTemplateId }: ContractSettingsProps) {
  const { schema } = useTenant();
  const qc = useQueryClient();
  const { data: templatesData } = useContractTemplates();
  const [selectedTemplate, setSelectedTemplate] = useState(currentTemplateId || "");
  const [isEditing, setIsEditing] = useState(false);

  const updateContract = useMutation({
    mutationFn: (data: { template_id: string | null }) =>
      apiClient.patch(`/contracts/contracts/${contractId}/`, { template: data.template_id }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["contracts", schema, "detail", contractId] });
      setIsEditing(false);
    },
  });

  const templates = templatesData?.results ?? [];

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Settings className="h-4 w-4 text-slate-400" />
          <h3 className="text-sm font-bold text-foreground">Definições do Documento</h3>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-[11px] font-bold text-primary hover:underline transition-all"
          >
            Alterar
          </button>
        )}
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100">
          <div className="h-10 w-10 rounded-lg bg-white shadow-sm border border-slate-200 flex items-center justify-center">
            <FileCode2 className="h-5 w-5 text-primary/60" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-tight">Template de Impressão</p>
            {isEditing ? (
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="mt-1 w-full bg-white border border-slate-200 rounded-lg px-2 py-1 text-xs outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="">Sem Template (Padrão)</option>
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            ) : (
              <p className="text-xs font-bold text-foreground truncate">
                {templates.find((t) => t.id === currentTemplateId)?.name ?? "Template Padrão (imoOS)"}
              </p>
            )}
          </div>
        </div>

        {isEditing && (
          <div className="flex items-center gap-2 pt-2">
            <button
              onClick={() => setIsEditing(false)}
              className="flex-1 py-2 text-xs font-bold text-muted-foreground hover:text-foreground transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={() => updateContract.mutate({ template_id: selectedTemplate || null })}
              disabled={updateContract.isPending}
              className="flex-1 py-2 bg-primary text-white text-xs font-bold rounded-lg shadow-md shadow-primary/10 hover:bg-primary/90 transition-all flex items-center justify-center gap-2"
            >
              {updateContract.isPending ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <Check className="h-3 w-3" />
              )}
              Guardar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
