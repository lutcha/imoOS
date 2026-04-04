"use client";

/**
 * Tenant Detail — Super Admin Backoffice
 * Sprint 9 - P03/P04
 * Tabs: Visão Geral | Utilizadores | Configurações
 */
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, Copy, Check, UserX, LogIn, Plus } from "lucide-react";
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
  is_staff: boolean;
  date_joined: string;
}

interface ImpersonateResult {
  access_token: string;
  tenant_schema: string;
  tenant_name: string;
  email: string;
  domain: string | null;
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
              {tenant.domain && <span className="ml-2 text-gray-400">{tenant.domain}</span>}
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
              { id: "users", label: `Utilizadores${users.length > 0 ? ` (${users.length})` : ""}` },
              { id: "settings", label: "Configurações" },
            ] as const
          ).map(({ id: tabId, label }) => (
            <button
              key={tabId}
              onClick={() => setTab(tabId as Tab)}
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

      {tab === "overview" && <OverviewTab tenant={tenant} />}
      {tab === "users" && (
        <UsersTab
          tenantId={id}
          tenantDomain={tenant.domain}
          users={users}
          loading={usersLoading}
          onRefresh={loadUsers}
          onUsersChange={setUsers}
        />
      )}
      {tab === "settings" && <SettingsTab tenant={tenant} />}
    </div>
  );
}

// ---- Tab: Visão Geral ----

