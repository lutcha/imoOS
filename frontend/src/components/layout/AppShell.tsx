"use client";

/**
 * AppShell — renders Sidebar+Topbar only for authenticated app routes.
 * Auth routes (/login) and superadmin routes (/superadmin) render children directly.
 */
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth, useRequireAuth } from "@/contexts/AuthContext";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

const AUTH_PATHS = ["/login", "/register", "/verify-email", "/superadmin/login", "/impersonate", "/landing"];
const SUPERADMIN_PATHS = ["/superadmin"];

function isAuthPath(p: string): boolean {
  return AUTH_PATHS.some((prefix) => p.startsWith(prefix));
}
function isSuperAdminPath(p: string): boolean {
  return SUPERADMIN_PATHS.some((prefix) => p.startsWith(prefix));
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isLoading, isAuthenticated } = useAuth();

  const isPublic = isAuthPath(pathname) || isSuperAdminPath(pathname);

  // Client-side auth guard for protected pages:
  // Handles the case where the cookie expires while the user is already on a page.
  // The middleware covers unauthenticated initial page loads; this covers session expiry.
  useEffect(() => {
    if (!isPublic && !isLoading && !isAuthenticated) {
      router.replace("/login?next=" + encodeURIComponent(pathname));
    }
  }, [isPublic, isLoading, isAuthenticated, pathname, router]);

  // Auth/public pages — no shell
  if (isPublic) {
    return <>{children}</>;
  }

  // Loading or awaiting redirect after session expiry
  if (isLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <>
      <Sidebar />
      <div className="flex flex-col min-h-screen bg-muted/30 ml-64">
        <Topbar />
        <main className="flex-1 mt-16 p-8">
          {children}
        </main>
      </div>
    </>
  );
}

// Wrapper for protected pages
export function ProtectedPage({ children }: { children: React.ReactNode }) {
  useRequireAuth();
  return <>{children}</>;
}
