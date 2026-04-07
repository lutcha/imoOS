"""
useUsers — Hook for user management (admin only)
"""
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: "admin" | "gestor" | "vendedor" | "engenheiro" | "investidor";
  is_active: boolean;
  phone?: string;
  created_at: string;
}

export interface CreateUserPayload {
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  password?: string;
  phone?: string;
}

// Query keys
const usersKeys = {
  all: ["users"] as const,
  list: () => [...usersKeys.all, "list"] as const,
  detail: (id: string) => [...usersKeys.all, "detail", id] as const,
};

// List users
export function useUsers() {
  return useQuery({
    queryKey: usersKeys.list(),
    queryFn: async () => {
      const response = await apiClient.get<User[]>("/users/");
      return response.data;
    },
  });
}

// Get single user
export function useUser(id: string) {
  return useQuery({
    queryKey: usersKeys.detail(id),
    queryFn: async () => {
      const response = await apiClient.get<User>(`/users/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

// Create user
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: CreateUserPayload) => {
      const response = await apiClient.post<User>("/users/", payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: usersKeys.list() });
    },
  });
}

// Update user
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...payload }: CreateUserPayload & { id: string }) => {
      const response = await apiClient.patch<User>(`/users/${id}/`, payload);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: usersKeys.list() });
      queryClient.invalidateQueries({ queryKey: usersKeys.detail(variables.id) });
    },
  });
}

// Delete user
export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/users/${id}/`);
      return id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: usersKeys.list() });
    },
  });
}

// Reset user password
export function useResetPassword() {
  return useMutation({
    mutationFn: async ({ id, new_password }: { id: string; new_password: string }) => {
      const response = await apiClient.post(`/users/${id}/reset-password/`, {
        new_password,
      });
      return response.data;
    },
  });
}
