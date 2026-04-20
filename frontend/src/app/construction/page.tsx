"use client";

import { useState } from "react";
import Link from "next/link";
import { 
  HardHat, 
  Plus, 
  LayoutGrid, 
  List,
  ArrowRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useConstructionProjects, useConstructionAggregatedStats } from "@/hooks/useConstructionStats";
import { ConstructionStatsCards, ObrasTable, ProgressChart } from "@/components/dashboard";
import { Button } from "@/components/ui/button";
import { ConstructionModal } from "@/components/construction/ConstructionModal";

type ViewMode = "list" | "grid";

export default function ConstructionListPage() {
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: projectsPage, isLoading: projectsLoading, error: projectsError } = useConstructionProjects({ page_size: 50 });
  const { data: stats, isLoading: statsLoading } = useConstructionAggregatedStats();

  const projects = projectsPage?.results ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-blue-50 flex items-center justify-center border border-blue-100">
            <HardHat className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">Obras</h1>
            <p className="text-sm text-muted-foreground">
              {projectsPage?.count ?? 0} projeto{projectsPage?.count !== 1 ? "s" : ""} de construção
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 bg-white rounded-lg border border-border p-1">
            <button
              onClick={() => setViewMode("list")}
              className={cn(
                "p-2 rounded-md transition-colors",
                viewMode === "list" 
                  ? "bg-slate-100 text-foreground" 
                  : "text-muted-foreground hover:text-foreground"
              )}
              title="Lista"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode("grid")}
              className={cn(
                "p-2 rounded-md transition-colors",
                viewMode === "grid" 
                  ? "bg-slate-100 text-foreground" 
                  : "text-muted-foreground hover:text-foreground"
              )}
              title="Grid"
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
          </div>

          <Button className="gap-2" onClick={() => setIsModalOpen(true)}>
            <Plus className="h-4 w-4" />
            Nova Obra
          </Button>
        </div>
      </div>

      <ConstructionModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
      />

      {/* Stats Cards */}
      <ConstructionStatsCards 
        stats={stats} 
        isLoading={statsLoading} 
      />

      {/* Progress Chart */}
      <ProgressChart 
        projects={projects} 
        isLoading={projectsLoading}
        maxItems={6}
      />

      {/* Projects List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Todas as Obras</h2>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
          >
            Dashboard
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        
        {viewMode === "list" ? (
          <ObrasTable 
            projects={projects} 
            isLoading={projectsLoading}
            error={projectsError}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projectsLoading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="rounded-2xl border border-border bg-white p-6 shadow-sm">
                  <div className="animate-pulse space-y-4">
                    <div className="h-4 w-3/4 bg-slate-200 rounded" />
                    <div className="h-3 w-1/2 bg-slate-200 rounded" />
                    <div className="h-2 w-full bg-slate-200 rounded" />
                  </div>
                </div>
              ))
            ) : projects.length === 0 ? (
              <div className="col-span-full text-center py-12">
                <HardHat className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <p className="text-muted-foreground">Nenhuma obra encontrada</p>
              </div>
            ) : (
              projects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

import { ConstructionProject, getStatusColor, getStatusLabel } from "@/hooks/useConstructionStats";
import { formatDate, formatCveCompact } from "@/lib/format";

function ProjectCard({ project }: { project: ConstructionProject }) {
  const statusColors = getStatusColor(project.status);
  const progress = Math.round(project.overall_progress_pct);

  return (
    <Link
      href={`/construction/${project.id}`}
      className="group rounded-2xl border border-border bg-white p-6 shadow-sm hover:shadow-md transition-all hover:-translate-y-0.5"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center">
          <HardHat className="h-5 w-5 text-blue-600" />
        </div>
        <span className={cn(
          "text-[10px] font-medium px-2 py-0.5 rounded-full border",
          statusColors.bg,
          statusColors.text,
          statusColors.border
        )}>
          {getStatusLabel(project.status)}
        </span>
      </div>

      <h3 className="font-semibold text-foreground mb-1 line-clamp-1 group-hover:text-primary transition-colors">
        {project.name}
      </h3>
      <p className="text-xs text-muted-foreground line-clamp-2 mb-4">
        {project.description || "Sem descrição"}
      </p>

      {/* Progress */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-muted-foreground">Progresso</span>
          <span className="font-medium">{progress}%</span>
        </div>
        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all",
              progress >= 100 ? "bg-emerald-500" : 
              progress >= 50 ? "bg-blue-500" : "bg-amber-500"
            )}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-muted-foreground pt-4 border-t border-border">
        <div>
          <p>Previsão</p>
          <p className="font-medium text-foreground">{formatDate(project.expected_end_date)}</p>
        </div>
        <div className="text-right">
          <p>Orçamento</p>
          <p className="font-medium text-foreground">
            {formatCveCompact(parseFloat(project.budget_cve || "0"))}
          </p>
        </div>
      </div>
    </Link>
  );
}
