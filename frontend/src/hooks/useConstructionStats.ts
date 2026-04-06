/**
 * useConstructionStats — ImoOS
 * API: /construction/* — estatísticas de obras e projetos de construção
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type PhaseStatus = "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED" | "DELAYED";
export type TaskStatus = "TODO" | "IN_PROGRESS" | "DONE" | "BLOCKED";
export type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface ConstructionProject {
  id: string;
  name: string;
  description: string;
  start_date: string | null;
  expected_end_date: string | null;
  actual_end_date: string | null;
  overall_progress_pct: number;
  status: "PLANNING" | "ACTIVE" | "ON_HOLD" | "COMPLETED" | "CANCELLED";
  budget_cve: string | null;
  actual_cost_cve: string | null;
  manager_name: string | null;
  phases_count: number;
  tasks_count: number;
  completed_tasks_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConstructionPhase {
  id: string;
  project: string;
  name: string;
  description: string;
  order: number;
  start_date: string | null;
  end_date: string | null;
  progress_pct: number;
  status: PhaseStatus;
  dependencies: string[];
  created_at: string;
  updated_at: string;
}

export interface ConstructionTask {
  id: string;
  project: string;
  phase: string | null;
  name: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  start_date: string | null;
  due_date: string | null;
  completed_date: string | null;
  assigned_to: string | null;
  assigned_to_name: string | null;
  progress_pct: number;
  created_at: string;
  updated_at: string;
}

export interface GanttItem {
  id: string;
  name: string;
  type: "phase" | "task";
  start_date: string;
  end_date: string;
  progress_pct: number;
  dependencies: string[];
  status: PhaseStatus | TaskStatus;
}

export interface ConstructionStats {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  delayed_projects: number;
  total_tasks: number;
  pending_tasks: number;
  completed_tasks: number;
  blocked_tasks: number;
  average_progress: number;
  total_budget_cve: string;
  total_actual_cost_cve: string;
  budget_variance_pct: number;
}

export interface ProjectsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: ConstructionProject[];
}

export interface PhasesPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: ConstructionPhase[];
}

export interface TasksPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: ConstructionTask[];
}

export interface ProjectFilters {
  status?: string;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

// ----- Query keys -----

export const constructionStatsKeys = {
  all: (schema: string) => ["construction-stats", schema] as const,
  list: (schema: string, filters: ProjectFilters) =>
    ["construction-stats", schema, "list", filters] as const,
  detail: (schema: string, id: string) =>
    ["construction-stats", schema, "detail", id] as const,
  phases: (schema: string, projectId: string) =>
    ["construction-stats", schema, "phases", projectId] as const,
  tasks: (schema: string, projectId: string) =>
    ["construction-stats", schema, "tasks", projectId] as const,
  gantt: (schema: string, projectId: string) =>
    ["construction-stats", schema, "gantt", projectId] as const,
  stats: (schema: string) =>
    ["construction-stats", schema, "aggregated"] as const,
};

// ----- Hooks -----

export function useConstructionProjects(filters: ProjectFilters = {}) {
  const { schema } = useTenant();

  return useQuery<ProjectsPage>({
    queryKey: constructionStatsKeys.list(schema, filters),
    queryFn: () =>
      apiClient
        .get<ProjectsPage>("/construction/projects/", { params: filters })
        .then((r) => r.data),
    staleTime: 60_000,
    enabled: !!schema,
  });
}

export function useConstructionProject(id: string) {
  const { schema } = useTenant();

  return useQuery<ConstructionProject>({
    queryKey: constructionStatsKeys.detail(schema, id),
    queryFn: () =>
      apiClient
        .get<ConstructionProject>(`/construction/projects/${id}/`)
        .then((r) => r.data),
    enabled: !!schema && !!id,
  });
}

export function useConstructionPhases(projectId: string) {
  const { schema } = useTenant();

  return useQuery<PhasesPage>({
    queryKey: constructionStatsKeys.phases(schema, projectId),
    queryFn: () =>
      apiClient
        .get<PhasesPage>("/construction/phases/", { params: { project: projectId } })
        .then((r) => r.data),
    enabled: !!schema && !!projectId,
  });
}

export function useConstructionTasks(projectId: string, phaseId?: string) {
  const { schema } = useTenant();

  return useQuery<TasksPage>({
    queryKey: constructionStatsKeys.tasks(schema, projectId),
    queryFn: () =>
      apiClient
        .get<TasksPage>("/construction/tasks/", { 
          params: { project: projectId, phase: phaseId || undefined } 
        })
        .then((r) => r.data),
    enabled: !!schema && !!projectId,
  });
}

export function useGanttData(projectId: string) {
  const { schema } = useTenant();

  return useQuery<GanttItem[]>({
    queryKey: constructionStatsKeys.gantt(schema, projectId),
    queryFn: () =>
      apiClient
        .get<{ results: GanttItem[] }>("/construction/gantt/", { params: { project: projectId } })
        .then((r) => r.data.results),
    enabled: !!schema && !!projectId,
  });
}

export function useConstructionAggregatedStats() {
  const { schema } = useTenant();

  return useQuery<ConstructionStats>({
    queryKey: constructionStatsKeys.stats(schema),
    queryFn: () =>
      apiClient
        .get<ConstructionStats>("/construction/stats/")
        .then((r) => r.data),
    staleTime: 60_000,
    enabled: !!schema,
  });
}

// ----- Mutations -----

export function useUpdateTaskStatus() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: TaskStatus }) =>
      apiClient
        .patch<ConstructionTask>(`/construction/tasks/${id}/`, { status })
        .then((r) => r.data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: constructionStatsKeys.all(schema) });
    },
  });
}

// ----- Helpers -----

export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    // Project status
    PLANNING: "Planeamento",
    ACTIVE: "Em Construção",
    ON_HOLD: "Em Pausa",
    COMPLETED: "Concluído",
    CANCELLED: "Cancelado",
    // Phase status
    NOT_STARTED: "Não Iniciado",
    IN_PROGRESS: "Em Progresso",
    DELAYED: "Atrasado",
    // Task status
    TODO: "Por Fazer",
    DONE: "Concluído",
    BLOCKED: "Bloqueado",
    // Priority
    LOW: "Baixa",
    MEDIUM: "Média",
    HIGH: "Alta",
    CRITICAL: "Crítica",
  };
  return labels[status] || status;
}

// ----- Daily Reports -----

export interface DailyReport {
  id: string;
  project: string;
  date: string;
  progress_pct: number;
  summary: string;
  status: "DRAFT" | "SUBMITTED" | "APPROVED" | "REJECTED";
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface DailyReportFilters {
  project?: string;
  date?: string;
  status?: string;
  page?: number;
  page_size?: number;
}

export interface DailyReportsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: DailyReport[];
}

export function useDailyReports(filters: DailyReportFilters = {}) {
  const { schema } = useTenant();

  return useQuery<DailyReportsPage>({
    queryKey: ["daily-reports", schema, filters],
    queryFn: () =>
      apiClient
        .get<DailyReportsPage>("/construction/daily-reports/", { params: filters })
        .then((r) => r.data),
    enabled: !!schema,
  });
}

// ----- Helpers -----

export function getStatusColor(status: string): { bg: string; text: string; border: string } {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    // Project status
    PLANNING: { bg: "bg-slate-50", text: "text-slate-600", border: "border-slate-200" },
    ACTIVE: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200" },
    ON_HOLD: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200" },
    COMPLETED: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200" },
    CANCELLED: { bg: "bg-red-50", text: "text-red-600", border: "border-red-200" },
    // Phase/Task status
    NOT_STARTED: { bg: "bg-slate-50", text: "text-slate-500", border: "border-slate-200" },
    IN_PROGRESS: { bg: "bg-blue-50", text: "text-blue-600", border: "border-blue-200" },
    DELAYED: { bg: "bg-red-50", text: "text-red-600", border: "border-red-200" },
    TODO: { bg: "bg-slate-50", text: "text-slate-600", border: "border-slate-200" },
    DONE: { bg: "bg-emerald-50", text: "text-emerald-600", border: "border-emerald-200" },
    BLOCKED: { bg: "bg-red-50", text: "text-red-600", border: "border-red-200" },
  };
  return colors[status] || { bg: "bg-gray-50", text: "text-gray-600", border: "border-gray-200" };
}
