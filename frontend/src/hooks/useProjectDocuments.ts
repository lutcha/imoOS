import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

export interface ProjectDocument {
  id: string;
  project: string;
  category: "PLAN" | "LICENSE" | "CONTRACT" | "OTHER";
  title: string;
  file: string;
  version: number;
  uploaded_by_name: string;
  created_at: string;
}

export const documentKeys = {
  all: (schema: string, projectId: string) => ["projects", schema, projectId, "documents"] as const,
};

export function useProjectDocuments(projectId: string) {
  const { schema } = useTenant();

  return useQuery<ProjectDocument[]>({
    queryKey: documentKeys.all(schema, projectId),
    queryFn: () =>
      apiClient
        .get<ProjectDocument[]>(`/projects/projects/${projectId}/documents/`)
        .then((r) => r.data),
    enabled: !!schema && !!projectId,
  });
}

export function useUploadDocument() {
  const { schema } = useTenant();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      projectId: string;
      formData: FormData;
    }) =>
      apiClient.post<ProjectDocument>(
        `/projects/projects/${data.projectId}/documents/`,
        data.formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKeys.all(schema, variables.projectId),
      });
    },
  });
}
