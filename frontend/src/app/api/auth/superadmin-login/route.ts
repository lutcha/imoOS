import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

function decodeJwt(token: string): Record<string, unknown> {
  try {
    const [, payload] = token.split(".");
    const padded = payload + "=".repeat((4 - (payload.length % 4)) % 4);
    return JSON.parse(Buffer.from(padded, "base64url").toString("utf-8"));
  } catch { return {}; }
}

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  const resp = await fetch(`${API_URL}/api/v1/users/auth/superadmin/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    return NextResponse.json(
      { detail: (err as { detail?: string }).detail ?? "Credenciais inválidas" },
      { status: resp.status }
    );
  }

  const { access, refresh } = await resp.json();
  const claims = decodeJwt(access);
  if (!claims.is_staff) {
    return NextResponse.json({ detail: "Acesso negado: sem permissão de staff" }, { status: 403 });
  }

  const response = NextResponse.json({ access_token: access, tenant_schema: "public" });
  response.cookies.set("superadmin_refresh_token", refresh, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
  return response;
}
