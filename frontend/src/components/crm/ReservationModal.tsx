"use client";

import { useState } from "react";
import { X, Loader2, AlertCircle } from "lucide-react";
import { useUnits } from "@/hooks/useUnits";
import apiClient from "@/lib/api-client";
import { formatCve } from "@/lib/format";
import type { Lead } from "@/hooks/useLeads";

interface ReservationModalProps {
    lead: Lead | null;
    onClose: () => void;
    onSuccess: () => void;
}

export function ReservationModal({ lead, onClose, onSuccess }: ReservationModalProps) {
    const [unitId, setUnitId] = useState("");
    const [deposit, setDeposit] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load available units
    const { data: unitsPage, isLoading: unitsLoading } = useUnits({
        status: "AVAILABLE",
        page_size: 100,
    });
    const units = unitsPage?.results ?? [];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!lead || !unitId || !deposit) return;

        setIsSubmitting(true);
        setError(null);

        try {
            await apiClient.post("/crm/reservations/create-reservation/", {
                unit_id: unitId,
                lead_id: lead.id,
                deposit_amount_cve: parseFloat(deposit),
                expires_at: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(), // 48h
            });
            onSuccess();
        } catch (err: unknown) {
            if (err && typeof err === "object" && "response" in err && (err.response as { status: number }).status === 409) {
                setError("Esta unidade já se encontra reservada ou indisponível.");
            } else {
                setError("Erro ao criar reserva. Por favor, tente novamente.");
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!lead) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
            <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-slate-50/50">
                    <div>
                        <h2 className="text-lg font-bold text-foreground">Reservar Unidade</h2>
                        <p className="text-xs text-muted-foreground">Lead: {lead.first_name} {lead.last_name}</p>
                    </div>
                    <button onClick={onClose} className="rounded-lg p-2 hover:bg-muted transition-colors">
                        <X className="h-5 w-5 text-muted-foreground" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-5">
                    {error && (
                        <div className="flex items-start space-x-2 rounded-xl bg-red-50 p-3 text-red-700 border border-red-100 text-xs">
                            <AlertCircle className="h-4 w-4 shrink-0" />
                            <span>{error}</span>
                        </div>
                    )}

                    <div className="space-y-1.5">
                        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                            Unidade Disponível
                        </label>
                        <select
                            value={unitId}
                            onChange={(e) => setUnitId(e.target.value)}
                            required
                            className="w-full rounded-xl border border-border bg-slate-50 px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium h-11"
                        >
                            <option value="">Seleccione uma unidade…</option>
                            {units.map((u) => (
                                <option key={u.id} value={u.id}>
                                    {u.code} — {u.unit_type_detail?.name} ({formatCve(u.pricing?.final_price_cve ?? "0")})
                                </option>
                            ))}
                        </select>
                        {unitsLoading && <p className="text-[10px] text-muted-foreground animate-pulse ml-1">Carregando unidades…</p>}
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                            Valor do Depósito (CVE)
                        </label>
                        <input
                            type="number"
                            value={deposit}
                            onChange={(e) => setDeposit(e.target.value)}
                            placeholder="Ex: 50000"
                            required
                            className="w-full rounded-xl border border-border bg-slate-50 px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium h-11"
                        />
                    </div>

                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={isSubmitting || unitsLoading}
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
                        <p className="text-[10px] text-center text-muted-foreground mt-4">
                            A unidade ficará bloqueada por 48 horas após a reserva.
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
}
