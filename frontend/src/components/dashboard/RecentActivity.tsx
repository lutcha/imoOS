"use client";

import { 
  HardHat, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  FileText,
  TrendingUp,
  User
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDateTime, formatDate } from "@/lib/format";

type ActivityType = "task_completed" | "phase_started" | "delay_reported" | "budget_alert" | "progress_update";

interface Activity {
  id: string;
  type: ActivityType;
  title: string;
  description: string;
  project_name: string;
  timestamp: string;
  user_name?: string;
}

interface RecentActivityProps {
  activities: Activity[];
  isLoading?: boolean;
}

const activityConfig: Record<ActivityType, { icon: React.ElementType; color: string; bg: string }> = {
  task_completed: { 
    icon: CheckCircle2, 
    color: "text-emerald-600", 
    bg: "bg-emerald-50" 
  },
  phase_started: { 
    icon: HardHat, 
    color: "text-blue-600", 
    bg: "bg-blue-50" 
  },
  delay_reported: { 
    icon: AlertCircle, 
    color: "text-red-600", 
    bg: "bg-red-50" 
  },
  budget_alert: { 
    icon: TrendingUp, 
    color: "text-amber-600", 
    bg: "bg-amber-50" 
  },
  progress_update: { 
    icon: FileText, 
    color: "text-purple-600", 
    bg: "bg-purple-50" 
  },
};

// Mock activities para demonstração - em produção viriam da API
const mockActivities: Activity[] = [
  {
    id: "1",
    type: "task_completed",
    title: "Tarefa concluída",
    description: "Fundações do Bloco A finalizadas",
    project_name: "Residencial Ocean View",
    timestamp: "2026-04-05T10:30:00Z",
    user_name: "João Silva",
  },
  {
    id: "2",
    type: "phase_started",
    title: "Nova fase iniciada",
    description: "Estrutura do Bloco B iniciada",
    project_name: "Residencial Ocean View",
    timestamp: "2026-04-05T08:00:00Z",
    user_name: "Maria Santos",
  },
  {
    id: "3",
    type: "budget_alert",
    title: "Alerta de orçamento",
    description: "Material de construção excedeu em 15%",
    project_name: "Edifício Central",
    timestamp: "2026-04-04T16:45:00Z",
    user_name: "Carlos Mendes",
  },
  {
    id: "4",
    type: "delay_reported",
    title: "Atraso reportado",
    description: "Entrega de materiais atrasada 2 dias",
    project_name: "Villa Paradiso",
    timestamp: "2026-04-04T14:20:00Z",
    user_name: "Ana Costa",
  },
  {
    id: "5",
    type: "progress_update",
    title: "Atualização de progresso",
    description: "Obra atingiu 75% de conclusão",
    project_name: "Residencial Ocean View",
    timestamp: "2026-04-03T09:00:00Z",
    user_name: "João Silva",
  },
];

export function RecentActivity({ activities, isLoading }: RecentActivityProps) {
  const displayActivities = activities.length > 0 ? activities : mockActivities;

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
        <Skeleton className="h-6 w-40 mb-6" />
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex gap-3">
              <Skeleton className="h-10 w-10 rounded-full shrink-0" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-full" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Atividade Recente</h3>
      <div className="space-y-4">
        {displayActivities.map((activity) => {
          const config = activityConfig[activity.type];
          const Icon = config.icon;

          return (
            <div key={activity.id} className="flex gap-3 group">
              <div className={cn(
                "h-10 w-10 rounded-full flex items-center justify-center shrink-0",
                config.bg
              )}>
                <Icon className={cn("h-5 w-5", config.color)} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium text-foreground truncate">
                    {activity.title}
                  </p>
                  <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                    {formatDate(activity.timestamp)}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-1">
                  {activity.description}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                    {activity.project_name}
                  </span>
                  {activity.user_name && (
                    <span className="text-[10px] text-muted-foreground flex items-center gap-0.5">
                      <User className="h-3 w-3" />
                      {activity.user_name}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {activities.length === 0 && (
        <p className="text-xs text-muted-foreground text-center mt-4 italic">
          Dados de demonstração - em produção viriam da API
        </p>
      )}
    </div>
  );
}
