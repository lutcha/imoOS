"use client";

import { Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useState, useMemo, useCallback, useEffect } from "react";
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

function LoadingFallback() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );
}

function MobileObraContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = (searchParams.get("tab") as TabKey) || "today";

  const [activeTab, setActiveTab] = useState<TabKey>(initialTab);
  const [mounted, setMounted] = useState(false);
  const { tasks, isLoading, error, refresh, updateTaskStatus } = useMobileTasks();
  const { queueAction } = useOfflineSync();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <LoadingFallback />;
  }

  // Filter tasks based on active tab
  const filteredTasks = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    const weekFromNow = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);

    switch (activeTab) {
      case "today":
        return tasks.filter((t) => t.dueDate === today && t.status !== "completed");
      case "week":
        return tasks.filter(
          (t) => t.dueDate >= today && t.dueDate <= weekFromNow && t.status !== "completed"
        );
      case "completed":
        return tasks.filter((t) => t.status === "completed");
      default:
        return tasks;
    }
  }, [tasks, activeTab]);

  const handleTabChange = (tab: TabKey) => {
    setActiveTab(tab);
    const newParams = new URLSearchParams(searchParams);
    if (tab === "today") {
      newParams.delete("tab");
    } else {
      newParams.set("tab", tab);
    }
    router.replace(`/mobile/obra?${newParams.toString()}`);
  };

  const handleStatusChange = useCallback(
    async (taskId: string, status: TaskStatus) => {
      await updateTaskStatus(taskId, status);
      await queueAction({
        type: status === "completed" ? "task_complete" : "task_update",
        payload: { taskId, status },
      });
    },
    [updateTaskStatus, queueAction]
  );

  return (
    <div className="min-h-screen bg-gray-50 p-4 space-y-4">
      {/* Header */}
      <div className="bg-blue-600 text-white rounded-2xl p-4 shadow-md">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
            <MapPin className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm opacity-90">Obra Atual</p>
            <h2 className="text-lg font-bold truncate">Residencial Palmira</h2>
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
            <p className="text-2xl font-bold">{tasks.filter((t) => t.status !== "completed").length}</p>
            <p className="text-xs opacity-90">Pendentes</p>
          </div>
          <div className="flex-1">
            <p className="text-2xl font-bold">{tasks.filter((t) => t.status === "completed").length}</p>
            <p className="text-xs opacity-90">Concluídas</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-gray-200 rounded-xl">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => handleTabChange(tab.key)}
            className={cn(
              "flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold transition-all",
              activeTab === tab.key
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl shadow-sm border p-4 space-y-3">
              <div className="h-4 bg-gray-200 rounded w-24 animate-pulse" />
              <div className="h-6 bg-gray-200 rounded w-3/4 animate-pulse" />
            </div>
          ))
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-red-500 font-medium">{error}</p>
            <button onClick={refresh} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg">
              Tentar novamente
            </button>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="font-medium">Nenhuma tarefa encontrada</p>
          </div>
        ) : (
          filteredTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onStatusChange={handleStatusChange}
              onPress={(task) => router.push(`/mobile/obra/${task.id}`)}
              onReportIssue={(task) => router.push(`/mobile/obra/${task.id}?mode=issue`)}
            />
          ))
        )}
      </div>

      {/* Floating Action Button */}
      <button
        onClick={() => router.push("/mobile/obra/photo")}
        className="fixed bottom-20 right-4 z-40 w-14 h-14 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-lg hover:shadow-xl active:scale-95 transition-all"
        aria-label="Adicionar foto"
      >
        <Plus className="w-7 h-7" />
      </button>
    </div>
  );
}

export default function MobileObraPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <MobileObraContent />
    </Suspense>
  );
}
