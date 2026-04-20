"use client";

import React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { useConstructionProject } from "@/hooks/useConstructionStats";
import { DailyReportsTab } from "@/components/construction/DailyReportsTab";
import { Skeleton } from "@/components/ui/Skeleton";

export default function ConstructionLogsPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  const { data: project, isLoading: projectLoading } = useConstructionProject(projectId);

  if (projectLoading) {
    return <LogsSkeleton />;
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h2 className="text-xl font-semibold">Projecto não encontrado</h2>
        <Link href="/construction" className="text-primary hover:underline mt-2">
          Voltar às obras
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/construction" className="hover:text-foreground transition-colors">
          Obras
        </Link>
        <span>/</span>
        <Link href={`/construction/${projectId}`} className="hover:text-foreground transition-colors">
          {project.name}
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">Diário de Obra</span>
      </div>

      {/* Header */}
      <div className="flex items-start gap-4 mb-8">
        <Link
          href={`/construction/${projectId}`}
          className="p-2 rounded-xl border border-border hover:bg-muted transition-colors"
        >
          <ArrowLeft className="h-5 w-5 text-muted-foreground" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Diário de Obra Digital</h1>
          <p className="text-sm text-muted-foreground">Registo técnico diário e documentação fotográfica da evolução</p>
        </div>
      </div>

      <DailyReportsTab projectId={projectId} />
    </div>
  );
}

function LogsSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-64" />
      <div className="flex gap-4">
        <Skeleton className="h-10 w-10 rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
      </div>
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-2xl" />
        ))}
      </div>
    </div>
  );
}
