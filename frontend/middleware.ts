/**
 * Next.js Middleware — ImoOS
 * Auth guard using refresh_token cookie as session indicator.
 *
 * Design: the middleware cannot access the in-memory access token.
 * It uses refresh_token cookie as a proxy for "has active session".
 * Real JWT validation happens in AuthContext.restoreSession() on the client.
 * Double protection: if refresh fails, AuthContext redirects to /login.
 *
 * Skills: nextjs-tenant-routing, auth-jwt-handling
 */
import { NextRequest, NextResponse } from "next/server";

// (auth) route group → URL is /login, not /auth/login
const PUBLIC_PATHS = ["/login", "/api/auth", "/api/health", "/_next", "/favicon.ico", "/robots.txt"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));

  if (isPublic) {
    // Already authenticated — don't show login page again
    if (pathname.startsWith("/login")) {
      const hasSession = request.cookies.has("refresh_token");
      if (hasSession) {
        return NextResponse.redirect(new URL("/", request.url));
      }
    }
    return NextResponse.next();
  }

  // Protected route — check for session cookie
  const hasSession = request.cookies.has("refresh_token");
  if (!hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname); // preserve intended destination
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    // Match everything except Next.js internals and static assets
    "/((?!_next/static|_next/image|favicon.ico|robots.txt).*)",
  ],
};
