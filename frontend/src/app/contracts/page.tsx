"use client";

import { useState } from "react";
import { FileText, Search, FileCheck2, Clock, Ban, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useContracts, type ContractStatus } from "@/hooks/useContracts";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate, formatCve } from "@/lib/format";

// ----- Status config -----

const STATUS_CONFIG: Record<
  ContractStatus,
  { label: string; className: string; icon: React.ElementType }
> = {
  DRAFT:     { label: "Rascunho",  className: "bg-slate-100 text-slate-600 border-slate-200",    icon: Clock },
  ACTIVE:    { label: "Activo",    className: "bg-emerald-50 text-emerald-700 border-emerald-200", icon: CheckCircle2 },
  COMPLETED: { label: "Concluído", className: "bg-blue-50 text-blue-700 border-blue-200",         icon: FileCheck2 },
  CANCELLED: { label: "Cancelado", className: "bg-red-50 text-red-600 border-red-200",            icon: Ban },
};

function ContractStatusBadge({ status }: { status: ContractStatus }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.DRAFT;
  const Icon = cfg.icon;
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-bold", cfg.className)}>
      <Icon className="h-3 w-3" />
      {cfg.label}
    </span>
  );
}

const STATUS_FILTERS: { value: ContractStatus | "ALL"; label: string }[] = [
  { value: "ALL",       label: "Todos" },
  { value: "DRAFT",     label: "Rascunho" },
  { value: "ACTIVE",    label: "Activos" },
  { value: "COMPLETED", label: "Concluídos" },
  { value: "CANCELLED", label: "Cancelados" },
];

// ----- Page -----

export default function ContractsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<ContractStatus | "ALL">("ALL");

  const { data, isLoading, isError } = useContracts({
    search: search || undefined,
    status: statusFilter === "ALL" ? undefined : statusFilter,
    page_size: 50,
    ordering: "-created_at",
  });

  const contracts = data?.results ?? [];

  return (
    <div className="space-y-6">

      {/* Filters bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <input
            type="search"
            placeholder="Pesquisar por nº, lead ou unidade…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-border bg-white pl-10 pr-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all"
          />
        </div>

        {/* Status tabs */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {STATUS_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setStatusFilter(f.value)}
              className={cn(
                "rounded-lg px-3.5 py-2 text-xs font-bold transition-all",
                statusFilter === f.value
                  ? "bg-primary text-white shadow-md shadow-primary/20"
                  : "bg-white border border-border text-muted-foreground hover:text-foreground hover:border-primary/30"
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 space-y-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full rounded-xl" />
            ))}
          </div>
        ) : isError ? (
          <div className="p-20 text-center">
            <p className="text-sm font-bold text-red-600">Erro ao carregar contratos.</p>
          </div>
        ) : contracts.length === 0 ? (
          <div className="p-20 flex flex-col items-center text-center">
            <div className="h-16 w-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
              <FileText className="h-8 w-8 text-muted-foreground/40" />
            </div>
            <p className="text-sm font-bold text-foreground">Nenhum contrato encontrado</p>
            <p className="text-xs text-muted-foreground mt-1">
              {search || statusFilter !== "ALL"
                ? "Tente ajustar os filtros."
                : "Os contratos aparecerão aqui quando forem criados."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-slate-50/50">
                  {["Nº Contrato", "Lead", "Unidade", "Valor CVE", "Estado", "Assinado em", "Criado em"].map((h) => (
                    <th
                      key={h}
                      className="px-6 py-4 text-left text-[10px] font-bold text-muted-foreground uppercase tracking-widest whitespace-nowrap"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {contracts.map((c) => (
                  <tr
                    key={c.id}
                    className="hover:bg-slate-50/70 transition-colors group"
                  >
                    <td className="px-6 py-4 font-mono font-bold text-foreground text-xs group-hover:text-primary transition-colors whitespace-nowrap">
                      {c.contract_number}
                    </td>
                    <td className="px-6 py-4 font-medium text-foreground">
                      {c.lead_name}
                    </td>
                    <td className="px-6 py-4 font-mono text-muted-foreground font-bold text-xs">
                      {c.unit_code}
                    </td>
                    <td className="px-6 py-4 font-black text-foreground whitespace-nowrap">
                      {formatCve(c.total_price_cve)}
                    </td>
                    <td className="px-6 py-4">
                      <ContractStatusBadge status={c.status} />
                    </td>
                    <td className="px-6 py-4 text-muted-foreground text-xs whitespace-nowrap">
                      {c.signed_at ? formatDate(c.signed_at) : <span className="text-muted-foreground/50">—</span>}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground text-xs whitespace-nowrap">
                      {formatDate(c.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
