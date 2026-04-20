/**
 * useContractSettings — ImoOS
 * Hooks for Contract Templates and Payment Patterns
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export interface ContractTemplate {
  id: string;
  name: string;
  description: string;
  content: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaymentPattern {
  id: string;
  name: string;
  description: string;
  pattern_type: "SINGLE" | "RECURRING" | "STAGED";
  down_payment_percentage: string;
  down_payment_due_days: number;
  installments_count: number;
  installments_interval_days: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface GenericPagination<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ----- Query keys -----

export const contractSettingsKeys = {
  all: (schema: string) => ["contract-settings", schema] as const,
  templates: (schema: string) => ["contract-settings", schema, "templates"] as const,
  patterns: (schema: string) => ["contract-settings", schema, "patterns"] as const,
};

// ----- Hooks: Templates -----

export function useContractTemplates() {
  const { schema } = useTenant();

  return useQuery<GenericPagination<ContractTemplate>>({
    queryKey: contractSettingsKeys.templates(schema),
    queryFn: () =>
      apiClient
        .get<GenericPagination<ContractTemplate>>("/contracts/templates/")
        .then((r) => r.data),
    enabled: !!schema,
  });
}

export function useCreateContractTemplate() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (data: Partial<ContractTemplate>) =>
      apiClient
        .post<ContractTemplate>("/contracts/templates/", data)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: contractSettingsKeys.templates(schema) });
    },
  });
}

// ----- Hooks: Patterns -----

export function usePaymentPatterns() {
  const { schema } = useTenant();

  return useQuery<GenericPagination<PaymentPattern>>({
    queryKey: contractSettingsKeys.patterns(schema),
    queryFn: () =>
      apiClient
        .get<GenericPagination<PaymentPattern>>("/contracts/patterns/")
        .then((r) => r.data),
    enabled: !!schema,
  });
}

export function useCreatePaymentPattern() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (data: Partial<PaymentPattern>) =>
      apiClient
        .post<PaymentPattern>("/contracts/patterns/", data)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: contractSettingsKeys.patterns(schema) });
    },
  });
}

export function useApplyPaymentPattern() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: ({ contractId, patternId }: { contractId: string; patternId: string }) =>
      apiClient
        .post(`/contracts/contracts/${contractId}/apply_pattern/`, { pattern_id: patternId })
        .then((r) => r.data),
    onSuccess: (_, { contractId }) => {
      qc.invalidateQueries({ queryKey: ["contracts", schema, "detail", contractId] });
    },
  });
}
