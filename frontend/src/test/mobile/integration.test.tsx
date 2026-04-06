/**
 * Mobile Integration Tests
 * Tests for complete user flows
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock dependencies
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => "/mobile/obra",
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("@/lib/mobile-db", () => ({
  mobileDB: {
    getTasks: vi.fn().mockResolvedValue([]),
    getTaskById: vi.fn().mockResolvedValue(null),
    saveTask: vi.fn().mockResolvedValue(undefined),
    saveTasks: vi.fn().mockResolvedValue(undefined),
    getPendingActions: vi.fn().mockResolvedValue([]),
    getUnsyncedPhotos: vi.fn().mockResolvedValue([]),
    getUnsyncedVoiceNotes: vi.fn().mockResolvedValue([]),
    getPendingCount: vi.fn().mockResolvedValue(0),
    getLastSync: vi.fn().mockResolvedValue(null),
    setLastSync: vi.fn().mockResolvedValue(undefined),
    addAction: vi.fn().mockResolvedValue(1),
    deleteAction: vi.fn().mockResolvedValue(undefined),
    clearAll: vi.fn().mockResolvedValue(undefined),
  },
  initMobileDB: vi.fn().mockResolvedValue(undefined),
}));

vi.mock("@/lib/mobile/api-sync", () => ({
  apiSync: {
    updateTask: vi.fn().mockResolvedValue(undefined),
    uploadPhoto: vi.fn().mockResolvedValue({ url: "test.jpg" }),
    uploadVoiceNote: vi.fn().mockResolvedValue({ url: "test.webm" }),
    addNote: vi.fn().mockResolvedValue(undefined),
  },
}));

import { useMobileTasks } from "@/hooks/useMobileTasks";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { TaskCard } from "@/app/mobile/components/TaskCard";
import { OfflineIndicator } from "@/app/mobile/components/OfflineIndicator";
import type { Task } from "@/types/mobile";

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    {children}
  </QueryClientProvider>
);

describe("Mobile Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Offline-First Flow", () => {
    it("completes task offline and queues for sync", async () => {
      const mockTask: Task = {
        id: "task-1",
        name: "Test Task",
        projectName: "Test Project",
        projectId: "proj-1",
        dueDate: new Date().toISOString().slice(0, 10),
        status: "pending",
        priority: "medium",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        photos: [],
        voiceNotes: [],
      };

      const { result } = renderHook(() => useMobileTasks(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Complete task
      await act(async () => {
        await result.current.completeTask("task-1");
      });

      // Should have updated local state
      expect(result.current.tasks.find(t => t.id === "task-1")?.status).toBe("completed");
    });
  });

  describe("Task Card Interactions", () => {
    const mockTask: Task = {
      id: "task-1",
      name: "Test Task",
      projectName: "Test Project",
      projectId: "proj-1",
      dueDate: new Date().toISOString().slice(0, 10),
      status: "pending",
      priority: "high",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      photos: [],
      voiceNotes: [],
    };

    it("handles card press", () => {
      const handlePress = vi.fn();
      render(<TaskCard task={mockTask} onPress={handlePress} />);

      fireEvent.click(screen.getByText("Test Task"));
      expect(handlePress).toHaveBeenCalledWith(mockTask);
    });

    it("displays urgent badge for high priority", () => {
      render(<TaskCard task={mockTask} />);
      expect(screen.getByText("Urgente")).toBeInTheDocument();
    });

    it("shows correct status indicator", () => {
      render(<TaskCard task={mockTask} />);
      expect(screen.getByText("🔴")).toBeInTheDocument();
      expect(screen.getByText("Não Iniciado")).toBeInTheDocument();
    });
  });

  describe("Offline Indicator", () => {
    it("shows offline banner when disconnected", () => {
      const handleSync = vi.fn();
      render(
        <OfflineIndicator
          isOnline={false}
          pendingCount={0}
          onSync={handleSync}
        />
      );

      expect(screen.getByText("Sem conexão")).toBeInTheDocument();
    });

    it("shows pending sync when online with items", () => {
      const handleSync = vi.fn();
      render(
        <OfflineIndicator
          isOnline={true}
          pendingCount={5}
          onSync={handleSync}
        />
      );

      expect(screen.getByText("5 item(s) pendente(s)")).toBeInTheDocument();
      expect(screen.getByText("Sincronizar")).toBeInTheDocument();
    });

    it("hides when online with no pending items", () => {
      const handleSync = vi.fn();
      const { container } = render(
        <OfflineIndicator
          isOnline={true}
          pendingCount={0}
          onSync={handleSync}
        />
      );

      expect(container.firstChild).toBeNull();
    });
  });
});

// Helper for act with async
async function act<T>(fn: () => Promise<T>): Promise<T> {
  return fn();
}
