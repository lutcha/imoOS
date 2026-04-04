"use client";

/**
 * Impersonation Handoff Page — ImoOS
 * Sprint 9 - P04
 *
 * Flow:
 *  1. Super Admin clicks "Impersonar" → backend generates short-lived access token
 *  2. Browser opens: https://{tenant.domain}/impersonate?token=<access>&schema=<schema>
 *  3. This page reads the params, hydrates the in-memory auth state, and redirects to /
 *
 * Security notes:
 *  - Token lives only in memory (setAccessToken) — never written to localStorage/cookies
 *  - URL param is cleared immediately after reading
 *  - Token is short-lived (30 min), non-renewable (no refresh cookie issued)
 *  - Django marks the JWT payload with impersonated_by for audit trail
 */
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { setAccessToken, setTenantSchema } from "@/lib/api-client";
import { jwtDecode } from "jwt-decode";
import { ShieldAlert, Loader2 } from "lucide-react";

interface JwtClaims {
  email: string;
  full_name: string;
  tenant_schema: string;
  tenant_name: string;
  impersonated_by?: string;
  exp: number;
}

function ImpersonateHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    const schema = searchParams.get("schema");

    if (!token || !schema) {
      setError("Parâmetros de impersonation em falta.");
      return;
    }

    try {
      const claims = jwtDecode<JwtClaims>(token);

      // Basic sanity checks
      if (!claims.impersonated_by) {
        setError("Token inválido: não é um token de impersonation.");
        return;
      }
      if (claims.exp * 1000 < Date.now()) {
        setError("Token de impersonation expirado.");
        return;
      }

      // Hydrate in-memory auth state — same pattern as AuthContext
      setAccessToken(token);
      setTenantSchema(schema);

      // Clear the token from the URL immediately (security hygiene)
      window.history.replaceState({}, "", "/impersonate");

      // Brief visual feedback, then redirect
      setTimeout(() => router.replace("/"), 1200);
    } catch {
      setError("Token de impersonation inválido.");
    }
  }, []);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="max-w-sm w-full rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <ShieldAlert className="h-10 w-10 text-red-500 mx-auto mb-3" />
          <h1 className="text-base font-semibold text-red-800">Impersonation falhou</h1>
          <p className="mt-2 text-sm text-red-600">{error}</p>
          <a href="/login" className="mt-4 inline-block text-sm text-red-700 underline">
            Ir para o login
          </a>
        </div>
      </div>
    );
  }

  const schema = typeof window !== "undefined"
    ? new URLSearchParams(window.location.search).get("schema")
    : null;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 p-4">
      <div className="text-center">
        <Loader2 className="h-10 w-10 text-red-400 animate-spin mx-auto mb-4" />
        <p className="text-slate-300 text-sm">A iniciar sessão como...</p>
        {schema && (
          <p className="mt-1 text-xs font-mono text-slate-500">{schema}</p>
        )}
      </div>
    </div>
  );
}

export default function ImpersonatePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
      </div>
    }>
      <ImpersonateHandler />
    </Suspense>
  );
}
