/**
 * useTenantStats — ImoOS
 * Aggregates dashboard KPI stats from unit counts + project count + pending leads.
 * Uses page_size=1 requests to get counts cheaply without loading data.
 * Skill: react-query-tenant
 */
import { useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

export interface TenantStats {
  totalProjects: number;
  totalUnits: number;
  availableUnits: number;
  soldUnits: number;
  reservedUnits: number;
  pendingLeads: number;
  /** Gross revenue estimate: sold units with pricing (CVE) */
  soldRevenueCve: number;
}

interface CountResponse {
  count: number;
}

async function fetchCount(path: string, params?: Record<string, string | number>): Promise<number> {
  const { data } = await apiClient.get<CountResponse>(path, {
    params: { page_size: 1, ...params },
  });
  return data.count;
}

export const statKeys = {
  dashboard: (schema: string) => ["stats", schema, "dashboard"] as const,
};

export function useTenantStats() {
  const { schema } = useTenant();

  return useQuery<TenantStats>({
    queryKey: statKeys.dashboard(schema),
    queryFn: async () => {
      const [
        totalProjects,
        totalUnits,
        availableUnits,
        soldUnits,
        reservedUnits,
        pendingLeads,
      ] = await Promise.all([
        fetchCount("/projects/projects/"),
        fetchCount("/inventory/units/"),
        fetchCount("/inventory/units/", { status: "AVAILABLE" }),
        fetchCount("/inventory/units/", { status: "SOLD" }),
        fetchCount("/inventory/units/", { status: "RESERVED" }),
        fetchCount("/crm/leads/", { status: "NEW" }),
      ]);

      return {
        totalProjects,
        totalUnits,
        availableUnits,
        soldUnits,
        reservedUnits,
        pendingLeads,
        soldRevenueCve: 0, // will be computed from contract module in Sprint 3
      };
    },
    staleTime: 60_000,
    enabled: !!schema,
  });
}
