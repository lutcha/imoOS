"use client";

/**
 * Super-Admin Dashboard — ImoOS
 * Sprint 9 - P03: Platform overview + tenant list
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { useSuperAdminSession } from "@/hooks/useSuperAdminSession";
import { superadminFetch } from "@/lib/superadmin-client";
import { Plus, RefreshCw } from "lucide-react";

interface Tenant {
  id: string;
  name: string;
  slug: string;
  schema_name: string;
  plan: "starter" | "pro" | "enterprise";
  is_active: boolean;
  country: string;
  domain: string | null;
  user_count: number;
  project_count: number;
  unit_count: number;
  created_at: string;
}

interface PlatformSummary {
  total_tenants: number;
  active_tenants: number;
  inactive_tenants: number;
  tenants_by_plan: Record<string, number>;
  total_resources: { projects: number; units: number; users: number };
}

const PLAN_BADGE: Record<string, string> = {
  starter: "bg-green-100 text-green-800",
  pro: "bg-blue-100 text-blue-800",
  enterprise: "bg-purple-100 text-purple-800",
};

export default function SuperAdminDashboard() {
  const { user } = useSuperAdminSession();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [summary, setSummary] = useState<PlatformSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [tenantsResp, summaryResp] = await Promise.all([
        superadminFetch("/superadmin/tenants/"),
        superadminFetch("/superadmin/tenants/platform_summary/"),
      ]);
      if (!tenantsResp.ok || !summaryResp.ok) throw new Error("Erro ao carregar dados");
      const tenantsData = await tenantsResp.json();
      const summaryData = await summaryResp.json();
      setTenants(tenantsData.results ?? tenantsData);
      setSummary(summaryData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleToggleActive(tenant: Tenant) {
    const action = tenant.is_active ? "suspend" : "activate";
    const label = tenant.is_active ? "suspender" : "activar";
    if (!confirm(`Tem a certeza que deseja ${label} "${tenant.name}"?`)) return;
    try {
      const resp = await superadminFetch(`/superadmin/tenants/${tenant.id}/${action}/`, {
        method: "POST",
      });
      if (!resp.ok) throw new Error("Operação falhou");
      await load();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro");
    }
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tenants</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Bem-vindo, {user?.email}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={load}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Actualizar
          </button>
          <Link
            href="/superadmin/tenants/new"
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            <Plus className="h-4 w-4" />
            Novo Tenant
          </Link>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* KPI Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Total</p>
            <p className="mt-2 text-3xl font-bold text-gray-900">{summary.total_tenants}</p>
            <p className="mt-1 text-xs text-gray-500">
              {summary.active_tenants} activos · {summary.inactive_tenants} inactivos
            </p>
          </div>
          {["starter", "pro", "enterprise"].map((plan) => (
            <div key={plan} className="bg-white rounded-xl border border-gray-200 p-5">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{plan}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {summary.tenants_by_plan?.[plan] ?? 0}
              </p>
              <p className="mt-1 text-xs text-gray-500">tenants</p>
            </div>
          ))}
        </div>
      )}

      {/* Resources */}
      {summary && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Recursos da Plataforma</h2>
          <div className="grid grid-cols-3 gap-6">
            {[
              { label: "Projectos", value: summary.total_resources?.projects ?? 0 },
              { label: "Unidades", value: summary.total_resources?.units ?? 0 },
              { label: "Utilizadores", value: summary.total_resources?.users ?? 0 },
            ].map(({ label, value }) => (
              <div key={label}>
                <p className="text-xs text-gray-500">{label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tenants Table */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">
            Todos os Tenants {tenants.length > 0 && `(${tenants.length})`}
          </h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600" />
          </div>
        ) : tenants.length === 0 ? (
          <div className="py-16 text-center">
            <p className="text-gray-500 text-sm">Sem tenants registados</p>
            <Link
              href="/superadmin/tenants/new"
              className="mt-3 inline-flex items-center gap-1.5 text-sm text-red-600 hover:text-red-700"
            >
              <Plus className="h-4 w-4" />
              Criar primeiro tenant
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100">
              <thead>
                <tr className="bg-gray-50">
                  {["Empresa", "Schema", "Plano", "Recursos", "País", "Estado", "Acções"].map((h) => (
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
                {tenants.map((tenant) => (
                  <tr key={tenant.id} className="hover:bg-gray-50 transition">
                    <td className="px-5 py-4">
                      <div className="font-medium text-gray-900 text-sm">{tenant.name}</div>
                      {tenant.domain && (
                        <div className="text-xs text-gray-400 mt-0.5">{tenant.domain}</div>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <code className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                        {tenant.schema_name}
                      </code>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${PLAN_BADGE[tenant.plan] ?? ""}`}>
                        {tenant.plan}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-xs text-gray-600 space-y-0.5">
                      <div>{tenant.user_count} utilizadores</div>
                      <div>{tenant.project_count} projectos</div>
                      <div>{tenant.unit_count} unidades</div>
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-600">{tenant.country}</td>
                    <td className="px-5 py-4">
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                          tenant.is_active
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {tenant.is_active ? "Activo" : "Suspenso"}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3 text-sm">
                        <Link
                          href={`/superadmin/tenants/${tenant.id}`}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          Detalhes
                        </Link>
                        <button
                          onClick={() => handleToggleActive(tenant)}
                          className={`font-medium ${
                            tenant.is_active
                              ? "text-red-600 hover:text-red-800"
                              : "text-green-600 hover:text-green-800"
                          }`}
                        >
                          {tenant.is_active ? "Suspender" : "Activar"}
                        </button>
                      </div>
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
