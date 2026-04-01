/**
 * Super-Admin Dashboard — ImoOS
 * Sprint 7 - Prompt 02: Admin Backoffice
 * 
 * Features:
 * - Platform KPIs (total tenants, by plan, resources)
 * - Tenant list with actions (suspend/activate)
 * - Quick access to Django Admin, Health Check, Metrics
 */
"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

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
  total_resources: {
    projects: number;
    units: number;
    users: number;
  };
}

export default function SuperAdminDashboard() {
  const { user } = useAuth();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [summary, setSummary] = useState<PlatformSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTenants();
    fetchSummary();
  }, []);

  async function fetchTenants() {
    try {
      const resp = await fetch("/api/v1/tenants/superadmin/tenants/", {
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!resp.ok) throw new Error("Failed to fetch tenants");
      const data = await resp.json();
      setTenants(data.results || data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function fetchSummary() {
    try {
      const resp = await fetch(
        "/api/v1/tenants/superadmin/tenants/platform_summary/",
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!resp.ok) throw new Error("Failed to fetch summary");
      const data = await resp.json();
      setSummary(data);
    } catch (err) {
      console.error("Summary fetch error:", err);
    }
  }

  async function handleSuspend(tenantId: string) {
    if (!confirm("Tem a certeza que deseja suspender este tenant?")) return;

    try {
      const resp = await fetch(
        `/api/v1/tenants/superadmin/tenants/${tenantId}/suspend/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!resp.ok) throw new Error("Failed to suspend tenant");
      await fetchTenants();
      await fetchSummary();
      alert("Tenant suspenso com sucesso");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao suspender tenant");
    }
  }

  async function handleActivate(tenantId: string) {
    try {
      const resp = await fetch(
        `/api/v1/tenants/superadmin/tenants/${tenantId}/activate/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!resp.ok) throw new Error("Failed to activate tenant");
      await fetchTenants();
      await fetchSummary();
      alert("Tenant activado com sucesso");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao activar tenant");
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Erro: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* KPI Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Total Tenants</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {summary.total_tenants}
            </div>
            <div className="mt-2 text-sm text-gray-600">
              {summary.active_tenants} activos • {summary.inactive_tenants} inactivos
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Starter</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {summary.tenants_by_plan?.starter || 0}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Pro</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {summary.tenants_by_plan?.pro || 0}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Enterprise</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {summary.tenants_by_plan?.enterprise || 0}
            </div>
          </div>
        </div>
      )}

      {/* Resources Summary */}
      {summary && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Recursos da Plataforma
          </h2>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <div className="text-sm text-gray-500">Projectos</div>
              <div className="text-2xl font-bold text-gray-900">
                {summary.total_resources?.projects || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Unidades</div>
              <div className="text-2xl font-bold text-gray-900">
                {summary.total_resources?.units || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Utilizadores</div>
              <div className="text-2xl font-bold text-gray-900">
                {summary.total_resources?.users || 0}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tenants Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Tenants</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Empresa
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Schema
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Plano
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  País
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recursos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acções
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tenants.map((tenant) => (
                <tr key={tenant.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {tenant.name}
                    </div>
                    {tenant.domain && (
                      <div className="text-sm text-gray-500">
                        {tenant.domain}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {tenant.schema_name}
                    </code>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        tenant.plan === "starter"
                          ? "bg-green-100 text-green-800"
                          : tenant.plan === "pro"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-purple-100 text-purple-800"
                      }`}
                    >
                      {tenant.plan}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {tenant.country}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">
                      <div>👥 {tenant.user_count}</div>
                      <div>🏢 {tenant.project_count}</div>
                      <div>🏠 {tenant.unit_count}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {tenant.is_active ? (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                        Activo
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                        Suspenso
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {tenant.is_active ? (
                      <button
                        onClick={() => handleSuspend(tenant.id)}
                        className="text-red-600 hover:text-red-900 mr-3"
                      >
                        Suspender
                      </button>
                    ) : (
                      <button
                        onClick={() => handleActivate(tenant.id)}
                        className="text-green-600 hover:text-green-900 mr-3"
                      >
                        Activar
                      </button>
                    )}
                    <a
                      href={`https://${tenant.slug}.imos.cv`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Visitar
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {tenants.length === 0 && (
          <div className="px-6 py-12 text-center text-gray-500">
            Sem tenants registados
          </div>
        )}
      </div>
    </div>
  );
}
