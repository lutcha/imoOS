/**
 * POST /api/auth/login
 * Proxies credentials to Django, returns access_token in body,
 * stores refresh_token in httpOnly cookie.
 * Skill: auth-jwt-handling
 */
import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const TENANT_DOMAIN = process.env.TENANT_DOMAIN;
const PLATFORM_DOMAIN = process.env.PLATFORM_DOMAIN ?? "proptech.cv";

export async function POST(request: NextRequest) {
  const { email, password, tenant_domain } = await request.json();

  // Resolve the tenant hostname to send to Django:
  // 1. Explicit tenant_domain from client (e.g. for superadmin login)
  // 2. TENANT_DOMAIN env var if set
  // 3. Fall back to the host header from the browser request
  const requestHost = request.headers.get("host") || "localhost:3000";
  const tenantHost = tenant_domain ?? TENANT_DOMAIN ?? requestHost.split(':')[0];

  const djangoResp = await fetch(`${API_URL}/api/v1/users/auth/token/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Host": tenantHost,
    },
    body: JSON.stringify({ email, password }),
  });

  if (!djangoResp.ok) {
    const err = await djangoResp.json().catch(() => ({}));
    return NextResponse.json(
      { detail: err.detail ?? "Credenciais inválidas" },
      { status: djangoResp.status }
    );
  }

  const { access, refresh, tenant_schema } = await djangoResp.json();

  const response = NextResponse.json({
    access_token: access,
    tenant_schema,
  });

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
