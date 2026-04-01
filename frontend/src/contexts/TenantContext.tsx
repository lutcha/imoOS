"use client";

/**
 * TenantContext — ImoOS
 * Derives tenant info from AuthContext — single source of truth.
 * Skill: nextjs-tenant-routing
 */
import React, { createContext, useContext } from "react";
import { useAuth } from "@/contexts/AuthContext";

interface TenantContextValue {
  schema: string;
  name: string;
}

const TenantContext = createContext<TenantContextValue | null>(null);

export function TenantProvider({ children }: { children: React.ReactNode }) {
  const { tenant } = useAuth();

  if (!tenant) {
    // Not authenticated — children (middleware handles redirect)
    return <>{children}</>;
  }

  return (
    <TenantContext.Provider value={tenant}>
      {children}
    </TenantContext.Provider>
  );
}

// Returns empty strings when not authenticated — queries should guard with `enabled: !!schema`
export function useTenant(): TenantContextValue {
  return useContext(TenantContext) ?? { schema: "", name: "" };
}
