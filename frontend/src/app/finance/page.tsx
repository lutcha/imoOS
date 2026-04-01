"use client";

/**
 * Financeiro page — ImoOS
 * Overview of payment plans, installments due, and revenue collected.
 */
import { useState } from "react";
import { Wallet, Search, CheckCircle2, Clock, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatCve, formatDate } from "@/lib/format";
import { Skeleton } from "@/components/ui/Skeleton";
import { useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

type ItemStatus = "PAID" | "PENDING" | "OVERDUE";

interface PlanItem {
  id: string;
  item_type: "DEPOSIT" | "INSTALLMENT" | "FINAL";
  amount_cve: string;
  due_date: string;
  mbe_reference: string;
  order: number;
  is_paid: boolean;
}

interface PaymentPlan {
  id: string;
  plan_type: string;
  plan_type_display: string;
  total_cve: string;
  contract_number: string;
  items_count: number;
  paid_count: number;
  items: PlanItem[];
  created_at: string;
}

interface PlanListResponse {
  count: number;
  results: PaymentPlan[];
}

// ----- Status helpers -----

function itemStatus(item: PlanItem): ItemStatus {
  if (item.is_paid) return "PAID";
  const today = new Date().toISOString().slice(0, 10);
  return item.due_date < today ? "OVERDUE" : "PENDING";
}

const STATUS_CONFIG: Record<ItemStatus, { label: string; className: string; icon: React.ElementType }> = {
  PAID:    { label: "Pago",      className: "bg-emerald-50 text-emerald-700 border-emerald-200", icon: CheckCircle2 },
  PENDING: { label: "Pendente",  className: "bg-slate-100 text-slate-600 border-slate-200",      icon: Clock },
  OVERDUE: { label: "Em atraso", className: "bg-red-50 text-red-600 border-red-200",             icon: AlertCircle },
};

const TYPE_LABEL: Record<PlanItem["item_type"], string> = {
  DEPOSIT:     "Sinal",
  INSTALLMENT: "Prestação",
  FINAL:       "Final",
};

// ----- Hook -----

function usePaymentPlans(search: string) {
  const { schema } = useTenant();
  return useQuery<PlanListResponse>({
    queryKey: ["finance-plans", schema, search],
    queryFn: async () => {
      const r = await apiClient.get<PlanListResponse>("/payments/plans/", {
        params: { page_size: 50, ordering: "-created_at", search: search || undefined },
      });
      return r.data;
    },
    staleTime: 30_000,
    enabled: !!schema,
  });
}

// ----- Stat card -----

function StatCard({ label, value, sub, color }: { label: string; value: string | null; sub?: string; color: string }) {
  return (
    <div className="rounded-xl border border-border bg-white px-5 py-4 shadow-sm">
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</p>
      {value === null ? (
        <Skeleton className="mt-2 h-7 w-24" />
      ) : (
        <p className={cn("mt-1 text-2xl font-bold tabular-nums", color)}>{value}</p>
      )}
      {sub && <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>}
    </div>
  );
}

// ----- Page -----

export default function FinancePage() {
  const [search, setSearch] = useState("");
  const { data, isLoading, isError } = usePaymentPlans(search);

  const plans = data?.results ?? [];

  // Flatten all items for stats
  const allItems = plans.flatMap((p) => p.items);
  const totalRevenue = allItems
    .filter((i) => i.is_paid)
    .reduce((sum, i) => sum + parseFloat(i.amount_cve), 0);
  const pendingRevenue = allItems
    .filter((i) => !i.is_paid)
    .reduce((sum, i) => sum + parseFloat(i.amount_cve), 0);
  const overdueCount = allItems.filter((i) => itemStatus(i) === "OVERDUE").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div className="flex items-center space-x-4">
          <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/10">
            <Wallet className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">Financeiro</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              {data ? `${data.count} plano${data.count !== 1 ? "s" : ""} de pagamento` : "A carregar…"}
            </p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Planos activos"   value={isLoading ? null : String(plans.length)}          color="text-foreground" />
        <StatCard label="Recebido"         value={isLoading ? null : formatCve(totalRevenue)}        color="text-emerald-700" />
        <StatCard label="Por receber"      value={isLoading ? null : formatCve(pendingRevenue)}      color="text-blue-700" />
        <StatCard label="Em atraso"        value={isLoading ? null : String(overdueCount) + " prestações"} color="text-red-600" />
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
        <input
          type="search"
          placeholder="Pesquisar por contrato, lead ou unidade…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-xl border border-border bg-white pl-10 pr-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all"
        />
      </div>

      {/* Plans */}
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-2xl" />
          ))}
        </div>
      ) : isError ? (
        <div className="rounded-2xl border border-border bg-white p-20 text-center">
          <p className="text-sm font-bold text-red-600">Erro ao carregar planos de pagamento.</p>
        </div>
      ) : plans.length === 0 ? (
        <div className="rounded-2xl border border-border bg-white p-20 flex flex-col items-center text-center">
          <div className="h-16 w-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
            <Wallet className="h-8 w-8 text-muted-foreground/40" />
          </div>
          <p className="text-sm font-bold text-foreground">Nenhum plano de pagamento</p>
          <p className="text-xs text-muted-foreground mt-1">
            Os planos são criados a partir dos contratos activos.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {plans.map((plan) => (
            <div key={plan.id} className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
              {/* Plan header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-slate-50/50">
                <div className="flex items-center gap-4">
                  <span className="font-mono text-xs font-bold text-primary">{plan.contract_number}</span>
                  <span className="text-xs text-muted-foreground">{plan.plan_type_display}</span>
                  <span className="text-xs text-muted-foreground">
                    {plan.paid_count}/{plan.items_count} prestações pagas
                  </span>
                </div>
                <span className="text-sm font-bold text-foreground tabular-nums">
                  {formatCve(parseFloat(plan.total_cve))}
                </span>
              </div>

              {/* Items table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      {["Tipo", "Valor", "Vencimento", "Ref. MBE", "Estado"].map((h) => (
                        <th key={h} className="px-5 py-3 text-left text-[10px] font-bold text-muted-foreground uppercase tracking-widest whitespace-nowrap">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {plan.items.map((item) => {
                      const st = itemStatus(item);
                      const cfg = STATUS_CONFIG[st];
                      const Icon = cfg.icon;
                      return (
                        <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                          <td className="px-5 py-3 font-medium text-foreground whitespace-nowrap">
                            {TYPE_LABEL[item.item_type]}
                          </td>
                          <td className="px-5 py-3 font-bold tabular-nums whitespace-nowrap">
                            {formatCve(parseFloat(item.amount_cve))}
                          </td>
                          <td className="px-5 py-3 text-muted-foreground whitespace-nowrap">
                            {formatDate(item.due_date)}
                          </td>
                          <td className="px-5 py-3 font-mono text-xs text-muted-foreground">
                            {item.mbe_reference || "—"}
                          </td>
                          <td className="px-5 py-3">
                            <span className={cn(
                              "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-bold",
                              cfg.className
                            )}>
                              <Icon className="h-3 w-3" />
                              {cfg.label}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
