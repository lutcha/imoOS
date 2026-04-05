/**
 * Sync Manager — ImoOS Field App
 * Background sync logic com exponential backoff
 */

import { mobileDB } from "@/lib/mobile-db";
import apiClient from "@/lib/api-client";
import type { ActionQueue, PhotoMetadata, VoiceNote, Task } from "@/types/mobile";

// Exponential backoff config
const RETRY_DELAYS = [5000, 15000, 30000, 60000]; // 5s, 15s, 30s, 60s
const MAX_RETRY_ATTEMPTS = 4;

export interface SyncResult {
  success: boolean;
  processed: number;
  failed: number;
  errors: string[];
}

/**
 * Process a single action from the queue
 */
async function processAction(action: ActionQueue): Promise<void> {
  switch (action.type) {
    case "task_complete": {
      const payload = action.payload as { taskId: string };
      await apiClient.patch(`/construction/tasks/${payload.taskId}/`, {
        status: "completed",
      });
      break;
    }

    case "task_update": {
      const payload = action.payload as { taskId: string; status: string };
      await apiClient.patch(`/construction/tasks/${payload.taskId}/`, {
        status: payload.status,
      });
      break;
    }

    case "note_add": {
      const payload = action.payload as { taskId: string; note: string };
      await apiClient.post(`/construction/tasks/${payload.taskId}/notes/`, {
        note: payload.note,
      });
      break;
    }

    case "photo_upload": {
      // Photo upload handled separately (multipart/form-data)
      const payload = action.payload as { photoId: string };
      await uploadPhoto(payload.photoId);
      break;
    }

    case "voice_upload": {
      // Voice upload handled separately
      const payload = action.payload as { voiceId: string };
      await uploadVoiceNote(payload.voiceId);
      break;
    }

    default:
      console.warn("Unknown action type:", (action as ActionQueue).type);
  }
}

/**
 * Upload a photo to the server
 */
async function uploadPhoto(photoId: string): Promise<void> {
  // Get photo from IndexedDB
  const photos = await mobileDB.getUnsyncedPhotos();
  const photo = photos.find((p) => p.id === photoId);
  
  if (!photo || !photo.blob) {
    throw new Error(`Photo ${photoId} not found or missing blob`);
  }

  const formData = new FormData();
  formData.append("file", photo.blob, `${photo.id}.jpg`);
  formData.append("task_id", photo.taskId);
  formData.append("timestamp", photo.timestamp.toString());
  
  if (photo.geolocation) {
    formData.append("latitude", photo.geolocation.latitude.toString());
    formData.append("longitude", photo.geolocation.longitude.toString());
  }

  const response = await apiClient.post(
    `/construction/tasks/${photo.taskId}/photos/`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      timeout: 60000, // 60s for uploads
    }
  );

  // Update photo with remote URL
  const updatedPhoto: PhotoMetadata = {
    ...photo,
    url: response.data.url,
    synced: true,
  };
  await mobileDB.savePhoto(updatedPhoto);
}

/**
 * Upload a voice note to the server
 */
async function uploadVoiceNote(voiceId: string): Promise<void> {
  const voices = await mobileDB.getUnsyncedVoiceNotes();
  const voice = voices.find((v) => v.id === voiceId);
  
  if (!voice || !voice.blob) {
    throw new Error(`Voice note ${voiceId} not found or missing blob`);
  }

  const formData = new FormData();
  formData.append("file", voice.blob, `${voice.id}.webm`);
  formData.append("task_id", voice.taskId);
  formData.append("duration", voice.duration.toString());
  formData.append("timestamp", voice.timestamp.toString());

  const response = await apiClient.post(
    `/construction/tasks/${voice.taskId}/voice-notes/`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      timeout: 60000,
    }
  );

  const updatedVoice: VoiceNote = {
    ...voice,
    url: response.data.url,
    synced: true,
  };
  await mobileDB.saveVoiceNote(updatedVoice);
}

