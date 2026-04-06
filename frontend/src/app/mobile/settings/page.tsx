"use client";

/**
 * Settings Page — ImoOS Field App
 * Configurações e informações da app
 */
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { 
  ArrowLeft, 
  Moon,
  Bell,
  Wifi,
  Database,
  Info,
  LogOut,
  Trash2,
  ChevronRight,
  HardHat,
  Smartphone
} from "lucide-react";
import { cn } from "@/lib/utils";
import { usePWAStatus } from "@/app/register-sw";
import { mobileDB } from "@/lib/mobile-db";

export default function SettingsPage() {
  const router = useRouter();
  const { canInstall, isInstalled, install } = usePWAStatus();
  const [storageInfo, setStorageInfo] = useState<{ used: number; total: number } | null>(null);
  const [appVersion] = useState("1.0.0");

  useEffect(() => {
    // Get storage info
    const getStorageInfo = async () => {
      if ("storage" in navigator && "estimate" in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        setStorageInfo({
          used: estimate.usage || 0,
          total: estimate.quota || 0,
        });
      }
    };
    getStorageInfo();
  }, []);

  const handleClearCache = async () => {
    if (confirm("Tem certeza que deseja limpar todos os dados locais?\n\nIsso não afetará os dados já sincronizados.")) {
      try {
        await mobileDB.clearAll();
        alert("Cache limpo com sucesso!");
        window.location.reload();
      } catch (error) {
        alert("Erro ao limpar cache.");
      }
    }
  };

  const handleLogout = () => {
    if (confirm("Tem certeza que deseja sair?")) {
      // Clear auth token
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      router.push("/login");
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          className="p-2 -ml-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>
        <h1 className="text-xl font-bold">Configurações</h1>
      </div>

      {/* User Info */}
      <div className="bg-blue-600 text-white rounded-2xl p-5">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
            <HardHat className="w-8 h-8" />
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="font-bold text-lg truncate">Encarregado de Obra</h2>
            <p className="text-sm opacity-90">Residencial Palmira</p>
          </div>
        </div>
      </div>

      {/* Install PWA */}
      {canInstall && !isInstalled && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-4">
          <div className="flex items-start gap-3">
            <Smartphone className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-bold text-green-900">Instalar Aplicação</h3>
              <p className="text-sm text-green-700 mt-1">
                Adicione o ImoOS à tela inicial para acesso rápido e uso offline completo.
              </p>
              <button
                onClick={install}
                className="mt-3 px-4 py-2 bg-green-600 text-white rounded-xl font-medium text-sm hover:bg-green-700 active:scale-95 transition-all"
              >
                Instalar Agora
              </button>
            </div>
          </div>
        </div>
      )}

      {isInstalled && (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
          <div className="flex items-center gap-3">
            <Smartphone className="w-6 h-6 text-blue-600 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-blue-900">Aplicação Instalada</h3>
              <p className="text-sm text-blue-700">
                O ImoOS está instalado no seu dispositivo.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* General Settings */}
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b">
          <h3 className="font-bold">Geral</h3>
        </div>
        
        <SettingItem
          icon={Bell}
          label="Notificações"
          description="Receber alertas de tarefas"
          action={<Toggle defaultChecked />}
        />
        
        <SettingItem
          icon={Wifi}
          label="Sync Automático"
          description="Sincronizar quando online"
          action={<Toggle defaultChecked />}
        />
        
        <SettingItem
          icon={Moon}
          label="Modo Escuro"
          description="Tema escuro (em breve)"
          action={<Toggle disabled />}
        />
      </div>

      {/* Storage Settings */}
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b">
          <h3 className="font-bold">Armazenamento</h3>
        </div>
        
        <div className="p-4">
          <div className="flex items-center gap-3 mb-3">
            <Database className="w-5 h-5 text-gray-400" />
            <div className="flex-1">
              <p className="font-medium">Dados Locais</p>
              <p className="text-sm text-gray-500">
                {storageInfo 
                  ? `${formatBytes(storageInfo.used)} usados`
                  : "A calcular..."
                }
              </p>
            </div>
          </div>
          
          <button
            onClick={handleClearCache}
            className="w-full mt-2 py-3 px-4 bg-gray-100 text-gray-700 rounded-xl font-medium text-sm hover:bg-gray-200 active:scale-95 transition-all flex items-center justify-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Limpar Cache Local
          </button>
        </div>
      </div>

      {/* About */}
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b">
          <h3 className="font-bold">Sobre</h3>
        </div>
        
        <SettingItem
          icon={Info}
          label="Versão"
          description={appVersion}
        />
        
        <SettingItem
          icon={Info}
          label="Termos de Uso"
          onClick={() => router.push("/terms")}
        />
        
        <SettingItem
          icon={Info}
          label="Política de Privacidade"
          onClick={() => router.push("/privacy")}
        />
      </div>

      {/* Logout */}
      <button
        onClick={handleLogout}
        className="w-full py-4 bg-red-50 text-red-600 rounded-2xl font-semibold hover:bg-red-100 active:scale-95 transition-all flex items-center justify-center gap-2"
      >
        <LogOut className="w-5 h-5" />
        Terminar Sessão
      </button>

      {/* Footer */}
      <p className="text-center text-xs text-gray-400">
        ImoOS © 2025 • Sistema de Gestão Imobiliária
      </p>
    </div>
  );
}

function SettingItem({
  icon: Icon,
  label,
  description,
  action,
  onClick,
}: {
  icon?: React.ComponentType<{ className?: string }>;
  label: string;
  description?: string;
  action?: React.ReactNode;
  onClick?: () => void;
}) {
  const content = (
    <div className="flex items-center gap-3 py-4 px-4">
      {Icon && <Icon className="w-5 h-5 text-gray-400" />}
      <div className="flex-1 min-w-0">
        <p className="font-medium">{label}</p>
        {description && <p className="text-sm text-gray-500">{description}</p>}
      </div>
      {action || (onClick && <ChevronRight className="w-5 h-5 text-gray-400" />)}
    </div>
  );

  if (onClick) {
    return (
      <button
        onClick={onClick}
        className="w-full text-left hover:bg-gray-50 transition-colors"
      >
        {content}
      </button>
    );
  }

  return content;
}

function Toggle({ defaultChecked = false, disabled = false }: { defaultChecked?: boolean; disabled?: boolean }) {
  const [checked, setChecked] = useState(defaultChecked);

  return (
    <button
      onClick={() => !disabled && setChecked(!checked)}
      disabled={disabled}
      className={cn(
        "w-12 h-7 rounded-full transition-colors relative",
        checked ? "bg-blue-600" : "bg-gray-300",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <div
        className={cn(
          "w-5 h-5 bg-white rounded-full absolute top-1 transition-transform",
          checked ? "translate-x-6" : "translate-x-1"
        )}
      />
    </button>
  );
}
