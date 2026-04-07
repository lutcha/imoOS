"use client";

/**
 * AppShell — renders Sidebar+Topbar only for authenticated app routes.
 * Auth routes (/login) and superadmin routes (/superadmin) render children directly.
 */
import { usePathname } from "next/navigation";
import { useAuth, useRequireAuth } from "@/contexts/AuthContext";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

const AUTH_PATHS = ["/login", "/register", "/verify-email", "/superadmin/login", "/impersonate"];
const SUPERADMIN_PATHS = ["/superadmin"];

function isAuthPath(pathname: string): boolean {
  return AUTH_PATHS.some((p) => pathname.startsWith(p));
}

function isSuperAdminPath(pathname: string): boolean {
  return SUPERADMIN_PATHS.some((p) => pathname.startsWith(p));
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { isLoading, isAuthenticated } = useAuth();

  // Public/auth pages - no shell
  if (isAuthPath(pathname)) {
    return <>{children}</>;
  }

  // Superadmin pages - different shell (handled by superadmin layout)
  if (isSuperAdminPath(pathname)) {
    return <>{children}</>;
  }

  // Protected pages - require auth
  // useRequireAuth will redirect to login if not authenticated
  // But we need to handle the loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }

  // If not authenticated and not on public page, show loading
  // The redirect will happen via useRequireAuth in child components
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
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
