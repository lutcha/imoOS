"use client";

/**
 * useSuperAdminSession — session management for the Super Admin area.
 * Operates independently of AuthContext: uses superadmin_refresh_token cookie
 * and /api/auth/superadmin-refresh (Host: PLATFORM_DOMAIN → public schema).
 */
import { useCallback, useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import { setAccessToken, setTenantSchema } from "@/lib/api-client";

interface JwtClaims {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  tenant_schema: string;
  is_staff: boolean;
  exp: number;
}

export interface SuperAdminUser {
  id: string;
  email: string;
  fullName: string;
  isStaff: boolean;
}

interface SuperAdminSessionState {
  user: SuperAdminUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export function useSuperAdminSession() {
  const [state, setState] = useState<SuperAdminSessionState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  const refresh = useCallback(async () => {
    try {
      const resp = await fetch("/api/auth/superadmin-refresh", { method: "POST" });
      if (!resp.ok) throw new Error("No session");
      const { access_token, tenant_schema } = await resp.json();

      setAccessToken(access_token);
      setTenantSchema(tenant_schema ?? "public");

      const claims = jwtDecode<JwtClaims>(access_token);
      setState({
        user: {
          id: claims.user_id,
          email: claims.email,
          fullName: claims.full_name,
          isStaff: claims.is_staff,
        },
        isLoading: false,
        isAuthenticated: true,
      });
    } catch {
      setState({ user: null, isLoading: false, isAuthenticated: false });
    }
  }, []);

  // Restore session on mount
  useEffect(() => {
    refresh();
  }, [refresh]);

  const logout = useCallback(async () => {
    await fetch("/api/auth/logout", { method: "POST" }).catch(() => {});
    setAccessToken(null);
    setTenantSchema(null);
    setState({ user: null, isLoading: false, isAuthenticated: false });
    window.location.href = "/superadmin/login";
  }, []);

  return { ...state, logout };
}
