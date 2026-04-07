/**
 * ImoOS — Simplified Middleware
 * Only handles API auth and basic public path detection
 * Client-side auth handled by AuthContext
 */
import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = [
  "/login",
  "/register",
  "/verify-email",
  "/superadmin/login",
  "/impersonate",
  "/_next/",
  "/api/auth/",
  "/favicon.ico",
  "/robots.txt",
  "/manifest.json",
];

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some((p) => pathname.startsWith(p));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow all public paths
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  // Check for auth cookies
  const hasSession = request.cookies.has("refresh_token");
  const hasSuperAdminSession = request.cookies.has("superadmin_refresh_token");

  // Superadmin routes check
  if (pathname.startsWith("/superadmin")) {
    if (!hasSuperAdminSession && pathname !== "/superadmin/login") {
      return NextResponse.redirect(new URL("/superadmin/login", request.url));
    }
    return NextResponse.next();
  }

  // For RSC/navigation requests without cookie, return 401
  // This lets AuthContext handle the redirect client-side
  const isRSC = request.headers.has("RSC") || request.headers.has("Next-Router-State-Tree");
  
  if (!hasSession && isRSC) {
    return new NextResponse(null, { status: 401 });
  }

  // For non-RSC requests without cookie, let them through
  // AuthContext will check and redirect if needed
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon\\.ico).*)"],
};
