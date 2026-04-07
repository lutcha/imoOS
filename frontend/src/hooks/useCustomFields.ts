"""
useCustomFields — Hook for CRM custom fields
"""
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";

export interface CustomField {
  id: string;
  name: string;
  key: string;
  field_type: "text" | "number" | "date" | "boolean" | "choice" | "email" | "phone";
  required: boolean;
  help_text: string;
  choices: string[];
  order: number;
  is_active: boolean;
}

export interface CustomFieldValue {
  id: string;
  field: string;
  field_name: string;
  field_type: string;
  value: any;
}

const keys = {
  all: ["custom-fields"] as const,
  definitions: () => [...keys.all, "definitions"] as const,
  values: (leadId: string) => [...keys.all, "values", leadId] as const,
};

// Get custom field definitions
export function useCustomFields() {
  return useQuery({
    queryKey: keys.definitions(),
    queryFn: async () => {
      const response = await apiClient.get<CustomField[]>("/crm/custom-fields/");
      return response.data;
    },
  });
}

// Get custom values for a lead
export function useLeadCustomValues(leadId: string) {
  return useQuery({
    queryKey: keys.values(leadId),
    queryFn: async () => {
      const response = await apiClient.get<CustomFieldValue[]>("/crm/custom-values/", {
        params: { lead: leadId },
      });
      return response.data;
    },
    enabled: !!leadId,
  });
}

// Create/update custom field definitions (admin only)
export function useCreateCustomField() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<CustomField>) => {
      const response = await apiClient.post<CustomField>("/crm/custom-fields/", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: keys.definitions() });
    },
  });
}

// Update custom values for a lead
export function useUpdateCustomValues() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ leadId, values }: { leadId: string; values: { field: string; value: any }[] }) => {
      const payload = values.map((v) => ({ ...v, lead: leadId }));
      const response = await apiClient.post("/crm/custom-values/", payload);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: keys.values(variables.leadId) });
    },
  });
}
