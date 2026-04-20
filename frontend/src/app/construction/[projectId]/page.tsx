"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { 
  HardHat, 
  ArrowLeft, 
  Calendar, 
  User, 
  TrendingUp,
  ClipboardList,
  AlertCircle,
  CheckCircle2,
  Clock,
  MoreHorizontal,
  Edit,
  FileText,
  BarChart3,
  Users
} from "lucide-react";
import { cn } from "@/lib/utils";
import { 
  useConstructionProject, 
  useConstructionPhases, 
  useConstructionTasks,
  getStatusColor,
  getStatusLabel,
  type ConstructionPhase,
  type ConstructionTask
} from "@/hooks/useConstructionStats";
import { useBudgets, useBudgetStats } from "@/hooks/useBudgetStats";
import { Skeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/button";
import { formatDate, formatCveCompact } from "@/lib/format";

const TABS = [
  { id: "overview", label: "Visão Geral", icon: FileText },
  { id: "logs", label: "Diário", icon: ClipboardList },
  { id: "gantt", label: "Gantt", icon: BarChart3 },
  { id: "finance", label: "Financeiro", icon: TrendingUp },
  { id: "budget", label: "Orçamento", icon: ClipboardList },
  { id: "team", label: "Equipa", icon: Users },
];

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [activeTab, setActiveTab] = useState("overview");

  const { data: project, isLoading: projectLoading } = useConstructionProject(projectId);
  const { data: phasesPage, isLoading: phasesLoading } = useConstructionPhases(projectId);
  const { data: tasksPage, isLoading: tasksLoading } = useConstructionTasks(projectId);
  const { data: budgetsPage } = useBudgets({ project: projectId });
  const { data: budgetStats } = useBudgetStats(projectId);

  const phases = phasesPage?.results ?? [];
  const tasks = tasksPage?.results ?? [];
  const budgets = budgetsPage?.results ?? [];

  if (projectLoading) {
    return <ProjectDetailSkeleton />;
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <h2 className="text-lg font-semibold">Obra não encontrada</h2>
        <Link href="/construction" className="text-primary hover:underline mt-2">
          Voltar às obras
        </Link>
      </div>
    );
  }

  const statusColors = getStatusColor(project.status);
  const progress = Math.round(project.overall_progress_pct);
  const budgeted = parseFloat(project.budget_cve || "0");
  const actual = parseFloat(project.actual_cost_cve || "0");
  const variance = budgeted > 0 ? ((actual - budgeted) / budgeted) * 100 : 0;
  const isOverBudget = variance > 10;

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/construction" className="hover:text-foreground transition-colors">
          Obras
        </Link>
        <span>/</span>
        <span className="text-foreground">{project.name}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <Link
            href="/construction"
            className="p-2 rounded-xl border border-border hover:bg-slate-50 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-muted-foreground" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight text-foreground">{project.name}</h1>
              <span className={cn(
                "text-[11px] font-medium px-2.5 py-0.5 rounded-full border",
                statusColors.bg,
                statusColors.text,
                statusColors.border
              )}>
                {getStatusLabel(project.status)}
              </span>
            </div>
            <p className="text-sm text-muted-foreground mt-1">{project.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <Edit className="h-4 w-4" />
            Editar
          </Button>
          <Button size="sm" className="gap-2">
            <ClipboardList className="h-4 w-4" />
            Nova Tarefa
          </Button>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Progress Card */}
        <div className="rounded-2xl border border-border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Progresso Geral</p>
              <p className="text-xl font-bold">{progress}%</p>
            </div>
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all",
                progress >= 100 ? "bg-emerald-500" : 
                progress >= 50 ? "bg-blue-500" : "bg-amber-500"
              )}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Tasks Card */}
        <div className="rounded-2xl border border-border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-purple-50 flex items-center justify-center">
              <ClipboardList className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Tarefas</p>
              <p className="text-xl font-bold">{project.completed_tasks_count}/{project.tasks_count}</p>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {project.tasks_count > 0 
              ? Math.round((project.completed_tasks_count / project.tasks_count) * 100) 
              : 0}% concluídas
          </p>
        </div>

        {/* Timeline Card */}
        <div className="rounded-2xl border border-border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-amber-50 flex items-center justify-center">
              <Calendar className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Previsão de Conclusão</p>
              <p className="text-xl font-bold">{formatDate(project.expected_end_date)}</p>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Início: {formatDate(project.start_date)}
          </p>
        </div>

        {/* Budget Card */}
        <div className="rounded-2xl border border-border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-emerald-50 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Orçamento</p>
              <p className={cn("text-xl font-bold", isOverBudget && "text-red-600")}>
                {formatCveCompact(actual)}
              </p>
            </div>
          </div>
          <p className={cn("text-xs mt-2", isOverBudget ? "text-red-600" : "text-muted-foreground")}>
            Orçado: {formatCveCompact(budgeted)}
            {isOverBudget && ` (+${variance.toFixed(0)}%)`}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border">
        <div className="flex gap-1">
          {TABS.map((tab) => (
            <Link
              key={tab.id}
              href={tab.id === "overview" ? `/construction/${projectId}` : `/construction/${projectId}/${tab.id}`}
              className={cn(
                "flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors",
                activeTab === tab.id || (tab.id !== "overview" && activeTab === tab.id)
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
              )}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </Link>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Phases Section */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Fases da Obra</h2>
          <div className="space-y-3">
            {phasesLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-20 w-full rounded-xl" />
              ))
            ) : phases.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>Nenhuma fase definida</p>
              </div>
            ) : (
              phases.map((phase) => (
                <PhaseCard key={phase.id} phase={phase} tasks={tasks.filter(t => t.phase === phase.id)} />
              ))
            )}
          </div>
        </div>

        {/* Tasks Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Tarefas Recentes</h2>
            <Link
              href={`/construction/${projectId}/tasks`}
              className="text-sm text-primary hover:underline"
            >
              Ver todas
            </Link>
          </div>
          <div className="space-y-2">
            {tasksLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-xl" />
              ))
            ) : tasks.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>Nenhuma tarefa definida</p>
              </div>
            ) : (
              tasks.slice(0, 5).map((task) => (
                <TaskRow key={task.id} task={task} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function PhaseCard({ phase, tasks }: { phase: ConstructionPhase; tasks: ConstructionTask[] }) {
  const statusColors = getStatusColor(phase.status);
  const completedTasks = tasks.filter(t => t.status === "DONE").length;

  return (
    <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={cn("h-8 w-8 rounded-lg flex items-center justify-center", statusColors.bg)}>
            <HardHat className={cn("h-4 w-4", statusColors.text)} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-foreground">{phase.name}</h3>
              <span className={cn(
                "text-[10px] px-1.5 py-0.5 rounded-full border",
                statusColors.bg,
                statusColors.text,
                statusColors.border
              )}>
                {getStatusLabel(phase.status)}
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">{phase.description}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium">{Math.round(phase.progress_pct)}%</p>
          <p className="text-[10px] text-muted-foreground">
            {formatDate(phase.start_date)} - {formatDate(phase.end_date)}
          </p>
        </div>
      </div>
      
      {/* Phase Progress */}
      <div className="mt-3">
        <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all",
              phase.progress_pct >= 100 ? "bg-emerald-500" : "bg-blue-500"
            )}
            style={{ width: `${phase.progress_pct}%` }}
          />
        </div>
        {tasks.length > 0 && (
          <p className="text-[10px] text-muted-foreground mt-1.5">
            {completedTasks} de {tasks.length} tarefas concluídas
          </p>
        )}
      </div>
    </div>
  );
}