/**
 * Execute sync with retry logic
 */
export async function executeSync(): Promise<SyncResult> {
  const result: SyncResult = {
    success: true,
    processed: 0,
    failed: 0,
    errors: [],
  };

  try {
    // Get pending items
    const actions = await mobileDB.getPendingActions();
    const unsyncedPhotos = await mobileDB.getUnsyncedPhotos();
    const unsyncedVoices = await mobileDB.getUnsyncedVoiceNotes();

    // Process actions
    for (const action of actions) {
      try {
        await processActionWithRetry(action);
        await mobileDB.deleteAction(action.id as unknown as number);
        result.processed++;
      } catch (err) {
        result.failed++;
        const errorMsg = err instanceof Error ? err.message : "Unknown error";
        result.errors.push(`Action ${action.id}: ${errorMsg}`);
        
        // Update action with error
        action.retries++;
        action.error = errorMsg;
      }
    }

    // Process photos
    for (const photo of unsyncedPhotos) {
      try {
        await uploadPhoto(photo.id);
        result.processed++;
      } catch (err) {
        result.failed++;
        const errorMsg = err instanceof Error ? err.message : "Unknown error";
        result.errors.push(`Photo ${photo.id}: ${errorMsg}`);
      }
    }

    // Process voice notes
    for (const voice of unsyncedVoices) {
      try {
        await uploadVoiceNote(voice.id);
        result.processed++;
      } catch (err) {
        result.failed++;
        const errorMsg = err instanceof Error ? err.message : "Unknown error";
        result.errors.push(`Voice ${voice.id}: ${errorMsg}`);
      }
    }

    // Update last sync timestamp
    await mobileDB.setLastSync(Date.now());

    result.success = result.failed === 0;
    return result;

  } catch (err) {
    result.success = false;
    result.errors.push(err instanceof Error ? err.message : "Sync failed");
    return result;
  }
}

/**
 * Process action with exponential backoff retry
 */
async function processActionWithRetry(action: ActionQueue): Promise<void> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= Math.min(action.retries, MAX_RETRY_ATTEMPTS - 1); attempt++) {
    try {
      await processAction(action);
      return; // Success
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));
      
      if (attempt < Math.min(action.retries, MAX_RETRY_ATTEMPTS - 1)) {
        const delay = RETRY_DELAYS[attempt] || RETRY_DELAYS[RETRY_DELAYS.length - 1];
        await sleep(delay);
      }
    }
  }

  throw lastError || new Error("Max retries exceeded");
}

/**
 * Sleep utility
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Register for background sync (if supported)
 */
export async function registerBackgroundSync(): Promise<boolean> {
  if (!("serviceWorker" in navigator)) {
    return false;
  }

  const registration = await navigator.serviceWorker.ready;

  if ("sync" in registration) {
    try {
      await (registration as ServiceWorkerRegistration & { sync: { register: (tag: string) => Promise<void> } }).sync.register("imos-sync");
      return true;
    } catch {
      return false;
    }
  }

  return false;
}

/**
 * Check if background sync is supported
 */
export function isBackgroundSyncSupported(): boolean {
  return "serviceWorker" in navigator && "sync" in ServiceWorkerRegistration.prototype;
}

/**
 * Get sync statistics
 */
export async function getSyncStats(): Promise<{
  pendingActions: number;
  unsyncedPhotos: number;
  unsyncedVoices: number;
  lastSync: number | null;
}> {
  const [actions, photos, voices, lastSync] = await Promise.all([
    mobileDB.getPendingActions(),
    mobileDB.getUnsyncedPhotos(),
    mobileDB.getUnsyncedVoiceNotes(),
    mobileDB.getLastSync(),
  ]);

  return {
    pendingActions: actions.length,
    unsyncedPhotos: photos.length,
    unsyncedVoices: voices.length,
    lastSync,
  };
}
