import { NextRequest, NextResponse } from "next/server";

// Paths that don't require authentication
const PUBLIC_PATHS = [
  "/login",
  "/register", 
  "/verify-email",
  "/forgot-password",
  "/reset-password",
  "/superadmin/login",
  "/api/auth/login",
  "/api/auth/register",
  "/api/auth/refresh",
  "/api/auth/logout",
  "/api/auth/forgot-password",
  "/api/auth/reset-password",
  "/api/auth/verify-email",
  "/api/superadmin/login",
  "/api/superadmin/refresh",
  "/api/superadmin/logout",
];

// Static assets that should be skipped
const STATIC_PATHS = [
  "/_next/",
  "/static/",
  "/favicon.ico",
  "/robots.txt",
  "/manifest.json",
  "/sitemap.xml",
];

function isPublicPath(pathname: string): boolean {
  // Check static assets first
  if (STATIC_PATHS.some((path) => pathname.startsWith(path))) {
    return true;
  }
  
  // Check public paths
  return PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(path + "/"));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow all public paths without checks
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  // Superadmin routes (except login which is already handled above)
  if (pathname.startsWith("/superadmin")) {
    const superadminToken = request.cookies.get("superadmin_refresh_token")?.value;
    if (!superadminToken) {
      // Redirect to superadmin login
      return NextResponse.redirect(new URL("/superadmin/login", request.url));
    }
    return NextResponse.next();
  }

  // All other routes require regular auth token
  const authToken = request.cookies.get("refresh_token")?.value;
  if (!authToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
