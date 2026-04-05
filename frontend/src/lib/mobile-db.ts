/**
 * IndexedDB wrapper for offline storage
 * Mobile-first construction module
 */

import type { Task, PhotoMetadata, VoiceNote, ActionQueue } from '@/types/mobile';

const DB_NAME = 'imos_mobile_db';
const DB_VERSION = 1;

const STORES = {
  tasks: 'tasks',
  photos: 'photos',
  voiceNotes: 'voiceNotes',
  actions: 'actions',
  syncMeta: 'syncMeta',
} as const;

interface SyncMeta {
  key: string;
  value: number | string | null;
}

class MobileDatabase {
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Tasks store
        if (!db.objectStoreNames.contains(STORES.tasks)) {
          const taskStore = db.createObjectStore(STORES.tasks, { keyPath: 'id' });
          taskStore.createIndex('status', 'status', { unique: false });
          taskStore.createIndex('dueDate', 'dueDate', { unique: false });
          taskStore.createIndex('projectId', 'projectId', { unique: false });
        }

        // Photos store
        if (!db.objectStoreNames.contains(STORES.photos)) {
          const photoStore = db.createObjectStore(STORES.photos, { keyPath: 'id' });
          photoStore.createIndex('taskId', 'taskId', { unique: false });
          photoStore.createIndex('synced', 'synced', { unique: false });
        }

        // Voice notes store
        if (!db.objectStoreNames.contains(STORES.voiceNotes)) {
          const voiceStore = db.createObjectStore(STORES.voiceNotes, { keyPath: 'id' });
          voiceStore.createIndex('taskId', 'taskId', { unique: false });
          voiceStore.createIndex('synced', 'synced', { unique: false });
        }

        // Actions queue store
        if (!db.objectStoreNames.contains(STORES.actions)) {
          const actionStore = db.createObjectStore(STORES.actions, { 
            keyPath: 'id',
            autoIncrement: true 
          });
          actionStore.createIndex('timestamp', 'timestamp', { unique: false });
          actionStore.createIndex('type', 'type', { unique: false });
        }

