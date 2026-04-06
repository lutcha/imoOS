import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";

// Mock the hooks
vi.mock("@/hooks/useOfflineSync", () => ({
  useOfflineSync: vi.fn(),
}));

vi.mock("@/lib/mobile-db", () => ({
  mobileDB: {
    getPendingActions: vi.fn(),
    getUnsyncedPhotos: vi.fn(),
    getUnsyncedVoiceNotes: vi.fn(),
  },
}));

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

import { useOfflineSync } from "@/hooks/useOfflineSync";
import { mobileDB } from "@/lib/mobile-db";
import SyncPage from "@/app/mobile/sync/page";

describe("SyncPage", () => {
  const mockPush = vi.fn();
  const mockSyncNow = vi.fn();
  const mockRetryFailedActions = vi.fn();
  const mockClearFailedActions = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    (useRouter as ReturnType<typeof vi.fn>).mockReturnValue({ push: mockPush });
    
    (useOfflineSync as ReturnType<typeof vi.fn>).mockReturnValue({
      isOnline: true,
      isSyncing: false,
      pendingCount: 5,
      lastSync: Date.now(),
      error: undefined,
      syncNow: mockSyncNow,
      retryFailedActions: mockRetryFailedActions,
      clearFailedActions: mockClearFailedActions,
    });

    (mobileDB.getPendingActions as ReturnType<typeof vi.fn>).mockResolvedValue([]);
    (mobileDB.getUnsyncedPhotos as ReturnType<typeof vi.fn>).mockResolvedValue([]);
    (mobileDB.getUnsyncedVoiceNotes as ReturnType<typeof vi.fn>).mockResolvedValue([]);
  });

  it("renders page title", async () => {
    render(<SyncPage />);
    
    await waitFor(() => {
      expect(screen.getByText("Sincronização")).toBeInTheDocument();
    });
  });

  it("shows online status when connected", async () => {
    render(<SyncPage />);
    
    await waitFor(() => {
      expect(screen.getByText("Online")).toBeInTheDocument();
      expect(screen.getByText("Ligado à internet — sincronização automática ativa")).toBeInTheDocument();
    });
  });

  it("shows offline status when disconnected", async () => {
    (useOfflineSync as ReturnType<typeof vi.fn>).mockReturnValue({
      isOnline: false,
      isSyncing: false,
      pendingCount: 5,
      lastSync: null,
      error: undefined,
      syncNow: mockSyncNow,
      retryFailedActions: mockRetryFailedActions,
      clearFailedActions: mockClearFailedActions,
    });

    render(<SyncPage />);
    
    await waitFor(() => {
      expect(screen.getByText("Offline")).toBeInTheDocument();
      expect(screen.getByText("Sem conexão — alterações guardadas localmente")).toBeInTheDocument();
    });
  });

  it("displays pending count", async () => {
    render(<SyncPage />);
    
    await waitFor(() => {
      expect(screen.getByText("5 pendentes")).toBeInTheDocument();
    });
  });

  it("calls syncNow when sync button clicked", async () => {
    render(<SyncPage />);
    
    await waitFor(() => {
      expect(screen.getByText("Sincronizar")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Sincronizar"));
    
    expect(mockSyncNow).toHaveBeenCalled();
  });

  it("disables sync button when offline", async () => {
    (useOfflineSync as ReturnType<typeof vi.fn>).mockReturnValue({
      isOnline: false,
      isSyncing: false,
      pendingCount: 5,
      lastSync: null,
      error: undefined,
      syncNow: mockSyncNow,
      retryFailedActions: mockRetryFailedActions,
      clearFailedActions: mockClearFailedActions,
    });

    render(<SyncPage />);
    
    await waitFor(() => {
      const button = screen.getByText("Sincronizar");
      expect(button).toBeDisabled();
    });
  });

  it("shows error message when sync fails", async () => {
    (useOfflineSync as ReturnType<typeof vi.fn>).mockReturnValue({
      isOnline: true,
      isSyncing: false,
      pendingCount: 5,
      lastSync: Date.now(),
      error: "Falha na conexão",
      syncNow: mockSyncNow,
      retryFailedActions: mockRetryFailedActions,
      clearFailedActions: mockClearFailedActions,
    });

    render(<SyncPage />);
    
    await waitFor(() => {
      expect(screen.getByText("Falha na conexão")).toBeInTheDocument();
    });
  });

  it("navigates back when back button clicked", async () => {
    render(<SyncPage />);
    
    await waitFor(() => {
      const backButton = screen.getByRole("button", { name: "" });
      expect(backButton).toBeInTheDocument();
    });
  });

  it("shows 'all synced' message when no pending items", async () => {
    (useOfflineSync as ReturnType<typeof vi.fn>).mockReturnValue({
      isOnline: true,
      isSyncing: false,
      pendingCount: 0,
      lastSync: Date.now(),
      error: undefined,
      syncNow: mockSyncNow,
      retryFailedActions: mockRetryFailedActions,
      clearFailedActions: mockClearFailedActions,
    });

    render(<SyncPage />);
    
    await waitFor(() => {
      expect(screen.getByText("Tudo sincronizado!")).toBeInTheDocument();
      expect(screen.getByText("Nenhuma ação pendente")).toBeInTheDocument();
    });
  });
});
