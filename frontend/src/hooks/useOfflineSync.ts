"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import { mobileDB } from '@/lib/mobile-db';
import type { SyncStatus, ActionQueue, Task } from '@/types/mobile';

// Constants
const SYNC_INTERVAL = 30000; // 30 segundos
const MAX_RETRIES = 3;

interface UseOfflineSyncReturn extends SyncStatus {
  syncNow: () => Promise<void>;
  queueAction: (action: Omit<ActionQueue, 'id' | 'timestamp' | 'retries' | 'maxRetries'>) => Promise<void>;
  updateTaskLocal: (task: Task) => Promise<void>;
}

export function useOfflineSync(): UseOfflineSyncReturn {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [lastSync, setLastSync] = useState<number | null>(null);
  const [error, setError] = useState<string | undefined>(undefined);
  
  const syncInProgress = useRef<boolean>(false);

  // Initialize online status
  useEffect(() => {
    // Check initial status
    setIsOnline(navigator.onLine);
    
    // Load last sync from DB
    mobileDB.getLastSync().then((timestamp) => {
      setLastSync(timestamp);
    });

    // Update pending count
    updatePendingCount();

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
      // Get pending actions
      const actions = await mobileDB.getPendingActions();
      const unsyncedPhotos = await mobileDB.getUnsyncedPhotos();
      const unsyncedVoices = await mobileDB.getUnsyncedVoiceNotes();

      // Process actions
      for (const action of actions) {
        try {
          await processAction(action);
          await mobileDB.deleteAction(action.id as unknown as number);
        } catch (err) {
          console.error('Failed to process action:', action, err);
          // Increment retry count
          action.retries++;
          if (action.retries >= MAX_RETRIES) {
            action.error = err instanceof Error ? err.message : 'Unknown error';
          }
        }
      }

      // Process photos
      for (const photo of unsyncedPhotos) {
        if (!photo.blob) continue;
        
        try {
          // TODO: Implement actual upload when API is ready
          // await uploadPhoto(photo.blob, photo);
          
          // Mark as synced for now (mock)
          photo.synced = true;
          await mobileDB.savePhoto(photo);
        } catch (err) {
          console.error('Failed to upload photo:', photo.id, err);
        }
      }

      // Process voice notes
      for (const voice of unsyncedVoices) {
        if (!voice.blob) continue;
        
        try {
          // TODO: Implement actual upload when API is ready
          // await uploadVoiceNote(voice.blob, voice);
          
          // Mark as synced for now (mock)
          voice.synced = true;
          await mobileDB.saveVoiceNote(voice);
        } catch (err) {
          console.error('Failed to upload voice note:', voice.id, err);
        }
      }

      // Update last sync timestamp
      const now = Date.now();
      await mobileDB.setLastSync(now);
      setLastSync(now);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sync failed');
    } finally {
      setIsSyncing(false);
      syncInProgress.current = false;
      await updatePendingCount();
    }
  }, [updatePendingCount]);

  const processAction = async (action: ActionQueue): Promise<void> => {
    // TODO: Implement actual API calls when ready
    // For now, just simulate network delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    switch (action.type) {
      case 'task_complete':
        // await apiClient.patch(`/tasks/${action.payload.taskId}/`, { status: 'completed' });
        break;
      case 'task_update':
        // await apiClient.patch(`/tasks/${action.payload.taskId}/`, action.payload.data);
        break;
      case 'note_add':
        // await apiClient.post(`/tasks/${action.payload.taskId}/notes/`, { note: action.payload.note });
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
    if (navigator.onLine) {
      syncNow();
    }
  }, [syncNow, updatePendingCount]);

  const updateTaskLocal = useCallback(async (task: Task): Promise<void> => {
    await mobileDB.saveTask(task);
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
