"use client";

/**
 * Inventory page — ImoOS
 * Units table with inline filters: status, search, area range.
 * Pagination via page param.
 * Skill: unit-status-workflow, unit-pricing-currency
 */
import { useState, useCallback } from "react";
import { Search, SlidersHorizontal, ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { UnitModal } from "@/components/inventory/UnitModal";
import { cn } from "@/lib/utils";
import { useUnits, type UnitStatus } from "@/hooks/useUnits";
import { UnitStatusBadge } from "@/components/ui/StatusBadge";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatArea, formatCve, formatEur } from "@/lib/format";

const PAGE_SIZE = 20;

const STATUS_OPTIONS: { value: UnitStatus | ""; label: string }[] = [
  { value: "",            label: "Todos" },
  { value: "AVAILABLE",   label: "Disponível" },
  { value: "RESERVED",    label: "Reservado" },
  { value: "CONTRACT",    label: "Contrato" },
  { value: "SOLD",        label: "Vendido" },
  { value: "MAINTENANCE", label: "Manutenção" },
];

function TableSkeleton() {
  return (
    <tbody className="divide-y divide-border">
      {Array.from({ length: 8 }).map((_, i) => (
        <tr key={i}>
          {Array.from({ length: 7 }).map((_, j) => (
            <td key={j} className="px-4 py-3.5">
              <Skeleton className={cn("h-4", j === 0 ? "w-20" : j === 4 ? "w-24" : "w-16")} />
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  );
}

export default function InventoryPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<UnitStatus | "">("");
  const [showFilters, setShowFilters] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [areaMin, setAreaMin] = useState("");
  const [areaMax, setAreaMax] = useState("");

  const { data, isLoading, isError } = useUnits({
    page,
    page_size: PAGE_SIZE,
    search: search || undefined,
    status: status || undefined,
    area_bruta__gte: areaMin ? Number(areaMin) : undefined,
    area_bruta__lte: areaMax ? Number(areaMax) : undefined,
    ordering: "code",
  });

  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 1;

  const resetFilters = useCallback(() => {
    setSearch("");
    setStatus("");
    setAreaMin("");
    setAreaMax("");
    setPage(1);
  }, []);

  const hasActiveFilters = !!(search || status || areaMin || areaMax);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Inventário</h1>
          <p className="text-muted-foreground mt-1">
            {data
              ? `${data.count} unidade${data.count !== 1 ? "s" : ""} · Página ${page} de ${totalPages}`
              : "A carregar…"}
          </p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center space-x-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-primary/90 shadow-md shadow-primary/20"
        >
          <Plus className="h-4 w-4" />
          <span>Nova Unidade</span>
        </button>
      </div>

      <UnitModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
      />

      {/* Filter bar */}
      <div className="flex flex-wrap gap-3 items-center">
        {/* Search */}
        <div className="flex items-center rounded-lg border border-border bg-white px-3.5 py-2 min-w-56 shadow-sm">
          <Search className="h-4 w-4 text-muted-foreground mr-2 shrink-0" />
          <input
            type="text"
            placeholder="Código ou descrição…"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="bg-transparent text-sm outline-none placeholder:text-muted-foreground w-full"
          />
        </div>

        {/* Status filter pills */}
        <div className="flex gap-1.5 flex-wrap">
          {STATUS_OPTIONS.map((o) => (
            <button
              key={o.value}
              onClick={() => { setStatus(o.value as UnitStatus | ""); setPage(1); }}
              className={cn(
                "rounded-full px-3 py-1.5 text-xs font-semibold transition-colors border",
                status === o.value
                  ? "bg-primary text-white border-primary"
                  : "bg-white text-muted-foreground border-border hover:border-primary/40 hover:text-foreground"
              )}
            >
              {o.label}
            </button>
          ))}
        </div>

        {/* Advanced filters toggle */}
        <button
          onClick={() => setShowFilters((v) => !v)}
          className={cn(
            "flex items-center space-x-1.5 rounded-lg border px-3.5 py-2 text-sm font-medium transition-colors shadow-sm",
            showFilters
              ? "border-primary bg-primary/5 text-primary"
              : "border-border bg-white text-muted-foreground hover:text-foreground"
          )}
        >
          <SlidersHorizontal className="h-4 w-4" />
          <span>Filtros</span>
        </button>

        {hasActiveFilters && (
          <button
            onClick={resetFilters}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors underline-offset-2 hover:underline"
          >
            Limpar filtros
          </button>
        )}
      </div>

      {/* Advanced filter panel */}
      {showFilters && (
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">Área mín. (m²)</label>
            <input
              type="number"
              min={0}
              placeholder="0"
              value={areaMin}
              onChange={(e) => { setAreaMin(e.target.value); setPage(1); }}
              className="rounded-lg border border-border bg-white px-3 py-2 text-sm outline-none w-28 focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">Área máx. (m²)</label>
            <input
              type="number"
              min={0}
              placeholder="∞"
              value={areaMax}
              onChange={(e) => { setAreaMax(e.target.value); setPage(1); }}
              className="rounded-lg border border-border bg-white px-3 py-2 text-sm outline-none w-28 focus:border-primary"
            />
          </div>
        </div>
      )}

      {/* Table */}
      <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
        {isError && (
          <div className="p-6 text-center text-sm text-red-600">
            Erro ao carregar unidades. Verifique a ligação à API.
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/40">
                {[
                  { label: "Código",     w: "w-28" },
                  { label: "Tipologia",  w: "w-24" },
                  { label: "Piso",       w: "w-16" },
                  { label: "Área Bruta", w: "w-24" },
                  { label: "Preço CVE",  w: "w-32" },
                  { label: "Preço EUR",  w: "w-28" },
                  { label: "Estado",     w: "w-28" },
                ].map(({ label }) => (
                  <th
                    key={label}
                    className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap"
                  >
                    {label}
                  </th>
                ))}
              </tr>
            </thead>

            {isLoading ? (
              <TableSkeleton />
            ) : (
              <tbody className="divide-y divide-border">
                {(data?.results ?? []).length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-16 text-center text-muted-foreground text-sm">
                      Nenhuma unidade encontrada com os filtros actuais.
                    </td>
                  </tr>
                ) : (
                  (data?.results ?? []).map((unit) => (
                    <tr
                      key={unit.id}
                      className="hover:bg-muted/30 transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3.5 font-mono font-semibold text-foreground">
                        {unit.code}
                      </td>
                      <td className="px-4 py-3.5 text-muted-foreground">
                        {unit.unit_type_detail?.name ?? "—"}
                      </td>
                      <td className="px-4 py-3.5 text-muted-foreground">
                        {unit.floor_number}
                      </td>
                      <td className="px-4 py-3.5 text-muted-foreground tabular-nums">
                        {formatArea(unit.area_bruta)}
                      </td>
                      <td className="px-4 py-3.5 font-medium tabular-nums">
                        {unit.pricing ? formatCve(unit.pricing.final_price_cve) : "—"}
                      </td>
                      <td className="px-4 py-3.5 text-muted-foreground tabular-nums">
                        {unit.pricing?.price_eur ? formatEur(unit.pricing.price_eur) : "—"}
                      </td>
                      <td className="px-4 py-3.5">
                        <UnitStatusBadge status={unit.status} />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            )}
          </table>
        </div>

        {/* Pagination */}
        {!isLoading && totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-border px-4 py-3">
            <span className="text-sm text-muted-foreground">
              {((page - 1) * PAGE_SIZE) + 1}–{Math.min(page * PAGE_SIZE, data?.count ?? 0)} de {data?.count ?? 0}
            </span>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg border border-border p-1.5 transition hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed"
                aria-label="Página anterior"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-sm font-medium px-2">{page} / {totalPages}</span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="rounded-lg border border-border p-1.5 transition hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed"
                aria-label="Página seguinte"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
