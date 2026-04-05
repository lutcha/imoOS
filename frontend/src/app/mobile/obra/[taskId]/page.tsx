"use client";

/**
 * Task Detail Page — ImoOS Field App
 * Detalhe da tarefa com ações rápidas
 * Botões grandes: Concluir, Em Andamento, Foto, Voz, Nota
 */
import { useState, useCallback, useEffect } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { 
  ArrowLeft, 
  CheckCircle2, 
  Camera, 
  Mic, 
  FileText, 
  AlertCircle,
  Clock,
  MapPin,
  Calendar,
  User,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { QuickStatusUpdate } from "../../components/QuickStatusUpdate";
import { PhotoUpload } from "../../components/PhotoUpload";
import { VoiceRecorder } from "../../components/VoiceRecorder";
import { useMobileTask } from "@/hooks/useMobileTasks";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { mobileDB } from "@/lib/mobile-db";
import type { Task, TaskStatus, PhotoMetadata, VoiceNote } from "@/types/mobile";

export default function TaskDetailPage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const taskId = params.taskId as string;
  const issueMode = searchParams.get("mode") === "issue";
  
  const { task, isLoading, error, refresh } = useMobileTask(taskId);
  const { queueAction, isOnline } = useOfflineSync();
  
  const [localPhotos, setLocalPhotos] = useState<PhotoMetadata[]>([]);
  const [localVoices, setLocalVoices] = useState<VoiceNote[]>([]);
  const [noteText, setNoteText] = useState("");
  const [isSavingNote, setIsSavingNote] = useState(false);

  // Load local media
  useEffect(() => {
    if (!taskId) return;
    
    mobileDB.getPhotosByTask(taskId).then(setLocalPhotos);
    mobileDB.getVoiceNotesByTask(taskId).then(setLocalVoices);
  }, [taskId]);

  const handleStatusChange = useCallback(async (status: TaskStatus) => {
    if (!task) return;

    // Update in DB
    const updatedTask: Task = {
      ...task,
      status,
      updatedAt: new Date().toISOString(),
    };
    await mobileDB.saveTask(updatedTask);

    // Queue for sync
    await queueAction({
      type: status === "completed" ? "task_complete" : "task_update",
      payload: { taskId, status },
    });

    refresh();
  }, [task, taskId, queueAction, refresh]);

  const handlePhotoAdd = useCallback(async (photo: PhotoMetadata) => {
    await mobileDB.savePhoto(photo);
    setLocalPhotos((prev) => [...prev, photo]);
    
    await queueAction({
      type: "photo_upload",
      payload: { taskId, photoId: photo.id },
    });
  }, [taskId, queueAction]);

  const handlePhotoRemove = useCallback(async (photoId: string) => {
    await mobileDB.deletePhoto(photoId);
    setLocalPhotos((prev) => prev.filter((p) => p.id !== photoId));
  }, []);

  const handleVoiceAdd = useCallback(async (voice: VoiceNote) => {
    await mobileDB.saveVoiceNote(voice);
    setLocalVoices((prev) => [...prev, voice]);
    
    await queueAction({
      type: "voice_upload",
      payload: { taskId, voiceId: voice.id },
    });
  }, [taskId, queueAction]);

  const handleAddNote = useCallback(async () => {
    if (!noteText.trim() || !task) return;

    setIsSavingNote(true);
    
    const updatedTask: Task = {
      ...task,
      notes: task.notes ? `${task.notes}\n\n${noteText}` : noteText,
      updatedAt: new Date().toISOString(),
    };
    
    await mobileDB.saveTask(updatedTask);
    
    await queueAction({
      type: "note_add",
      payload: { taskId, note: noteText },
    });

    setNoteText("");
    setIsSavingNote(false);
    refresh();
  }, [noteText, task, taskId, queueAction, refresh]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 bg-muted rounded w-3/4 animate-pulse" />
        <div className="h-48 bg-muted rounded-2xl animate-pulse" />
        <div className="h-32 bg-muted rounded-2xl animate-pulse" />
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-500 font-medium">{error || "Tarefa não encontrada"}</p>
        <button
          onClick={() => router.back()}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg"
        >
          Voltar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Back Button */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
        <span className="font-medium">Voltar às tarefas</span>
      </button>

      {/* Task Header */}
      <div className="bg-white rounded-2xl shadow-sm border border-border p-5">
        <div className="flex items-start gap-3 mb-4">
          <div className={cn(
            "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0",
            task.status === "completed" ? "bg-green-100" :
            task.status === "in_progress" ? "bg-amber-100" :
            "bg-red-100"
          )}>
            <span className="text-2xl">
              {task.status === "completed" ? "🟢" :
               task.status === "in_progress" ? "🟡" : "🔴"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-foreground leading-tight">
              {task.name}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {task.projectName}
            </p>
          </div>
        </div>

        {/* Task Metadata */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="w-4 h-4" />
            <span>
              {new Date(task.dueDate).toLocaleDateString("pt-CV", {
                weekday: "short",
                day: "numeric",
                month: "short",
              })}
            </span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock className="w-4 h-4" />
            <span className={cn(
              task.priority === "high" && "text-red-500 font-medium"
            )}>
              {task.priority === "high" ? "Urgente" : 
               task.priority === "medium" ? "Normal" : "Baixa"}
            </span>
          </div>
        </div>

        {/* Description */}
        {task.description && (
          <div className="mt-4 pt-4 border-t border-border">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
              Descrição
            </h3>
            <p className="text-foreground leading-relaxed">
              {task.description}
            </p>
          </div>
        )}
      </div>

      {/* Status Update */}
      <div className="bg-white rounded-2xl shadow-sm border border-border p-5">
        <QuickStatusUpdate
          currentStatus={task.status}
          onChange={handleStatusChange}
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-3">
        <ActionButton
          icon={CheckCircle2}
          label="Marcar Concluído"
          color="green"
          onClick={() => handleStatusChange("completed")}
          disabled={task.status === "completed"}
        />
        <ActionButton
          icon={Clock}
          label="Em Andamento"
          color="amber"
          onClick={() => handleStatusChange("in_progress")}
          disabled={task.status === "in_progress"}
        />
      </div>

      {/* Photos Section */}
      <div className="bg-white rounded-2xl shadow-sm border border-border p-5">
        <PhotoUpload
          taskId={task.id}
          photos={[...(task.photos || []), ...localPhotos]}
          onPhotoAdd={handlePhotoAdd}
          onPhotoRemove={handlePhotoRemove}
        />
      </div>

      {/* Voice Notes Section */}
      <div className="bg-white rounded-2xl shadow-sm border border-border p-5">
        <VoiceRecorder
          taskId={task.id}
          voiceNotes={[...(task.voiceNotes || []), ...localVoices]}
          onVoiceNoteAdd={handleVoiceAdd}
        />
      </div>

      {/* Notes Section */}
      <div className="bg-white rounded-2xl shadow-sm border border-border p-5">
        <label className="block text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Notas
        </label>
        
        {task.notes && (
          <div className="mb-4 p-3 bg-muted rounded-xl">
            <p className="text-sm text-foreground whitespace-pre-wrap">{task.notes}</p>
          </div>
        )}

        <div className="space-y-3">
          <textarea
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder="Adicionar nota..."
            rows={3}
            className={cn(
              "w-full px-4 py-3 rounded-xl border border-border",
              "bg-background text-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary",
              "resize-none text-base"
            )}
          />
          <button
            onClick={handleAddNote}
            disabled={!noteText.trim() || isSavingNote}
            className={cn(
              "w-full py-3 px-4 rounded-xl font-semibold",
              "bg-primary text-primary-foreground",
              "active:scale-[0.98] transition-transform",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "flex items-center justify-center gap-2"
            )}
          >
            <FileText className="w-5 h-5" />
            {isSavingNote ? "A guardar..." : "Adicionar Nota"}
          </button>
        </div>
      </div>

      {/* Timeline / Activity */}
      <div className="bg-white rounded-2xl shadow-sm border border-border p-5">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-4">
          Histórico
        </h3>
        <div className="space-y-4">
          <TimelineItem
            icon={CheckCircle2}
            iconColor="green"
            title="Tarefa criada"
            timestamp={task.createdAt}
          />
          {task.status !== "pending" && (
            <TimelineItem
              icon={Clock}
              iconColor="amber"
              title={`Estado alterado para: ${task.status === "completed" ? "Concluído" : "Em Andamento"}`}
              timestamp={task.updatedAt}
            />
          )}
          {localPhotos.length > 0 && (
            <TimelineItem
              icon={Camera}
              iconColor="blue"
              title={`${localPhotos.length} foto(s) adicionada(s)`}
              timestamp={new Date().toISOString()}
            />
          )}
        </div>
      </div>

      {/* Bottom spacing for nav */}
      <div className="h-8" />
    </div>
  );
}

// Action Button Component
function ActionButton({
  icon: Icon,
  label,
  color,
  onClick,
  disabled,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  color: "green" | "amber" | "blue" | "red";
  onClick: () => void;
  disabled?: boolean;
}) {
  const colorClasses = {
    green: "bg-green-500 hover:bg-green-600 text-white",
    amber: "bg-amber-500 hover:bg-amber-600 text-white",
    blue: "bg-blue-500 hover:bg-blue-600 text-white",
    red: "bg-red-500 hover:bg-red-600 text-white",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "flex flex-col items-center justify-center gap-2",
        "py-4 px-3 rounded-xl font-semibold",
        "min-h-[100px]",
        colorClasses[color],
        "active:scale-[0.98] transition-all shadow-sm",
        disabled && "opacity-50 cursor-not-allowed bg-gray-400 hover:bg-gray-400"
      )}
    >
      <Icon className="w-8 h-8" />
      <span className="text-sm text-center">{label}</span>
    </button>
  );
}

// Timeline Item Component
function TimelineItem({
  icon: Icon,
  iconColor,
  title,
  timestamp,
}: {
  icon: React.ComponentType<{ className?: string }>;
  iconColor: "green" | "amber" | "blue" | "gray";
  title: string;
  timestamp: string;
}) {
  const colorClasses = {
    green: "bg-green-100 text-green-600",
    amber: "bg-amber-100 text-amber-600",
    blue: "bg-blue-100 text-blue-600",
    gray: "bg-gray-100 text-gray-600",
  };

  const date = new Date(timestamp);
  const isValidDate = !isNaN(date.getTime());

  return (
    <div className="flex gap-3">
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
        colorClasses[iconColor]
      )}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-foreground">{title}</p>
        {isValidDate && (
          <p className="text-xs text-muted-foreground">
            {date.toLocaleDateString("pt-CV", {
              day: "numeric",
              month: "short",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>
    </div>
  );
}