function OverviewTab({ tenant }: { tenant: TenantDetail }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
  tenantId,
  tenantDomain,
  users,
  loading,
  onRefresh,
  onUsersChange,
}: {
  tenantId: string;
  tenantDomain: string | null;
  users: TenantUser[];
  loading: boolean;
  onRefresh: () => void;
  onUsersChange: (users: TenantUser[]) => void;
}) {
  const [actionUserId, setActionUserId] = useState<string | null>(null);
  const [impersonating, setImpersonating] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({ email: "", first_name: "", last_name: "", role: "gestor", password: "" });
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  async function handleDeactivate(userId: string, email: string) {
    if (!confirm(`Desactivar utilizador "${email}"? Esta acção pode ser revertida no Django Admin.`)) return;
    setActionUserId(userId);
    try {
      const resp = await superadminFetch(
        `/superadmin/tenants/${tenantId}/users/${userId}/deactivate/`,
        { method: "POST" }
      );
      if (!resp.ok) throw new Error("Operação falhou");
      onUsersChange(users.map((u) => u.id === userId ? { ...u, is_active: false } : u));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro");
    } finally {
      setActionUserId(null);
    }
  }

  async function handleImpersonate(userId: string) {
    setImpersonating(userId);
    try {
      const resp = await superadminFetch(
        `/superadmin/tenants/${tenantId}/impersonate/${userId}/`,
        { method: "POST" }
      );
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error((err as { detail?: string }).detail ?? "Erro de impersonation");
      }
      const result: ImpersonateResult = await resp.json();

      // Open impersonation handoff page in new tab
      const domain = result.domain ?? tenantDomain;
      const url = domain
        ? `https://${domain}/impersonate?token=${encodeURIComponent(result.access_token)}&schema=${result.tenant_schema}`
        : `/impersonate?token=${encodeURIComponent(result.access_token)}&schema=${result.tenant_schema}`;

      window.open(url, "_blank", "noopener,noreferrer");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro");
    } finally {
      setImpersonating(null);
    }
  }

  async function handleCopyToken(userId: string) {
    setImpersonating(userId);
    try {
      const resp = await superadminFetch(
        `/superadmin/tenants/${tenantId}/impersonate/${userId}/`,
        { method: "POST" }
      );
      if (!resp.ok) throw new Error("Erro ao gerar token");
      const result: ImpersonateResult = await resp.json();
      await navigator.clipboard.writeText(result.access_token);
      setCopiedId(userId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro");
    } finally {
      setImpersonating(null);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreateLoading(true);
    setCreateError(null);
    try {
      const resp = await superadminFetch(`/superadmin/tenants/${tenantId}/users/`, {
        method: "POST",
        body: JSON.stringify(createForm),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail ?? "Erro ao criar utilizador");
      setShowCreate(false);
      setCreateForm({ email: "", first_name: "", last_name: "", role: "gestor", password: "" });
      onRefresh();
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Erro");
    } finally {
      setCreateLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Create user form */}
      {showCreate && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Novo Utilizador</h3>
          <form onSubmit={handleCreate} className="grid grid-cols-2 gap-3">
            <input
              required
              type="email"
              placeholder="Email *"
              value={createForm.email}
              onChange={(e) => setCreateForm((f) => ({ ...f, email: e.target.value }))}
              className="col-span-2 rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-red-400"
            />
            <input
              placeholder="Primeiro nome"
              value={createForm.first_name}
              onChange={(e) => setCreateForm((f) => ({ ...f, first_name: e.target.value }))}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-red-400"
            />
            <input
              placeholder="Último nome"
              value={createForm.last_name}
              onChange={(e) => setCreateForm((f) => ({ ...f, last_name: e.target.value }))}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-red-400"
            />
            <select
              value={createForm.role}
              onChange={(e) => setCreateForm((f) => ({ ...f, role: e.target.value }))}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-red-400"
            >
              {["admin", "gestor", "vendedor", "engenheiro", "investidor"].map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
            <input
              required
              type="password"
              placeholder="Palavra-passe *"
              value={createForm.password}
              onChange={(e) => setCreateForm((f) => ({ ...f, password: e.target.value }))}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-red-400"
            />
            {createError && (
              <p className="col-span-2 text-xs text-red-600">{createError}</p>
            )}
            <div className="col-span-2 flex gap-2">
              <button
                type="submit"
                disabled={createLoading}
                className="flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {createLoading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                Criar
              </button>
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:border-gray-300"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">
            Utilizadores {users.length > 0 && `(${users.length})`}
          </h2>
          <div className="flex items-center gap-2">
            <button onClick={onRefresh} className="text-xs text-gray-400 hover:text-gray-600">
              Actualizar
            </button>
            <button
              onClick={() => setShowCreate((v) => !v)}
              className="flex items-center gap-1 text-xs text-red-600 hover:text-red-700 font-medium"
            >
              <Plus className="h-3.5 w-3.5" />
              Convidar
            </button>
          </div>
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
                  {["Email", "Nome", "Role", "Estado", "Desde", "Acções"].map((h) => (
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
                      <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{u.role}</span>
                    </td>
                    <td className="px-5 py-3">
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                          u.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                        }`}
                      >
                        {u.is_active ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-xs text-gray-400">
                      {new Date(u.date_joined).toLocaleDateString("pt-PT")}
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        {/* Impersonate — open in new tab */}
                        {u.is_active && (
                          <button
                            onClick={() => handleImpersonate(u.id)}
                            disabled={impersonating === u.id}
                            title="Abrir sessão como este utilizador"
                            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 disabled:opacity-50"
                          >
                            {impersonating === u.id
                              ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              : <LogIn className="h-3.5 w-3.5" />}
                            Impersonar
                          </button>
                        )}
                        {/* Copy token */}
                        {u.is_active && (
                          <button
                            onClick={() => handleCopyToken(u.id)}
                            disabled={impersonating === u.id}
                            title="Copiar token de acesso"
                            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
                          >
                            {copiedId === u.id
                              ? <Check className="h-3.5 w-3.5 text-green-600" />
                              : <Copy className="h-3.5 w-3.5" />}
                          </button>
                        )}
                        {/* Deactivate */}
                        {u.is_active && (
                          <button
                            onClick={() => handleDeactivate(u.id, u.email)}
                            disabled={actionUserId === u.id}
                            title="Desactivar utilizador"
                            className="text-red-400 hover:text-red-600 disabled:opacity-50"
                          >
                            {actionUserId === u.id
                              ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              : <UserX className="h-3.5 w-3.5" />}
                          </button>
                        )}
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
