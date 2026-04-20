/**
 * useProjectFinance — ImoOS
 * Hook para gerir dados financeiros de construção (Despesas, Adiantamentos, Sumário).
 * API path: api/v1/budget/expenses/ | api/v1/budget/advances/
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type ExpenseCategory = "MATERIALS" | "LABOR" | "EQUIPMENT" | "SERVICES" | "OTHER";
export type FinanceStatus = "PENDING" | "APPROVED" | "PAID" | "CANCELLED";

export interface ConstructionExpense {
  id: string;
  project: string;
  project_name: string;
  task?: string;
  task_name?: string;
  description: string;
  category: ExpenseCategory;
  category_display: string;
  amount_cve: string;
  amount_eur: string;
  payment_date: string;
  supplier: string;
  invoice_number?: string;
  receipt_photo?: string;
  status: FinanceStatus;
  status_display: string;
  notes?: string;
  created_at: string;
}

export interface ConstructionAdvance {
  id: string;
  project: string;
  project_name: string;
  description: string;
  amount_cve: string;
  amount_eur: string;
  payment_date: string;
  recipient: string;
  is_settled: boolean;
  settled_at?: string;
  status: FinanceStatus;
  status_display: string;
  notes?: string;
  created_at: string;
}

export interface CategoryComparison {
  category: ExpenseCategory;
  name: string;
  budget: number;
  actual: number;
  variance: number;
}

export interface ProjectFinancialStatus {
  project_name: string;
  budget_total_cve: number;
  actual_total_cve: number;
  pending_advances_cve: number;
  variance_cve: number;
  variance_pct: number;
  currency_cve: string;
  currency_eur: string;
  eur_rate: number;
  categories: CategoryComparison[];
}

// ----- Query Keys -----

export const financeKeys = {
  all: (schema: string) => ["finance", schema] as const,
  summary: (schema: string, projectId: string) => [...financeKeys.all(schema), "summary", projectId] as const,
  expenses: (schema: string, projectId: string) => [...financeKeys.all(schema), "expenses", projectId] as const,
  advances: (schema: string, projectId: string) => [...financeKeys.all(schema), "advances", projectId] as const,
};

// ----- Hooks -----

export function useProjectFinanceSummary(projectId: string) {
  const { schema } = useTenant();

  return useQuery<ProjectFinancialStatus>({
    queryKey: financeKeys.summary(schema, projectId),
    queryFn: () =>
      apiClient
        .get<ProjectFinancialStatus>("/budget/expenses/project_summary/", {
          params: { project: projectId },
        })
        .then((r) => r.data),
    enabled: !!schema && !!projectId,
  });
}

export function useProjectExpenses(projectId: string) {
  const { schema } = useTenant();

  return useQuery<ConstructionExpense[]>({
    queryKey: financeKeys.expenses(schema, projectId),
    queryFn: () =>
      apiClient
        .get<any>("/budget/expenses/", { params: { project: projectId } })
        .then((r) => r.data.results), // Assumindo paginação padrão do DRF
    enabled: !!schema && !!projectId,
  });
}

export function useProjectAdvances(projectId: string) {
  const { schema } = useTenant();

  return useQuery<ConstructionAdvance[]>({
    queryKey: financeKeys.advances(schema, projectId),
    queryFn: () =>
      apiClient
        .get<any>("/budget/advances/", { params: { project: projectId } })
        .then((r) => r.data.results),
    enabled: !!schema && !!projectId,
  });
}

export function useAddExpense() {
  const { schema } = useTenant();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<ConstructionExpense>) =>
      apiClient.post("/budget/expenses/", data),
    onSuccess: (_, variables) => {
      if (variables.project) {
        queryClient.invalidateQueries({ queryKey: financeKeys.expenses(schema, variables.project) });
        queryClient.invalidateQueries({ queryKey: financeKeys.summary(schema, variables.project) });
      }
    },
  });
}

export function useAddAdvance() {
  const { schema } = useTenant();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<ConstructionAdvance>) =>
      apiClient.post("/budget/advances/", data),
    onSuccess: (_, variables) => {
      if (variables.project) {
        queryClient.invalidateQueries({ queryKey: financeKeys.advances(schema, variables.project) });
        queryClient.invalidateQueries({ queryKey: financeKeys.summary(schema, variables.project) });
      }
    },
  });
}
