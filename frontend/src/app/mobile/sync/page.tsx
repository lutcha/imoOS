"use client";

/**
 * Sync Status Page — ImoOS Field App
 * Página de gerenciamento de sincronização offline
 */
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { 
  ArrowLeft, 
  RefreshCw, 
  Cloud, 
  CloudOff, 
  CheckCircle2, 
  AlertCircle,
  Trash2,
  Clock,
  Database,
  ImageIcon,
  Mic
} from "lucide-react";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { mobileDB } from "@/lib/mobile-db";
import { cn } from "@/lib/utils";
import type { ActionQueue, PhotoMetadata, VoiceNote } from "@/types/mobile";

export default function SyncPage() {
  const router = useRouter();
  const { 
    isOnline, 
    isSyncing, 
    pendingCount, 
    lastSync, 
    error,
    syncNow,
    retryFailedActions,
    clearFailedActions,
  } = useOfflineSync();

  const [queue, setQueue] = useState<ActionQueue[]>([]);
  const [photos, setPhotos] = useState<PhotoMetadata[]>([]);
  const [voices, setVoices] = useState<VoiceNote[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [queueData, photosData, voicesData] = await Promise.all([
        mobileDB.getPendingActions(),
        mobileDB.getUnsyncedPhotos(),
        mobileDB.getUnsyncedVoiceNotes(),
      ]);
      setQueue(queueData);
      setPhotos(photosData);
      setVoices(voicesData);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSync = async () => {
    await syncNow();
    await loadData();
  };

  const handleRetry = async () => {
    await retryFailedActions();
    await loadData();
  };

  const handleClear = async () => {
    if (confirm("Tem certeza que deseja remover todas as ações falhadas?")) {
      await clearFailedActions();
      await loadData();
    }
  };

  const formatLastSync = () => {
    if (!lastSync) return "Nunca sincronizado";
    const date = new Date(lastSync);
    return date.toLocaleString("pt-CV", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const failedActions = queue.filter((a) => a.error);

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
        <h1 className="text-xl font-bold">Sincronização</h1>
      </div>

      {/* Connection Status */}
      <div
        className={cn(
          "rounded-2xl p-5 flex items-center gap-4",
          isOnline ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"
        )}
      >
        <div
          className={cn(
            "w-14 h-14 rounded-full flex items-center justify-center",
            isOnline ? "bg-green-500" : "bg-red-500"
          )}
        >
          {isOnline ? (
            <Cloud className="w-7 h-7 text-white" />
          ) : (
            <CloudOff className="w-7 h-7 text-white" />
          )}
        </div>
        <div className="flex-1">
          <h2 className={cn("font-bold text-lg", isOnline ? "text-green-900" : "text-red-900")}>
            {isOnline ? "Online" : "Offline"}
          </h2>
          <p className={cn("text-sm", isOnline ? "text-green-700" : "text-red-700")}>
            {isOnline 
              ? "Ligado à internet — sincronização automática ativa" 
              : "Sem conexão — alterações guardadas localmente"}
          </p>
        </div>
      </div>

      {/* Sync Action */}
      <div className="bg-white rounded-2xl shadow-sm border p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-lg">Sincronizar Agora</h3>
            <p className="text-sm text-gray-500">
              Última sincronização: {formatLastSync()}
            </p>
          </div>
          <button
            onClick={handleSync}
            disabled={isSyncing || !isOnline || pendingCount === 0}
            className={cn(
              "px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-colors",
              isSyncing || !isOnline || pendingCount === 0
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700 active:scale-95"
            )}
          >
            <RefreshCw className={cn("w-5 h-5", isSyncing && "animate-spin")} />
            {isSyncing ? "A sincronizar..." : "Sincronizar"}
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-50 rounded-xl text-red-700 text-sm flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            {error}
          </div>
        )}
      </div>

      {/* Pending Items Summary */}
      <div className="grid grid-cols-3 gap-3">
        <SummaryCard
          icon={Database}
          count={queue.length}
          label="Ações"
          color="blue"
        />
        <SummaryCard
          icon={ImageIcon}
          count={photos.length}
          label="Fotos"
          color="amber"
        />
        <SummaryCard
          icon={Mic}
          count={voices.length}
          label="Vozes"
          color="purple"
        />
      </div>

      {/* Pending Queue */}
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b flex items-center justify-between">
          <h3 className="font-bold">Fila de Sincronização</h3>
          <span className="px-3 py-1 bg-gray-100 rounded-full text-sm font-medium">
            {pendingCount} pendentes
          </span>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin" />
            A carregar...
          </div>
        ) : queue.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <CheckCircle2 className="w-12 h-12 mx-auto mb-3 text-green-500" />
            <p className="font-medium">Tudo sincronizado!</p>
            <p className="text-sm mt-1">Nenhuma ação pendente</p>
          </div>
        ) : (
          <div className="divide-y">
            {queue.map((action) => (
              <QueueItem key={action.id} action={action} />
            ))}
          </div>
        )}
      </div>

      {/* Failed Actions */}
      {failedActions.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
          <div className="p-4 border-b bg-red-50">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-red-900">Ações Falhadas</h3>
              <div className="flex gap-2">
                <button
                  onClick={handleRetry}
                  className="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
                >
                  Tentar Novamente
                </button>
                <button
                  onClick={handleClear}
                  className="px-3 py-1.5 bg-red-100 text-red-700 text-sm font-medium rounded-lg hover:bg-red-200"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          <div className="divide-y">
            {failedActions.map((action) => (
              <QueueItem key={action.id} action={action} isFailed />
            ))}
          </div>
        </div>
      )}

      {/* Storage Info */}
      <div className="bg-gray-100 rounded-2xl p-4 text-sm text-gray-600">
        <div className="flex items-center gap-2 mb-2">
          <Database className="w-4 h-4" />
          <span className="font-medium">Armazenamento Local</span>
        </div>
        <p>
          Os dados são guardados localmente no dispositivo usando IndexedDB. 
          Quando a conexão for restabelecida, os dados serão sincronizados automaticamente.
        </p>
      </div>
    </div>
  );
}

