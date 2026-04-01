/**
 * usePaymentPlans — ImoOS
 * API: /payments/plans/ + /contracts/payments/{id}/mark_paid/
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";
import { contractKeys } from "@/hooks/useContracts";

// ----- Types -----

export type PaymentStatus = "PENDING" | "PAID" | "OVERDUE";
export type PaymentType = "DEPOSIT" | "INSTALLMENT" | "FINAL";

export interface PaymentInstallment {
  id: string;
  payment_type: PaymentType;
  amount_cve: string;
  due_date: string;
  paid_date: string | null;
  status: PaymentStatus;
  reference: string;
}

export interface PaymentPlan {
  id: string;
  contract: string;
  generated_at: string | null;
  payments: PaymentInstallment[];
  created_at: string;
}

export interface MarkPaidPayload {
  payment_id: string;
  paid_date?: string;
  reference?: string;
}

// ----- Query keys -----

export const paymentPlanKeys = {
  all: (schema: string) => ["payment-plans", schema] as const,
  byContract: (schema: string, contractId: string) =>
    ["payment-plans", schema, "contract", contractId] as const,
};

// ----- Hooks -----

export function usePaymentPlan(contractId: string) {
  const { schema } = useTenant();

  return useQuery<PaymentPlan | null>({
    queryKey: paymentPlanKeys.byContract(schema, contractId),
    queryFn: async () => {
      const r = await apiClient.get<{ results: PaymentPlan[] }>(
        "/payments/plans/",
        { params: { contract: contractId } }
      );
      return r.data.results[0] ?? null;
    },
    staleTime: 30_000,
    enabled: !!schema && !!contractId,
  });
}

export function useGeneratePaymentPlan() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: async (contractId: string) => {
      const plan = await apiClient
        .post<PaymentPlan>("/payments/plans/", { contract: contractId })
        .then((r) => r.data);
      const generated = await apiClient
        .post<PaymentPlan>(`/payments/plans/${plan.id}/generate/`)
        .then((r) => r.data);
      return generated;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: paymentPlanKeys.all(schema) });
      qc.invalidateQueries({ queryKey: contractKeys.all(schema) });
    },
  });
}

export function useMarkPaymentPaid() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: ({ payment_id, paid_date, reference }: MarkPaidPayload) =>
      apiClient
        .post(`/contracts/payments/${payment_id}/mark_paid/`, {
          paid_date: paid_date ?? new Date().toISOString().slice(0, 10),
          reference,
        })
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: paymentPlanKeys.all(schema) });
      qc.invalidateQueries({ queryKey: contractKeys.all(schema) });
    },
  });
}
