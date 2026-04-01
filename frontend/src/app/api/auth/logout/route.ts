/**
 * POST /api/auth/logout
 * Blacklists refresh token in Django, clears httpOnly cookie.
 * Skill: auth-jwt-handling
 */
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export async function POST() {
  const cookieStore = await cookies();
  const refreshToken = cookieStore.get("refresh_token")?.value;

  if (refreshToken) {
    // Best-effort blacklist — don't fail if Django is unavailable
    await fetch(`${API_URL}/api/v1/users/auth/token/blacklist/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    }).catch(() => {});
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.set("refresh_token", "", { path: "/", maxAge: 0 });
  return response;
}
