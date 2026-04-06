import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { useOfflineSync, useNetworkStatus } from "@/hooks/useOfflineSync";
import { mobileDB } from "@/lib/mobile-db";
import { apiSync } from "@/lib/mobile/api-sync";

// Mocks
vi.mock("@/lib/mobile-db", () => ({
  mobileDB: {
    getLastSync: vi.fn(),
    setLastSync: vi.fn(),
    getPendingCount: vi.fn(),
    getPendingActions: vi.fn(),
    getUnsyncedPhotos: vi.fn(),
    getUnsyncedVoiceNotes: vi.fn(),
    getTasks: vi.fn(),
    deleteAction: vi.fn(),
    addAction: vi.fn(),
    saveTask: vi.fn(),
    savePhoto: vi.fn(),
    saveVoiceNote: vi.fn(),
  },
}));

vi.mock("@/lib/mobile/api-sync", () => ({
  apiSync: {
    updateTask: vi.fn(),
    uploadPhoto: vi.fn(),
    uploadVoiceNote: vi.fn(),
    addNote: vi.fn(),
  },
}));

// Mock navigator.onLine
let mockOnline = true;
Object.defineProperty(navigator, "onLine", {
  get: () => mockOnline,
  configurable: true,
});

describe("useOfflineSync", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockOnline = true;
    
    // Default mock returns
    (mobileDB.getLastSync as ReturnType<typeof vi.fn>).mockResolvedValue(null);
    (mobileDB.getPendingCount as ReturnType<typeof vi.fn>).mockResolvedValue(0);
    (mobileDB.getPendingActions as ReturnType<typeof vi.fn>).mockResolvedValue([]);
    (mobileDB.getUnsyncedPhotos as ReturnType<typeof vi.fn>).mockResolvedValue([]);
    (mobileDB.getUnsyncedVoiceNotes as ReturnType<typeof vi.fn>).mockResolvedValue([]);
    (mobileDB.getTasks as ReturnType<typeof vi.fn>).mockResolvedValue([]);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("initializes with online status", async () => {
    mockOnline = true;
    
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.isOnline).toBe(true);
    });
  });

  it("updates offline status when navigator changes", async () => {
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.isOnline).toBe(true);
    });

    // Simulate offline event
    act(() => {
      mockOnline = false;
      window.dispatchEvent(new Event("offline"));
    });

    await waitFor(() => {
      expect(result.current.isOnline).toBe(false);
    });
  });

  it("loads last sync timestamp", async () => {
    const mockTimestamp = Date.now();
    (mobileDB.getLastSync as ReturnType<typeof vi.fn>).mockResolvedValue(mockTimestamp);
    
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.lastSync).toBe(mockTimestamp);
    });
  });

  it("loads pending count on init", async () => {
    (mobileDB.getPendingCount as ReturnType<typeof vi.fn>).mockResolvedValue(5);
    
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.pendingCount).toBe(5);
    });
  });

  it("queues action correctly", async () => {
    const { result } = renderHook(() => useOfflineSync());
    
    await act(async () => {
      await result.current.queueAction({
        type: "task_complete",
        payload: { taskId: "task-1" },
      });
    });

    expect(mobileDB.addAction).toHaveBeenCalledWith(
      expect.objectContaining({
        type: "task_complete",
        payload: { taskId: "task-1" },
        retries: 0,
        maxRetries: 5,
      })
    );
  });

  it("updates task locally", async () => {
    const { result } = renderHook(() => useOfflineSync());
    const mockTask = {
      id: "task-1",
      name: "Test Task",
      status: "completed",
      updatedAt: new Date().toISOString(),
    } as const;
    
    await act(async () => {
      await result.current.updateTaskLocal(mockTask as any);
    });

    expect(mobileDB.saveTask).toHaveBeenCalledWith(mockTask);
  });

  it("syncs pending actions", async () => {
    const mockActions = [
      {
        id: 1,
        type: "task_complete" as const,
        payload: { taskId: "task-1" },
        timestamp: Date.now(),
        retries: 0,
        maxRetries: 5,
      },
    ];
    
    (mobileDB.getPendingActions as ReturnType<typeof vi.fn>).mockResolvedValue(mockActions);
    (apiSync.updateTask as ReturnType<typeof vi.fn>).mockResolvedValue(undefined);
    
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.isOnline).toBe(true);
    });

    await act(async () => {
      await result.current.syncNow();
    });

    expect(apiSync.updateTask).toHaveBeenCalledWith("task-1", { status: "completed" });
    expect(mobileDB.deleteAction).toHaveBeenCalledWith(1);
  });

  it("syncs photos", async () => {
    const mockPhotos = [
      {
        id: "photo-1",
        taskId: "task-1",
        blob: new Blob(["test"]),
        synced: false,
      },
    ];
    
    (mobileDB.getUnsyncedPhotos as ReturnType<typeof vi.fn>).mockResolvedValue(mockPhotos);
    (apiSync.uploadPhoto as ReturnType<typeof vi.fn>).mockResolvedValue({ url: "http://example.com/photo.jpg" });
    
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.isOnline).toBe(true);
    });

    await act(async () => {
      await result.current.syncNow();
    });

    expect(apiSync.uploadPhoto).toHaveBeenCalled();
  });

  it("handles sync errors", async () => {
    const mockActions = [
      {
        id: 1,
        type: "task_complete" as const,
        payload: { taskId: "task-1" },
        timestamp: Date.now(),
        retries: 0,
        maxRetries: 5,
      },
    ];
    
    (mobileDB.getPendingActions as ReturnType<typeof vi.fn>).mockResolvedValue(mockActions);
    (apiSync.updateTask as ReturnType<typeof vi.fn>).mockRejectedValue(new Error("Network error"));
    
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.isOnline).toBe(true);
    });

    await act(async () => {
      await result.current.syncNow();
    });

    expect(result.current.error).toBeTruthy();
  });

  it("does not sync when offline", async () => {
    mockOnline = false;
    
    const { result } = renderHook(() => useOfflineSync());
    
    await act(async () => {
      await result.current.syncNow();
    });

    expect(apiSync.updateTask).not.toHaveBeenCalled();
  });

  it("retries failed actions", async () => {
    const mockActions = [
      {
        id: 1,
        type: "task_complete" as const,
        payload: { taskId: "task-1" },
        timestamp: Date.now(),
        retries: 5,
        maxRetries: 5,
        error: "Failed",
      },
    ];
    
    (mobileDB.getPendingActions as ReturnType<typeof vi.fn>).mockResolvedValue(mockActions);
    (apiSync.updateTask as ReturnType<typeof vi.fn>).mockResolvedValue(undefined);
    
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.isOnline).toBe(true);
    });

    await act(async () => {
      await result.current.retryFailedActions();
    });

    expect(mobileDB.addAction).toHaveBeenCalled();
  });

  it("clears failed actions", async () => {
    const mockActions = [
      {
        id: 1,
        type: "task_complete" as const,
        payload: { taskId: "task-1" },
        timestamp: Date.now(),
        retries: 5,
        maxRetries: 5,
        error: "Failed",
      },
    ];
    
    (mobileDB.getPendingActions as ReturnType<typeof vi.fn>).mockResolvedValue(mockActions);
    
    const { result } = renderHook(() => useOfflineSync());
    
    await waitFor(() => {
      expect(result.current.isOnline).toBe(true);
    });

    await act(async () => {
      await result.current.clearFailedActions();
    });

    expect(mobileDB.deleteAction).toHaveBeenCalledWith(1);
  });

  it("returns sync queue", async () => {
    const mockActions = [
      { id: 1, type: "task_complete" as const, payload: {}, timestamp: Date.now(), retries: 0, maxRetries: 5 },
    ];
    
    (mobileDB.getPendingActions as ReturnType<typeof vi.fn>).mockResolvedValue(mockActions);
    
    const { result } = renderHook(() => useOfflineSync());
    
    const queue = await result.current.getSyncQueue();
    
    expect(queue).toEqual(mockActions);
  });
});

describe("useNetworkStatus", () => {
  it("returns online status", () => {
    mockOnline = true;
    
    const { result } = renderHook(() => useNetworkStatus());
    
    expect(result.current.isOnline).toBe(true);
  });

  it("updates when going offline", () => {
    mockOnline = true;
    
    const { result } = renderHook(() => useNetworkStatus());
    
    act(() => {
      mockOnline = false;
      window.dispatchEvent(new Event("offline"));
    });

    expect(result.current.isOnline).toBe(false);
  });

  it("updates when coming online", () => {
    mockOnline = false;
    
    const { result } = renderHook(() => useNetworkStatus());
    
    act(() => {
      mockOnline = true;
      window.dispatchEvent(new Event("online"));
    });

    expect(result.current.isOnline).toBe(true);
  });
});
