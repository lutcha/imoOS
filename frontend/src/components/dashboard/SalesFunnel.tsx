"use client";

import { useLeadsByStage, LeadStatus, initialLeadPipeline } from "@/hooks/useLeads";
import { cn } from "@/lib/utils";
import { TrendingUp, Users, ShoppingCart } from "lucide-react";

export function SalesFunnel() {
  const { data: pipeline, isLoading } = useLeadsByStage();

  const stages: { status: LeadStatus; label: string; color: string }[] = [
    { status: "NEW", label: "Novos", color: "bg-blue-500" },
    { status: "CONTACTED", label: "Contactados", color: "bg-indigo-500" },
    { status: "VISIT_SCHEDULED", label: "Visitas", color: "bg-purple-500" },
    { status: "PROPOSAL_SENT", label: "Propostas", color: "bg-pink-500" },
    { status: "NEGOTIATION", label: "Negociação", color: "bg-orange-500" },
    { status: "WON", label: "Ganhos", color: "bg-emerald-500" },
  ];

  const totalLeads = stages.reduce((acc, stage) => {
    return acc + (pipeline?.[stage.status]?.count ?? 0);
  }, 0);

  // Simulating imotech.cv leads percentage (usually majority in this context)
  const imotechPercentage = 75; 

  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-2xl border border-border animate-pulse h-[350px]">
        <div className="h-6 w-48 bg-slate-100 rounded mb-8" />
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-10 bg-slate-50 rounded" />
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
            <TrendingUp className="h-5 w-5 text-primary" />
            Funil de Vendas
          </h3>
          <p className="text-xs text-muted-foreground">Marketplace imotech.cv</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-primary/5 text-primary rounded-full border border-primary/10">
          <ShoppingCart className="h-3.5 w-3.5" />
          <span className="text-[10px] font-bold uppercase tracking-wider">imotech.cv</span>
        </div>
      </div>

      <div className="flex-1 space-y-3">
        {stages.map((stage, idx) => {
          const count = pipeline?.[stage.status]?.count ?? 0;
          const percentage = totalLeads > 0 ? (count / totalLeads) * 100 : 0;
          
          return (
            <div key={stage.status} className="group relative">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-slate-600">{stage.label}</span>
                <span className="text-xs font-bold">{count}</span>
              </div>
              <div className="h-2 w-full bg-slate-50 rounded-full overflow-hidden">
                <div 
                  className={cn("h-full rounded-full transition-all duration-1000 ease-out", stage.color)}
                  style={{ width: `${Math.max(percentage, 2)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 p-4 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white rounded-lg shadow-sm">
            <Users className="h-4 w-4 text-primary" />
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight">Origem</p>
            <p className="text-xs font-semibold">imotech.cv</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-primary">{imotechPercentage}%</p>
          <p className="text-[9px] text-muted-foreground">do tráfego total</p>
        </div>
      </div>
    </div>
  );
}
