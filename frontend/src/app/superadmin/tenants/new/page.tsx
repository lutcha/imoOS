"use client";

/**
 * Criar Novo Tenant — Super Admin Backoffice
 * Sprint 9 - P03
 * POST /api/v1/superadmin/tenants/provision/
 */
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";
import { superadminFetch } from "@/lib/superadmin-client";

const PLANS = [
  { value: "starter", label: "Starter", description: "Até 3 projectos · 150 unidades · 10 utilizadores" },
  { value: "pro", label: "Pro", description: "Até 20 projectos · 1 000 unidades · 50 utilizadores" },
  { value: "enterprise", label: "Enterprise", description: "Sem limites" },
];

const COUNTRIES = [
  { code: "CV", label: "Cabo Verde" },
  { code: "AO", label: "Angola" },
  { code: "SN", label: "Senegal" },
];

const BASE_DOMAIN = "proptech.cv";

function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 50);
}

export default function NewTenantPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [schemaManual, setSchemaManual] = useState(false);

  const [form, setForm] = useState({
    name: "",
    schema_name: "",
    domain: "",
    plan: "starter",
    contact_email: "",
    country: "CV",
  });

  function handleNameChange(value: string) {
    const generated = slugify(value);
    setForm((f) => ({
      ...f,
      name: value,
      schema_name: schemaManual ? f.schema_name : generated,
      domain: schemaManual ? f.domain : (generated ? `${generated.replace(/_/g, "-")}.${BASE_DOMAIN}` : ""),
    }));
  }

  function handleSchemaChange(value: string) {
    setSchemaManual(true);
    const safe = value.toLowerCase().replace(/[^a-z0-9_]/g, "").slice(0, 50);
    setForm((f) => ({
      ...f,
      schema_name: safe,
      domain: safe ? `${safe.replace(/_/g, "-")}.${BASE_DOMAIN}` : "",
    }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldErrors({});
    setIsLoading(true);

    try {
      const resp = await superadminFetch("/superadmin/tenants/provision/", {
        method: "POST",
        body: JSON.stringify(form),
      });

      const data = await resp.json();

      if (!resp.ok) {
        if (typeof data === "object" && !data.detail) {
          // Field-level validation errors
          const errs: Record<string, string> = {};
          for (const [key, val] of Object.entries(data)) {
            errs[key] = Array.isArray(val) ? (val as string[])[0] : String(val);
          }
          setFieldErrors(errs);
        } else {
          setError(data.detail ?? "Erro ao criar tenant");
        }
        return;
      }

      router.push(`/superadmin/tenants/${data.tenant_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro de ligação");
    } finally {
      setIsLoading(false);
    }
  }

  const schemaValid = /^[a-z][a-z0-9_]{2,49}$/.test(form.schema_name);

  return (
    <div className="max-w-2xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <Link
          href="/superadmin"
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="h-4 w-4" />
          Tenants
        </Link>
        <span className="text-gray-300">/</span>
        <span className="text-sm text-gray-700 font-medium">Novo Tenant</span>
      </div>

      <h1 className="text-xl font-bold text-gray-900 mb-6">Criar Novo Tenant</h1>

      {error && (
        <div className="mb-5 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5 bg-white rounded-xl border border-gray-200 p-6">
        {/* Nome */}
        <Field
          label="Nome da Empresa"
          error={fieldErrors.name}
          required
        >
          <input
            type="text"
            required
            value={form.name}
            onChange={(e) => handleNameChange(e.target.value)}
            placeholder="Tecnicil Imobiliário"
            className={inputCls(!!fieldErrors.name)}
          />
        </Field>

        {/* Schema */}
        <Field
          label="Schema (identificador único)"
          error={fieldErrors.schema_name}
          hint={
            form.schema_name
              ? schemaValid
                ? "✓ Válido"
                : "Mín. 3 chars · só minúsculas, dígitos, underscores"
              : "Gerado automaticamente a partir do nome"
          }
          hintOk={schemaValid && !!form.schema_name}
          required
        >
          <input
            type="text"
            required
            value={form.schema_name}
            onChange={(e) => handleSchemaChange(e.target.value)}
            placeholder="tecnicil_imobiliario"
            className={inputCls(!!fieldErrors.schema_name)}
          />
        </Field>

        {/* Domain preview */}
        <Field label="Domínio" error={fieldErrors.domain} required>
          <input
            type="text"
            required
            value={form.domain}
            onChange={(e) => setForm((f) => ({ ...f, domain: e.target.value }))}
            placeholder={`empresa.${BASE_DOMAIN}`}
            className={inputCls(!!fieldErrors.domain)}
          />
          {form.domain && (
            <p className="mt-1 text-xs text-gray-400">
              URL: <span className="font-mono">https://{form.domain}</span>
            </p>
          )}
        </Field>

        {/* Plano */}
        <Field label="Plano" error={fieldErrors.plan} required>
          <div className="grid grid-cols-3 gap-3">
            {PLANS.map((p) => (
              <label
                key={p.value}
                className={`cursor-pointer rounded-lg border p-3 transition ${
                  form.plan === p.value
                    ? "border-red-500 bg-red-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <input
                  type="radio"
                  name="plan"
                  value={p.value}
                  checked={form.plan === p.value}
                  onChange={() => setForm((f) => ({ ...f, plan: p.value }))}
                  className="sr-only"
                />
                <p className="text-sm font-semibold text-gray-900">{p.label}</p>
                <p className="text-xs text-gray-500 mt-1 leading-snug">{p.description}</p>
              </label>
            ))}
          </div>
        </Field>

        {/* País */}
        <Field label="País" error={fieldErrors.country} required>
          <select
            value={form.country}
            onChange={(e) => setForm((f) => ({ ...f, country: e.target.value }))}
            className={inputCls(false)}
          >
            {COUNTRIES.map((c) => (
              <option key={c.code} value={c.code}>
                {c.label}
              </option>
            ))}
          </select>
        </Field>

        {/* Email de contacto */}
        <Field label="Email de Contacto" error={fieldErrors.contact_email}>
          <input
            type="email"
            value={form.contact_email}
            onChange={(e) => setForm((f) => ({ ...f, contact_email: e.target.value }))}
            placeholder="admin@empresa.cv"
            className={inputCls(!!fieldErrors.contact_email)}
          />
        </Field>

        {/* Actions */}
        <div className="flex items-center gap-3 pt-2 border-t border-gray-100">
          <button
            type="submit"
            disabled={isLoading || !schemaValid}
            className="flex items-center gap-2 px-5 py-2.5 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            {isLoading ? "A criar..." : "Criar Tenant"}
          </button>
          <Link
            href="/superadmin"
            className="px-4 py-2.5 text-sm text-gray-600 hover:text-gray-800 border border-gray-200 rounded-lg hover:border-gray-300 transition"
          >
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}

// ---- Helpers ----

function inputCls(hasError: boolean) {
  return [
    "w-full rounded-lg border px-3.5 py-2.5 text-sm text-gray-900 outline-none transition",
    hasError
      ? "border-red-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
      : "border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-500/20",
  ].join(" ");
}

function Field({
  label,
  error,
  hint,
  hintOk,
  required,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  hintOk?: boolean;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
      {!error && hint && (
        <p className={`mt-1 text-xs ${hintOk ? "text-green-600" : "text-gray-400"}`}>{hint}</p>
      )}
    </div>
  );
}
