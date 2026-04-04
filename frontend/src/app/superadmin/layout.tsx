/**
 * Super-Admin Layout — ImoOS
 * Uses useSuperAdminSession (public schema auth) instead of AuthContext.
 * Redirects to /superadmin/login if not authenticated or not staff.
 */
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSuperAdminSession } from "@/hooks/useSuperAdminSession";

export default function SuperAdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading, logout } = useSuperAdminSession();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/superadmin/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-red-500 mx-auto"></div>
          <p className="mt-4 text-sm text-slate-400">A verificar acesso...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Bar */}
      <header className="bg-slate-900 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14">
            <div className="flex items-center">
              <span className="text-red-500 mr-2 text-xs font-bold uppercase tracking-widest">
                ● Super Admin
              </span>
              <nav className="ml-6 flex space-x-1">
                <a
                  href="/superadmin"
                  className="text-slate-300 hover:text-white hover:bg-slate-700 px-3 py-1.5 rounded text-sm transition"
                >
                  Tenants
                </a>
                <a
                  href="/superadmin/registrations"
                  className="text-slate-300 hover:text-white hover:bg-slate-700 px-3 py-1.5 rounded text-sm transition"
                >
                  Registrations
                </a>
                <a
                  href="/api/v1/health/"
                  className="text-slate-300 hover:text-white hover:bg-slate-700 px-3 py-1.5 rounded text-sm transition"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Health
                </a>
                <a
                  href="/metrics/"
                  className="text-slate-300 hover:text-white hover:bg-slate-700 px-3 py-1.5 rounded text-sm transition"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Metrics
                </a>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-xs text-slate-400">{user?.email}</span>
              <button
                onClick={logout}
                className="text-xs text-slate-400 hover:text-red-400 transition"
              >
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
