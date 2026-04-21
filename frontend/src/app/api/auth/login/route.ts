import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const TENANT_DOMAIN = process.env.TENANT_DOMAIN;

export async function POST(request: NextRequest) {
  const { email, password, tenant_domain } = await request.json();
  const requestHost = request.headers.get("host") ?? "localhost";
  const resolvedDomain = tenant_domain ?? TENANT_DOMAIN ?? requestHost.split(":")[0];

  const resp = await fetch(`${API_URL}/api/v1/users/auth/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, tenant_domain: resolvedDomain }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    return NextResponse.json(
      { detail: (err as { detail?: string }).detail ?? "Credenciais inválidas" },
      { status: resp.status }
    );
  }

  const { access, refresh, tenant_schema, tenant_domain: resp_tenant_domain } = await resp.json();
  const response = NextResponse.json({ 
    access_token: access, 
    tenant_schema, 
    tenant_domain: resp_tenant_domain ?? '' 
  });
  response.cookies.set("refresh_token", refresh, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
  return response;
}
