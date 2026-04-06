"use client";

/**
 * useOfflineSync — ImoOS Field App
 * Sync offline completo com queue, retry exponencial e conflict resolution
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { mobileDB } from '@/lib/mobile-db';
import { apiSync } from '@/lib/mobile/api-sync';
import type { SyncStatus, ActionQueue, Task, PhotoMetadata, VoiceNote } from '@/types/mobile';

// Constants
const SYNC_INTERVAL = 30000; // 30 segundos
const MAX_RETRIES = 5;
const RETRY_DELAYS = [5000, 15000, 30000, 60000, 300000]; // 5s, 15s, 30s, 60s, 5min

interface UseOfflineSyncReturn extends SyncStatus {
  syncNow: () => Promise<void>;
  queueAction: (action: Omit<ActionQueue, 'id' | 'timestamp' | 'retries' | 'maxRetries'>) => Promise<void>;
  updateTaskLocal: (task: Task) => Promise<void>;
  retryFailedActions: () => Promise<void>;
  clearFailedActions: () => Promise<void>;
  getSyncQueue: () => Promise<ActionQueue[]>;
}

export function useOfflineSync(): UseOfflineSyncReturn {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [lastSync, setLastSync] = useState<number | null>(null);
  const [error, setError] = useState<string | undefined>(undefined);
  
  const syncInProgress = useRef<boolean>(false);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize online status
  useEffect(() => {
    const init = async () => {
      setIsOnline(navigator.onLine);
      
      // Load last sync from DB
      const timestamp = await mobileDB.getLastSync();
      setLastSync(timestamp);

      // Update pending count
      await updatePendingCount();
    };
    
    init();

    // Event listeners
    const handleOnline = () => {
      setIsOnline(true);
      setError(undefined);
      // Auto-sync when coming back online
      syncNow();
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  // Periodic sync when online
  useEffect(() => {
    if (!isOnline) return;

    const interval = setInterval(() => {
      if (pendingCount > 0 && !syncInProgress.current) {
        syncNow();
      }
    }, SYNC_INTERVAL);

    return () => clearInterval(interval);
  }, [isOnline, pendingCount]);

  const updatePendingCount = useCallback(async () => {
    const count = await mobileDB.getPendingCount();
    setPendingCount(count);
  }, []);

  const syncNow = useCallback(async () => {
    if (syncInProgress.current || !navigator.onLine) return;

    syncInProgress.current = true;
    setIsSyncing(true);
    setError(undefined);

    try {
      // Sync in order of priority
      await syncTaskUpdates();
      await syncPhotos();
      await syncVoiceNotes();
      await syncActions();

      // Update last sync timestamp
      const now = Date.now();
      await mobileDB.setLastSync(now);
      setLastSync(now);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Falha na sincronização';
      setError(errorMessage);
      console.error('Sync error:', err);
    } finally {
      setIsSyncing(false);
      syncInProgress.current = false;
      await updatePendingCount();
    }
  }, [updatePendingCount]);

  // Sync task updates from local DB to server
  const syncTaskUpdates = async (): Promise<void> => {
    const tasks = await mobileDB.getTasks();
    const modifiedTasks = tasks.filter(t => {
      // Check if task was modified since last sync
      if (!lastSync) return false;
      const updatedAt = new Date(t.updatedAt).getTime();
      return updatedAt > lastSync;
    });

    for (const task of modifiedTasks) {
      try {
        await apiSync.updateTask(task.id, { status: task.status, notes: task.notes });
      } catch (err) {
        console.error('Failed to sync task:', task.id, err);
        throw err;
      }
    }
  };

  // Sync photos to server
  const syncPhotos = async (): Promise<void> => {
    const photos = await mobileDB.getUnsyncedPhotos();
    
    for (const photo of photos) {
      if (!photo.blob) continue;
      
      try {
        await apiSync.uploadPhoto(photo.taskId, photo.blob, photo.geolocation);
        
        // Mark as synced
        photo.synced = true;
        photo.uploadProgress = 100;
        await mobileDB.savePhoto(photo);
      } catch (err) {
        console.error('Failed to upload photo:', photo.id, err);
        // Don't throw, continue with other items
      }
    }
  };

  // Sync voice notes to server
  const syncVoiceNotes = async (): Promise<void> => {
    const voices = await mobileDB.getUnsyncedVoiceNotes();
    
    for (const voice of voices) {
      if (!voice.blob) continue;
      
      try {
        await apiSync.uploadVoiceNote(voice.taskId, voice.blob, voice.duration);
        
        // Mark as synced
        voice.synced = true;
        await mobileDB.saveVoiceNote(voice);
      } catch (err) {
        console.error('Failed to upload voice note:', voice.id, err);
      }
    }
  };

  // Sync action queue
  const syncActions = async (): Promise<void> => {
    const actions = await mobileDB.getPendingActions();
    
    for (const action of actions) {
      try {
        await processAction(action);
        await mobileDB.deleteAction(action.id as unknown as number);
      } catch (err) {
        console.error('Failed to process action:', action, err);
        
        // Increment retry count
        action.retries++;
        if (action.retries >= MAX_RETRIES) {
          action.error = err instanceof Error ? err.message : 'Erro desconhecido';
        }
        
        // Schedule retry with exponential backoff
        if (action.retries < MAX_RETRIES) {
          const delay = RETRY_DELAYS[Math.min(action.retries - 1, RETRY_DELAYS.length - 1)];
          retryTimeoutRef.current = setTimeout(() => {
            syncNow();
          }, delay);
        }
      }
    }
  };

  const processAction = async (action: ActionQueue): Promise<void> => {
    switch (action.type) {
      case 'task_complete':
        await apiSync.updateTask(
          (action.payload as { taskId: string }).taskId, 
          { status: 'completed' }
        );
        break;
      case 'task_update':
        const payload = action.payload as { taskId: string; status: string };
        await apiSync.updateTask(payload.taskId, { status: payload.status });
        break;
      case 'note_add':
        const notePayload = action.payload as { taskId: string; note: string };
        await apiSync.addNote(notePayload.taskId, notePayload.note);
        break;
      case 'photo_upload':
        // Photos are handled separately in syncPhotos
        break;
      case 'voice_upload':
        // Voice notes are handled separately in syncVoiceNotes
        break;
      default:
        console.warn('Unknown action type:', action.type);
    }
  };

  const queueAction = useCallback(async (
    action: Omit<ActionQueue, 'id' | 'timestamp' | 'retries' | 'maxRetries'>
  ): Promise<void> => {
    await mobileDB.addAction({
      ...action,
      timestamp: Date.now(),
      retries: 0,
      maxRetries: MAX_RETRIES,
    });
    
    await updatePendingCount();

    // Try to sync immediately if online
    if (navigator.onLine && !syncInProgress.current) {
      syncNow();
    }
  }, [syncNow, updatePendingCount]);

  const updateTaskLocal = useCallback(async (task: Task): Promise<void> => {
    await mobileDB.saveTask(task);
  }, []);

  const retryFailedActions = useCallback(async (): Promise<void> => {
    const actions = await mobileDB.getPendingActions();
    const failedActions = actions.filter(a => a.error && a.retries >= MAX_RETRIES);
    
    for (const action of failedActions) {
      action.retries = 0;
      action.error = undefined;
      await mobileDB.addAction(action);
    }
    
    await updatePendingCount();
    await syncNow();
  }, [syncNow, updatePendingCount]);

  const clearFailedActions = useCallback(async (): Promise<void> => {
    const actions = await mobileDB.getPendingActions();
    const failedActions = actions.filter(a => a.error && a.retries >= MAX_RETRIES);
    
    for (const action of failedActions) {
      await mobileDB.deleteAction(action.id as unknown as number);
    }
    
    await updatePendingCount();
  }, [updatePendingCount]);

  const getSyncQueue = useCallback(async (): Promise<ActionQueue[]> => {
    return mobileDB.getPendingActions();
  }, []);

  return {
    isOnline,
    isSyncing,
    pendingCount,
    lastSync,
    error,
    syncNow,
    queueAction,
    updateTaskLocal,
    retryFailedActions,
    clearFailedActions,
    getSyncQueue,
  };
}

// Hook for network status only
export function useNetworkStatus(): { isOnline: boolean } {
  const [isOnline, setIsOnline] = useState<boolean>(true);

  useEffect(() => {
    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return { isOnline };
}
