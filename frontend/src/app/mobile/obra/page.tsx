"use client";

/**
 * Lista de Tarefas — ImoOS Field App
 * Página principal com filtros, search, swipe actions e pull-to-refresh
 */
import { Suspense, useMemo, useCallback, useState, useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { 
  Plus, 
  RefreshCw, 
  Search, 
  SlidersHorizontal, 
  Calendar,
  AlertCircle,
  CheckCircle2,
  Clock,
  X
} from "lucide-react";
import { TaskCard } from "../components/TaskCard";
import { OfflineIndicator } from "../components/OfflineIndicator";
import { useMobileTasks } from "@/hooks/useMobileTasks";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { cn } from "@/lib/utils";
import type { TaskStatus, Task, TaskPriority } from "@/types/mobile";

type FilterType = "all" | "today" | "overdue" | "high" | "in_progress";
type SortType = "dueDate" | "priority" | "name" | "status";

interface FilterChip {
  key: FilterType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const FILTERS: FilterChip[] = [
  { key: "all", label: "Todas", icon: SlidersHorizontal },
  { key: "today", label: "Hoje", icon: Calendar },
  { key: "overdue", label: "Atrasadas", icon: AlertCircle },
  { key: "high", label: "Urgentes", icon: AlertCircle },
  { key: "in_progress", label: "Em Andamento", icon: Clock },
];

const SORT_OPTIONS: { key: SortType; label: string }[] = [
  { key: "dueDate", label: "Data" },
  { key: "priority", label: "Prioridade" },
  { key: "name", label: "Nome" },
  { key: "status", label: "Status" },
];

function LoadingFallback() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
    </div>
  );
}

function MobileObraContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = (searchParams.get("tab") as TaskStatus) || "all";
  
  const [activeFilter, setActiveFilter] = useState<FilterType>("all");
  const [sortBy, setSortBy] = useState<SortType>("dueDate");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [pullStartY, setPullStartY] = useState<number | null>(null);
  const [pullProgress, setPullProgress] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const { tasks, isLoading, error, refresh, updateTaskStatus } = useMobileTasks();
  const { queueAction, isOnline, pendingCount, syncNow, isSyncing } = useOfflineSync();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Filter and sort tasks
  const filteredTasks = useMemo(() => {
    let filtered = [...tasks];
    const today = new Date().toISOString().slice(0, 10);

    // Apply filter
    switch (activeFilter) {
      case "today":
        filtered = filtered.filter((t) => t.dueDate === today && t.status !== "completed");
        break;
      case "overdue":
        filtered = filtered.filter((t) => t.dueDate < today && t.status !== "completed");
        break;
      case "high":
        filtered = filtered.filter((t) => t.priority === "high" && t.status !== "completed");
        break;
      case "in_progress":
        filtered = filtered.filter((t) => t.status === "in_progress");
        break;
      default:
        // Show all except completed by default
        if (initialTab === "completed") {
          filtered = filtered.filter((t) => t.status === "completed");
        } else {
          filtered = filtered.filter((t) => t.status !== "completed");
        }
    }

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (t) =>
          t.name.toLowerCase().includes(query) ||
          t.projectName.toLowerCase().includes(query) ||
          t.description?.toLowerCase().includes(query)
      );
    }

    // Apply sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "dueDate":
          return a.dueDate.localeCompare(b.dueDate);
        case "priority": {
          const priorityOrder: Record<TaskPriority, number> = { high: 0, medium: 1, low: 2 };
          return priorityOrder[a.priority] - priorityOrder[b.priority];
        }
        case "name":
          return a.name.localeCompare(b.name);
        case "status": {
          const statusOrder: Record<string, number> = { blocked: 0, pending: 1, in_progress: 2, completed: 3 };
          return statusOrder[a.status] - statusOrder[b.status];
        }
        default:
          return 0;
      }
    });

    return filtered;
  }, [tasks, activeFilter, searchQuery, sortBy, initialTab]);

  // Pull to refresh handlers
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (scrollRef.current?.scrollTop === 0) {
      setPullStartY(e.touches[0].clientY);
    }
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (pullStartY !== null && scrollRef.current?.scrollTop === 0) {
      const diff = e.touches[0].clientY - pullStartY;
      if (diff > 0) {
        const progress = Math.min(diff / 100, 1);
        setPullProgress(progress);
      }
    }
  }, [pullStartY]);

  const handleTouchEnd = useCallback(async () => {
    if (pullProgress >= 0.8) {
      setIsRefreshing(true);
      await refresh();
      setIsRefreshing(false);
    }
    setPullStartY(null);
    setPullProgress(0);
  }, [pullProgress, refresh]);

  const handleStatusChange = useCallback(
    async (taskId: string, status: TaskStatus) => {
      await updateTaskStatus(taskId, status);
      await queueAction({
        type: status === "completed" ? "task_complete" : "task_update",
        payload: { taskId, status },
      });
      
      // Haptic feedback
      if (navigator.vibrate) {
        navigator.vibrate(50);
      }
    },
    [updateTaskStatus, queueAction]
  );

  const handleSwipeComplete = useCallback(
    async (task: Task) => {
      await handleStatusChange(task.id, "completed");
    },
    [handleStatusChange]
  );

  const handleSwipeProblem = useCallback(
    async (task: Task) => {
      router.push(`/mobile/obra/${task.id}?mode=issue`);
    },
    [router]
  );

  const stats = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    return {
      pending: tasks.filter((t) => t.status === "pending").length,
      inProgress: tasks.filter((t) => t.status === "in_progress").length,
      completed: tasks.filter((t) => t.status === "completed").length,
      overdue: tasks.filter((t) => t.dueDate < today && t.status !== "completed").length,
    };
  }, [tasks]);

  if (!mounted) {
    return <LoadingFallback />;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Pull to refresh indicator */}
      <div
        className={cn(
          "fixed top-0 left-0 right-0 z-50 flex items-center justify-center transition-transform",
          isRefreshing && "animate-pulse"
        )}
        style={{
          transform: `translateY(${(pullProgress * 80) - 80}px)`,
          opacity: pullProgress,
        }}
      >
        <div className="bg-white rounded-full p-3 shadow-lg">
          <RefreshCw className={cn("w-6 h-6 text-blue-600", isRefreshing && "animate-spin")} />
        </div>
      </div>

      {/* Offline Indicator */}
      <OfflineIndicator
        isOnline={isOnline}
        pendingCount={pendingCount}
        onSync={syncNow}
        isSyncing={isSyncing}
      />

      {/* Main Content */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto overscroll-y-contain"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <div className="p-4 space-y-4">
          {/* Header */}
          <div className="bg-blue-600 text-white rounded-2xl p-4 shadow-md">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm opacity-90">Obra Atual</p>
                <h2 className="text-lg font-bold truncate">Residencial Palmira</h2>
              </div>
              <button
                onClick={refresh}
                disabled={isLoading}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 active:bg-white/30 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={cn("w-5 h-5", isLoading && "animate-spin")} />
              </button>
            </div>

            {/* Quick Stats */}
            <div className="flex gap-4 mt-4 pt-4 border-t border-white/20">
              <div className="flex-1">
                <p className="text-2xl font-bold">{stats.pending}</p>
                <p className="text-xs opacity-90">Pendentes</p>
              </div>
              <div className="flex-1">
                <p className="text-2xl font-bold">{stats.inProgress}</p>
                <p className="text-xs opacity-90">Em Andamento</p>
              </div>
              <div className="flex-1">
                <p className="text-2xl font-bold">{stats.completed}</p>
                <p className="text-xs opacity-90">Concluídas</p>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative">
            {isSearchOpen ? (
              <div className="flex items-center gap-2 bg-white rounded-xl border border-gray-200 p-1">
                <Search className="w-5 h-5 text-gray-400 ml-2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Pesquisar tarefas..."
                  className="flex-1 px-2 py-2 text-base bg-transparent outline-none"
                  autoFocus
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="p-1 hover:bg-gray-100 rounded-full"
                  >
                    <X className="w-4 h-4 text-gray-400" />
                  </button>
                )}
                <button
                  onClick={() => {
                    setIsSearchOpen(false);
                    setSearchQuery("");
                  }}
                  className="px-3 py-2 text-sm font-medium text-blue-600"
                >
                  Cancelar
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={() => setIsSearchOpen(true)}
                  className="flex-1 flex items-center gap-2 px-4 py-3 bg-white rounded-xl border border-gray-200 text-gray-500"
                >
                  <Search className="w-5 h-5" />
                  <span>Pesquisar tarefas...</span>
                </button>
                {/* Sort Dropdown */}
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortType)}
                  className="px-3 py-2 bg-white rounded-xl border border-gray-200 text-sm font-medium"
                >
                  {SORT_OPTIONS.map((opt) => (
                    <option key={opt.key} value={opt.key}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Filter Chips */}
          <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
            {FILTERS.map((filter) => {
              const Icon = filter.icon;
              const isActive = activeFilter === filter.key;
              return (
                <button
                  key={filter.key}
                  onClick={() => setActiveFilter(filter.key)}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-colors",
                    isActive
                      ? "bg-blue-600 text-white"
                      : "bg-white text-gray-700 border border-gray-200 hover:bg-gray-50"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {filter.label}
                </button>
              );
            })}
          </div>

          {/* Results Count */}
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>
              {filteredTasks.length} {filteredTasks.length === 1 ? "tarefa" : "tarefas"}
            </span>
            {activeFilter !== "all" && (
              <button
                onClick={() => setActiveFilter("all")}
                className="text-blue-600 font-medium"
              >
                Limpar filtros
              </button>
            )}
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
              <div className="text-center py-12 text-gray-500">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Search className="w-8 h-8 text-gray-400" />
                </div>
                <p className="font-medium">Nenhuma tarefa encontrada</p>
                <p className="text-sm mt-1">Tente ajustar os filtros</p>
              </div>
            ) : (
              filteredTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onStatusChange={handleStatusChange}
                  onPress={(t) => router.push(`/mobile/obra/${t.id}`)}
                  onReportIssue={handleSwipeProblem}
                  onSwipeComplete={() => handleSwipeComplete(task)}
                />
              ))
            )}
          </div>

          {/* Bottom spacing for FAB and nav */}
          <div className="h-24" />
        </div>
      </div>

      {/* Floating Action Button */}
      <button
        onClick={() => router.push("/mobile/obra/new")}
        className="fixed bottom-24 right-4 z-40 w-14 h-14 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-lg hover:shadow-xl active:scale-95 transition-all"
        aria-label="Nova tarefa"
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
