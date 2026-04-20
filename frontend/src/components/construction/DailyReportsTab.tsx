"use client";

import { useState } from "react";
import { 
  CloudSun, 
  Users, 
  FileText, 
  Plus, 
  Camera, 
  CheckCircle2, 
  Clock,
  ChevronRight,
  Loader2,
  X
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

interface DailyReport {
  id: string;
  date: string;
  weather: string;
  workers_count: number;
  summary: string;
  status: "DRAFT" | "SUBMITTED" | "APPROVED";
  created_by_name: string;
}

export function DailyReportsTab({ projectId }: { projectId: string }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Mock data for now based on the model we created
  const reports: DailyReport[] = [
    {
      id: "1",
      date: new Date().toISOString(),
      weather: "Ensolarado",
      workers_count: 12,
      summary: "Conclusão da betonagem do pilar P12 e início da cofragem da laje do 1º piso.",
      status: "APPROVED",
      created_by_name: "Manuel Silva",
    },
    {
      id: "2",
      date: new Date(Date.now() - 86400000).toISOString(),
      weather: "Nublado",
      workers_count: 8,
      summary: "Preparação de armaduras e limpeza do estaleiro. Atraso devido a falha na entrega de inertes.",
      status: "SUBMITTED",
      created_by_name: "António Costa",
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Diários de Obra</h3>
          <p className="text-sm text-muted-foreground">Registo diário de actividades, efectivos e condições</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          Novo Registo
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {reports.map((report) => (
          <div 
            key={report.id}
            className="group bg-white rounded-2xl border border-border p-5 hover:border-primary/30 transition-all cursor-pointer shadow-sm"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="h-12 w-12 rounded-xl bg-slate-50 flex flex-col items-center justify-center border border-slate-100 shrink-0">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">
                    {format(new Date(report.date), "MMM", { locale: ptBR })}
                  </span>
                  <span className="text-lg font-bold text-slate-700 leading-none">
                    {format(new Date(report.date), "dd")}
                  </span>
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={cn(
                      "text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider",
                      report.status === "APPROVED" ? "bg-emerald-50 text-emerald-600 border-emerald-100" :
                      report.status === "SUBMITTED" ? "bg-blue-50 text-blue-600 border-blue-100" :
                      "bg-slate-50 text-slate-600 border-slate-100"
                    )}>
                      {report.status === "APPROVED" ? "Aprovado" : "Submetido"}
                    </span>
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <CloudSun className="h-3 w-3" />
                      {report.weather}
                    </span>
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      {report.workers_count} trabalhadores
                    </span>
                  </div>
                  <p className="text-sm font-medium text-slate-700 line-clamp-2">
                    {report.summary}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4 shrink-0">
                <div className="text-right hidden md:block">
                  <p className="text-xs font-semibold text-slate-600">{report.created_by_name}</p>
                  <p className="text-[10px] text-muted-foreground">Responsável</p>
                </div>
                <ChevronRight className="h-5 w-5 text-slate-300 group-hover:text-primary transition-colors" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {isModalOpen && (
        <NewReportModal 
          isOpen={isModalOpen} 
          onClose={() => setIsModalOpen(false)} 
          projectId={projectId} 
        />
      )}
    </div>
  );
}

function NewReportModal({ isOpen, onClose, projectId }: { isOpen: boolean; onClose: () => void; projectId: string }) {
  const [loading, setLoading] = useState(false);

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white w-full max-w-xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="border-b border-slate-100 px-6 py-4 flex items-center justify-between bg-slate-50/50">
          <div>
            <h2 className="text-lg font-bold text-slate-800">Novo Diário de Obra</h2>
            <p className="text-xs text-slate-500">Registe o progresso do dia hoje</p>
          </div>
          <button onClick={onClose} className="p-2 -mr-2 text-slate-400 hover:bg-slate-100 rounded-full">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form className="p-6 space-y-4" onSubmit={(e) => { e.preventDefault(); onClose(); }}>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Data</label>
              <input 
                type="date" 
                defaultValue={new Date().toISOString().split('T')[0]}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:ring-2 focus:ring-primary/20 outline-none" 
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Clima</label>
              <select className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:ring-2 focus:ring-primary/20 outline-none appearance-none">
                <option>Ensolarado</option>
                <option>Nublado</option>
                <option>Chuvoso</option>
                <option>Vento Forte</option>
              </select>
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Nº de Trabalhadores</label>
            <input 
              type="number" 
              placeholder="0"
              className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:ring-2 focus:ring-primary/20 outline-none" 
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Resumo das Actividades</label>
            <textarea 
              rows={4}
              placeholder="Descreva o que foi feito hoje, materiais recebidos, eventuais problemas..."
              className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:ring-2 focus:ring-primary/20 outline-none resize-none"
            />
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-dashed border-slate-200 flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-slate-100 transition-colors">
            <Camera className="h-6 w-6 text-slate-400" />
            <p className="text-xs font-medium text-slate-500">Adicionar Fotos da Obra</p>
          </div>

          <div className="pt-4 flex justify-end gap-3">
            <Button type="button" variant="ghost" onClick={onClose}>Cancelar</Button>
            <Button type="submit" disabled={loading} className="px-8">
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <CheckCircle2 className="h-4 w-4 mr-2" />}
              Submeter Diário
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
