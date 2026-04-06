import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { useMobileTasks, useMobileTask } from "@/hooks/useMobileTasks";
import { mobileDB } from "@/lib/mobile-db";
import type { Task } from "@/types/mobile";

// Mock mobileDB
vi.mock("@/lib/mobile-db", () => ({
  mobileDB: {
    getTasks: vi.fn(),
    getTaskById: vi.fn(),
    saveTask: vi.fn(),
    saveTasks: vi.fn(),
  },
}));

const mockTasks: Task[] = [
  {
    id: "task-1",
    name: "Test Task 1",
    projectName: "Project A",
    projectId: "proj-1",
    dueDate: "2025-01-15",
    status: "pending",
    priority: "high",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    photos: [],
    voiceNotes: [],
  },
  {
    id: "task-2",
    name: "Test Task 2",
    projectName: "Project B",
    projectId: "proj-2",
    dueDate: "2025-01-10",
    status: "completed",
    priority: "medium",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    photos: [],
    voiceNotes: [],
  },
  {
    id: "task-3",
    name: "Another Task",
    projectName: "Project A",
    projectId: "proj-1",
    dueDate: "2025-01-20",
    status: "in_progress",
    priority: "low",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    photos: [],
    voiceNotes: [],
    description: "Test description",
  },
];

describe("useMobileTasks", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (mobileDB.getTasks as ReturnType<typeof vi.fn>).mockResolvedValue(mockTasks);
  });

  it("loads tasks on mount", async () => {
    const { result } = renderHook(() => useMobileTasks());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.tasks).toEqual(mockTasks);
    expect(result.current.error).toBeNull();
  });

  it("loads mock tasks when DB is empty", async () => {
    (mobileDB.getTasks as ReturnType<typeof vi.fn>).mockResolvedValue([]);

    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.tasks.length).toBeGreaterThan(0);
    expect(mobileDB.saveTasks).toHaveBeenCalled();
  });

  it("handles error when loading tasks", async () => {
    (mobileDB.getTasks as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error("DB Error")
    );

    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe("DB Error");
  });

  it("refreshes tasks", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    (mobileDB.getTasks as ReturnType<typeof vi.fn>).mockResolvedValue([
      ...mockTasks,
      { ...mockTasks[0], id: "task-4", name: "New Task" },
    ]);

    await act(async () => {
      await result.current.refresh();
    });

    expect(result.current.tasks).toHaveLength(4);
  });

  it("completes a task", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.completeTask("task-1");
    });

    const completedTask = result.current.tasks.find((t) => t.id === "task-1");
    expect(completedTask?.status).toBe("completed");
    expect(mobileDB.saveTask).toHaveBeenCalled();
  });

  it("updates task status", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.updateTaskStatus("task-1", "in_progress");
    });

    const updatedTask = result.current.tasks.find((t) => t.id === "task-1");
    expect(updatedTask?.status).toBe("in_progress");
  });

  it("adds note to task", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.addNote("task-1", "New note");
    });

    const updatedTask = result.current.tasks.find((t) => t.id === "task-1");
    expect(updatedTask?.notes).toContain("New note");
  });

  it("searches tasks by name", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const searchResults = result.current.searchTasks("Another");
    expect(searchResults).toHaveLength(1);
    expect(searchResults[0].name).toBe("Another Task");
  });

  it("searches tasks by description", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const searchResults = result.current.searchTasks("Test description");
    expect(searchResults).toHaveLength(1);
    expect(searchResults[0].id).toBe("task-3");
  });

  it("filters tasks by status", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const filtered = result.current.filterTasks({ status: ["completed"] });
    expect(filtered).toHaveLength(1);
    expect(filtered[0].status).toBe("completed");
  });

  it("filters tasks by priority", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const filtered = result.current.filterTasks({ priority: ["high"] });
    expect(filtered).toHaveLength(1);
    expect(filtered[0].priority).toBe("high");
  });

  it("sorts tasks by due date", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const sorted = result.current.sortTasks(mockTasks, "dueDate");
    expect(sorted[0].dueDate).toBe("2025-01-10");
    expect(sorted[2].dueDate).toBe("2025-01-20");
  });

  it("sorts tasks by priority", async () => {
    const { result } = renderHook(() => useMobileTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const sorted = result.current.sortTasks(mockTasks, "priority");
    expect(sorted[0].priority).toBe("high");
    expect(sorted[2].priority).toBe("low");
  });
});

describe("useMobileTask", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (mobileDB.getTaskById as ReturnType<typeof vi.fn>).mockImplementation((id) => {
      return Promise.resolve(mockTasks.find((t) => t.id === id));
    });
  });

  it("loads single task", async () => {
    const { result } = renderHook(() => useMobileTask("task-1"));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.task?.name).toBe("Test Task 1");
  });

  it("returns undefined for non-existent task", async () => {
    (mobileDB.getTaskById as ReturnType<typeof vi.fn>).mockResolvedValue(undefined);

    const { result } = renderHook(() => useMobileTask("non-existent"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.task).toBeUndefined();
  });

  it("does not load when taskId is null", async () => {
    const { result } = renderHook(() => useMobileTask(null));

    expect(result.current.isLoading).toBe(false);
    expect(result.current.task).toBeUndefined();
  });

  it("refreshes task", async () => {
    const { result } = renderHook(() => useMobileTask("task-1"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const updatedTask = { ...mockTasks[0], name: "Updated Name" };
    (mobileDB.getTaskById as ReturnType<typeof vi.fn>).mockResolvedValue(updatedTask);

    await act(async () => {
      await result.current.refresh();
    });

    expect(result.current.task?.name).toBe("Updated Name");
  });
});
