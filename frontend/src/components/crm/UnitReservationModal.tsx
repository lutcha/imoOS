"use client";

/**
 * UnitReservationModal — ImoOS
 * Opens from the Units tab on /projects/[id].
 * Flow: unit is already known → user selects a lead + enters deposit.
 * Contrast with ReservationModal (lead-first, unit is selected inside).
 */
import { useState } from "react";
import { X, Loader2, AlertCircle, Home } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useLeads } from "@/hooks/useLeads";
import { useTenant } from "@/contexts/TenantContext";
import { unitKeys, type Unit } from "@/hooks/useUnits";
import { formatCve, formatArea } from "@/lib/format";

interface UnitReservationModalProps {
  unit: Unit | null;
  onClose: () => void;
  onSuccess: () => void;
}

export function UnitReservationModal({
  unit,
  onClose,
  onSuccess,
}: UnitReservationModalProps) {
  const queryClient = useQueryClient();
  const { schema } = useTenant();

  const [leadId, setLeadId] = useState("");
  const [deposit, setDeposit] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load active leads — exclude WON and LOST
  const { data: leadsPage, isLoading: leadsLoading } = useLeads({
    page_size: 100,
  });
  const leads = (leadsPage?.results ?? []).filter(
    (l) => l.status !== "WON" && l.status !== "LOST"
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!unit || !leadId || !deposit) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await apiClient.post("/crm/reservations/create-reservation/", {
        unit_id: unit.id,
        lead_id: leadId,
        deposit_amount_cve: parseFloat(deposit),
      });

      // Invalidate units so the table reflects the new RESERVED status
      queryClient.invalidateQueries({ queryKey: unitKeys.all(schema) });

      onSuccess();
    } catch (err: unknown) {
      const status = (err as { response?: { status: number } })?.response?.status;
      if (status === 400) {
        const detail = (err as { response?: { data?: { detail?: string } } })
          ?.response?.data?.detail;
        setError(detail ?? "Unidade já reservada ou indisponível.");
      } else {
        setError("Erro ao criar reserva. Por favor, tente novamente.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!unit) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-slate-50/50">
          <div>
            <h2 className="text-lg font-bold text-foreground">Reservar Unidade</h2>
            <p className="text-xs text-muted-foreground">
              Unidade:{" "}
              <span className="font-mono font-bold text-foreground">
                {unit.code}
              </span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 hover:bg-muted transition-colors"
          >
            <X className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>

        {/* Unit summary */}
        <div className="mx-6 mt-5 flex items-center space-x-3 rounded-xl border border-border bg-slate-50 px-4 py-3">
          <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
            <Home className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-bold text-foreground truncate">
              {unit.unit_type_detail?.name ?? "—"} · Piso {unit.floor_number}
            </p>
            <p className="text-xs text-muted-foreground">
              {formatArea(unit.area_bruta)} ·{" "}
              <span className="font-bold text-foreground">
                {unit.pricing ? formatCve(unit.pricing.final_price_cve) : "—"}
              </span>
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="flex items-start space-x-2 rounded-xl bg-red-50 p-3 text-red-700 border border-red-100 text-xs">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Lead selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
              Lead / Comprador
            </label>
            <select
              value={leadId}
              onChange={(e) => setLeadId(e.target.value)}
              required
              className="w-full rounded-xl border border-border bg-slate-50 px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium h-11"
            >
              <option value="">Seleccione um lead…</option>
              {leads.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.first_name} {l.last_name}
                  {l.phone ? ` · ${l.phone}` : ""}
                </option>
              ))}
            </select>
            {leadsLoading && (
              <p className="text-[10px] text-muted-foreground animate-pulse ml-1">
                Carregando leads…
              </p>
            )}
            {!leadsLoading && leads.length === 0 && (
              <p className="text-[10px] text-amber-600 ml-1">
                Sem leads activos. Crie um lead no CRM primeiro.
              </p>
            )}
          </div>

          {/* Deposit */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
              Valor do Depósito (CVE)
            </label>
            <input
              type="number"
              min="0"
              step="1"
              value={deposit}
              onChange={(e) => setDeposit(e.target.value)}
              placeholder="Ex: 50 000"
              required
              className="w-full rounded-xl border border-border bg-slate-50 px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium h-11"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isSubmitting || leadsLoading || leads.length === 0}
              className="w-full rounded-xl bg-primary px-4 py-3 text-sm font-bold text-white shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  A processar…
                </>
              ) : (
                "Confirmar Reserva"
              )}
            </button>
            <p className="text-[10px] text-center text-muted-foreground mt-3">
              A unidade ficará bloqueada durante 48 horas.
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
