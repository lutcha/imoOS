"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { 
  ArrowLeft, 
  Clock, 
  Calendar, 
  CheckCircle2, 
  AlertTriangle, 
  Camera, 
  Plus,
  ChevronRight,
  TrendingDown,
  TrendingUp,
  Info
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useProject, featureToProject } from "@/hooks/useProjects";
import { usePhases, useUpdateProgressPhoto } from "@/hooks/usePhases";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter 
} from "@/components/ui/dialog";

export default function ProjectTimelinePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  
  const [isUpdateOpen, setIsUpdateOpen] = useState(false);
  const [selectedPhaseId, setSelectedPhaseId] = useState<string | null>(null);
  
  // Data
  const { data: feature, isLoading: projectLoading } = useProject(id);
  const project = feature ? featureToProject(feature) : null;
  const { data: phases = [], isLoading: phasesLoading } = usePhases(id);
  const { mutate: updateProgress, isPending: isUpdating } = useUpdateProgressPhoto();

  const handleUpdate = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedPhaseId) return;

    const formData = new FormData(e.currentTarget);
    formData.append("phase_id", selectedPhaseId);
    
    updateProgress({ projectId: id, formData }, {
      onSuccess: () => {
        setIsUpdateOpen(false);
        setSelectedPhaseId(null);
      }
    });
  };

  if (projectLoading || phasesLoading) {
    return (
      <div className="p-8 space-y-8">
        <Skeleton className="h-8 w-64" />
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-20">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => router.back()}
          className="h-10 w-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="h-5 w-5 text-gray-500" />
        </button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Cronograma de Progresso</h1>
          <p className="text-sm text-muted-foreground font-medium">
            Acompanhamento em tempo real das fases de obra de {project?.name}
          </p>
        </div>
      </div>

      {/* Progress Stepper Visualizer */}
      <div className="relative space-y-0">
        {/* The connectors line */}
        <div className="absolute left-[27px] top-6 bottom-6 w-0.5 bg-gray-100 -z-10" />

        {phases.length === 0 ? (
          <div className="p-20 text-center flex flex-col items-center bg-white border border-dashed rounded-3xl">
            <Clock className="h-10 w-10 text-gray-300 mb-4" />
            <p className="text-sm font-bold text-muted-foreground">Nenhuma fase definida para este projecto.</p>
          </div>
        ) : (
          phases.sort((a,b) => a.order - b.order).map((phase, index) => {
            const isCompleted = phase.status === "COMPLETED";
            const isInProgress = phase.status === "IN_PROGRESS";
            const isDelayed = phase.deadline_deviation_days > 0;
            
            return (
              <div key={phase.id} className="relative flex gap-8 py-6 group">
                {/* Node */}
                <div className={cn(
                  "h-14 w-14 rounded-full border-4 shrink-0 flex items-center justify-center transition-all bg-white shadow-sm",
                  isCompleted ? "border-emerald-500" : isInProgress ? "border-primary" : "border-gray-200"
                )}>
                  {isCompleted ? (
                    <CheckCircle2 className="h-6 w-6 text-emerald-500" />
                  ) : (
                    <span className={cn(
                      "text-sm font-black",
                      isInProgress ? "text-primary" : "text-gray-400"
                    )}>
                      {index + 1}
                    </span>
                  )}
                </div>

                {/* Content Card */}
                <div className={cn(
                  "flex-1 bg-white border border-border p-6 rounded-3xl shadow-sm hover:shadow-md transition-all group-hover:border-primary/20",
                  isInProgress && "ring-2 ring-primary/5 border-primary/20"
                )}>
                  <div className="flex flex-wrap justify-between items-start gap-4 mb-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-bold text-foreground">{phase.name}</h3>
                        {isDelayed && (
                          <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-50 text-red-600 border border-red-100">
                            <AlertTriangle className="h-3 w-3" />
                            <span className="text-[10px] font-black uppercase tracking-tighter">Atraso</span>
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground font-medium">{phase.description}</p>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-2xl font-black text-primary">{phase.progress_percent}%</div>
                      <div className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest mt-1">Concluído</div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden mb-6 flex">
                    <div 
                      className={cn(
                        "h-full transition-all duration-1000",
                        isCompleted ? "bg-emerald-500" : "bg-primary"
                      )}
                      style={{ width: `${phase.progress_percent}%` }}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-dashed">
                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Previsão</div>
                      <div className="flex items-center gap-2 text-sm font-bold text-foreground">
                        <Calendar className="h-3.5 w-3.5 text-primary/60" />
                        {formatDate(phase.start_planned)} → {formatDate(phase.end_planned)}
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Execução</div>
                      <div className="flex items-center gap-2 text-sm font-bold text-foreground">
                        <Clock className="h-3.5 w-3.5 text-primary/60" />
                        {phase.start_actual ? formatDate(phase.start_actual) : "Aguardando"} 
                        {phase.end_actual && ` — ${formatDate(phase.end_actual)}`}
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Desvio Financeiro/Tempo</div>
                      <div className={cn(
                        "flex items-center gap-2 text-sm font-black",
                        phase.deadline_deviation_days > 0 ? "text-red-500" : "text-emerald-600"
                      )}>
                        {phase.deadline_deviation_days > 0 ? (
                          <TrendingUp className="h-3.5 w-3.5" />
                        ) : (
                          <TrendingDown className="h-3.5 w-3.5" />
                        )}
                        {Math.abs(phase.deadline_deviation_days)} Dias {phase.deadline_deviation_days > 0 ? "Atraso" : "Antecipação"}
                      </div>
                    </div>
                  </div>

                  {/* Actions for managers */}
                  <div className="mt-8 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                       <span className="text-[11px] font-bold text-muted-foreground bg-slate-50 px-3 py-1 rounded-full border border-border">
                         {phase.completed_task_count} / {phase.task_count} Tarefas
                       </span>
                    </div>
                    
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="gap-2 border-primary/20 text-primary hover:bg-primary/5 font-bold"
                      onClick={() => {
                        setSelectedPhaseId(phase.id);
                        setIsUpdateOpen(true);
                      }}
                    >
                      <Camera className="h-3.5 w-3.5" />
                      Registar Progresso
                    </Button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Update Progress Modal */}
      <Dialog open={isUpdateOpen} onOpenChange={setIsUpdateOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <form onSubmit={handleUpdate} className="space-y-4">
            <DialogHeader>
              <DialogTitle>Registar Evidência de Progresso</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl flex gap-3">
                <Info className="h-5 w-5 text-blue-600 shrink-0" />
                <p className="text-xs text-blue-800 leading-relaxed">
                  Esta actualização será visível para o investidor. O sistema irá calcular o desvio 
                  e registar as fotos no portal da diáspora.
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-bold">Nova Percentagem de Conclusão (%)</label>
                <Input 
                  name="progress_percent" 
                  type="number" 
                  min="0" 
                  max="100" 
                  placeholder="Ex: 45" 
                  required 
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-bold">Notas de Execução</label>
                <textarea 
                  name="notes"
                  className="w-full min-h-[100px] p-3 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  placeholder="Descreva o progresso actual ou motivos de eventuais atrasos..."
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-bold">Foto da Obra (Obrigatório para ROI)</label>
                <Input 
                  name="image" 
                  type="file" 
                  accept="image/*" 
                  required 
                  className="cursor-pointer" 
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" disabled={isUpdating} className="w-full bg-primary hover:bg-primary/90 text-white font-bold">
                {isUpdating ? "A processar..." : "Publicar Actualização"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
