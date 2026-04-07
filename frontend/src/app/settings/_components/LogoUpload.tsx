"use client";

import { useRef, useState } from "react";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import { useUploadLogo, useDeleteAsset } from "@/hooks/useTenantAssets";

interface LogoUploadProps {
  currentUrl?: string;
}

export function LogoUpload({ currentUrl }: LogoUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  
  const uploadLogo = useUploadLogo();
  const deleteLogo = useDeleteAsset();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);

    // Upload
    uploadLogo.mutate(file, {
      onSuccess: () => setPreview(null),
      onError: () => setPreview(null),
    });
  };

  const handleDelete = () => {
    if (confirm("Remover logo?")) {
      deleteLogo.mutate("logo");
    }
  };

  const displayUrl = preview || currentUrl;
  const isLoading = uploadLogo.isPending || deleteLogo.isPending;

  return (
    <div className="space-y-4 text-sm">
      <label className="font-bold text-foreground">Logo da Empresa</label>
      
      <div className="flex items-center space-x-5">
        {/* Preview / Upload area */}
        <div 
          onClick={() => !isLoading && fileInputRef.current?.click()}
          className={`
            relative h-20 w-20 rounded-2xl border-2 border-dashed 
            flex items-center justify-center overflow-hidden
            transition-colors cursor-pointer
            ${displayUrl ? "border-primary bg-white" : "border-border bg-slate-50/50 hover:bg-slate-100/50"}
            ${isLoading ? "opacity-50 cursor-not-allowed" : ""}
          `}
        >
          {displayUrl ? (
            <img 
              src={displayUrl} 
              alt="Logo preview" 
              className="h-full w-full object-contain p-2"
            />
          ) : (
            <ImageIcon className="h-8 w-8 text-muted-foreground" />
          )}
          
          {isLoading && (
            <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
            </div>
          )}
        </div>

        <div className="flex-1">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/svg+xml"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg border border-border text-xs font-bold hover:bg-slate-50 transition-colors disabled:opacity-50"
          >
            <Upload className="h-4 w-4" />
            <span>{currentUrl ? "Alterar Logo" : "Carregar Logo"}</span>
          </button>
          
          {currentUrl && (
            <button
              type="button"
              onClick={handleDelete}
              disabled={isLoading}
              className="ml-2 px-4 py-2 rounded-lg text-xs font-bold text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              <X className="h-4 w-4 inline mr-1" />
              Remover
            </button>
          )}
          
          <div className="mt-2 text-[11px] text-muted-foreground space-y-1">
            <p>SVG, PNG ou JPG • Máx: 2MB</p>
            <p>Recomendado: 512x512px</p>
          </div>
        </div>
      </div>
      
      {uploadLogo.isError && (
        <p className="text-xs text-red-600">
          Erro ao carregar logo. Tente novamente.
        </p>
      )}
    </div>
  );
}
