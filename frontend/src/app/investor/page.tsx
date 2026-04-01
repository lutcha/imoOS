"use client";

import { useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useAuth } from "@/contexts/AuthContext";
import { Skeleton } from "@/components/ui/Skeleton";
import { StatusBadge } from "@/components/ui/StatusBadge";

interface UpcomingPayment {
  id: string;
  contract_number: string;
  unit_code: string;
  payment_type: string;
  amount_cve: string;
  due_date: string;
  status: string;
}

interface Summary {
  units_by_status: Record<string, number>;
  total_invested_cve: string;
  upcoming_payments: UpcomingPayment[];
}

interface Contract {
  id: string;
  contract_number: string;
  unit_code: string;
  project_name: string;
  status: string;
  total_price_cve: string;
  signed_at: string | null;
  pdf_s3_key: string;
}

function formatCVE(value: string): string {
  return new Intl.NumberFormat("pt-CV", {
    style: "currency",
    currency: "CVE",
    minimumFractionDigits: 0,
  }).format(Number(value));
}

export default function InvestorDashboard() {
  const { isAuthenticated } = useAuth();

  const { data: summary, isLoading: loadingSummary } = useQuery<Summary>({
    queryKey: ["investor-summary"],
    queryFn: () =>
      apiClient.get<Summary>("/investors/portal/my_summary/").then((r) => r.data),
    enabled: isAuthenticated,
  });

  const { data: contracts, isLoading: loadingContracts } = useQuery<Contract[]>({
    queryKey: ["investor-contracts"],
    queryFn: () =>
      apiClient.get<Contract[]>("/investors/portal/").then((r) => r.data),
    enabled: isAuthenticated,
  });

  if (loadingSummary || loadingContracts) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[0, 1, 2].map((i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
        </div>
        <Skeleton className="h-64 rounded-xl" />
      </div>
    );
  }

  const unitsTotal = summary
    ? Object.values(summary.units_by_status).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-foreground">O Meu Portfólio</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-border p-5">
          <p className="text-sm text-muted-foreground">Unidades</p>
          <p className="text-3xl font-bold mt-1">{unitsTotal}</p>
        </div>
        <div className="bg-white rounded-xl border border-border p-5">
          <p className="text-sm text-muted-foreground">Total Investido</p>
          <p className="text-3xl font-bold mt-1 text-primary">
            {summary ? formatCVE(summary.total_invested_cve) : "—"}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-border p-5">
          <p className="text-sm text-muted-foreground">Pagamentos Próximos (30 dias)</p>
          <p className="text-3xl font-bold mt-1 text-amber-600">
            {summary?.upcoming_payments.length ?? 0}
          </p>
        </div>
      </div>

      {/* Upcoming Payments */}
      {summary && summary.upcoming_payments.length > 0 && (
        <div className="bg-white rounded-xl border border-border overflow-hidden">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="font-semibold text-foreground">Pagamentos Pendentes</h2>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Contrato</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Unidade</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Tipo</th>
                <th className="text-right px-6 py-3 text-muted-foreground font-medium">Valor (CVE)</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Vencimento</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {summary.upcoming_payments.map((p) => (
                <tr key={p.id} className="hover:bg-muted/30">
                  <td className="px-6 py-3 font-mono text-xs">{p.contract_number}</td>
                  <td className="px-6 py-3">{p.unit_code}</td>
                  <td className="px-6 py-3">{p.payment_type}</td>
                  <td className="px-6 py-3 text-right">{formatCVE(p.amount_cve)}</td>
                  <td className="px-6 py-3">{p.due_date}</td>
                  <td className="px-6 py-3">
                    <StatusBadge status={p.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Contracts */}
      <div className="bg-white rounded-xl border border-border overflow-hidden">
        <div className="px-6 py-4 border-b border-border">
          <h2 className="font-semibold text-foreground">Os Meus Contratos</h2>
        </div>
        {!contracts || contracts.length === 0 ? (
          <p className="px-6 py-8 text-muted-foreground text-sm text-center">
            Nenhum contrato encontrado.
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Nº Contrato</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Unidade</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Projecto</th>
                <th className="text-right px-6 py-3 text-muted-foreground font-medium">Valor (CVE)</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {contracts.map((c) => (
                <tr key={c.id} className="hover:bg-muted/30">
                  <td className="px-6 py-3 font-mono text-xs">{c.contract_number}</td>
                  <td className="px-6 py-3">{c.unit_code}</td>
                  <td className="px-6 py-3 text-muted-foreground">{c.project_name}</td>
                  <td className="px-6 py-3 text-right">{formatCVE(c.total_price_cve)}</td>
                  <td className="px-6 py-3">
                    <StatusBadge status={c.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
