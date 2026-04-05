"use client";

/**
 * useConstructionTasksMobile — ImoOS Field App
 * Hook otimizado para mobile com estratégias de cache agressivas
 * TanStack Query com staleTime de 5 minutos
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTenant } from "@/contexts/TenantContext";
import apiClient from "@/lib/api-client";
import { mobileDB } from "@/lib/mobile-db";
import type { Task, TaskStatus } from "@/types/mobile";

// Query keys
const taskKeys = {
  all: ["mobile-tasks"] as const,
  list: (schema: string, filters?: Record<string, string>) => 
    [...taskKeys.all, schema, "list", filters] as const,
  detail: (schema: string, id: string) => 
    [...taskKeys.all, schema, "detail", id] as const,
};

interface TasksFilters {
  status?: string;
  assigned_to_me?: boolean;
  project_id?: string;
}

/**
 * Hook for fetching tasks optimized for mobile
 * - 5 min stale time (less network requests)
 * - 10 min cache time
 * - No refetch on window focus
 * - 3 retries on failure
 */
export function useConstructionTasksMobile(filters: TasksFilters = {}) {
  const { schema } = useTenant();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: taskKeys.list(schema, filters as Record<string, string>),
    queryFn: async () => {
      // Try network first
      try {
        const response = await apiClient.get("/construction/tasks/", {
          params: {
            ...filters,
            ordering: "due_date",
          },
          timeout: 10000, // 10s timeout for mobile
        });

        const tasks = response.data as Task[];

        // Cache tasks in IndexedDB for offline
        await mobileDB.saveTasks(tasks);

        return tasks;
      } catch (error) {
        // Fallback to cached tasks
        const cachedTasks = await mobileDB.getTasks();
        
        if (cachedTasks.length > 0) {
          // Apply filters locally
          let filtered = cachedTasks;
          
          if (filters.status) {
            const statuses = filters.status.split(",");
            filtered = filtered.filter((t) => statuses.includes(t.status));
          }
          
          if (filters.assigned_to_me) {
            // In real app, filter by current user ID
            // For now, return all
          }

          return filtered;
        }

        throw error;
      }
    },
    // Mobile-optimized cache strategy
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    refetchOnReconnect: true, // Refetch when coming back online
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
    enabled: !!schema,
  });

  return {
    tasks: query.data ?? [],
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    error: query.error,
    refetch: query.refetch,
  };
}

/**
 * Hook for single task detail
 */
export function useConstructionTaskMobile(taskId: string | null) {
  const { schema } = useTenant();

  return useQuery({
    queryKey: taskKeys.detail(schema, taskId ?? ""),
    queryFn: async () => {
      if (!taskId) throw new Error("Task ID required");

      try {
        const response = await apiClient.get(`/construction/tasks/${taskId}/`);
        const task = response.data as Task;
        
        // Update local cache
        await mobileDB.saveTask(task);
        
        return task;
      } catch (error) {
        // Fallback to local cache
        const cached = await mobileDB.getTaskById(taskId);
        if (cached) return cached;
        
        throw error;
      }
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    enabled: !!schema && !!taskId,
  });
}

/**
 * Mutation for updating task status
 */
export function useTaskUpdateMutation() {
  const { schema } = useTenant();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ 
      taskId, 
      status, 
      notes 
    }: { 
      taskId: string; 
      status: TaskStatus; 
      notes?: string;
    }) => {
      const response = await apiClient.patch(`/construction/tasks/${taskId}/`, {
        status,
        notes,
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      // Invalidate task list
      queryClient.invalidateQueries({
        queryKey: taskKeys.list(schema),
      });
      // Invalidate specific task
      queryClient.invalidateQueries({
        queryKey: taskKeys.detail(schema, variables.taskId),
      });
    },
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
  });
}

/**
 * Mutation for uploading photos
 */
export function usePhotoUploadMutation() {
  return useMutation({
    mutationFn: async ({
      taskId,
      file,
      geolocation,
    }: {
      taskId: string;
      file: File;
      geolocation?: { latitude: number; longitude: number };
    }) => {
      const formData = new FormData();
      formData.append("file", file);
      
      if (geolocation) {
        formData.append("latitude", geolocation.latitude.toString());
        formData.append("longitude", geolocation.longitude.toString());
      }

      const response = await apiClient.post(
        `/construction/tasks/${taskId}/photos/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 60000,
        }
      );
      return response.data;
    },
    retry: 2,
    retryDelay: 5000,
  });
}
