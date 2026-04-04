"use client";

/**
 * Registration Approval Queue — Super Admin Backoffice
 * Sprint 9 - P05
 *
 * Shows all self-service tenant registrations.
 * Staff can approve (trigger provisioning) or reject with a reason.
 */
import { useEffect, useState } from "react";
import { Loader2, CheckCircle, XCircle, Clock, RefreshCw, ChevronDown } from "lucide-react";
import { superadminFetch } from "@/lib/superadmin-client";

// ---- Types ----

interface Registration {
  id: string;
  company_name: string;
  subdomain: string;
  plan: string;
  plan_display: string;
  contact_email: string;
  contact_name: string;
  contact_phone: string;
  country: string;
  status: string;
  status_display: string;
  error_message: string;
  is_token_expired: boolean;
  created_at: string;
  provisioned_at: string | null;
}

// ---- Constants ----

const STATUS_BADGE: Record<string, string> = {
  PENDING_VERIFICATION: "bg-yellow-100 text-yellow-800",
  VERIFIED:             "bg-blue-100 text-blue-800",
  PROVISIONING:         "bg-purple-100 text-purple-800",
  ACTIVE:               "bg-green-100 text-green-800",
  REJECTED:             "bg-red-100 text-red-800",
};

const STATUS_OPTIONS = [
  { value: "", label: "Todos" },
  { value: "PENDING_VERIFICATION", label: "Pendente" },
  { value: "VERIFIED", label: "Verificado" },
  { value: "PROVISIONING", label: "A Provisionar" },
  { value: "ACTIVE", label: "Activo" },
  { value: "REJECTED", label: "Rejeitado" },
];

const PLAN_BADGE: Record<string, string> = {
  starter:    "bg-green-100 text-green-700",
  pro:        "bg-blue-100 text-blue-700",
  enterprise: "bg-purple-100 text-purple-700",
};

// ---- Page ----

