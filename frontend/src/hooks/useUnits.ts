/**
 * useUnits — ImoOS
 * Skill: react-query-tenant
 * API path: api/v1/inventory/units/
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type UnitStatus =
  | "AVAILABLE"
  | "RESERVED"
  | "CONTRACT"
  | "SOLD"
  | "MAINTENANCE";

export interface UnitType {
  id: string;
  name: string;
  code: string;
  bedrooms: number;
  bathrooms: number;
}

export interface UnitPricing {
  id: string;
  price_cve: string;
  price_eur: string | null;
  price_per_sqm: string | null;
  discount_type: "NONE" | "PERCENT" | "FIXED";
  discount_value: string;
  final_price_cve: string;
  updated_at: string;
}

export interface Unit {
  id: string;
  floor: string;
  unit_type: string;
  unit_type_detail: UnitType;
  code: string;
  description: string;
  status: UnitStatus;
  status_display: string;
  area_bruta: string;
  area_util: string | null;
  orientation: string;
  floor_number: number;
  bim_guid: string;
  pricing: UnitPricing | null;
  created_at: string;
  updated_at: string;
}

export interface UnitsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: Unit[];
}

export interface UnitFilters {
  status?: UnitStatus;
  floor?: string;
  search?: string;
  project?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
  price_cve__gte?: number;
  price_cve__lte?: number;
  area_bruta__gte?: number;
  area_bruta__lte?: number;
}

export type OccurrenceStatus = "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CANCELLED";
export type OccurrencePriority = "LOW" | "NORMAL" | "HIGH" | "URGENT";

export interface UnitOccurrence {
  id: string;
  unit: string;
  unit_code: string;
  reported_by_name: string;
  assigned_to: string | null;
  assigned_to_name: string | null;
  occurrence_type: "TECHNICAL" | "MAINTENANCE" | "STRUCTURAL" | "OTHER";
  description: string;
  priority: OccurrencePriority;
  status: OccurrenceStatus;
  status_display: string;
  created_at: string;
  resolved_at: string | null;
}

export interface UnitOccurrencesPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: UnitOccurrence[];
}

// ----- Query keys -----

export const unitKeys = {
  all: (schema: string) => ["units", schema] as const,
  list: (schema: string, filters: UnitFilters) =>
    ["units", schema, "list", filters] as const,
  detail: (schema: string, id: string) =>
    ["units", schema, "detail", id] as const,
  occurrences: (schema: string, unitId?: string) =>
    ["units", schema, "occurrences", unitId || "all"] as const,
};

// ----- Hooks -----

export function useUnits(filters: UnitFilters = {}) {
  const { schema } = useTenant();

  return useQuery<UnitsPage>({
    queryKey: unitKeys.list(schema, filters),
    queryFn: () =>
      apiClient
        .get<UnitsPage>("/inventory/units/", { params: filters })
        .then((r) => r.data),
    staleTime: 30_000,
    enabled: !!schema,
  });
}

export function useUnit(id: string) {
  const { schema } = useTenant();

  return useQuery<Unit>({
    queryKey: unitKeys.detail(schema, id),
    queryFn: () =>
      apiClient.get<Unit>(`/inventory/units/${id}/`).then((r) => r.data),
    enabled: !!schema && !!id,
  });
}

export function useUpdateUnitStatus() {
  const queryClient = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: UnitStatus }) =>
      apiClient
        .patch<Unit>(`/inventory/units/${id}/update_status/`, { status })
        .then((r) => r.data),

    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: unitKeys.all(schema) });
      const prev = queryClient.getQueryData(unitKeys.detail(schema, id));
      queryClient.setQueryData(
        unitKeys.detail(schema, id),
        (old: Unit | undefined) => (old ? { ...old, status } : old)
      );
      return { prev };
    },
    onError: (_err, vars, ctx) => {
      queryClient.setQueryData(unitKeys.detail(schema, vars.id), ctx?.prev);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: unitKeys.all(schema) });
    },
  });
}

export function useCreateUnit() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (data: Partial<Unit>) =>
      apiClient.post<Unit>("/inventory/units/", data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: unitKeys.all(schema) });
    },
  });
}

export function useUnitTypes() {
  const { schema } = useTenant();

  return useQuery<UnitType[]>({
    queryKey: ["unit-types", schema],
    queryFn: () =>
      apiClient
        .get<{ results: UnitType[] }>("/inventory/unit-types/")
        .then((r) => r.data.results),
    enabled: !!schema,
  });
}

export function useUnitOccurrences(unitId?: string) {
  const { schema } = useTenant();

  return useQuery<UnitOccurrencesPage>({
    queryKey: unitKeys.occurrences(schema, unitId),
    queryFn: () =>
      apiClient
        .get<UnitOccurrencesPage>("/inventory/unit-occurrences/", {
          params: unitId ? { unit: unitId } : {},
        })
        .then((r) => r.data),
    enabled: !!schema,
  });
}

export function useResolveOccurrence() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (id: string) =>
      apiClient
        .post<UnitOccurrence>(`/inventory/unit-occurrences/${id}/resolve/`)
        .then((r) => r.data),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: unitKeys.occurrences(schema) });
      qc.invalidateQueries({ queryKey: unitKeys.occurrences(schema, data.unit) });
    },
  });
}
