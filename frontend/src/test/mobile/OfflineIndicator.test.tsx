import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { OfflineIndicator } from "@/app/mobile/components/OfflineIndicator";

describe("OfflineIndicator", () => {
  it("renders nothing when online with no pending items", () => {
    const { container } = render(
      <OfflineIndicator isOnline={true} pendingCount={0} onSync={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("shows offline message when not online", () => {
    render(<OfflineIndicator isOnline={false} pendingCount={0} onSync={vi.fn()} />);
    
    expect(screen.getByText("Sem conexão")).toBeInTheDocument();
    expect(screen.getByText("📡")).toBeInTheDocument();
  });

  it("shows pending count when online with pending items", () => {
    render(<OfflineIndicator isOnline={true} pendingCount={3} onSync={vi.fn()} />);
    
    expect(screen.getByText("3 item(s) pendente(s)")).toBeInTheDocument();
    expect(screen.getByText("Sincronizar")).toBeInTheDocument();
  });

  it("calls onSync when sync button is clicked", () => {
    const handleSync = vi.fn();
    render(<OfflineIndicator isOnline={true} pendingCount={2} onSync={handleSync} />);
    
    fireEvent.click(screen.getByText("Sincronizar"));
    expect(handleSync).toHaveBeenCalled();
  });

  it("shows sync spinner when isSyncing is true", () => {
    render(
      <OfflineIndicator isOnline={true} pendingCount={2} onSync={vi.fn()} isSyncing={true} />
    );
    
    expect(screen.getByText("A sincronizar...")).toBeInTheDocument();
  });
});
