/**
 * Types for Mobile Construction Module
 * Optimized for offline-first PWA
 */

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'blocked';
export type TaskPriority = 'high' | 'medium' | 'low';

export interface Task {
  id: string;
  name: string;
  description?: string;
  projectName: string;
  projectId: string;
  dueDate: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignedTo?: string;
  createdAt: string;
  updatedAt: string;
  photos?: PhotoMetadata[];
  voiceNotes?: VoiceNote[];
  notes?: string;
  location?: GeolocationCoordinates;
}

export interface PhotoMetadata {
  id: string;
  taskId: string;
  url?: string; // URL remota (após upload)
  localUrl: string; // Blob URL local
  blob?: Blob; // Dados binários para upload posterior
  timestamp: number;
  geolocation?: {
    latitude: number;
    longitude: number;
    accuracy?: number;
  };
  synced: boolean;
  uploadProgress?: number;
}

export interface VoiceNote {
  id: string;
  taskId: string;
  url?: string; // URL remota
  localUrl: string;
  blob?: Blob;
  duration: number; // segundos
  timestamp: number;
  transcription?: string;
  synced: boolean;
}

export interface ActionQueue {
  id: string;
  type: 'task_complete' | 'task_update' | 'photo_upload' | 'voice_upload' | 'note_add';
  payload: unknown;
  timestamp: number;
  retries: number;
  maxRetries: number;
  error?: string;
}

export interface OfflineStorage {
  tasks: Task[];
  photos: PhotoMetadata[];
  actions: ActionQueue[];
  lastSync: number | null;
}

export interface SyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  pendingCount: number;
  lastSync: number | null;
  error?: string;
}

export interface MobileUser {
  id: string;
  name: string;
  role: 'foreman' | 'worker' | 'supervisor';
  avatar?: string;
}

// Geolocation position com propriedades opcionais para Safari iOS
export interface GeolocationCoordinates {
  latitude: number;
  longitude: number;
  altitude?: number | null;
  accuracy: number;
  altitudeAccuracy?: number | null;
  heading?: number | null;
  speed?: number | null;
}
