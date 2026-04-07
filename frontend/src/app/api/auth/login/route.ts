/**
 * POST /api/auth/login
 * Proxies credentials to Django, returns access_token in body,
 * stores refresh_token in httpOnly cookie.
 *
 * Tenant resolution: Node.js 18+ native fetch treats `Host` as a forbidden
 * header and silently ignores overrides. We pass `tenant_domain` in the JSON
 * body instead, and Django resolves the schema from there.
 */
import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const TENANT_DOMAIN = process.env.TENANT_DOMAIN;

export async function POST(request: NextRequest) {
  const { email, password, tenant_domain } = await request.json();

  // Resolve the tenant domain:
  // 1. Explicit tenant_domain from client
  // 2. TENANT_DOMAIN env var (set per-deployment in app.yaml)
  // 3. Host header from the browser (strips port)
  const requestHost = request.headers.get("host") || "localhost:3000";
  const resolvedTenantDomain =
    tenant_domain ?? TENANT_DOMAIN ?? requestHost.split(":")[0];

  const djangoResp = await fetch(`${API_URL}/api/v1/users/auth/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // Pass tenant_domain in the body — the Django view switches the schema
    // explicitly, bypassing the Host-header approach which doesn't work for
    // server-to-server fetch in Node.js 18+.
    body: JSON.stringify({ email, password, tenant_domain: resolvedTenantDomain }),
  });

  if (!djangoResp.ok) {
    const err = await djangoResp.json().catch(() => ({}));
    return NextResponse.json(
      { detail: err.detail ?? "Credenciais inválidas" },
      { status: djangoResp.status }
    );
  }

  const { access, refresh, tenant_schema } = await djangoResp.json();

  const response = NextResponse.json({ access_token: access, tenant_schema });

  // httpOnly — not accessible by JS — XSS protection
  response.cookies.set("refresh_token", refresh, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 7 days
  });

  return response;
}
