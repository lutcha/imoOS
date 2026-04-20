"use client";

import { useState } from "react";
import { X, Info, Wrench, Building2, Layout, MapPin, DollarSign } from "lucide-react";
import { cn } from "@/lib/utils";
import { MaintenanceTab } from "./MaintenanceTab";
import { UnitStatusBadge } from "@/components/ui/StatusBadge";
import { formatArea, formatCve } from "@/lib/format";

interface UnitDetailsModalProps {
  unit: any | null;
  isOpen: boolean;
  onClose: () => void;
}

export function UnitDetailsModal({ unit, isOpen, onClose }: UnitDetailsModalProps) {
  const [activeTab, setActiveTab] = useState<"info" | "maintenance">("info");

  if (!isOpen || !unit) return null;

  const tabs = [
    { id: "info", label: "Informação Geral", icon: Info },
    { id: "maintenance", label: "Manutenção", icon: Wrench },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200" 
        onClick={onClose} 
      />
      <div className="relative bg-white w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="border-b border-slate-100 px-6 py-4 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-3">
             <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
                <Building2 className="h-5 w-5 text-primary" />
             </div>
             <div>
                <h2 className="text-xl font-bold text-slate-800">Unidade {unit.code}</h2>
                <div className="flex items-center gap-2 mt-0.5">
                  <UnitStatusBadge status={unit.status} />
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">• {unit.unit_type_detail?.name || unit.unit_type}</span>
                </div>
             </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 -mr-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 border-b border-slate-100 flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "py-3 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition-all",
                activeTab === tab.id 
                  ? "border-primary text-primary" 
                  : "border-transparent text-slate-400 hover:text-slate-600"
              )}
            >
              <tab.icon className="h-3.5 w-3.5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === "info" && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <DetailItem icon={Layout} label="Localização" value={`${unit.floor_number}º Piso • Nível ${unit.floor_level || "-"}`} />
                  <DetailItem icon={MapPin} label="Área Bruta" value={formatArea(unit.area_bruta)} />
                  <DetailItem icon={Building2} label="Edifício" value="Edifício Principal" />
                </div>
                <div className="space-y-4">
                  <DetailItem 
                    icon={DollarSign} 
                    label="Preço de Venda" 
                    value={unit.pricing ? formatCve(unit.pricing.final_price_cve) : "Sob Consulta"} 
                    highlight 
                  />
                  <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                    <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Descrição</p>
                    <p className="text-sm text-slate-600 leading-relaxed italic">
                      {unit.description || "Sem descrição disponível."}
                    </p>
                  </div>
                </div>
              </div>

              {/* CRM Info Summary if reserved/sold */}
              {(unit.status === "RESERVED" || unit.status === "SOLD") && (
                <div className="mt-8 p-4 bg-blue-50/50 rounded-2xl border border-blue-100 flex items-center justify-between">
                   <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">
                        JS
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-blue-600 uppercase">Proprietário / Comprador</p>
                        <p className="text-sm font-bold text-slate-800">João Silva</p>
                      </div>
                   </div>
                   <button className="text-xs font-bold text-primary hover:underline">Ver CRM</button>
                </div>
              )}
            </div>
          )}

          {activeTab === "maintenance" && (
            <MaintenanceTab unitId={unit.id} unitCode={unit.code} />
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex justify-end gap-3">
          <button 
            onClick={onClose}
            className="px-4 py-2 text-xs font-bold text-slate-500 hover:text-slate-700"
          >
            Fechar
          </button>
          <button className="px-6 py-2 bg-slate-800 text-white text-xs font-bold rounded-lg hover:bg-slate-900 transition-colors shadow-lg shadow-slate-800/10">
            Editar Unidade
          </button>
        </div>
      </div>
    </div>
  );
}

function DetailItem({ icon: Icon, label, value, highlight }: any) {
  return (
    <div className="flex items-start gap-3">
      <div className={cn("p-2 rounded-lg bg-slate-100 text-slate-500", highlight && "bg-primary/10 text-primary")}>
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{label}</p>
        <p className={cn("text-sm font-semibold text-slate-700", highlight && "text-slate-900 font-bold")}>{value}</p>
      </div>
    </div>
  );
}
