/**
 * useConstruction — ImoOS
 * API: /construction/daily-reports/
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type ReportStatus = "DRAFT" | "SUBMITTED" | "APPROVED" | "REJECTED";
export type WeatherCondition = "SUNNY" | "CLOUDY" | "RAINY" | "STORMY" | "WINDY";

export interface DailyReport {
  id: string;
  project: string;
  project_name: string;
  building: string | null;
  building_name: string | null;
  date: string;
  status: ReportStatus;
  summary: string;
  progress_pct: number;
  weather: WeatherCondition | null;
  workers_count: number | null;
  photos_count: number;
  author: string | null;
  author_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface DailyReportFilters {
  project?: string;
  building?: string;
  status?: ReportStatus;
  date_from?: string;
  date_to?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface DailyReportsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: DailyReport[];
}

export interface CreateDailyReportPayload {
  project: string;
  building?: string | null;
  date: string;
  summary: string;
  progress_pct: number;
  weather?: WeatherCondition | null;
  workers_count?: number | null;
}

// ----- Query keys -----

export const constructionKeys = {
  all: (schema: string) => ["construction", schema] as const,
  list: (schema: string, filters: DailyReportFilters) =>
    ["construction", schema, "list", filters] as const,
  detail: (schema: string, id: string) =>
    ["construction", schema, "detail", id] as const,
};

// ----- Hooks -----

export function useDailyReports(filters: DailyReportFilters = {}) {
  const { schema } = useTenant();

  return useQuery<DailyReportsPage>({
    queryKey: constructionKeys.list(schema, filters),
    queryFn: () =>
      apiClient
        .get<DailyReportsPage>("/construction/daily-reports/", { params: filters })
        .then((r) => r.data),
    staleTime: 30_000,
    enabled: !!schema,
  });
}

export function useDailyReport(id: string) {
  const { schema } = useTenant();

  return useQuery<DailyReport>({
    queryKey: constructionKeys.detail(schema, id),
    queryFn: () =>
      apiClient
        .get<DailyReport>(`/construction/daily-reports/${id}/`)
        .then((r) => r.data),
    enabled: !!schema && !!id,
  });
}

export function useCreateDailyReport() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (payload: CreateDailyReportPayload) =>
      apiClient
        .post<DailyReport>("/construction/daily-reports/", payload)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: constructionKeys.all(schema) });
    },
  });
}

export function useSubmitReport() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (id: string) =>
      apiClient
        .post<DailyReport>(`/construction/daily-reports/${id}/submit/`)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: constructionKeys.all(schema) });
    },
  });
}
