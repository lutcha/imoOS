"use client";

/**
 * PhotoUpload — ImoOS Field App
 * Camera com compressão otimizada para 3G
 * Target: <500KB por foto
 */
import { useState, useRef, useCallback } from "react";
import { Camera, X, Loader2, ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { compressPhoto } from "@/lib/mobile/image-compression";
import type { PhotoMetadata } from "@/types/mobile";

interface PhotoUploadProps {
  taskId: string;
  photos: PhotoMetadata[];
  onPhotoAdd: (photo: PhotoMetadata) => void;
  onPhotoRemove?: (photoId: string) => void;
  maxPhotos?: number;
  disabled?: boolean;
}

export function PhotoUpload({
  taskId,
  photos,
  onPhotoAdd,
  onPhotoRemove,
  maxPhotos = 10,
  disabled = false,
}: PhotoUploadProps) {
  const [isCapturing, setIsCapturing] = useState(false);
  const [compressing, setCompressing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleCapture = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setCompressing(true);
    
    try {
      // Compress image for 3G
      const compressedFile = await compressPhoto(file, {
        maxWidth: 1200,
        quality: 0.7,
        maxSizeMB: 0.5,
      });

      // Create local URL
      const localUrl = URL.createObjectURL(compressedFile);

      // Get geolocation (optional)
      let geolocation: PhotoMetadata["geolocation"] | undefined;
      try {
        const position = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            timeout: 5000,
            enableHighAccuracy: false,
          });
        });
        geolocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
        };
      } catch {
        // Geolocation failed, continue without it
      }

      const photo: PhotoMetadata = {
        id: `photo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        taskId,
        localUrl,
        blob: compressedFile,
        timestamp: Date.now(),
        geolocation,
        synced: false,
      };

      onPhotoAdd(photo);
    } catch (error) {
      console.error("Failed to process photo:", error);
      alert("Erro ao processar foto. Tente novamente.");
    } finally {
      setCompressing(false);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }, [taskId, onPhotoAdd]);

  const canAddMore = photos.length < maxPhotos;

  return (
    <div className="w-full">
      <label className="block text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
        Fotos ({photos.length}/{maxPhotos})
      </label>

      {/* Photo Grid */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        {/* Existing Photos */}
        {photos.map((photo) => (
          <div
            key={photo.id}
            className={cn(
              "relative aspect-square rounded-xl overflow-hidden",
              "bg-gray-100 border border-border"
            )}
          >
            <img
              src={photo.localUrl}
              alt="Foto da tarefa"
              className="w-full h-full object-cover"
              loading="lazy"
            />
            
            {/* Sync status indicator */}
            {!photo.synced && (
              <div className="absolute top-1 left-1 bg-amber-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                ⏳
              </div>
            )}

            {/* Remove button */}
            {onPhotoRemove && (
              <button
                onClick={() => onPhotoRemove(photo.id)}
                disabled={disabled}
                className={cn(
                  "absolute top-1 right-1 w-7 h-7",
                  "bg-red-500 text-white rounded-full",
                  "flex items-center justify-center",
                  "shadow-md active:scale-90 transition-transform",
                  disabled && "opacity-50"
                )}
                aria-label="Remover foto"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        ))}

        {/* Add Photo Button */}
        {canAddMore && (
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || compressing}
            className={cn(
              "aspect-square rounded-xl border-2 border-dashed",
              "flex flex-col items-center justify-center gap-2",
              "border-muted-foreground/30 hover:border-primary/50",
              "bg-muted/30 active:bg-muted/50 transition-colors",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          >
            {compressing ? (
              <>
                <Loader2 className="w-8 h-8 text-muted-foreground animate-spin" />
                <span className="text-xs text-muted-foreground">A comprimir...</span>
              </>
            ) : (
              <>
                <Camera className="w-8 h-8 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Adicionar</span>
              </>
            )}
          </button>
        )}

        {/* Empty placeholders to maintain grid */}
        {Array.from({ length: Math.max(0, 3 - ((photos.length + (canAddMore ? 1 : 0)) % 3)) }).map((_, i) => (
          <div
            key={`empty-${i}`}
            className="aspect-square rounded-xl bg-transparent"
          />
        ))}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleCapture}
        className="hidden"
      />

      {/* Helper text */}
      <p className="text-xs text-muted-foreground text-center">
        Fotos são comprimidas automaticamente para economizar dados
      </p>
    </div>
  );
}

// Compact version for lists
export function PhotoThumbnail({ 
  count, 
  onClick 
}: { 
  count: number; 
  onClick?: () => void;
}) {
  if (count === 0) return null;

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg",
        "bg-muted text-muted-foreground text-sm",
        "active:bg-muted/70 transition-colors"
      )}
    >
      <ImageIcon className="w-4 h-4" />
      <span className="font-medium">{count}</span>
    </button>
  );
}
