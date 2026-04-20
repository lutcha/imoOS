import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

export interface ConstructionPhase {
  id: string;
  project: string;
  phase_type: string;
  name: string;
  description: string;
  start_planned: string;
  end_planned: string;
  start_actual: string | null;
  end_actual: string | null;
  status: "PLANNED" | "IN_PROGRESS" | "COMPLETED" | "DELAYED" | "PAUSED";
  progress_percent: number;
  order: number;
  deadline_deviation_days: number;
  task_count: number;
  completed_task_count: number;
}

export const phaseKeys = {
  all: (schema: string, projectId: string) => ["construction", schema, "phases", projectId] as const,
};

export function usePhases(projectId: string) {
  const { schema } = useTenant();

  return useQuery<ConstructionPhase[]>({
    queryKey: phaseKeys.all(schema, projectId),
    queryFn: () =>
      apiClient
        .get<ConstructionPhase[]>("/construction/phases/", { params: { project: projectId } })
        .then((r) => r.data),
    enabled: !!schema && !!projectId,
  });
}

export function useUpdateProgressPhoto() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (data: {
      projectId: string;
      formData: FormData;
    }) =>
      apiClient.post(
        `/projects/projects/${data.projectId}/update_progress_photo/`,
        data.formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      ),
    onSuccess: (_, variables) => {
      // Invalidate both phases and project detail
      qc.invalidateQueries({ queryKey: ["projects", schema, "detail", variables.projectId] });
      qc.invalidateQueries({ queryKey: phaseKeys.all(schema, variables.projectId) });
    },
  });
}
