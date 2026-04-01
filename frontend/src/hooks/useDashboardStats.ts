/**
 * useDashboardStats — ImoOS Sprint 5
 * Single aggregated endpoint covering inventory, revenue, pipeline, and contracts.
 * Query key includes schema for tenant isolation.
 */
import { useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

export interface DashboardStats {
  inventory: {
    total: number;
    available: number;
    reserved: number;
    contract: number;
    sold: number;
  };
  revenue_cve: string;
  /** Counts keyed by Lead.stage (new, contacted, visit_scheduled, proposal_sent, negotiation, won, lost) */
  pipeline: Record<string, number>;
  reservations_expiring_soon: number;
  /** Counts keyed by Contract.status (DRAFT, ACTIVE, COMPLETED, CANCELLED) */
  contracts: Record<string, number>;
}

export const PIPELINE_TERMINAL_STAGES = new Set(["won", "lost"]);

/** Sum of all non-terminal pipeline stages */
export function activeLeadsCount(pipeline: Record<string, number>): number {
  return Object.entries(pipeline)
    .filter(([stage]) => !PIPELINE_TERMINAL_STAGES.has(stage))
    .reduce((sum, [, count]) => sum + count, 0);
}

export const dashboardKeys = {
  stats: (schema: string) => ["dashboard", "stats", schema] as const,
};

export function useDashboardStats() {
  const { schema } = useTenant();

  return useQuery<DashboardStats>({
    queryKey: dashboardKeys.stats(schema),
    queryFn: () => apiClient.get("/dashboard/stats/").then((r) => r.data),
    staleTime: 60_000,       // 1 minute
    refetchInterval: 300_000, // auto-refresh every 5 minutes
    enabled: !!schema,
  });
}
