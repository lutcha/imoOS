"use client";

import { useState, useRef, useCallback } from "react";
import { CheckCircle2, Camera, AlertCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Task, TaskStatus, TaskPriority } from "@/types/mobile";

interface TaskCardProps {
  task: Task;
  onComplete?: (taskId: string) => void;
  onPhoto?: (taskId: string) => void;
  onPress?: (task: Task) => void;
  onLongPress?: (task: Task) => void;
  className?: string;
}

const priorityConfig: Record<TaskPriority, { label: string; color: string; bg: string }> = {
  high: { label: "Alta", color: "text-red-600", bg: "bg-red-50 border-red-200" },
  medium: { label: "Média", color: "text-amber-600", bg: "bg-amber-50 border-amber-200" },
  low: { label: "Baixa", color: "text-green-600", bg: "bg-green-50 border-green-200" },
};

const statusConfig: Record<TaskStatus, { label: string; icon: typeof Clock; color: string }> = {
  pending: { label: "Pendente", icon: Clock, color: "text-gray-500" },
  in_progress: { label: "Em curso", icon: Clock, color: "text-blue-500" },
  completed: { label: "Concluída", icon: CheckCircle2, color: "text-green-500" },
  blocked: { label: "Bloqueada", icon: AlertCircle, color: "text-red-500" },
};

export function TaskCard({
  task,
  onComplete,
  onPhoto,
  onPress,
  onLongPress,
  className,
}: TaskCardProps) {
  const [isPressed, setIsPressed] = useState(false);
  const longPressTimer = useRef<NodeJS.Timeout | null>(null);
  const isLongPress = useRef(false);

  const priority = priorityConfig[task.priority];
  const status = statusConfig[task.status];
  const isCompleted = task.status === "completed";

  const handleTouchStart = useCallback(() => {
    isLongPress.current = false;
    setIsPressed(true);
    
    longPressTimer.current = setTimeout(() => {
      isLongPress.current = true;
      onLongPress?.(task);
    }, 500);
  }, [task, onLongPress]);

  const handleTouchEnd = useCallback(() => {
    setIsPressed(false);
    
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
    }

    if (!isLongPress.current) {
      onPress?.(task);
    }
  }, [task, onPress]);

  const handleTouchMove = useCallback(() => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
    }
  }, []);

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border bg-white",
        "transition-all duration-200",
        isPressed && "scale-[0.98]",
        isCompleted && "opacity-75",
        className
      )}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onTouchMove={handleTouchMove}
      onMouseDown={handleTouchStart}
      onMouseUp={handleTouchEnd}
      onMouseLeave={handleTouchEnd}
    >
      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <span
            className={cn(
              "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border",
              priority.bg,
              priority.color
            )}
          >
            {priority.label}
          </span>
          <span className={cn("flex items-center gap-1 text-xs", status.color)}>
            <status.icon className="w-3.5 h-3.5" />
            {status.label}
          </span>
        </div>

        <h3
          className={cn(
            "text-lg font-bold text-gray-900 mb-1 leading-tight",
            isCompleted && "line-through text-gray-500"
          )}
        >
          {task.name}
        </h3>

        {task.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {task.description}
          </p>
        )}

        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span>{task.projectName}</span>
            <span className="w-1 h-1 rounded-full bg-gray-300" />
            <span>{formatDate(task.dueDate)}</span>
          </div>

          {!isCompleted && (
            <div className="flex items-center gap-2">
              {onPhoto && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onPhoto(task.id);
                  }}
                  className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 active:bg-gray-200 transition-colors"
                  aria-label="Adicionar foto"
                >
                  <Camera className="w-5 h-5 text-gray-600" />
                </button>
              )}
              {onComplete && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onComplete(task.id);
                  }}
                  className="flex items-center justify-center w-10 h-10 rounded-full bg-green-100 active:bg-green-200 transition-colors"
                  aria-label="Marcar como concluída"
                >
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                </button>
              )}
            </div>
          )}
        </div>

        {task.notes && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <p className="text-xs text-gray-500 line-clamp-1">
              <span className="font-medium">Nota:</span> {task.notes}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export function TaskCardCompact({
  task,
  onPress,
  className,
}: {
  task: Task;
  onPress?: (task: Task) => void;
  className?: string;
}) {
  const priority = priorityConfig[task.priority];

  return (
    <button
      onClick={() => onPress?.(task)}
      className={cn(
        "w-full flex items-center gap-3 p-3 rounded-xl border bg-white",
        "active:scale-[0.98] transition-all",
        task.status === "completed" && "opacity-60",
        className
      )}
    >
      <div
        className={cn(
          "w-3 h-3 rounded-full flex-shrink-0",
          task.status === "completed" && "bg-green-500",
          task.status === "in_progress" && "bg-blue-500",
          task.status === "pending" && "bg-gray-300",
          task.status === "blocked" && "bg-red-500"
        )}
      />

      <div className="flex-1 min-w-0 text-left">
        <p
          className={cn(
            "font-semibold text-gray-900 truncate",
            task.status === "completed" && "line-through"
          )}
        >
          {task.name}
        </p>
        <p className="text-xs text-gray-500 truncate">{task.projectName}</p>
      </div>

      <span
        className={cn(
          "px-2 py-0.5 rounded-full text-[10px] font-bold",
          priority.bg,
          priority.color
        )}
      >
        {priority.label.charAt(0)}
      </span>
    </button>
  );
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const today = new Date();
  const diff = Math.floor((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  if (diff === 0) return "Hoje";
  if (diff === 1) return "Amanhã";
  if (diff === -1) return "Ontem";
  
  return date.toLocaleDateString("pt-PT", {
    day: "numeric",
    month: "short",
  });
}
