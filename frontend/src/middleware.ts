/**
 * ImoOS — Next.js Edge Middleware
 * Skill: nextjs-tenant-routing / auth-jwt-handling
 *
 * Strategy: httpOnly cookie `refresh_token` as the session indicator.
 *   - The cookie is set by /api/auth/login and cleared by /api/auth/logout.
 *   - The middleware does NOT validate the JWT signature (Edge runtime has no
 *     access to the secret). Real token validation happens server-side in
 *     /api/auth/refresh, which is called by AuthContext.restoreSession() on
 *     every page mount. If the refresh fails (expired / revoked), the client
 *     redirects to /login via AuthContext — this is an intentional two-layer
 *     defence: middleware blocks the obvious unauthenticated requests quickly,
 *     AuthContext handles the subtle "stale cookie" case.
 *
 * Public paths (no cookie required):
 *   /login          — login page
 *   /api/auth/*     — auth API routes (login, refresh, logout)
 *   /_next/*        — Next.js internals (static, image optimisation)
 *   /favicon.ico, /robots.txt, /manifest.json — static assets
 */
import { NextRequest, NextResponse } from "next/server";

// Paths that are always publicly accessible
const PUBLIC_PREFIXES = [
  "/api/auth/",
  "/_next/",
  "/register",        // Sprint 7 - Prompt 03: Self-service registration
  "/verify-email",    // Sprint 7 - Prompt 03: Email verification
  "/superadmin/login", // Sprint 9 - P01: Staff login via public schema
  "/impersonate",     // Sprint 9 - P04: Impersonation token handoff
];

const PUBLIC_EXACT = new Set([
  "/login",
  "/favicon.ico",
  "/robots.txt",
  "/manifest.json",
]);

function isPublicPath(pathname: string): boolean {
  if (PUBLIC_EXACT.has(pathname)) return true;
  return PUBLIC_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // ------------------------------------------------------------------
  // 0. RSC / prefetch navigation requests to protected routes
  //    → return 401 instead of redirecting.
  //    A redirect during an RSC fetch causes Next.js to follow the
  //    redirect and return text/x-component for the login page, which
  //    the browser renders as raw RSC flight data instead of HTML.
  // ------------------------------------------------------------------
  const isRSCNavigation =
    request.headers.has("RSC") ||
    request.headers.has("Next-Router-State-Tree") ||
    request.headers.has("Next-Router-Prefetch");

  if (isRSCNavigation && !isPublicPath(pathname)) {
    const hasSession =
      pathname.startsWith("/superadmin")
        ? request.cookies.has("superadmin_refresh_token")
        : request.cookies.has("refresh_token");
    if (!hasSession) {
      return new NextResponse(null, { status: 401 });
    }
  }

  // ------------------------------------------------------------------
  // 1. Always allow public paths
  // ------------------------------------------------------------------
  if (isPublicPath(pathname)) {
    // Special case: already-authenticated user hitting /login
    // → redirect to / so they don't see the login form again.
    if (pathname === "/login" && request.cookies.has("refresh_token")) {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  // ------------------------------------------------------------------
  // 2. Super Admin area — requires superadmin_refresh_token cookie
  // ------------------------------------------------------------------
  if (pathname.startsWith("/superadmin")) {
    if (!request.cookies.has("superadmin_refresh_token")) {
      const loginUrl = request.nextUrl.clone();
      loginUrl.pathname = "/superadmin/login";
      return NextResponse.redirect(loginUrl);
    }
    return NextResponse.next();
  }

  // ------------------------------------------------------------------
  // 3. Protected path — require refresh_token cookie
  // ------------------------------------------------------------------
  if (!request.cookies.has("refresh_token")) {
    // Use request.nextUrl.clone() so Next.js handles basePath automatically.
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // ------------------------------------------------------------------
  // 4. Cookie present — allow through (AuthContext validates on mount)
  // ------------------------------------------------------------------
  return NextResponse.next();
}

export const config = {
  /*
   * Match every path EXCEPT:
   *   - _next/static  (static files)
   *   - _next/image   (image optimisation API)
   *   - favicon.ico   (browser default request)
   *
   * Note: /api/auth/* is matched here but handled explicitly in step 1
   * so that login/refresh/logout remain publicly accessible.
   */
  matcher: [
    "/((?!_next/static|_next/image|favicon\\.ico).*)",
  ],
};
