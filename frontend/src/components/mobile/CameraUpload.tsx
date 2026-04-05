"use client";

import { useState, useRef, useCallback } from "react";
import { Camera, X, Check, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import { mobileDB } from "@/lib/mobile-db";
import type { PhotoMetadata } from "@/types/mobile";

interface CameraUploadProps {
  taskId: string;
  onPhotoTaken?: (photo: PhotoMetadata) => void;
  onClose?: () => void;
}

async function compressImage(
  file: File,
  maxWidth: number = 1920,
  quality: number = 0.8
): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(url);

      let { width, height } = img;
      if (width > maxWidth) {
        height = Math.round((height * maxWidth) / width);
        width = maxWidth;
      }

      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");

      if (!ctx) {
        reject(new Error("Failed to get canvas context"));
        return;
      }

      ctx.drawImage(img, 0, 0, width, height);
      
      ctx.font = "14px sans-serif";
      ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
      ctx.fillRect(10, height - 30, 200, 20);
      ctx.fillStyle = "#000";
      ctx.fillText(
        `${new Date().toLocaleString("pt-PT")}`,
        15,
        height - 15
      );

      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error("Failed to compress image"));
          }
        },
        "image/jpeg",
        quality
      );
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("Failed to load image"));
    };

    img.src = url;
  });
}

async function getCurrentPosition(timeout: number = 5000): Promise<GeolocationPosition | null> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(null);
      return;
    }

    const timeoutId = setTimeout(() => {
      resolve(null);
    }, timeout);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        clearTimeout(timeoutId);
        resolve(position);
      },
      () => {
        clearTimeout(timeoutId);
        resolve(null);
      },
      { enableHighAccuracy: true, timeout, maximumAge: 60000 }
    );
  });
}

export function CameraUpload({
  taskId,
  onPhotoTaken,
  onClose,
}: CameraUploadProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      setIsProcessing(true);

      try {
        const compressedBlob = await compressImage(file, 1920, 0.8);
        
        if (compressedBlob.size > 500 * 1024) {
          const moreCompressed = await compressImage(file, 1280, 0.6);
          if (moreCompressed.size > 500 * 1024) {
            alert("Imagem muito grande. Tente uma foto com menor resolução.");
            setIsProcessing(false);
            return;
          }
        }

        const previewUrl = URL.createObjectURL(compressedBlob);
        setPreview(previewUrl);
      } catch (err) {
        console.error("Failed to process image:", err);
        alert("Erro ao processar imagem. Tente novamente.");
      } finally {
        setIsProcessing(false);
      }
    },
    []
  );

  const handleCapture = useCallback(async () => {
    if (!preview) return;

    setIsProcessing(true);

    try {
      const position = await getCurrentPosition(3000);

      const response = await fetch(preview);
      const blob = await response.blob();

      const photo: PhotoMetadata = {
        id: `photo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        taskId,
        localUrl: preview,
        blob,
        timestamp: Date.now(),
        geolocation: position?.coords
          ? {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
              accuracy: position.coords.accuracy,
            }
          : undefined,
        synced: false,
      };

      await mobileDB.savePhoto(photo);

      onPhotoTaken?.(photo);

      setPreview(null);
    } catch (err) {
      console.error("Failed to save photo:", err);
      alert("Erro ao guardar foto. Tente novamente.");
    } finally {
      setIsProcessing(false);
    }
  }, [preview, taskId, onPhotoTaken]);

  const handleRetake = useCallback(() => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setPreview(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }, [preview]);

  return (
    <div className="flex flex-col h-full bg-black">
      <div className="flex items-center justify-between p-4 bg-black">
        <button
          onClick={onClose}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-white/20 text-white"
        >
          <X className="w-5 h-5" />
        </button>
        <span className="text-white font-semibold">Tirar Foto</span>
        <div className="w-10" />
      </div>

      <div className="flex-1 flex items-center justify-center relative">
        {preview ? (
          <img
            src={preview}
            alt="Preview"
            className="max-w-full max-h-full object-contain"
          />
        ) : (
          <div className="flex flex-col items-center gap-4">
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              onClick={() => inputRef.current?.click()}
              disabled={isProcessing}
              className="flex flex-col items-center gap-3 p-8 rounded-2xl bg-white/10 text-white active:bg-white/20 transition-colors"
            >
              <Camera className="w-16 h-16" />
              <span className="text-lg font-medium">
                {isProcessing ? "A processar..." : "Tocar para fotografar"}
              </span>
            </button>
          </div>
        )}

        {isProcessing && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </div>

      <div className="p-6 bg-black">
        {preview ? (
          <div className="flex items-center justify-center gap-6">
            <button
              onClick={handleRetake}
              disabled={isProcessing}
              className="flex flex-col items-center gap-2 text-white"
            >
              <div className="flex items-center justify-center w-14 h-14 rounded-full bg-white/20">
                <RotateCcw className="w-6 h-6" />
              </div>
              <span className="text-xs">Repetir</span>
            </button>

            <button
              onClick={handleCapture}
              disabled={isProcessing}
              className="flex flex-col items-center gap-2 text-white"
            >
              <div className="flex items-center justify-center w-16 h-16 rounded-full bg-green-500">
                <Check className="w-8 h-8" />
              </div>
              <span className="text-xs">Confirmar</span>
            </button>
          </div>
        ) : (
          <div className="text-center text-white/60 text-sm">
            <p>Fotos são comprimidas automaticamente</p>
            <p>e sincronizadas quando houver internet</p>
          </div>
        )}
      </div>
    </div>
  );
}

export function CameraButton({
  onCapture,
  className,
}: {
  onCapture: (blob: Blob) => void;
  className?: string;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);

    try {
      const compressedBlob = await compressImage(file, 1920, 0.8);
      onCapture(compressedBlob);
    } catch (err) {
      console.error("Failed to process image:", err);
    } finally {
      setIsProcessing(false);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  };

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileSelect}
        className="hidden"
      />
      <button
        onClick={() => inputRef.current?.click()}
        disabled={isProcessing}
        className={cn(
          "flex items-center justify-center",
          "w-14 h-14 rounded-full bg-blue-100 text-blue-600",
          "active:bg-blue-200 transition-colors disabled:opacity-50",
          className
        )}
        aria-label="Tirar foto"
      >
        {isProcessing ? (
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        ) : (
          <Camera className="w-6 h-6" />
        )}
      </button>
    </>
  );
}
