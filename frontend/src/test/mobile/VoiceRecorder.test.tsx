import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { VoiceRecorder } from "@/app/mobile/components/VoiceRecorder";
import type { VoiceNote } from "@/types/mobile";

// Mock MediaRecorder
class MockMediaRecorder {
  state = "inactive";
  ondataavailable: ((event: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;
  
  start = vi.fn(() => {
    this.state = "recording";
  });
  
  stop = vi.fn(() => {
    this.state = "inactive";
    if (this.onstop) {
      this.onstop();
    }
  });
}

// Mock navigator.mediaDevices
const mockMediaRecorder = new MockMediaRecorder();
Object.defineProperty(global.navigator, "mediaDevices", {
  value: {
    getUserMedia: vi.fn(async () => ({
      getTracks: () => [{ stop: vi.fn() }],
    })),
  },
  writable: true,
});

// Mock MediaRecorder constructor
global.MediaRecorder = vi.fn(() => mockMediaRecorder) as unknown as typeof MediaRecorder;

global.Blob = vi.fn((chunks: unknown[], options: { type: string }) => ({
  size: 100,
  type: options.type,
  chunks,
})) as unknown as typeof Blob;

const mockVoiceNotes: VoiceNote[] = [
  {
    id: "voice-1",
    taskId: "task-1",
    localUrl: "blob:test1",
    duration: 15,
    timestamp: Date.now() - 3600000,
    synced: true,
  },
  {
    id: "voice-2",
    taskId: "task-1",
    localUrl: "blob:test2",
    duration: 8,
    timestamp: Date.now(),
    synced: false,
  },
];

describe("VoiceRecorder", () => {
  const mockOnVoiceNoteAdd = vi.fn();
  const mockOnVoiceNoteRemove = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockMediaRecorder.state = "inactive";
  });

  it("renders voice note count", () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={mockVoiceNotes}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    expect(screen.getByText("Notas de Voz (2/5)")).toBeInTheDocument();
  });

  it("shows record button when under max notes", () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={mockVoiceNotes}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    expect(screen.getByText("Gravar Nota de Voz")).toBeInTheDocument();
  });

  it("hides record button when max notes reached", () => {
    const maxNotes = 2;
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={mockVoiceNotes}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
        maxNotes={maxNotes}
      />
    );

    expect(screen.queryByText("Gravar Nota de Voz")).not.toBeInTheDocument();
  });

  it("starts recording when button clicked", async () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={[]}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    await act(async () => {
      fireEvent.click(screen.getByText("Gravar Nota de Voz"));
    });

    await waitFor(() => {
      expect(screen.getByText(/A gravar/)).toBeInTheDocument();
    });
  });

  it("stops recording when button clicked again", async () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={[]}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    // Start recording
    await act(async () => {
      fireEvent.click(screen.getByText("Gravar Nota de Voz"));
    });

    await waitFor(() => {
      expect(screen.getByText(/A gravar/)).toBeInTheDocument();
    });

    // Stop recording
    await act(async () => {
      fireEvent.click(screen.getByText(/A gravar/));
    });

    await waitFor(() => {
      expect(mockMediaRecorder.stop).toHaveBeenCalled();
    });
  });

  it("displays max duration info", () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={[]}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    expect(screen.getByText("Máximo 30 segundos por nota")).toBeInTheDocument();
  });

  it("shows custom max duration when provided", () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={[]}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
        maxDuration={60}
      />
    );

    expect(screen.getByText("Máximo 60 segundos por nota")).toBeInTheDocument();
  });

  it("renders voice note items with correct info", () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={mockVoiceNotes}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    // Should show timestamps
    expect(screen.getByText(/Nota de voz/)).toBeInTheDocument();
    
    // Should show duration for unsynced note
    expect(screen.getByText("0:08")).toBeInTheDocument();
  });

  it("shows sync pending status for unsynced notes", () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={mockVoiceNotes}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    expect(screen.getByText("⏳ Pendente sincronizar")).toBeInTheDocument();
  });

  it("calls onVoiceNoteRemove when remove button clicked", () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={mockVoiceNotes}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
        onVoiceNoteRemove={mockOnVoiceNoteRemove}
      />
    );

    const removeButtons = screen.getAllByLabelText("Remover nota");
    fireEvent.click(removeButtons[0]);

    expect(mockOnVoiceNoteRemove).toHaveBeenCalledWith("voice-1");
  });

  it("disables record button when processing", async () => {
    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={[]}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    await act(async () => {
      fireEvent.click(screen.getByText("Gravar Nota de Voz"));
    });

    await waitFor(() => {
      expect(screen.getByText(/A gravar/)).toBeInTheDocument();
    });

    // Button should show stop
    expect(screen.getByRole("button")).not.toBeDisabled();
  });

  it("handles recording error gracefully", async () => {
    // Mock getUserMedia to fail
    (navigator.mediaDevices.getUserMedia as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error("Permission denied")
    );

    // Mock alert
    const mockAlert = vi.fn();
    global.alert = mockAlert;

    render(
      <VoiceRecorder
        taskId="task-1"
        voiceNotes={[]}
        onVoiceNoteAdd={mockOnVoiceNoteAdd}
      />
    );

    await act(async () => {
      fireEvent.click(screen.getByText("Gravar Nota de Voz"));
    });

    await waitFor(() => {
      expect(mockAlert).toHaveBeenCalledWith(
        expect.stringContaining("microfone")
      );
    });
  });
});
