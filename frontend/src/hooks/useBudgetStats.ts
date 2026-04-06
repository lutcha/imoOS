/**
 * useBudgetStats — ImoOS
 * API: /budget/* — estatísticas e gestão de orçamentos
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type BudgetStatus = "DRAFT" | "APPROVED" | "REJECTED" | "REVISED";

export interface BudgetCategory {
  id: string;
  name: string;
  code: string;
  description: string;
}

export interface BudgetItem {
  id: string;
  budget: string;
  category: string | null;
  category_name: string | null;
  description: string;
  quantity: string;
  unit: string;
  unit_price_cve: string;
  total_price_cve: string;
  actual_cost_cve: string | null;
  variance_pct: number | null;
  notes: string;
  order: number;
}

export interface Budget {
  id: string;
  project: string;
  project_name: string;
  name: string;
  description: string;
  status: BudgetStatus;
  version: number;
  total_budget_cve: string;
  total_actual_cve: string | null;
  variance_pct: number | null;
  created_by: string | null;
  approved_by: string | null;
  approved_date: string | null;
  valid_until: string | null;
  created_at: string;
  updated_at: string;
}

export interface BudgetDetail extends Budget {
  items: BudgetItem[];
}

export interface BudgetStats {
  total_budgets: number;
  total_budgeted_cve: string;
  total_actual_cve: string;
  overall_variance_pct: number;
  budgets_by_status: Record<BudgetStatus, number>;
  categories_summary: {
    category: string;
    category_name: string;
    budgeted_cve: string;
    actual_cve: string;
    variance_pct: number;
  }[];
}

export interface BudgetsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: Budget[];
}

export interface BudgetFilters {
  project?: string;
  status?: BudgetStatus;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

// ----- Query keys -----

export const budgetKeys = {
  all: (schema: string) => ["budget", schema] as const,
  list: (schema: string, filters: BudgetFilters) =>
    ["budget", schema, "list", filters] as const,
  detail: (schema: string, id: string) =>
    ["budget", schema, "detail", id] as const,
  stats: (schema: string, projectId?: string) =>
    ["budget", schema, "stats", projectId || "all"] as const,
  categories: (schema: string) =>
    ["budget", schema, "categories"] as const,
};

// ----- Hooks -----

export function useBudgets(filters: BudgetFilters = {}) {
  const { schema } = useTenant();

  return useQuery<BudgetsPage>({
    queryKey: budgetKeys.list(schema, filters),
    queryFn: () =>
      apiClient
        .get<BudgetsPage>("/budget/budgets/", { params: filters })
        .then((r) => r.data),
    staleTime: 60_000,
    enabled: !!schema,
  });
}

export function useBudget(id: string) {
  const { schema } = useTenant();

  return useQuery<BudgetDetail>({
    queryKey: budgetKeys.detail(schema, id),
    queryFn: () =>
      apiClient
        .get<BudgetDetail>(`/budget/budgets/${id}/`)
        .then((r) => r.data),
    enabled: !!schema && !!id,
  });
}

export function useBudgetStats(projectId?: string) {
  const { schema } = useTenant();

  return useQuery<BudgetStats>({
    queryKey: budgetKeys.stats(schema, projectId),
    queryFn: () =>
      apiClient
        .get<BudgetStats>("/budget/stats/", { 
          params: projectId ? { project: projectId } : undefined 
        })
        .then((r) => r.data),
    staleTime: 60_000,
    enabled: !!schema,
  });
}

export function useBudgetCategories() {
  const { schema } = useTenant();

  return useQuery<BudgetCategory[]>({
    queryKey: budgetKeys.categories(schema),
    queryFn: () =>
      apiClient
        .get<{ results: BudgetCategory[] }>("/budget/categories/")
        .then((r) => r.data.results),
    staleTime: 300_000, // 5 minutos, categories don't change often
    enabled: !!schema,
  });
}

// ----- Mutations -----

export function useApproveBudget() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (id: string) =>
      apiClient
        .post<Budget>(`/budget/budgets/${id}/approve/`)
        .then((r) => r.data),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: budgetKeys.all(schema) });
      qc.invalidateQueries({ queryKey: budgetKeys.detail(schema, id) });
    },
  });
}

export function useCreateBudgetItem() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (payload: Omit<BudgetItem, "id" | "total_price_cve" | "variance_pct">) =>
      apiClient
        .post<BudgetItem>("/budget/items/", payload)
        .then((r) => r.data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: budgetKeys.all(schema) });
      qc.invalidateQueries({ queryKey: budgetKeys.detail(schema, variables.budget) });
    },
  });
}

// ----- Helpers -----

export function getBudgetStatusLabel(status: BudgetStatus): string {
  const labels: Record<BudgetStatus, string> = {
    DRAFT: "Rascunho",
    APPROVED: "Aprovado",
    REJECTED: "Rejeitado",
    REVISED: "Revisto",
  };
  return labels[status];
}

export function getBudgetStatusColor(status: BudgetStatus): { bg: string; text: string; border: string } {
  const colors: Record<BudgetStatus, { bg: string; text: string; border: string }> = {
    DRAFT: { bg: "bg-slate-50", text: "text-slate-600", border: "border-slate-200" },
    APPROVED: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200" },
    REJECTED: { bg: "bg-red-50", text: "text-red-600", border: "border-red-200" },
    REVISED: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200" },
  };
  return colors[status];
}

export function formatBudgetVariance(variancePct: number | null): {
  label: string;
  color: string;
  isAlert: boolean;
} {
  if (variancePct === null) {
    return { label: "—", color: "text-slate-400", isAlert: false };
  }
  
  const formatted = `${variancePct > 0 ? "+" : ""}${variancePct.toFixed(1)}%`;
  
  if (variancePct > 10) {
    return { label: formatted, color: "text-red-600", isAlert: true };
  }
  if (variancePct > 5) {
    return { label: formatted, color: "text-amber-600", isAlert: true };
  }
  if (variancePct < -5) {
    return { label: formatted, color: "text-emerald-600", isAlert: false };
  }
  return { label: formatted, color: "text-slate-600", isAlert: false };
}

export function calculateItemTotalPrice(quantity: number, unitPrice: number): number {
  return quantity * unitPrice;
}

export function calculateVariancePct(budgeted: number, actual: number | null): number | null {
  if (actual === null || budgeted === 0) return null;
  return ((actual - budgeted) / budgeted) * 100;
}
