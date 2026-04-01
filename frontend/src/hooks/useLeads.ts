/**
 * useLeads — ImoOS
 * Skill: react-query-tenant
 * API path: api/v1/crm/leads/
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type LeadStatus =
  | "NEW"
  | "CONTACTED"
  | "VISIT_SCHEDULED"
  | "PROPOSAL_SENT"
  | "NEGOTIATION"
  | "WON"
  | "LOST";

export type LeadSource =
  | "WEB"
  | "INSTAGRAM"
  | "FACEBOOK"
  | "REFERRAL"
  | "OTHER";

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  status: LeadStatus;
  source: LeadSource;
  budget: string | null;
  preferred_typology: string;
  notes: string;
  assigned_to: string | null;
  assigned_to_name: string | null;
  interested_unit: string | null;
  unit_number: string | null;
  project_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeadsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: Lead[];
}

export interface LeadFilters {
  status?: LeadStatus;
  source?: LeadSource;
  assigned_to?: string;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface PipelineColumn {
  label: string;
  count: number;
  leads: Lead[];
}

export type LeadPipeline = Record<LeadStatus, PipelineColumn>;

export const initialLeadPipeline: LeadPipeline = {
  NEW: { label: "Novo", count: 0, leads: [] },
  CONTACTED: { label: "Contactado", count: 0, leads: [] },
  VISIT_SCHEDULED: { label: "Visita Agendada", count: 0, leads: [] },
  PROPOSAL_SENT: { label: "Proposta Enviada", count: 0, leads: [] },
  NEGOTIATION: { label: "Em Negociação", count: 0, leads: [] },
  WON: { label: "Ganho", count: 0, leads: [] },
  LOST: { label: "Perdido", count: 0, leads: [] },
};

/** Helper to group leads by stage for Kanban */
function groupByStage(leads: Lead[]): LeadPipeline {
  const pipeline = { ...initialLeadPipeline };

  // Reset leads arrays to be sure we don't share references if this is called multiple times
  Object.keys(pipeline).forEach(key => {
    pipeline[key as LeadStatus] = { ...pipeline[key as LeadStatus], leads: [], count: 0 };
  });

  if (!leads) return pipeline;

  return leads.reduce((acc, lead) => {
    const stage = lead.status;
    if (acc[stage]) {
      acc[stage].leads.push(lead);
      acc[stage].count++;
    }
    return acc;
  }, pipeline);
}

// ----- Query keys -----

export const leadKeys = {
  all: (schema: string) => ["leads", schema] as const,
  list: (schema: string, filters: LeadFilters) =>
    ["leads", schema, "list", filters] as const,
  detail: (schema: string, id: string) =>
    ["leads", schema, "detail", id] as const,
  pipeline: (schema: string) => ["leads", schema, "pipeline"] as const,
};

// ----- Hooks -----

export function useLeads(filters: LeadFilters = {}) {
  const { schema } = useTenant();

  return useQuery<LeadsPage>({
    queryKey: leadKeys.list(schema, filters),
    queryFn: () =>
      apiClient
        .get<LeadsPage>("/crm/leads/", { params: filters })
        .then((r) => r.data),
    staleTime: 15_000, // leads are more time-sensitive — 15s
    enabled: !!schema,
  });
}

export function useLeadPipeline() {
  const { schema } = useTenant();

  return useQuery<LeadPipeline>({
    queryKey: leadKeys.pipeline(schema),
    queryFn: () =>
      apiClient.get<LeadPipeline>("/crm/leads/pipeline/").then((r) => r.data),
    staleTime: 30_000,
    enabled: !!schema,
  });
}

/** Grouped by stage — useful for the Kanban */
export function useLeadsByStage() {
  const { schema } = useTenant();
  return useQuery({
    queryKey: ["leads", schema, "by-stage"],
    queryFn: () =>
      apiClient
        .get<LeadsPage>("/crm/leads/", { params: { page_size: 200 } })
        .then((r) => r.data),
    select: (data) => groupByStage(data.results),
    staleTime: 15_000,
    enabled: !!schema,
    placeholderData: { results: [] } as any, // This ensures it works with select
  });
}

/** Mutation: move stage */
export function useMoveLeadStage() {
  const qc = useQueryClient();
  const { schema } = useTenant();
  return useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: LeadStatus }) =>
      apiClient
        .patch(`/crm/leads/${id}/move-stage/`, { status: stage })
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["leads", schema] });
    },
  });
}
