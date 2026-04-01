/**
 * POST /api/auth/login
 * Proxies credentials to Django, returns access_token in body,
 * stores refresh_token in httpOnly cookie.
 * Skill: auth-jwt-handling
 */
import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
// TENANT_DOMAIN overrides the Host header sent to Django.
// Required when running behind Docker/reverse-proxy where the browser-facing
// host (e.g. localhost:3001) differs from the Django tenant domain (e.g. demo.localhost).
const TENANT_DOMAIN = process.env.TENANT_DOMAIN;

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  // Resolve the tenant hostname to send to Django:
  // 1. Use TENANT_DOMAIN env var if set (Docker / production proxy)
  // 2. Fall back to the host header from the browser request
  const requestHost = request.headers.get("host") || "localhost:3000";
  const tenantHost = TENANT_DOMAIN ?? requestHost.split(':')[0];

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
