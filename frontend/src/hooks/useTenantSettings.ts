"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

export interface TenantSettings {
    id: string;
    name: string;
    subdomain: string;
    logo: string | null;
    primary_color: string;
    secondary_color: string;
    email_contact: string | null;
    phone_contact: string | null;
    address: string | null;
}

export function useTenantSettings() {
    const { schema } = useTenant();

    return useQuery<TenantSettings>({
        queryKey: ["tenant-settings", schema],
        queryFn: () => apiClient.get<TenantSettings>(`/tenants/current/`).then((r) => r.data),
        enabled: !!schema,
    });
}

export function useUpdateTenantSettings() {
    const queryClient = useQueryClient();
    const { schema } = useTenant();

    return useMutation({
        mutationFn: (data: Partial<TenantSettings>) =>
            apiClient.patch<TenantSettings>(`/tenants/current/`, data).then((r) => r.data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["tenant-settings", schema] });
        },
    });
}
