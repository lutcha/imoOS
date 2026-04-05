"use client";

/**
 * Mobile Obra Dashboard — ImoOS Field App
 * Dashboard da obra para equipas de campo
 * Tabs: [Hoje] [Esta Semana] [Concluídas]
 * Lista de TaskCards com swipe actions
 */
import dynamic from "next/dynamic";
import { useState, useMemo, useCallback, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Plus, RefreshCw, MapPin } from "lucide-react";
import { cn } from "@/lib/utils";
import { TaskCard } from "../components/TaskCard";
import { useMobileTasks } from "@/hooks/useMobileTasks";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import type { Task, TaskStatus } from "@/types/mobile";

type TabKey = "today" | "week" | "completed";

interface Tab {
  key: TabKey;
  label: string;
}

const TABS: Tab[] = [
  { key: "today", label: "Hoje" },
  { key: "week", label: "Esta Semana" },
  { key: "completed", label: "Concluídas" },
];

export default function MobileObraPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = (searchParams.get("tab") as TabKey) || "today";
  
  const [activeTab, setActiveTab] = useState<TabKey>(initialTab);
  const [mounted, setMounted] = useState(false);
  const { tasks, isLoading, error, refresh, updateTaskStatus, getTaskById } = useMobileTasks();
  const { isOnline, queueAction } = useOfflineSync();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Prevent hydration issues - render loading state until mounted
  if (!mounted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Filter tasks based on active tab
  const filteredTasks = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    const weekFromNow = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);

    switch (activeTab) {
      case "today":
        return tasks.filter(
          (t) => t.dueDate === today && t.status !== "completed"
        );
      case "week":
        return tasks.filter(
          (t) =>
            t.dueDate >= today &&
            t.dueDate <= weekFromNow &&
            t.status !== "completed"
        );
      case "completed":
        return tasks.filter((t) => t.status === "completed");
      default:
        return tasks;
    }
  }, [tasks, activeTab]);

  // Group by project
  const groupedTasks = useMemo(() => {
    const groups: Record<string, Task[]> = {};
    filteredTasks.forEach((task) => {
      if (!groups[task.projectName]) {
        groups[task.projectName] = [];
      }
      groups[task.projectName].push(task);
    });
    return groups;
  }, [filteredTasks]);

  const handleTabChange = (tab: TabKey) => {
    setActiveTab(tab);
    // Update URL without navigation
    const newParams = new URLSearchParams(searchParams);
    if (tab === "today") {
      newParams.delete("tab");
    } else {
      newParams.set("tab", tab);
    }
    router.replace(`/mobile/obra?${newParams.toString()}`);
  };

  const handleTaskPress = useCallback((task: Task) => {
    router.push(`/mobile/obra/${task.id}`);
  }, [router]);

  const handleStatusChange = useCallback(async (taskId: string, status: TaskStatus) => {
    // Update local state immediately
    await updateTaskStatus(taskId, status);
    
    // Queue for sync
    await queueAction({
      type: status === "completed" ? "task_complete" : "task_update",
      payload: { taskId, status },
    });
  }, [updateTaskStatus, queueAction]);

  const handleReportIssue = useCallback((task: Task) => {
    // Navigate to task detail with issue mode
    router.push(`/mobile/obra/${task.id}?mode=issue`);
  }, [router]);

  return (
    <div className="space-y-4">
      {/* Project Header */}
      <div className="bg-primary text-primary-foreground rounded-2xl p-4 shadow-md">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
            <MapPin className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm opacity-90">Obra Atual</p>
            <h2 className="text-lg font-bold truncate">
              {Object.keys(groupedTasks)[0] || "Residencial Palmira"}
            </h2>
          </div>
          <button
            onClick={refresh}
            disabled={isLoading}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 active:bg-white/30 transition-colors"
          >
            <RefreshCw className={cn("w-5 h-5", isLoading && "animate-spin")} />
          </button>
        </div>

        {/* Quick Stats */}
        <div className="flex gap-4 mt-4 pt-4 border-t border-white/20">
          <div className="flex-1">
            <p className="text-2xl font-bold">
              {tasks.filter((t) => t.status !== "completed").length}
            </p>
            <p className="text-xs opacity-90">Pendentes</p>
          </div>
          <div className="flex-1">
            <p className="text-2xl font-bold">
              {tasks.filter((t) => t.status === "completed").length}
            </p>
            <p className="text-xs opacity-90">Concluídas</p>
          </div>
          <div className="flex-1">
            <p className="text-2xl font-bold">
              {tasks.filter((t) => t.priority === "high" && t.status !== "completed").length}
            </p>
            <p className="text-xs opacity-90">Urgentes</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-muted rounded-xl">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => handleTabChange(tab.key)}
            className={cn(
              "flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold transition-all",
              activeTab === tab.key
                ? "bg-white text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="space-y-4">
        {isLoading ? (
          // Loading skeletons
          Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="bg-white rounded-2xl shadow-sm border border-border p-4 space-y-3"
            >
              <div className="h-4 bg-muted rounded w-24 animate-pulse" />
              <div className="h-6 bg-muted rounded w-3/4 animate-pulse" />
              <div className="h-4 bg-muted rounded w-1/2 animate-pulse" />
            </div>
          ))
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-red-500 font-medium">{error}</p>
            <button
              onClick={refresh}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg"
            >
              Tentar novamente
            </button>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              <span className="text-3xl">✅</span>
            </div>
            <p className="text-muted-foreground font-medium">
              {activeTab === "completed"
                ? "Nenhuma tarefa concluída ainda"
                : "Nenhuma tarefa para este período"}
            </p>
            {activeTab !== "completed" && (
              <p className="text-sm text-muted-foreground mt-1">
                Deslize para ver outras abas
              </p>
            )}
          </div>
        ) : (
          Object.entries(groupedTasks).map(([projectName, projectTasks]) => (
            <div key={projectName}>
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3 px-1">
                {projectName}
              </h3>
              <div>
                {projectTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onStatusChange={handleStatusChange}
                    onPress={handleTaskPress}
                    onReportIssue={handleReportIssue}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Floating Action Button */}
      <button
        onClick={() => router.push("/mobile/obra/photo")}
        className={cn(
          "fixed bottom-20 right-4 z-40",
          "w-14 h-14 rounded-full bg-primary text-primary-foreground",
          "flex items-center justify-center shadow-lg",
          "hover:shadow-xl active:scale-95 transition-all",
          "md:bottom-24"
        )}
        aria-label="Adicionar foto"
      >
        <Plus className="w-7 h-7" />
      </button>
    </div>
  );
}
