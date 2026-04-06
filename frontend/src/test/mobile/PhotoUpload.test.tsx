import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { PhotoUpload } from "@/app/mobile/components/PhotoUpload";
import type { PhotoMetadata } from "@/types/mobile";

// Mock compressPhoto
vi.mock("@/lib/mobile/image-compression", () => ({
  compressPhoto: vi.fn(async (file: File) => file),
}));

// Mock navigator.geolocation
const mockGeolocation = {
  getCurrentPosition: vi.fn(),
};
Object.defineProperty(global.navigator, "geolocation", {
  value: mockGeolocation,
  writable: true,
});

const mockPhotos: PhotoMetadata[] = [
  {
    id: "photo-1",
    taskId: "task-1",
    localUrl: "blob:test1",
    timestamp: Date.now(),
    synced: true,
  },
  {
    id: "photo-2",
    taskId: "task-1",
    localUrl: "blob:test2",
    timestamp: Date.now(),
    synced: false,
  },
];

describe("PhotoUpload", () => {
  const mockOnPhotoAdd = vi.fn();
  const mockOnPhotoRemove = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset geolocation mock
    mockGeolocation.getCurrentPosition.mockImplementation((success) => {
      success({
        coords: {
          latitude: 14.9,
          longitude: -23.5,
          accuracy: 10,
        },
      });
    });
  });

  it("renders photo count and grid", () => {
    render(
      <PhotoUpload
        taskId="task-1"
        photos={mockPhotos}
        onPhotoAdd={mockOnPhotoAdd}
        onPhotoRemove={mockOnPhotoRemove}
      />
    );

    expect(screen.getByText("Fotos (2/10)")).toBeInTheDocument();
    expect(screen.getAllByAltText("Foto da tarefa")).toHaveLength(2);
  });

  it("shows sync status for unsynced photos", () => {
    render(
      <PhotoUpload
        taskId="task-1"
        photos={mockPhotos}
        onPhotoAdd={mockOnPhotoAdd}
        onPhotoRemove={mockOnPhotoRemove}
      />
    );

    // Should show pending sync indicator
    expect(document.querySelector(".bg-amber-500")).toBeInTheDocument();
  });

  it("calls onPhotoRemove when remove button clicked", () => {
    render(
      <PhotoUpload
        taskId="task-1"
        photos={mockPhotos}
        onPhotoAdd={mockOnPhotoAdd}
        onPhotoRemove={mockOnPhotoRemove}
      />
    );

    const removeButtons = screen.getAllByLabelText("Remover foto");
    fireEvent.click(removeButtons[0]);

    expect(mockOnPhotoRemove).toHaveBeenCalledWith("photo-1");
  });

  it("shows add button when under max photos", () => {
    render(
      <PhotoUpload
        taskId="task-1"
        photos={mockPhotos}
        onPhotoAdd={mockOnPhotoAdd}
      />
    );

    expect(screen.getByText("Adicionar")).toBeInTheDocument();
  });

  it("hides add button when max photos reached", () => {
    const maxPhotos = 2;
    render(
      <PhotoUpload
        taskId="task-1"
        photos={mockPhotos}
        onPhotoAdd={mockOnPhotoAdd}
        maxPhotos={maxPhotos}
      />
    );

    expect(screen.queryByText("Adicionar")).not.toBeInTheDocument();
  });

  it("handles file selection", async () => {
    render(
      <PhotoUpload
        taskId="task-1"
        photos={[]}
        onPhotoAdd={mockOnPhotoAdd}
      />
    );

    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    await waitFor(() => {
      fireEvent.change(input, { target: { files: [file] } });
    });

    await waitFor(() => {
      expect(mockOnPhotoAdd).toHaveBeenCalled();
    });
  });

  it("displays helper text about compression", () => {
    render(
      <PhotoUpload
        taskId="task-1"
        photos={[]}
        onPhotoAdd={mockOnPhotoAdd}
      />
    );

    expect(
      screen.getByText("Fotos são comprimidas automaticamente para economizar dados")
    ).toBeInTheDocument();
  });

  it("is disabled when disabled prop is true", () => {
    render(
      <PhotoUpload
        taskId="task-1"
        photos={mockPhotos}
        onPhotoAdd={mockOnPhotoAdd}
        onPhotoRemove={mockOnPhotoRemove}
        disabled
      />
    );

    const removeButtons = screen.getAllByLabelText("Remover foto");
    removeButtons.forEach((button) => {
      expect(button).toBeDisabled();
    });
  });
});

describe("PhotoThumbnail", () => {
  it("renders count when greater than 0", () => {
    const { PhotoThumbnail } = require("@/app/mobile/components/PhotoUpload");
    render(<PhotoThumbnail count={5} />);

    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("returns null when count is 0", () => {
    const { PhotoThumbnail } = require("@/app/mobile/components/PhotoUpload");
    const { container } = render(<PhotoThumbnail count={0} />);

    expect(container.firstChild).toBeNull();
  });

  it("calls onClick when clicked", () => {
    const { PhotoThumbnail } = require("@/app/mobile/components/PhotoUpload");
    const handleClick = vi.fn();
    render(<PhotoThumbnail count={3} onClick={handleClick} />);

    fireEvent.click(screen.getByText("3"));
    expect(handleClick).toHaveBeenCalled();
  });
});
