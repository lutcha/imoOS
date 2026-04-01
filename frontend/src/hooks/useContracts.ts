/**
 * useContracts — ImoOS
 * Skill: react-query-tenant
 * API path: api/v1/contracts/contracts/
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type ContractStatus = "DRAFT" | "ACTIVE" | "COMPLETED" | "CANCELLED";

export interface PaymentSummary {
  id: string;
  payment_type: string;
  amount_cve: string;
  due_date: string;
  paid_date: string | null;
  status: "PENDING" | "PAID" | "OVERDUE";
  reference: string;
}

export interface Contract {
  id: string;
  reservation: string | null;
  unit: string;
  unit_code: string;
  lead: string;
  lead_name: string;
  vendor: string | null;
  vendor_email: string | null;
  status: ContractStatus;
  contract_number: string;
  total_price_cve: string;
  signed_at: string | null;
  pdf_s3_key: string;
  notes: string;
  payments: PaymentSummary[];
  created_at: string;
  updated_at: string;
}

export interface ContractsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: Contract[];
}

export interface ContractFilters {
  status?: ContractStatus;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

// ----- Query keys -----

export const contractKeys = {
  all: (schema: string) => ["contracts", schema] as const,
  list: (schema: string, filters: ContractFilters) =>
    ["contracts", schema, "list", filters] as const,
  detail: (schema: string, id: string) =>
    ["contracts", schema, "detail", id] as const,
};

// ----- Hooks -----

export function useContracts(filters: ContractFilters = {}) {
  const { schema } = useTenant();

  return useQuery<ContractsPage>({
    queryKey: contractKeys.list(schema, filters),
    queryFn: () =>
      apiClient
        .get<ContractsPage>("/contracts/contracts/", { params: filters })
        .then((r) => r.data),
    staleTime: 30_000,
    enabled: !!schema,
  });
}

export function useContract(id: string) {
  const { schema } = useTenant();

  return useQuery<Contract>({
    queryKey: contractKeys.detail(schema, id),
    queryFn: () =>
      apiClient.get<Contract>(`/contracts/contracts/${id}/`).then((r) => r.data),
    enabled: !!schema && !!id,
  });
}

export function useActivateContract() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (id: string) =>
      apiClient
        .post<Contract>(`/contracts/contracts/${id}/activate/`)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: contractKeys.all(schema) });
    },
  });
}

export function useCancelContract() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (id: string) =>
      apiClient
        .post<Contract>(`/contracts/contracts/${id}/cancel/`)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: contractKeys.all(schema) });
    },
  });
}
