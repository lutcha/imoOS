/**
 * POST /api/auth/superadmin-login
 * Authenticates staff users against the public schema (Host: PLATFORM_DOMAIN).
 * Staff-only: rejects tokens where is_staff=false.
 * Uses a separate cookie (superadmin_refresh_token) to avoid colliding
 * with the regular tenant session.
 */
import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const PLATFORM_DOMAIN = process.env.PLATFORM_DOMAIN ?? "localhost:8000";

function decodeJwtPayload(token: string): Record<string, unknown> {
  const [, payload] = token.split(".");
  if (!payload) return {};
  const padded = payload + "=".repeat((4 - (payload.length % 4)) % 4);
  try {
    return JSON.parse(Buffer.from(padded, "base64url").toString("utf-8"));
  } catch {
    return {};
  }
}

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  const djangoResp = await fetch(`${API_URL}/api/v1/users/auth/token/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Host: PLATFORM_DOMAIN,
    },
    body: JSON.stringify({ email, password }),
  });

  if (!djangoResp.ok) {
    const err = await djangoResp.json().catch(() => ({}));
    return NextResponse.json(
      { detail: (err as { detail?: string }).detail ?? "Credenciais inválidas" },
      { status: djangoResp.status }
    );
  }

  const { access, refresh, tenant_schema } = await djangoResp.json();

  // Validate is_staff before issuing the session
  const claims = decodeJwtPayload(access);
  if (!claims.is_staff) {
    return NextResponse.json(
      { detail: "Acesso negado: conta sem permissão de staff" },
      { status: 403 }
    );
  }

  const response = NextResponse.json({
    access_token: access,
    tenant_schema: tenant_schema ?? "public",
  });

  response.cookies.set("superadmin_refresh_token", refresh, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 7 days
  });

  return response;
}
