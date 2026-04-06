"use client";

/**
 * TaskCard — ImoOS Field App
 * Card otimizado para touch com swipe gestures
 * Design: card grande com sombra, status visível, swipe actions
 */
import { useState, useRef, useCallback } from "react";
import { Calendar, ChevronRight, Check, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { statusColors, type TaskStatusKey } from "./MobileDesignSystem";
import type { Task } from "@/types/mobile";

interface TaskCardProps {
  task: Task;
  onStatusChange?: (taskId: string, status: TaskStatusKey) => void;
  onPress?: (task: Task) => void;
  onReportIssue?: (task: Task) => void;
  onSwipeComplete?: (task: Task) => void;
}

const SWIPE_THRESHOLD = 80;

export function TaskCard({
  task,
  onStatusChange,
  onPress,
  onReportIssue,
  onSwipeComplete,
}: TaskCardProps) {
  const [swipeOffset, setSwipeOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const startX = useRef(0);
  const currentX = useRef(0);
  const cardRef = useRef<HTMLDivElement>(null);

  const status = task.status as TaskStatusKey;
  const statusConfig = statusColors[status] || statusColors.pending;

  // Format date to relative (Hoje, Amanhã, or date)
  const formatRelativeDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return "Hoje";
    }
    if (date.toDateString() === tomorrow.toDateString()) {
      return "Amanhã";
    }
    return date.toLocaleDateString("pt-CV", {
      day: "2-digit",
      month: "short",
    });
  };

  // Touch/Mouse handlers for swipe
  const handleStart = useCallback((clientX: number) => {
    startX.current = clientX;
    currentX.current = clientX;
    setIsDragging(true);
  }, []);

  const handleMove = useCallback((clientX: number) => {
    if (!isDragging) return;
    
    currentX.current = clientX;
    const diff = clientX - startX.current;
    
    // Limit swipe to reasonable bounds
    const clampedDiff = Math.max(-SWIPE_THRESHOLD * 1.5, Math.min(SWIPE_THRESHOLD * 1.5, diff));
    setSwipeOffset(clampedDiff);
  }, [isDragging]);

  const handleEnd = useCallback(() => {
    setIsDragging(false);
    
    // Check if threshold reached for actions
    if (swipeOffset > SWIPE_THRESHOLD) {
      // Swiped right - mark complete
      onStatusChange?.(task.id, "completed");
      onSwipeComplete?.(task);
    } else if (swipeOffset < -SWIPE_THRESHOLD) {
      // Swiped left - report issue
      onReportIssue?.(task);
    }
    
    // Reset position
    setSwipeOffset(0);
  }, [swipeOffset, task, onStatusChange, onReportIssue, onSwipeComplete]);

  // Touch events
  const onTouchStart = (e: React.TouchEvent) => {
    handleStart(e.touches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    handleMove(e.touches[0].clientX);
  };

  // Mouse events
  const onMouseDown = (e: React.MouseEvent) => {
    handleStart(e.clientX);
  };

  const onMouseMove = (e: React.MouseEvent) => {
    handleMove(e.clientX);
  };

  return (
    <div className="relative overflow-hidden rounded-2xl mb-3">
      {/* Background Actions */}
      <div className="absolute inset-0 flex">
        {/* Left action (Complete) - visible when swiping right */}
        <div
          className={cn(
            "flex-1 flex items-center justify-start pl-4 rounded-l-2xl",
            "bg-green-500 transition-opacity",
            swipeOffset > 0 ? "opacity-100" : "opacity-0"
          )}
        >
          <div className="flex items-center gap-2 text-white font-semibold">
            <Check className="w-6 h-6" />
            <span>Concluir</span>
          </div>
        </div>
        
        {/* Right action (Report) - visible when swiping left */}
        <div
          className={cn(
            "flex-1 flex items-center justify-end pr-4 rounded-r-2xl",
            "bg-red-500 transition-opacity",
            swipeOffset < 0 ? "opacity-100" : "opacity-0"
          )}
        >
          <div className="flex items-center gap-2 text-white font-semibold">
            <span>Reportar</span>
            <AlertCircle className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Card */}
      <div
        ref={cardRef}
        onClick={() => onPress?.(task)}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={handleEnd}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={handleEnd}
        onMouseLeave={handleEnd}
        style={{
          transform: `translateX(${swipeOffset}px)`,
          transition: isDragging ? "none" : "transform 0.3s ease-out",
        }}
        className={cn(
          "relative bg-white rounded-2xl shadow-md border border-border",
          "p-4 cursor-pointer select-none",
          "active:shadow-lg transition-shadow"
        )}
      >
        {/* Header: Status + Project */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl" aria-hidden="true">
              {statusConfig.icon}
            </span>
            <span className={cn("text-xs font-bold uppercase tracking-wide", statusConfig.text)}>
              {statusConfig.label}
            </span>
          </div>
          <span className="text-xs text-muted-foreground truncate max-w-[120px]">
            {task.projectName}
          </span>
        </div>

        {/* Task Name */}
        <h3 className="text-lg font-bold text-foreground leading-tight mb-2 line-clamp-2">
          {task.name}
        </h3>

        {/* Description (if exists) */}
        {task.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {task.description}
          </p>
        )}

        {/* Footer: Date + Priority + Arrow */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Due Date */}
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <span className={cn(
                task.dueDate < new Date().toISOString().slice(0, 10) && status !== "completed"
                  ? "text-red-500 font-medium"
                  : ""
              )}>
                {formatRelativeDate(task.dueDate)}
              </span>
            </div>

            {/* Priority Badge */}
            {task.priority === "high" && (
              <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-semibold rounded-full">
                Urgente
              </span>
            )}
          </div>

          <ChevronRight className="w-5 h-5 text-muted-foreground" />
        </div>

        {/* Swipe hint (only on first render or help) */}
        <div className="mt-3 pt-3 border-t border-border/50 flex items-center justify-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            ← Deslize para concluir
          </span>
        </div>
      </div>
    </div>
  );
}
