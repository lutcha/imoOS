/**
 * API Sync — ImoOS Field App
 * Cliente de API otimizado para sync offline
 */

import apiClient from '@/lib/api-client';
import type { TaskStatus } from '@/types/mobile';

interface TaskUpdateData {
  status?: TaskStatus;
  notes?: string;
}

interface GeolocationData {
  latitude: number;
  longitude: number;
  accuracy?: number;
}

/**
 * API Sync Manager
 * Handles all API calls for offline sync
 */
class ApiSyncManager {
  private abortControllers: Map<string, AbortController> = new Map();

  /**
   * Update task status
   */
  async updateTask(taskId: string, data: TaskUpdateData): Promise<void> {
    const controller = new AbortController();
    this.abortControllers.set(`task-${taskId}`, controller);

    try {
      await apiClient.patch(`/construction/tasks/${taskId}/`, data, {
        signal: controller.signal,
        timeout: 30000,
      });
    } finally {
      this.abortControllers.delete(`task-${taskId}`);
    }
  }

  /**
   * Add note to task
   */
  async addNote(taskId: string, note: string): Promise<void> {
    const controller = new AbortController();
    this.abortControllers.set(`note-${taskId}`, controller);

    try {
      await apiClient.post(`/construction/tasks/${taskId}/notes/`, {
        content: note,
        created_at: new Date().toISOString(),
      }, {
        signal: controller.signal,
        timeout: 30000,
      });
    } finally {
      this.abortControllers.delete(`note-${taskId}`);
    }
  }

  /**
   * Upload photo with progress tracking
   */
  async uploadPhoto(
    taskId: string, 
    blob: Blob, 
    geolocation?: GeolocationData
  ): Promise<{ url: string; id: string }> {
    const controller = new AbortController();
    this.abortControllers.set(`photo-${taskId}`, controller);

    try {
      const formData = new FormData();
      formData.append('file', blob, `photo-${Date.now()}.jpg`);
      
      if (geolocation) {
        formData.append('latitude', geolocation.latitude.toString());
        formData.append('longitude', geolocation.longitude.toString());
        if (geolocation.accuracy) {
          formData.append('accuracy', geolocation.accuracy.toString());
        }
      }

      const response = await apiClient.post(
        `/construction/tasks/${taskId}/photos/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          signal: controller.signal,
          timeout: 120000, // 2 min for large photos
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              this.onUploadProgress(taskId, progress);
            }
          },
        }
      );

      return response.data;
    } finally {
      this.abortControllers.delete(`photo-${taskId}`);
    }
  }

  /**
   * Upload voice note
   */
  async uploadVoiceNote(
    taskId: string, 
    blob: Blob, 
    duration: number
  ): Promise<{ url: string; id: string }> {
    const controller = new AbortController();
    this.abortControllers.set(`voice-${taskId}`, controller);

    try {
      const formData = new FormData();
      formData.append('file', blob, `voice-${Date.now()}.webm`);
      formData.append('duration', duration.toString());

      const response = await apiClient.post(
        `/construction/tasks/${taskId}/voice-notes/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          signal: controller.signal,
          timeout: 60000,
        }
      );

      return response.data;
    } finally {
      this.abortControllers.delete(`voice-${taskId}`);
    }
  }

  /**
   * Cancel all pending requests
   */
  cancelAll(): void {
    this.abortControllers.forEach((controller) => {
      controller.abort();
    });
    this.abortControllers.clear();
  }

  /**
   * Upload progress callback (can be overridden)
   */
  onUploadProgress(taskId: string, progress: number): void {
    // Emit event or update store
    if (typeof window !== 'undefined') {
      window.dispatchEvent(
        new CustomEvent('upload-progress', {
          detail: { taskId, progress },
        })
      );
    }
  }
}

export const apiSync = new ApiSyncManager();
