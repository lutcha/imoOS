/**
 * Authenticated fetch helper for the Super Admin area.
 * Uses the in-memory access token (set by useSuperAdminSession).
 * On 401: attempts one silent refresh via /api/auth/superadmin-refresh,
 * then redirects to /superadmin/login on failure.
 */
import { getAccessToken, setAccessToken, setTenantSchema } from "@/lib/api-client";

const API_BASE = "/api/v1";

async function refreshSuperAdminToken(): Promise<string | null> {
  const resp = await fetch("/api/auth/superadmin-refresh", { method: "POST" });
  if (!resp.ok) return null;
  const { access_token, tenant_schema } = await resp.json();
  setAccessToken(access_token);
  setTenantSchema(tenant_schema ?? "public");
  return access_token;
}

export async function superadminFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getAccessToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (resp.status === 401) {
    const newToken = await refreshSuperAdminToken();
    if (!newToken) {
      if (typeof window !== "undefined") {
        window.location.href = "/superadmin/login";
      }
      return resp;
    }
    headers["Authorization"] = `Bearer ${newToken}`;
    return fetch(`${API_BASE}${path}`, { ...options, headers });
  }

  return resp;
}