export default function RegistrationsPage() {
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [actionId, setActionId] = useState<string | null>(null);
  const [rejectId, setRejectId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState("");

  async function load(filter = statusFilter) {
    setLoading(true);
    setError(null);
    try {
      const qs = filter ? `?status=${encodeURIComponent(filter)}` : "";
      const resp = await superadminFetch(`/superadmin/registrations/${qs}`);
      if (!resp.ok) throw new Error("Erro ao carregar registos");
      const data = await resp.json();
      setRegistrations(data.results ?? data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  function handleFilterChange(value: string) {
    setStatusFilter(value);
    load(value);
  }

  async function handleApprove(reg: Registration) {
    if (!confirm(`Aprovar "${reg.company_name}" e iniciar provisionamento?`)) return;
    setActionId(reg.id);
    try {
      const resp = await superadminFetch(`/superadmin/registrations/${reg.id}/approve/`, {
        method: "POST",
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail ?? "Erro ao aprovar");
      await load();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro");
    } finally {
      setActionId(null);
    }
  }

  async function handleReject(reg: Registration) {
    setActionId(reg.id);
    try {
      const resp = await superadminFetch(`/superadmin/registrations/${reg.id}/reject/`, {
        method: "POST",
        body: JSON.stringify({ reason: rejectReason || "Rejeitado pelo administrador." }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail ?? "Erro ao rejeitar");
      setRejectId(null);
      setRejectReason("");
      await load();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro");
    } finally {
      setActionId(null);
    }
  }

  // Counts by status for the summary bar
  const counts = registrations.reduce<Record<string, number>>((acc, r) => {
    acc[r.status] = (acc[r.status] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Registos</h1>
          <p className="text-sm text-gray-500 mt-1">
            Fila de aprovação de novas empresas
          </p>
        </div>
        <button
          onClick={() => load()}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:border-gray-300 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Actualizar
        </button>
      </div>

      {/* Summary chips */}
      {!loading && (
        <div className="flex flex-wrap gap-2">
          {STATUS_OPTIONS.slice(1).map(({ value, label }) => (
            <button
              key={value}
              onClick={() => handleFilterChange(statusFilter === value ? "" : value)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition ${
                statusFilter === value
                  ? "bg-gray-900 text-white border-gray-900"
                  : "bg-white text-gray-600 border-gray-200 hover:border-gray-300"
              }`}
            >
              {label}
              {counts[value] !== undefined && (
                <span className={`ml-0.5 ${statusFilter === value ? "text-gray-300" : "text-gray-400"}`}>
                  {counts[value]}
                </span>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
          </div>
        ) : registrations.length === 0 ? (
          <div className="py-16 text-center text-sm text-gray-400">
            {statusFilter ? "Sem registos com este estado." : "Sem registos."}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100">
              <thead className="bg-gray-50">
                <tr>
                  {["Empresa", "Subdomínio", "Plano", "Contacto", "Estado", "Data", "Acções"].map((h) => (
                    <th
                      key={h}
                      className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {registrations.map((reg) => (
                  <>
                    <tr key={reg.id} className="hover:bg-gray-50">
                      <td className="px-5 py-3">
                        <div className="text-sm font-medium text-gray-900">{reg.company_name}</div>
                        <div className="text-xs text-gray-400">{reg.country}</div>
                      </td>
                      <td className="px-5 py-3 text-sm font-mono text-gray-700">
                        {reg.subdomain}
                      </td>
                      <td className="px-5 py-3">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${PLAN_BADGE[reg.plan] ?? "bg-gray-100 text-gray-600"}`}>
                          {reg.plan_display}
                        </span>
                      </td>
                      <td className="px-5 py-3">
                        <div className="text-sm text-gray-700">{reg.contact_name}</div>
                        <div className="text-xs text-gray-400">{reg.contact_email}</div>
                        {reg.contact_phone && (
                          <div className="text-xs text-gray-400">{reg.contact_phone}</div>
                        )}
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex flex-col gap-1">
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full w-fit ${STATUS_BADGE[reg.status] ?? "bg-gray-100 text-gray-600"}`}>
                            {reg.status_display}
                          </span>
                          {reg.is_token_expired && reg.status === "PENDING_VERIFICATION" && (
                            <span className="text-xs text-orange-500 flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              Token expirado
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3 text-xs text-gray-400 whitespace-nowrap">
                        {new Date(reg.created_at).toLocaleDateString("pt-PT")}
                        {reg.provisioned_at && (
                          <div className="text-green-600">
                            ✓ {new Date(reg.provisioned_at).toLocaleDateString("pt-PT")}
                          </div>
                        )}
                      </td>
                      <td className="px-5 py-3">
                        {reg.status !== "ACTIVE" && reg.status !== "PROVISIONING" && (
                          <div className="flex items-center gap-2">
                            {/* Approve */}
                            {reg.status !== "REJECTED" && (
                              <button
                                onClick={() => handleApprove(reg)}
                                disabled={actionId === reg.id}
                                title="Aprovar e provisionar"
                                className="flex items-center gap-1 text-xs text-green-700 hover:text-green-900 disabled:opacity-50"
                              >
                                {actionId === reg.id
                                  ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                  : <CheckCircle className="h-3.5 w-3.5" />}
                                Aprovar
                              </button>
                            )}
                            {/* Reject */}
                            <button
                              onClick={() => setRejectId(rejectId === reg.id ? null : reg.id)}
                              disabled={actionId === reg.id}
                              title="Rejeitar"
                              className="flex items-center gap-1 text-xs text-red-600 hover:text-red-800 disabled:opacity-50"
                            >
                              <XCircle className="h-3.5 w-3.5" />
                              Rejeitar
                              <ChevronDown className={`h-3 w-3 transition-transform ${rejectId === reg.id ? "rotate-180" : ""}`} />
                            </button>
                          </div>
                        )}
                        {(reg.status === "ACTIVE" || reg.status === "PROVISIONING") && (
                          <span className="text-xs text-gray-400">—</span>
                        )}
                      </td>
                    </tr>
                    {/* Inline reject form */}
                    {rejectId === reg.id && (
                      <tr key={`${reg.id}-reject`} className="bg-red-50">
                        <td colSpan={7} className="px-5 py-3">
                          <div className="flex items-center gap-3">
                            <input
                              autoFocus
                              type="text"
                              placeholder="Motivo da rejeição (opcional)"
                              value={rejectReason}
                              onChange={(e) => setRejectReason(e.target.value)}
                              className="flex-1 rounded-lg border border-red-200 bg-white px-3 py-1.5 text-sm outline-none focus:border-red-400"
                            />
                            <button
                              onClick={() => handleReject(reg)}
                              disabled={actionId === reg.id}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 disabled:opacity-50"
                            >
                              {actionId === reg.id && <Loader2 className="h-3 w-3 animate-spin" />}
                              Confirmar Rejeição
                            </button>
                            <button
                              onClick={() => { setRejectId(null); setRejectReason(""); }}
                              className="text-xs text-gray-500 hover:text-gray-700"
                            >
                              Cancelar
                            </button>
                          </div>
                          {reg.error_message && (
                            <p className="mt-1 text-xs text-red-500">
                              Motivo anterior: {reg.error_message}
                            </p>
                          )}
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
