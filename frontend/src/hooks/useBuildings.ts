"use client";

import { useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

export interface Building {
    id: string;
    name: string;
    code: string;
    floors_count: number;
    project: string;
    created_at: string;
    updated_at: string;
}

export interface BuildingsPage {
    count: number;
    next: string | null;
    previous: string | null;
    results: Building[];
}

export function useBuildings(projectId: string) {
    const { schema } = useTenant();

    return useQuery<Building[]>({
        queryKey: ["buildings", schema, projectId],
        queryFn: () =>
            apiClient
                .get<BuildingsPage>(`/projects/buildings/`, { params: { project: projectId } })
                .then((r) => r.data.results),
        enabled: !!schema && !!projectId,
    });
}
