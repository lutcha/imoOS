"use client";

/**
 * Marketplace page — ImoOS
 * Gestão de anúncios publicados no imo.cv.
 */
import { AlertTriangle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatCve, formatDateTime } from "@/lib/format";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  useMarketplaceListings,
  useSyncListing,
  useSyncAllListings,
  useUpdateListing,
  type ListingStatus,
  type MarketplaceListing,
} from "@/hooks/useMarketplace";

// ----- Status badge -----

const STATUS_LABEL: Record<ListingStatus, string> = {
  PUBLISHED:    "Publicado",
  PENDING_SYNC: "Pendente",
  PAUSED:       "Pausado",
  REMOVED:      "Removido",
};

const STATUS_CLASS: Record<ListingStatus, string> = {
  PUBLISHED:    "bg-green-100 text-green-800",
  PENDING_SYNC: "bg-yellow-100 text-yellow-800",
  PAUSED:       "bg-gray-100 text-gray-700",
  REMOVED:      "bg-red-100 text-red-700",
};

function ListingStatusBadge({
  status,
  syncError,
}: {
  status: ListingStatus;
  syncError: string | null;
}) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span
        className={cn(
          "inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold",
          STATUS_CLASS[status]
        )}
      >
        {STATUS_LABEL[status]}
      </span>
      {syncError && (
        <span title={syncError}>
          <AlertTriangle className="h-3.5 w-3.5 text-orange-500" />
        </span>
      )}
    </span>
  );
}

// ----- Skeleton -----

function TableSkeleton() {
  return (
    <tbody className="divide-y divide-border">
      {Array.from({ length: 6 }).map((_, i) => (
        <tr key={i}>
          {Array.from({ length: 6 }).map((_, j) => (
            <td key={j} className="px-4 py-3.5">
              <Skeleton className={cn("h-4", j === 0 ? "w-20" : "w-16")} />
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  );
}

// ----- Action button for a single listing -----

function ListingActions({
  listing,
  onSync,
  onToggle,
  isSyncing,
  isToggling,
}: {
  listing: MarketplaceListing;
  onSync: () => void;
  onToggle: () => void;
  isSyncing: boolean;
  isToggling: boolean;
}) {
  const toggleLabel =
    listing.status === "PUBLISHED"
      ? "Pausar"
      : listing.status === "PAUSED"
      ? "Retomar"
      : listing.status === "PENDING_SYNC"
      ? "Sincronizar"
      : null;

  return (
    <span className="flex items-center gap-2">
      <button
        onClick={onSync}
        disabled={isSyncing}
        title="Sincronizar com imo.cv"
        className="rounded-lg border border-border p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        aria-label="Sincronizar"
      >
        <RefreshCw className={cn("h-3.5 w-3.5", isSyncing && "animate-spin")} />
      </button>

      {toggleLabel && (
        <button
          onClick={onToggle}
          disabled={isToggling}
          className="rounded-lg border border-border px-2.5 py-1 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {toggleLabel}
        </button>
      )}
    </span>
  );
}

// ----- Page -----

export default function MarketplacePage() {
  const { data, isLoading, isError } = useMarketplaceListings();
  const syncAll = useSyncAllListings();
  const syncOne = useSyncListing();
  const updateListing = useUpdateListing();

  const listings = data?.results ?? [];

  const stats = {
    total:     listings.length,
    published: listings.filter((l) => l.status === "PUBLISHED").length,
    pending:   listings.filter((l) => l.status === "PENDING_SYNC").length,
    errors:    listings.filter((l) => l.sync_error_display !== null).length,
  };

  const handleToggle = (listing: MarketplaceListing) => {
    const next: ListingStatus =
      listing.status === "PUBLISHED"
        ? "PAUSED"
        : listing.status === "PAUSED"
        ? "PUBLISHED"
        : "PENDING_SYNC";
    updateListing.mutate({ id: listing.id, status: next });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Marketplace imo.cv
          </h1>
          <p className="text-muted-foreground mt-1">
            Gestão de anúncios publicados no imo.cv
          </p>
        </div>

        <button
          onClick={() => syncAll.mutate()}
          disabled={syncAll.isPending}
          className="flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
        >
          <RefreshCw
            className={cn("h-4 w-4", syncAll.isPending && "animate-spin")}
          />
          {syncAll.isPending ? "A sincronizar…" : "Sincronizar Tudo"}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Total",      value: isLoading ? null : stats.total,     color: "text-foreground" },
          { label: "Publicados", value: isLoading ? null : stats.published, color: "text-green-700" },
          { label: "Pendentes",  value: isLoading ? null : stats.pending,   color: "text-yellow-700" },
          { label: "Com erros",  value: isLoading ? null : stats.errors,    color: "text-orange-600" },
        ].map(({ label, value, color }) => (
          <div
            key={label}
            className="rounded-xl border border-border bg-white px-5 py-4 shadow-sm"
          >
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              {label}
            </p>
            {value === null ? (
              <Skeleton className="mt-2 h-7 w-12" />
            ) : (
              <p className={cn("mt-1 text-2xl font-bold tabular-nums", color)}>
                {value}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
        {isError && (
          <div className="p-6 text-center text-sm text-red-600">
            Erro ao carregar listings. Verifique a ligação à API.
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/40">
                {["Unidade", "Projecto", "Estado", "Último Sync", "Preço Publicado", "Acções"].map(
                  (label) => (
                    <th
                      key={label}
                      className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap"
                    >
                      {label}
                    </th>
                  )
                )}
              </tr>
            </thead>

            {isLoading ? (
              <TableSkeleton />
            ) : (
              <tbody className="divide-y divide-border">
                {listings.length === 0 ? (
                  <tr>
                    <td
                      colSpan={6}
                      className="px-4 py-16 text-center text-muted-foreground text-sm"
                    >
                      Sem anúncios. Crie listagens a partir do módulo de Inventário.
                    </td>
                  </tr>
                ) : (
                  listings.map((listing) => (
                    <tr
                      key={listing.id}
                      className="hover:bg-muted/30 transition-colors"
                    >
                      <td className="px-4 py-3.5 font-mono font-semibold text-foreground">
                        {listing.unit_code}
                      </td>
                      <td className="px-4 py-3.5 text-muted-foreground">
                        {listing.project_name}
                      </td>
                      <td className="px-4 py-3.5">
                        <ListingStatusBadge
                          status={listing.status}
                          syncError={listing.sync_error_display}
                        />
                      </td>
                      <td className="px-4 py-3.5 text-muted-foreground tabular-nums whitespace-nowrap">
                        {listing.last_synced_at
                          ? formatDateTime(listing.last_synced_at)
                          : "Nunca"}
                      </td>
                      <td className="px-4 py-3.5 tabular-nums">
                        {listing.price_override_cve
                          ? formatCve(listing.price_override_cve)
                          : "—"}
                      </td>
                      <td className="px-4 py-3.5">
                        <ListingActions
                          listing={listing}
                          onSync={() => syncOne.mutate(listing.id)}
                          onToggle={() => handleToggle(listing)}
                          isSyncing={syncOne.isPending}
                          isToggling={updateListing.isPending}
                        />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            )}
          </table>
        </div>
      </div>
    </div>
  );
}