        // Sync metadata store
        if (!db.objectStoreNames.contains(STORES.syncMeta)) {
          db.createObjectStore(STORES.syncMeta, { keyPath: 'key' });
        }
      };
    });
  }

  private getStore(storeName: string, mode: IDBTransactionMode = 'readonly'): IDBObjectStore {
    if (!this.db) throw new Error('Database not initialized');
    const transaction = this.db.transaction(storeName, mode);
    return transaction.objectStore(storeName);
  }

  // Tasks
  async saveTask(task: Task): Promise<void> {
    const store = this.getStore(STORES.tasks, 'readwrite');
    return new Promise((resolve, reject) => {
      const request = store.put(task);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async saveTasks(tasks: Task[]): Promise<void> {
    const store = this.getStore(STORES.tasks, 'readwrite');
    return new Promise((resolve, reject) => {
      let completed = 0;
      let hasError = false;

      tasks.forEach((task) => {
        const request = store.put(task);
        request.onsuccess = () => {
          completed++;
          if (completed === tasks.length && !hasError) resolve();
        };
        request.onerror = () => {
          hasError = true;
          reject(request.error);
        };
      });

      if (tasks.length === 0) resolve();
    });
  }

  async getTasks(): Promise<Task[]> {
    const store = this.getStore(STORES.tasks);
    return new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result as Task[]);
      request.onerror = () => reject(request.error);
    });
  }

  async getTaskById(id: string): Promise<Task | undefined> {
    const store = this.getStore(STORES.tasks);
    return new Promise((resolve, reject) => {
      const request = store.get(id);
      request.onsuccess = () => resolve(request.result as Task | undefined);
      request.onerror = () => reject(request.error);
    });
  }

  async getTasksByStatus(status: Task['status']): Promise<Task[]> {
    const store = this.getStore(STORES.tasks);
    return new Promise((resolve, reject) => {
      const request = store.index('status').getAll(status);
      request.onsuccess = () => resolve(request.result as Task[]);
      request.onerror = () => reject(request.error);
    });
  }

  // Photos
  async savePhoto(photo: PhotoMetadata): Promise<void> {
    const store = this.getStore(STORES.photos, 'readwrite');
    return new Promise((resolve, reject) => {
      const request = store.put(photo);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getPhotosByTask(taskId: string): Promise<PhotoMetadata[]> {
    const store = this.getStore(STORES.photos);
    return new Promise((resolve, reject) => {
      const request = store.index('taskId').getAll(taskId);
      request.onsuccess = () => resolve(request.result as PhotoMetadata[]);
      request.onerror = () => reject(request.error);
    });
  }

  async getUnsyncedPhotos(): Promise<PhotoMetadata[]> {
    const store = this.getStore(STORES.photos);
    return new Promise((resolve, reject) => {
      const request = store.index('synced').openCursor();
      const results: PhotoMetadata[] = [];
      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          if (cursor.value.synced === false) {
            results.push(cursor.value as PhotoMetadata);
          }
          cursor.continue();
        } else {
          resolve(results);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  async deletePhoto(id: string): Promise<void> {
    const store = this.getStore(STORES.photos, 'readwrite');
    return new Promise((resolve, reject) => {
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // Voice notes
  async saveVoiceNote(note: VoiceNote): Promise<void> {
    const store = this.getStore(STORES.voiceNotes, 'readwrite');
    return new Promise((resolve, reject) => {
      const request = store.put(note);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getVoiceNotesByTask(taskId: string): Promise<VoiceNote[]> {
    const store = this.getStore(STORES.voiceNotes);
    return new Promise((resolve, reject) => {
      const request = store.index('taskId').getAll(taskId);
      request.onsuccess = () => resolve(request.result as VoiceNote[]);
      request.onerror = () => reject(request.error);
    });
  }

  async getUnsyncedVoiceNotes(): Promise<VoiceNote[]> {
    const store = this.getStore(STORES.voiceNotes);
    return new Promise((resolve, reject) => {
      const request = store.index('synced').openCursor();
      const results: VoiceNote[] = [];
      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          if (cursor.value.synced === false) {
            results.push(cursor.value as VoiceNote);
          }
          cursor.continue();
        } else {
          resolve(results);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  // Action queue
  async addAction(action: Omit<ActionQueue, 'id'>): Promise<number> {
    const store = this.getStore(STORES.actions, 'readwrite');
    return new Promise((resolve, reject) => {
      const request = store.add(action);
      request.onsuccess = () => resolve(request.result as number);
      request.onerror = () => reject(request.error);
    });
  }

  async getPendingActions(): Promise<ActionQueue[]> {
    const store = this.getStore(STORES.actions);
    return new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result as ActionQueue[]);
      request.onerror = () => reject(request.error);
    });
  }

  async deleteAction(id: number): Promise<void> {
    const store = this.getStore(STORES.actions, 'readwrite');
    return new Promise((resolve, reject) => {
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async clearSyncedActions(): Promise<void> {
    const actions = await this.getPendingActions();
    const syncedActions = actions.filter(a => a.retries >= a.maxRetries || !a.error);
    
    for (const action of syncedActions) {
      await this.deleteAction(action.id as number);
    }
  }

  // Sync metadata
  async setLastSync(timestamp: number): Promise<void> {
    const store = this.getStore(STORES.syncMeta, 'readwrite');
    return new Promise((resolve, reject) => {
      const request = store.put({ key: 'lastSync', value: timestamp });
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getLastSync(): Promise<number | null> {
    const store = this.getStore(STORES.syncMeta);
    return new Promise((resolve, reject) => {
      const request = store.get('lastSync');
      request.onsuccess = () => {
        const result = request.result as SyncMeta | undefined;
        resolve(result?.value as number | null ?? null);
      };
      request.onerror = () => reject(request.error);
    });
  }

  // Get pending items count
  async getPendingCount(): Promise<number> {
    const [unsyncedPhotos, unsyncedVoices, pendingActions] = await Promise.all([
      this.getUnsyncedPhotos(),
      this.getUnsyncedVoiceNotes(),
      this.getPendingActions(),
    ]);

    return unsyncedPhotos.length + unsyncedVoices.length + pendingActions.length;
  }

  // Clear all data (logout)
  async clearAll(): Promise<void> {
    if (!this.db) return;
    
    const stores = Object.values(STORES);
    for (const storeName of stores) {
      const store = this.getStore(storeName, 'readwrite');
      await new Promise<void>((resolve, reject) => {
        const request = store.clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    }
  }
}

// Singleton instance
export const mobileDB = new MobileDatabase();

// Initialize database
export async function initMobileDB(): Promise<void> {
  return mobileDB.init();
}
