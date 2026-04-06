"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { 
  HardHat, 
  ArrowLeft, 
  BarChart3,
  Calendar,
  Info
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useConstructionProject, useGanttData } from "@/hooks/useConstructionStats";
import { GanttChart } from "@/components/dashboard";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate } from "@/lib/format";

export default function GanttPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  const { data: project, isLoading: projectLoading } = useConstructionProject(projectId);
  const { data: ganttItems, isLoading: ganttLoading } = useGanttData(projectId);

  if (projectLoading) {
    return <GanttSkeleton />;
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Info className="h-12 w-12 text-red-500 mb-4" />
        <h2 className="text-lg font-semibold">Obra não encontrada</h2>
        <Link href="/construction" className="text-primary hover:underline mt-2">
          Voltar às obras
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/construction" className="hover:text-foreground transition-colors">
          Obras
        </Link>
        <span>/</span>
        <Link href={`/construction/${projectId}`} className="hover:text-foreground transition-colors">
          {project.name}
        </Link>
        <span>/</span>
        <span className="text-foreground">Gantt</span>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <Link
            href={`/construction/${projectId}`}
            className="p-2 rounded-xl border border-border hover:bg-slate-50 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-muted-foreground" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center">
                <BarChart3 className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Cronograma Gantt</h1>
                <p className="text-sm text-muted-foreground">{project.name}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Timeline Info */}
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-border">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Início:</span>
            <span className="font-medium">{formatDate(project.start_date)}</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-border">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Fim previsto:</span>
            <span className="font-medium">{formatDate(project.expected_end_date)}</span>
          </div>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <p className="text-xs text-muted-foreground mb-1">Progresso Geral</p>
          <div className="flex items-center gap-3">
            <p className="text-2xl font-bold">{Math.round(project.overall_progress_pct)}%</p>
            <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  project.overall_progress_pct >= 100 ? "bg-emerald-500" : 
                  project.overall_progress_pct >= 50 ? "bg-blue-500" : "bg-amber-500"
                )}
                style={{ width: `${project.overall_progress_pct}%` }}
              />
            </div>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <p className="text-xs text-muted-foreground mb-1">Fases</p>
          <p className="text-2xl font-bold">{project.phases_count}</p>
        </div>
        
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <p className="text-xs text-muted-foreground mb-1">Tarefas</p>
          <p className="text-2xl font-bold">{project.tasks_count}</p>
        </div>
      </div>

      {/* Gantt Chart */}
      <GanttChart 
        items={ganttItems ?? []} 
        isLoading={ganttLoading}
        startDate={project.start_date || undefined}
        endDate={project.expected_end_date || undefined}
      />

      {/* Legend & Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <h3 className="text-sm font-semibold mb-3">Como ler o Gantt</h3>
          <ul className="space-y-2 text-xs text-muted-foreground">
            <li className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-blue-500" />
              <span>Barras azuis representam fases principais da obra</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-slate-400" />
              <span>Barras cinzentas representam tarefas individuais</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="w-12 h-2 bg-blue-500 rounded relative overflow-hidden">
                <span className="absolute right-0 top-0 bottom-0 w-1/3 bg-white/30" />
              </span>
              <span>A parte branca indica o progresso ainda não realizado</span>
            </li>
          </ul>
        </div>
        
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <h3 className="text-sm font-semibold mb-3">Status das Atividades</h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-slate-400" />
              <span className="text-muted-foreground">Não iniciado</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              <span className="text-muted-foreground">Em progresso</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="text-muted-foreground">Concluído</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-muted-foreground">Atrasado</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function GanttSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10 rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-20 rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-96 rounded-2xl" />
    </div>
  );
}
