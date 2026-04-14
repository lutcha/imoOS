/**
 * POST /api/auth/superadmin-logout
 * Clears the superadmin_refresh_token httpOnly cookie.
 */
import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.set("superadmin_refresh_token", "", { path: "/", maxAge: 0 });
  return response;
}
