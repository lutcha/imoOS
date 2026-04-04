/**
 * POST /api/auth/superadmin-refresh
 * Exchanges superadmin_refresh_token cookie for a new access token.
 * Sends Host: PLATFORM_DOMAIN so Django uses the public schema.
 */
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const PLATFORM_DOMAIN = process.env.PLATFORM_DOMAIN ?? "localhost:8000";

export async function POST() {
  const cookieStore = await cookies();
  const refreshToken = cookieStore.get("superadmin_refresh_token")?.value;

  if (!refreshToken) {
    return NextResponse.json({ detail: "No session" }, { status: 401 });
  }

  const djangoResp = await fetch(`${API_URL}/api/v1/users/auth/token/refresh/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Host: PLATFORM_DOMAIN,
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!djangoResp.ok) {
    const response = NextResponse.json({ detail: "Session expired" }, { status: 401 });
    response.cookies.delete("superadmin_refresh_token");
    return response;
  }

  const { access, tenant_schema } = await djangoResp.json();

  return NextResponse.json({
    access_token: access,
    tenant_schema: tenant_schema ?? "public",
  });
}
