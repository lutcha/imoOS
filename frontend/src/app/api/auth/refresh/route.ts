/**
 * POST /api/auth/refresh
 * Reads httpOnly refresh_token cookie, exchanges for new access token.
 * Called on: mount (session restore), 401 (auto-refresh).
 * Skill: auth-jwt-handling
 */
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const TENANT_DOMAIN = process.env.TENANT_DOMAIN;

export async function POST() {
  const cookieStore = await cookies();
  const refreshToken = cookieStore.get("refresh_token")?.value;

  if (!refreshToken) {
    return NextResponse.json({ detail: "No refresh token" }, { status: 401 });
  }

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (TENANT_DOMAIN) headers["Host"] = TENANT_DOMAIN;

  const djangoResp = await fetch(`${API_URL}/api/v1/users/auth/token/refresh/`, {
    method: "POST",
    headers,
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!djangoResp.ok) {
    const response = NextResponse.json(
      { detail: "Session expired" },
      { status: 401 }
    );
    // Clear stale cookie
    response.cookies.delete("refresh_token");
    return response;
  }

  const { access, tenant_schema, tenant_name, tenant_domain } = await djangoResp.json();

  // tenant_schema and tenant_domain are returned directly from the backend.
  // No need to decode JWT manually.

  return NextResponse.json({
    access_token: access,
    tenant_schema,
    tenant_name,
    tenant_domain: tenant_domain ?? '',
  });
}
