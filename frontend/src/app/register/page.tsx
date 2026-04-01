/**
 * Tenant Registration Page — ImoOS
 * Sprint 7 - Prompt 03: Self-Service Onboarding
 * 
 * Multi-step form:
 * 1. Company Info
 * 2. Contact Details
 * 3. Plan Selection
 * 4. Confirmation
 */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type Plan = "starter" | "pro" | "enterprise";
type Country = "CV" | "AO" | "SN";

interface FormData {
  companyName: string;
  subdomain: string;
  plan: Plan;
  contactEmail: string;
  contactName: string;
  contactPhone: string;
  country: Country;
}

const PLAN_FEATURES = {
  starter: {
    name: "Starter",
    price: "Gratuito",
    projects: 3,
    units: 100,
    users: 5,
    color: "green",
  },
  pro: {
    name: "Pro",
    price: "€49/mês",
    projects: 15,
    units: 1000,
    users: 50,
    color: "blue",
  },
  enterprise: {
    name: "Enterprise",
    price: "Contactar",
    projects: "Ilimitados",
    units: "Ilimitados",
    users: "Ilimitados",
    color: "purple",
  },
};

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [registrationToken, setRegistrationToken] = useState<string | null>(null);

  const [formData, setFormData] = useState<FormData>({
    companyName: "",
    subdomain: "",
    plan: "starter",
    contactEmail: "",
    contactName: "",
    contactPhone: "",
    country: "CV",
  });

  const [subdomainValid, setSubdomainValid] = useState<boolean | null>(null);
  const [subdomainChecking, setSubdomainChecking] = useState(false);

  function updateField(field: keyof FormData, value: string) {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }

  async function checkSubdomain(subdomain: string) {
    if (subdomain.length < 3) {
      setSubdomainValid(null);
      return;
    }

    setSubdomainChecking(true);
    // Debounce
    setTimeout(async () => {
      try {
        const resp = await fetch(
          `/api/v1/register/?subdomain_check=${subdomain}`,
          { method: "HEAD" }
        );
        setSubdomainValid(resp.ok);
      } catch {
        setSubdomainValid(null);
      } finally {
        setSubdomainChecking(false);
      }
    }, 500);
  }

  async function handleSubmit() {
    setLoading(true);
    setError(null);

    try {
      const resp = await fetch("/api/v1/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(
          Object.values(data as Record<string, string[]>).flat()[0] ||
            "Erro ao registar"
        );
      }

      setSubmitted(true);
      setRegistrationToken(data.verification_token || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-6xl mb-4">📧</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Verifique o seu email
          </h1>
          <p className="text-gray-600 mb-6">
            Enviámos um email de verificação para{" "}
            <strong>{formData.contactEmail}</strong>
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              Clique no link no email para activar a sua conta. O link expira em
              48 horas.
            </p>
          </div>
          <button
            onClick={() => router.push("/login")}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Ir para Login
          </button>
          <p className="text-xs text-gray-500 mt-4">
            Não recebeu o email? Verifique a pasta de spam.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    step >= s
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {s}
                </div>
                {s < 3 && (
                  <div
                    className={`w-20 h-1 mx-2 ${
                      step > s ? "bg-blue-600" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-sm text-gray-600">
            <span>Empresa</span>
            <span>Contacto</span>
            <span>Plano</span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Step 1: Company Info */}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Dados da Empresa
            </h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome da Empresa *
              </label>
              <input
                type="text"
                value={formData.companyName}
                onChange={(e) => updateField("companyName", e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Minha Empresa Lda"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subdomínio *
              </label>
              <div className="flex items-center">
                <input
                  type="text"
                  value={formData.subdomain}
                  onChange={(e) => {
                    updateField("subdomain", e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''));
                    checkSubdomain(e.target.value);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="minha-empresa"
                  pattern="[a-z0-9-]+"
                  minLength={3}
                  maxLength={30}
                  required
                />
                <span className="px-4 py-2 bg-gray-100 border border-l-0 border-gray-300 rounded-r-lg text-gray-600 text-sm whitespace-nowrap">
                  .imos.cv
                </span>
              </div>
              {subdomainChecking && (
                <p className="text-sm text-gray-500 mt-1">A verificar...</p>
              )}
              {subdomainValid === true && (
                <p className="text-sm text-green-600 mt-1">✓ Disponível</p>
              )}
              {subdomainValid === false && (
                <p className="text-sm text-red-600 mt-1">✗ Indisponível</p>
              )}
              <p className="text-xs text-gray-500 mt-1">
                3-30 caracteres, apenas letras minúsculas, números e hífens
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                País *
              </label>
              <select
                value={formData.country}
                onChange={(e) => updateField("country", e.target.value as Country)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="CV">Cabo Verde</option>
                <option value="AO">Angola</option>
                <option value="SN">Senegal</option>
              </select>
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!formData.companyName || !formData.subdomain}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Próximo
            </button>
          </div>
        )}

        {/* Step 2: Contact Details */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Dados de Contacto
            </h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome Completo *
              </label>
              <input
                type="text"
                value={formData.contactName}
                onChange={(e) => updateField("contactName", e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: João Silva"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Profissional *
              </label>
              <input
                type="email"
                value={formData.contactEmail}
                onChange={(e) => updateField("contactEmail", e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="joao@empresa.cv"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                WhatsApp / Telefone *
              </label>
              <input
                type="tel"
                value={formData.contactPhone}
                onChange={(e) => updateField("contactPhone", e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="+238 99 123 45 67"
                required
              />
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep(1)}
                className="flex-1 bg-gray-200 text-gray-800 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Voltar
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={
                  !formData.contactName ||
                  !formData.contactEmail ||
                  !formData.contactPhone
                }
                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Próximo
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Plan Selection */}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Seleccione o Plano
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(PLAN_FEATURES).map(([key, plan]) => (
                <div
                  key={key}
                  onClick={() => updateField("plan", key as Plan)}
                  className={`cursor-pointer rounded-lg border-2 p-4 transition-all ${
                    formData.plan === key
                      ? plan.color === "starter"
                        ? "border-green-500 bg-green-50"
                        : plan.color === "blue"
                        ? "border-blue-500 bg-blue-50"
                        : "border-purple-500 bg-purple-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <h3 className="font-bold text-lg text-gray-900">
                    {plan.name}
                  </h3>
                  <p className="text-2xl font-bold text-gray-900 my-2">
                    {plan.price}
                  </p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>🏢 {plan.projects} projectos</li>
                    <li>🏠 {plan.units} unidades</li>
                    <li>👥 {plan.users} utilizadores</li>
                  </ul>
                </div>
              ))}
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep(2)}
                className="flex-1 bg-gray-200 text-gray-800 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Voltar
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "A processar..." : "Criar Conta"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
