"use client";

/**
 * Tenant Detail — Super Admin Backoffice
 * Sprint 9 - P03
 * Tabs: Visão Geral | Utilizadores | Configurações
 */
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";
import { superadminFetch } from "@/lib/superadmin-client";

// ---- Types ----

interface TenantDetail {
  id: string;
  name: string;
  slug: string;
  schema_name: string;
  plan: "starter" | "pro" | "enterprise";
  is_active: boolean;
  country: string;
  currency: string;
  timezone: string;
  domain: string | null;
  user_count: number;
  project_count: number;
  unit_count: number;
  created_at: string;
  updated_at: string;
}

interface TenantUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  date_joined: string;
}

type Tab = "overview" | "users" | "settings";

const PLAN_BADGE: Record<string, string> = {
  starter: "bg-green-100 text-green-800",
  pro: "bg-blue-100 text-blue-800",
  enterprise: "bg-purple-100 text-purple-800",
};

// ---- Page ----

export default function TenantDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("overview");
  const [tenant, setTenant] = useState<TenantDetail | null>(null);
  const [users, setUsers] = useState<TenantUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [usersLoading, setUsersLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadTenant() {
    setLoading(true);
    setError(null);
    try {
      const resp = await superadminFetch(`/superadmin/tenants/${id}/`);
      if (!resp.ok) {
        if (resp.status === 404) { router.replace("/superadmin"); return; }
        throw new Error("Erro ao carregar tenant");
      }
      setTenant(await resp.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
    }
  }

  async function loadUsers() {
    setUsersLoading(true);
    try {
      const resp = await superadminFetch(`/superadmin/tenants/${id}/users/`);
      if (!resp.ok) throw new Error("Erro ao carregar utilizadores");
      const data = await resp.json();
      setUsers(data.results ?? data);
    } catch {
      setUsers([]);
    } finally {
      setUsersLoading(false);
    }
  }

  useEffect(() => { loadTenant(); }, [id]);

  useEffect(() => {
    if (tab === "users" && users.length === 0) loadUsers();
  }, [tab]);

  async function handleToggleActive() {
    if (!tenant) return;
    const action = tenant.is_active ? "suspend" : "activate";
    const label = tenant.is_active ? "suspender" : "activar";
    if (!confirm(`Confirma que deseja ${label} "${tenant.name}"?`)) return;
    setActionLoading(true);
    try {
      const resp = await superadminFetch(`/superadmin/tenants/${id}/${action}/`, { method: "POST" });
      if (!resp.ok) throw new Error("Operação falhou");
      await loadTenant();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-red-600" />
      </div>
    );
  }

  if (error || !tenant) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
        {error ?? "Tenant não encontrado"}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb + Header */}
      <div>
        <Link
          href="/superadmin"
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Tenants
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{tenant.name}</h1>
              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${PLAN_BADGE[tenant.plan]}`}>
                {tenant.plan}
              </span>
              <span
                className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                  tenant.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                }`}
              >
                {tenant.is_active ? "Activo" : "Suspenso"}
              </span>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">{tenant.schema_name}</code>
              {tenant.domain && (
                <span className="ml-2 text-gray-400">{tenant.domain}</span>
              )}
            </p>
          </div>

          <button
            onClick={handleToggleActive}
            disabled={actionLoading}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border transition disabled:opacity-50 ${
              tenant.is_active
                ? "border-red-300 text-red-700 hover:bg-red-50"
                : "border-green-300 text-green-700 hover:bg-green-50"
            }`}
          >
            {actionLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            {tenant.is_active ? "Suspender Tenant" : "Activar Tenant"}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex gap-6">
          {(
            [
              { id: "overview", label: "Visão Geral" },
              { id: "users", label: "Utilizadores" },
              { id: "settings", label: "Configurações" },
            ] as const
          ).map(({ id: tabId, label }) => (
            <button
              key={tabId}
              onClick={() => setTab(tabId)}
              className={`py-3 text-sm font-medium border-b-2 transition ${
                tab === tabId
                  ? "border-red-600 text-red-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      {tab === "overview" && <OverviewTab tenant={tenant} />}
      {tab === "users" && <UsersTab users={users} loading={usersLoading} onRefresh={loadUsers} />}
      {tab === "settings" && <SettingsTab tenant={tenant} />}
    </div>
  );
}

// ---- Tab: Visão Geral ----

function OverviewTab({ tenant }: { tenant: TenantDetail }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* KPIs */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Recursos</h2>
        <div className="space-y-3">
          {[
            { label: "Utilizadores", value: tenant.user_count },
            { label: "Projectos", value: tenant.project_count },
            { label: "Unidades", value: tenant.unit_count },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between items-center">
              <span className="text-sm text-gray-600">{label}</span>
              <span className="text-sm font-semibold text-gray-900">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Informação</h2>
        <dl className="space-y-3">
          {[
            { label: "ID", value: tenant.id },
            { label: "Slug", value: tenant.slug },
            { label: "País", value: tenant.country },
            { label: "Moeda", value: tenant.currency },
            { label: "Timezone", value: tenant.timezone },
            {
              label: "Criado em",
              value: new Date(tenant.created_at).toLocaleDateString("pt-PT", {
                day: "2-digit", month: "long", year: "numeric",
              }),
            },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between gap-4">
              <dt className="text-sm text-gray-500 shrink-0">{label}</dt>
              <dd className="text-sm text-gray-900 text-right font-mono truncate">{value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}

// ---- Tab: Utilizadores ----

function UsersTab({
  users,
  loading,
  onRefresh,
}: {
  users: TenantUser[];
  loading: boolean;
  onRefresh: () => void;
}) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-700">
          Utilizadores {users.length > 0 && `(${users.length})`}
        </h2>
        <button
          onClick={onRefresh}
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          Actualizar
        </button>
      </div>

      {users.length === 0 ? (
        <div className="py-12 text-center text-sm text-gray-400">
          Sem utilizadores neste tenant
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-100">
            <thead className="bg-gray-50">
              <tr>
                {["Email", "Nome", "Role", "Estado", "Desde"].map((h) => (
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
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 text-sm text-gray-900">{u.email}</td>
                  <td className="px-5 py-3 text-sm text-gray-600">{u.full_name || "—"}</td>
                  <td className="px-5 py-3">
                    <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                      {u.role || "gestor"}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        u.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {u.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-xs text-gray-400">
                    {new Date(u.date_joined).toLocaleDateString("pt-PT")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ---- Tab: Configurações ----

function SettingsTab({ tenant }: { tenant: TenantDetail }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 max-w-lg">
      <h2 className="text-sm font-semibold text-gray-700 mb-4">Configurações do Tenant</h2>
      <p className="text-sm text-gray-500">
        Gestão de planos e limites disponível na próxima sprint (P06).
      </p>
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-400">
          Tenant ID: <code className="font-mono">{tenant.id}</code>
        </p>
      </div>
    </div>
  );
}
