import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";

// Mocks
vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

vi.mock("@/app/register-sw", () => ({
  usePWAStatus: vi.fn(),
}));

vi.mock("@/lib/mobile-db", () => ({
  mobileDB: {
    clearAll: vi.fn(),
  },
}));

import { usePWAStatus } from "@/app/register-sw";
import { mobileDB } from "@/lib/mobile-db";
import SettingsPage from "@/app/mobile/settings/page";

describe("SettingsPage", () => {
  const mockPush = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as ReturnType<typeof vi.fn>).mockReturnValue({ push: mockPush });
    
    // Default PWA status
    (usePWAStatus as ReturnType<typeof vi.fn>).mockReturnValue({
      canInstall: false,
      isInstalled: false,
      install: vi.fn(),
    });

    // Mock navigator.storage
    Object.defineProperty(navigator, "storage", {
      value: {
        estimate: vi.fn().mockResolvedValue({ usage: 1024 * 1024, quota: 1024 * 1024 * 100 }),
      },
      writable: true,
    });
  });

  it("renders page title", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Configurações")).toBeInTheDocument();
  });

  it("shows user info", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Encarregado de Obra")).toBeInTheDocument();
    expect(screen.getByText("Residencial Palmira")).toBeInTheDocument();
  });

  it("shows install prompt when canInstall is true", () => {
    (usePWAStatus as ReturnType<typeof vi.fn>).mockReturnValue({
      canInstall: true,
      isInstalled: false,
      install: vi.fn(),
    });

    render(<SettingsPage />);
    
    expect(screen.getByText("Instalar Aplicação")).toBeInTheDocument();
    expect(screen.getByText("Instalar Agora")).toBeInTheDocument();
  });

  it("shows installed status when isInstalled is true", () => {
    (usePWAStatus as ReturnType<typeof vi.fn>).mockReturnValue({
      canInstall: false,
      isInstalled: true,
      install: vi.fn(),
    });

    render(<SettingsPage />);
    
    expect(screen.getByText("Aplicação Instalada")).toBeInTheDocument();
  });

  it("renders general settings section", () => {
    render(<SettingsPage />);
    
    expect(screen.getByText("Geral")).toBeInTheDocument();
    expect(screen.getByText("Notificações")).toBeInTheDocument();
    expect(screen.getByText("Sync Automático")).toBeInTheDocument();
    expect(screen.getByText("Modo Escuro")).toBeInTheDocument();
  });

  it("renders storage settings section", () => {
    render(<SettingsPage />);
    
    expect(screen.getByText("Armazenamento")).toBeInTheDocument();
    expect(screen.getByText("Dados Locais")).toBeInTheDocument();
    expect(screen.getByText("Limpar Cache Local")).toBeInTheDocument();
  });

  it("renders about section", () => {
    render(<SettingsPage />);
    
    expect(screen.getByText("Sobre")).toBeInTheDocument();
    expect(screen.getByText("Versão")).toBeInTheDocument();
    expect(screen.getByText("1.0.0")).toBeInTheDocument();
    expect(screen.getByText("Termos de Uso")).toBeInTheDocument();
    expect(screen.getByText("Política de Privacidade")).toBeInTheDocument();
  });

  it("renders logout button", () => {
    render(<SettingsPage />);
    
    expect(screen.getByText("Terminar Sessão")).toBeInTheDocument();
  });

  it("shows storage usage when available", async () => {
    render(<SettingsPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/usados/)).toBeInTheDocument();
    });
  });

  it("calls install when install button clicked", () => {
    const mockInstall = vi.fn();
    (usePWAStatus as ReturnType<typeof vi.fn>).mockReturnValue({
      canInstall: true,
      isInstalled: false,
      install: mockInstall,
    });

    render(<SettingsPage />);
    
    fireEvent.click(screen.getByText("Instalar Agora"));
    expect(mockInstall).toHaveBeenCalled();
  });

  it("navigates to terms page", () => {
    render(<SettingsPage />);
    
    fireEvent.click(screen.getByText("Termos de Uso"));
    expect(mockPush).toHaveBeenCalledWith("/terms");
  });

  it("navigates to privacy page", () => {
    render(<SettingsPage />);
    
    fireEvent.click(screen.getByText("Política de Privacidade"));
    expect(mockPush).toHaveBeenCalledWith("/privacy");
  });
});
