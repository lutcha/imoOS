"use client";

/**
 * AuthContext — ImoOS
 * Simplified auth with proper error handling
 */
import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { jwtDecode } from "jwt-decode";
import { setAccessToken, setTenantSchema, getAccessToken } from "@/lib/api-client";

interface JwtClaims {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  tenant_schema: string;
  tenant_name: string;
  is_staff: boolean;
  exp: number;
}

interface User {
  id: string;
  email: string;
  fullName: string;
  role: string;
  isStaff: boolean;
  initials: string;
}

interface Tenant {
  schema: string;
  name: string;
}

interface AuthState {
  user: User | null;
  tenant: Tenant | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string, tenantDomain?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function extractInitials(name: string): string {
  return name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("");
}

function hydrateFromToken(token: string): { user: User; tenant: Tenant } {
  const claims = jwtDecode<JwtClaims>(token);
  return {
    user: {
      id: claims.user_id,
      email: claims.email,
      fullName: claims.full_name,
      role: claims.role,
      isStaff: claims.is_staff,
      initials: extractInitials(claims.full_name),
    },
    tenant: {
      schema: claims.tenant_schema,
      name: claims.tenant_name,
    },
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [state, setState] = useState<AuthState>({
    user: null,
    tenant: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Restore session on mount
  useEffect(() => {
    async function restoreSession() {
      try {
        const resp = await fetch("/api/auth/refresh", { 
          method: "POST",
          credentials: "include",
        });
        
        if (!resp.ok) {
          throw new Error("Session expired");
        }
        
        const { access_token, tenant_schema } = await resp.json();
        
        if (!access_token) {
          throw new Error("No token received");
        }

        setAccessToken(access_token);
        setTenantSchema(tenant_schema);
        const { user, tenant } = hydrateFromToken(access_token);
        setState({ user, tenant, isLoading: false, isAuthenticated: true });
      } catch {
        setState({ user: null, tenant: null, isLoading: false, isAuthenticated: false });
        // Don't redirect superadmin, auth, or impersonation paths — they manage
        // their own sessions independently of the tenant refresh_token cookie.
        const noRedirectPrefixes = ["/login", "/register", "/verify-email", "/superadmin", "/impersonate", "/landing"];
        if (!noRedirectPrefixes.some((p) => pathname.startsWith(p))) {
          router.replace("/login?next=" + encodeURIComponent(pathname));
        }
      }
    }
    restoreSession();
  }, []);

  const login = useCallback(async (email: string, password: string, tenantDomain?: string) => {
    const resp = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password, tenant_domain: tenantDomain }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail ?? "Credenciais inválidas");
    }

    const { access_token, tenant_schema } = await resp.json();
    
    if (!access_token) {
      throw new Error("Invalid response from server");
    }
    
    setAccessToken(access_token);
    setTenantSchema(tenant_schema);
    const { user, tenant } = hydrateFromToken(access_token);
    setState({ user, tenant, isLoading: false, isAuthenticated: true });
  }, []);

  const logout = useCallback(() => {
    fetch("/api/auth/logout", { 
      method: "POST",
      credentials: "include",
    }).catch(() => {});
    
    setAccessToken(null);
    setTenantSchema(null);
    setState({ user: null, tenant: null, isLoading: false, isAuthenticated: false });
    
    // Hard redirect to login
    window.location.replace("/login");
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}

// Hook for protected routes
export function useRequireAuth() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      const noRedirectPrefixes = ["/login", "/register", "/verify-email", "/superadmin", "/impersonate", "/landing"];
      if (!noRedirectPrefixes.some((p) => pathname.startsWith(p))) {
        router.replace("/login?next=" + encodeURIComponent(pathname));
      }
    }
  }, [isAuthenticated, isLoading, pathname, router]);
}
