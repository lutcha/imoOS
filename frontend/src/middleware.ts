/**
 * ImoOS — Next.js Edge Middleware (Next.js 15)
 * Skill: nextjs-tenant-routing / auth-jwt-handling
 *
 * Strategy: httpOnly cookie `refresh_token` as the session indicator.
 *   - Set by /api/auth/login, cleared by /api/auth/logout.
 *   - Middleware does NOT validate JWT signature (Edge has no access to secret).
 *   - Real validation happens server-side in /api/auth/refresh (called by
 *     AuthContext.restoreSession on every mount). Two-layer defence: middleware
 *     handles the obvious unauthenticated case; AuthContext handles stale cookies.
 *
 * Next.js 15: NextResponse.redirect() from middleware correctly triggers a
 * full-page navigation even for RSC (client-side router) fetch requests.
 * The old "return 401 for RSC" pattern is no longer needed and caused the
 * router to crash with errors on sidebar tab clicks for unauthenticated users.
 */
import { NextRequest, NextResponse } from "next/server";

// Prefix-based public paths (startsWith check)
const PUBLIC_PREFIXES = [
  "/api/auth/",
  "/_next/",
  "/register",
  "/verify-email",
  "/superadmin/login",
  "/impersonate",
  "/api/health",
];

// Exact public paths
const PUBLIC_EXACT = new Set([
  "/login",
  "/favicon.ico",
  "/robots.txt",
  "/manifest.json",
]);

function isPublicPath(pathname: string): boolean {
  if (PUBLIC_EXACT.has(pathname)) return true;
  return PUBLIC_PREFIXES.some((p) => pathname.startsWith(p));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // ── 1. Public paths ──────────────────────────────────────────────────
  if (isPublicPath(pathname)) {
    // Authenticated user hitting /login → bounce to app root
    if (pathname === "/login" && request.cookies.has("refresh_token")) {
      const home = request.nextUrl.clone();
      home.pathname = "/";
      home.search = "";
      return NextResponse.redirect(home);
    }
    return NextResponse.next();
  }

  // ── 2. Superadmin area ───────────────────────────────────────────────
  if (pathname.startsWith("/superadmin")) {
    if (!request.cookies.has("superadmin_refresh_token")) {
      const url = request.nextUrl.clone();
      url.pathname = "/superadmin/login";
      url.search = "";
      return NextResponse.redirect(url);
    }
    return NextResponse.next();
  }

  // ── 3. Protected routes — require refresh_token cookie ───────────────
  //    NextResponse.redirect() in Next.js 15 triggers a full-page navigation
  //    even when the original request is an RSC fetch (client-side router).
  if (!request.cookies.has("refresh_token")) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon\\.ico).*)"],
};
