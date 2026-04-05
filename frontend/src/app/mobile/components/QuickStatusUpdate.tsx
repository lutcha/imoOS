"use client";

/**
 * QuickStatusUpdate — ImoOS Field App
 * Selector rápido de status 🔴🟡🟢
 * Touch targets grandes (60px+)
 */
import { cn } from "@/lib/utils";
import { statusColors, type TaskStatusKey } from "./MobileDesignSystem";

type StatusOption = {
  value: TaskStatusKey;
  icon: string;
  label: string;
  color: string;
  bgColor: string;
};

const STATUS_OPTIONS: StatusOption[] = [
  {
    value: "pending",
    icon: "🔴",
    label: "Não Iniciado",
    color: "text-red-700",
    bgColor: "bg-red-500",
  },
  {
    value: "in_progress",
    icon: "🟡",
    label: "Em Andamento",
    color: "text-amber-700",
    bgColor: "bg-amber-500",
  },
  {
    value: "completed",
    icon: "🟢",
    label: "Concluído",
    color: "text-green-700",
    bgColor: "bg-green-500",
  },
];

interface QuickStatusUpdateProps {
  currentStatus: TaskStatusKey;
  onChange: (status: TaskStatusKey) => void;
  disabled?: boolean;
}

export function QuickStatusUpdate({
  currentStatus,
  onChange,
  disabled = false,
}: QuickStatusUpdateProps) {
  return (
    <div className="w-full">
      <label className="block text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
        Estado da Tarefa
      </label>
      
      <div className="grid grid-cols-3 gap-2">
        {STATUS_OPTIONS.map((option) => {
          const isSelected = currentStatus === option.value;
          
          return (
            <button
              key={option.value}
              onClick={() => !disabled && onChange(option.value)}
              disabled={disabled}
              className={cn(
                "flex flex-col items-center justify-center gap-2",
                "py-4 px-2 rounded-xl border-2 transition-all",
                "min-h-[80px]",
                isSelected
                  ? cn(option.bgColor, "border-transparent text-white shadow-md")
                  : "bg-white border-border hover:border-muted-foreground/30",
                disabled && "opacity-50 cursor-not-allowed"
              )}
            >
              <span className="text-2xl">{option.icon}</span>
              <span className={cn(
                "text-xs font-semibold text-center leading-tight",
                isSelected ? "text-white" : option.color
              )}>
                {option.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// Versão simplificada (apenas ícones) para listas
export function QuickStatusBadge({
  status,
  onChange,
  size = "md",
}: {
  status: TaskStatusKey;
  onChange?: (status: TaskStatusKey) => void;
  size?: "sm" | "md" | "lg";
}) {
  const config = statusColors[status];
  
  const sizeClasses = {
    sm: "w-10 h-10 text-lg",
    md: "w-14 h-14 text-2xl",
    lg: "w-20 h-20 text-3xl",
  };

  if (!onChange) {
    return (
      <div
        className={cn(
          "flex items-center justify-center rounded-full",
          config.bgLight,
          sizeClasses[size]
        )}
        title={config.label}
      >
        {config.icon}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1">
      {( ["pending", "in_progress", "completed"] as TaskStatusKey[] ).map((s) => (
        <button
          key={s}
          onClick={() => onChange(s)}
          className={cn(
            "flex items-center justify-center rounded-full transition-all",
            sizeClasses[size],
            status === s 
              ? statusColors[s].bgLight 
              : "bg-transparent opacity-40 hover:opacity-70"
          )}
        >
          {statusColors[s].icon}
        </button>
      ))}
    </div>
  );
}
