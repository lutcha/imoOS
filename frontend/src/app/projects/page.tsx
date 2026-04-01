"use client";

import { useState } from "react";
import Link from "next/link";
import { Building2, MapPin, Plus, Search, CalendarClock } from "lucide-react";
import { cn } from "@/lib/utils";
import { useProjects, featureToProject, type ProjectStatus } from "@/hooks/useProjects";
import { ProjectStatusBadge } from "@/components/ui/StatusBadge";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate } from "@/lib/format";

const STATUS_OPTIONS: { value: ProjectStatus | ""; label: string }[] = [
  { value: "",             label: "Todos os estados" },
  { value: "PLANNING",    label: "Planeamento" },
  { value: "LICENSING",   label: "Licenciamento" },
  { value: "CONSTRUCTION",label: "Em Construção" },
  { value: "COMPLETED",   label: "Concluído" },
];

function ProjectCardSkeleton() {
  return (
    <div className="rounded-2xl border border-border bg-white p-6 space-y-4 shadow-sm">
      <div className="flex items-start justify-between">
        <Skeleton className="h-12 w-12 rounded-xl" />
        <Skeleton className="h-5 w-24 rounded-md" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-4 w-32" />
      </div>
      <Skeleton className="h-3 w-full rounded-full" />
      <div className="flex justify-between">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-20" />
      </div>
    </div>
  );
}

export default function ProjectsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<ProjectStatus | "">("");

  const { data, isLoading, isError } = useProjects({
    search: search || undefined,
    status: status || undefined,
    page_size: 20,
  });

  const projects = (data?.results ?? []).map(featureToProject);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Projectos</h1>
          <p className="text-muted-foreground mt-1">
            {data ? `${data.count} projecto${data.count !== 1 ? "s" : ""}` : "A carregar…"}
          </p>
        </div>
        <button className="flex items-center space-x-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-primary/90 shadow-md shadow-primary/20">
          <Plus className="h-4 w-4" />
          <span>Novo Projecto</span>
        </button>
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap gap-3">
        <div className="flex items-center rounded-lg border border-border bg-white px-3.5 py-2 min-w-64 shadow-sm">
          <Search className="h-4 w-4 text-muted-foreground mr-2 shrink-0" />
          <input
            type="text"
            placeholder="Pesquisar projectos…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent text-sm outline-none placeholder:text-muted-foreground w-full"
          />
        </div>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as ProjectStatus | "")}
          className="rounded-lg border border-border bg-white px-3.5 py-2 text-sm font-medium text-foreground outline-none shadow-sm cursor-pointer"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Grid */}
      {isLoading && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <ProjectCardSkeleton key={i} />)}
        </div>
      )}

      {isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
          Erro ao carregar projectos. Verifique a ligação à API.
        </div>
      )}

      {!isLoading && !isError && projects.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-muted py-24 text-center">
          <Building2 className="h-12 w-12 text-muted-foreground/40 mb-4" />
          <p className="text-muted-foreground font-medium">Nenhum projecto encontrado</p>
          <p className="text-muted-foreground/60 text-sm mt-1">Crie o primeiro projecto para começar.</p>
        </div>
      )}

      {!isLoading && projects.length > 0 && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
              className="group rounded-2xl border border-border bg-white p-6 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5 block"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="h-12 w-12 rounded-xl bg-blue-100 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Building2 className="h-6 w-6 text-blue-600" />
                </div>
                <ProjectStatusBadge status={project.status} />
              </div>

              <h3 className="font-bold text-foreground leading-snug mb-1 group-hover:text-primary transition-colors">
                {project.name}
              </h3>

              <div className="flex items-center text-xs text-muted-foreground mb-4">
                <MapPin className="h-3 w-3 mr-1 shrink-0" />
                {project.city}{project.island ? `, ${project.island}` : ""}
              </div>

              {project.description && (
                <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                  {project.description}
                </p>
              )}

              <div className="border-t border-border pt-4 flex items-center justify-between text-xs text-muted-foreground">
                <span className="flex items-center">
                  <CalendarClock className="h-3 w-3 mr-1" />
                  {project.start_date ? formatDate(project.start_date) : "Sem data de início"}
                </span>
                {project.total_units != null && (
                  <span className="font-medium text-foreground">
                    {project.total_units} unid.
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
