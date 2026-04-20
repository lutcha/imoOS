/**
 * useProjects — ImoOS
 * Skill: react-query-tenant
 *
 * NOTE: ProjectSerializer uses GeoFeatureModelSerializer.
 * Each API result item is a GeoJSON Feature — project data lives in `.properties`.
 * API path: api/v1/projects/projects/ (router prefix + resource)
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type ProjectStatus =
  | "PLANNING"
  | "LICENSING"
  | "CONSTRUCTION"
  | "COMPLETED";

export interface ProjectProperties {
  id: string;
  name: string;
  slug: string;
  status: ProjectStatus;
  description: string;
  address: string;
  city: string;
  island?: string;
  total_area?: number | null;
  total_units?: number | null;
  start_date?: string | null;
  expected_delivery_date?: string | null;
  created_at: string;
  updated_at: string;
}

export interface GeoFeatureProject {
  type: "Feature";
  id: string;
  geometry: { type: string; coordinates: number[] } | null;
  properties: ProjectProperties;
}

/** Normalised view — use this in components */
export type Project = ProjectProperties & {
  coordinates: [number, number] | null;
};

/** Raw shape from DRF + GeoFeatureModelSerializer */
interface ProjectsPageRaw {
  count: number;
  next: string | null;
  previous: string | null;
  results: GeoFeatureProject[] | { type: "FeatureCollection"; features: GeoFeatureProject[] };
}

export interface ProjectsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: GeoFeatureProject[];
}

export interface ProjectFilters {
  status?: ProjectStatus;
  search?: string;
  city?: string;
  page?: number;
  page_size?: number;
}

/** Convert GeoJSON Feature → flat Project object */
export function featureToProject(f: GeoFeatureProject): Project {
  const coords =
    f.geometry?.type === "Point"
      ? (f.geometry.coordinates as [number, number])
      : null;
  return { ...f.properties, id: f.id ?? f.properties.id, coordinates: coords };
}

// ----- Query keys -----

export const projectKeys = {
  all: (schema: string) => ["projects", schema] as const,
  list: (schema: string, filters: ProjectFilters) =>
    ["projects", schema, "list", filters] as const,
  detail: (schema: string, id: string) =>
    ["projects", schema, "detail", id] as const,
};

// ----- Hooks -----

export function useProjects(filters: ProjectFilters = {}) {
  const { schema } = useTenant();

  return useQuery<ProjectsPage>({
    queryKey: projectKeys.list(schema, filters),
    queryFn: () =>
      apiClient
        .get<ProjectsPageRaw>("/projects/projects/", { params: filters })
        .then((r) => {
          const raw = r.data;
          const features = Array.isArray(raw.results)
            ? raw.results
            : raw.results.features ?? [];
          return { ...raw, results: features };
        }),
    staleTime: 60_000,
    enabled: !!schema,
  });
}

export function useProject(id: string) {
  const { schema } = useTenant();

  return useQuery<GeoFeatureProject>({
    queryKey: projectKeys.detail(schema, id),
    queryFn: () =>
      apiClient
        .get<GeoFeatureProject>(`/projects/projects/${id}/`)
        .then((r) => r.data),
    enabled: !!schema && !!id,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (data: Partial<ProjectProperties>) =>
      apiClient.post<GeoFeatureProject>("/projects/projects/", data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: projectKeys.all(schema) });
    },
  });
}