function SummaryCard({
  icon: Icon,
  count,
  label,
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  count: number;
  label: string;
  color: "blue" | "amber" | "purple";
}) {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-700",
    amber: "bg-amber-50 text-amber-700",
    purple: "bg-purple-50 text-purple-700",
  };

  return (
    <div className={cn("rounded-2xl p-4 text-center", colorClasses[color])}>
      <Icon className="w-6 h-6 mx-auto mb-2 opacity-70" />
      <p className="text-2xl font-bold">{count}</p>
      <p className="text-sm opacity-80">{label}</p>
    </div>
  );
}

function QueueItem({ action, isFailed = false }: { action: ActionQueue; isFailed?: boolean }) {
  const typeLabels: Record<string, string> = {
    task_complete: "Concluir Tarefa",
    task_update: "Atualizar Tarefa",
    photo_upload: "Upload de Foto",
    voice_upload: "Upload de Voz",
    note_add: "Adicionar Nota",
  };

  const typeIcons: Record<string, string> = {
    task_complete: "✅",
    task_update: "📝",
    photo_upload: "📸",
    voice_upload: "🎙️",
    note_add: "📄",
  };

  const timestamp = new Date(action.timestamp);

  return (
    <div className={cn("p-4 flex items-start gap-3", isFailed && "bg-red-50/50")}>
      <span className="text-2xl">{typeIcons[action.type] || "📝"}</span>
      <div className="flex-1 min-w-0">
        <p className="font-medium">{typeLabels[action.type] || action.type}</p>
        <p className="text-xs text-gray-500">
          <Clock className="w-3 h-3 inline mr-1" />
          {timestamp.toLocaleTimeString("pt-CV", { hour: "2-digit", minute: "2-digit" })}
          {action.retries > 0 && (
            <span className="ml-2 text-amber-600">
              • {action.retries} tentativa(s)
            </span>
          )}
        </p>
        {isFailed && action.error && (
          <p className="text-xs text-red-600 mt-1">{action.error}</p>
        )}
      </div>
      <div
        className={cn(
          "w-3 h-3 rounded-full flex-shrink-0",
          isFailed ? "bg-red-500" : action.retries > 0 ? "bg-amber-500" : "bg-blue-500"
        )}
      />
    </div>
  );
}
