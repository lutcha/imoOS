import { describe, it, expect, vi, beforeEach } from "vitest";
import { 
  compressPhoto, 
  formatFileSize, 
  needsCompression,
  createThumbnail,
  type CompressionOptions 
} from "@/lib/mobile/image-compression";

// Mock canvas and URL
class MockCanvas {
  width = 0;
  height = 0;
  
  getContext() {
    return {
      fillRect: vi.fn(),
      drawImage: vi.fn(),
    };
  }
  
  toBlob(callback: (blob: Blob | null) => void) {
    callback(new Blob(["compressed"], { type: "image/jpeg" }));
  }
}

describe("image-compression", () => {
  beforeEach(() => {
    vi.stubGlobal("HTMLCanvasElement", MockCanvas);
    vi.stubGlobal("Image", class MockImage {
      onload: (() => void) | null = null;
      width = 2000;
      height = 1500;
      
      constructor() {
        setTimeout(() => this.onload?.(), 0);
      }
      
      set src(_: string) {}
    });
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:url"),
      revokeObjectURL: vi.fn(),
    });
  });

  describe("formatFileSize", () => {
    it("formats bytes correctly", () => {
      expect(formatFileSize(500)).toBe("500 B");
      expect(formatFileSize(1024)).toBe("1.0 KB");
      expect(formatFileSize(1024 * 1024)).toBe("1.00 MB");
      expect(formatFileSize(1536000)).toBe("1.46 MB");
    });
  });

  describe("needsCompression", () => {
    it("returns true for files larger than maxSizeMB", () => {
      const largeFile = new File(["x".repeat(600 * 1024)], "test.jpg");
      expect(needsCompression(largeFile, 0.5)).toBe(true);
    });

    it("returns false for files smaller than maxSizeMB", () => {
      const smallFile = new File(["x".repeat(400 * 1024)], "test.jpg");
      expect(needsCompression(smallFile, 0.5)).toBe(false);
    });
  });

  describe("compressPhoto", () => {
    it("returns original file if already small enough", async () => {
      const smallFile = new File(["x".repeat(400 * 1024)], "test.jpg");
      const result = await compressPhoto(smallFile);
      expect(result).toBe(smallFile);
    });
  });
});