function TaskRow({ task }: { task: ConstructionTask }) {
  const statusColors = getStatusColor(task.status);
  const priorityColors = {
    LOW: "bg-slate-100 text-slate-600",
    MEDIUM: "bg-blue-50 text-blue-600",
    HIGH: "bg-amber-50 text-amber-600",
    CRITICAL: "bg-red-50 text-red-600",
  };

  return (
    <div className="flex items-center justify-between p-3 rounded-xl border border-border bg-white hover:bg-slate-50/50 transition-colors">
      <div className="flex items-center gap-3">
        <div className={cn("h-2 w-2 rounded-full", statusColors.bg.replace("bg-", "bg-").replace("-50", "-500"))} />
        <div>
          <p className="text-sm font-medium text-foreground">{task.name}</p>
          <div className="flex items-center gap-2 mt-0.5">
            <span className={cn("text-[10px] px-1.5 py-0.5 rounded", priorityColors[task.priority])}>
              {task.priority === "LOW" ? "Baixa" :
               task.priority === "MEDIUM" ? "Média" :
               task.priority === "HIGH" ? "Alta" : "Crítica"}
            </span>
            <span className="text-[10px] text-muted-foreground">
              {formatDate(task.due_date)}
            </span>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {task.assigned_to_name && (
          <span className="text-xs text-muted-foreground flex items-center gap-1">
            <User className="h-3 w-3" />
            {task.assigned_to_name}
          </span>
        )}
        <span className={cn(
          "text-[10px] px-2 py-0.5 rounded-full border",
          statusColors.bg,
          statusColors.text,
          statusColors.border
        )}>
          {getStatusLabel(task.status)}
        </span>
      </div>
    </div>
  );
}

function ProjectDetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10 rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-2xl" />
        ))}
      </div>
      <Skeleton className="h-12 w-full rounded-xl" />
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-xl" />
        ))}
      </div>
    </div>
  );
}
