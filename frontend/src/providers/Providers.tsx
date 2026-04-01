"use client";

/**
 * Providers — ImoOS
 * Composes: QueryClient (tenant-scoped) + AuthProvider + TenantProvider
 * Skill: react-query-tenant
 */
import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { TenantProvider } from "@/contexts/TenantContext";

// One QueryClient per app instance — tenant scoping enforced by query keys
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,       // 30s default — overrideable per hook
      gcTime: 5 * 60_000,      // 5min cache retention
      retry: 1,                // one retry on failure
      refetchOnWindowFocus: false,
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TenantProvider>
          {children}
        </TenantProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
