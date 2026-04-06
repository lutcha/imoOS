"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { 
  HardHat, 
  ArrowLeft, 
  TrendingUp,
  Calendar,
  CheckCircle2,
  Clock,
  AlertCircle,
  Camera,
  FileText,
  Info,
  User,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { 
  useConstructionProject, 
  useDailyReports,
  getStatusLabel,
  getStatusColor
} from "@/hooks/useConstructionStats";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate, formatDateTime } from "@/lib/format";

export default function ProgressPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  const { data: project, isLoading: projectLoading } = useConstructionProject(projectId);
  const { data: reportsPage, isLoading: reportsLoading } = useDailyReports({ project: projectId });

  const reports = reportsPage?.results ?? [];

  if (projectLoading) {
    return <ProgressSkeleton />;
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Info className="h-12 w-12 text-red-500 mb-4" />
        <h2 className="text-lg font-semibold">Obra não encontrada</h2>
        <Link href="/construction" className="text-primary hover:underline mt-2">
          Voltar às obras
        </Link>
      </div>
    );
  }

  const progress = Math.round(project.overall_progress_pct);
  const progressHistory = reports.slice(0, 10).map(r => ({
    date: r.date,
    progress: r.progress_pct,
  }));

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
        <span className="text-foreground">Progresso</span>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <Link
            href={`/construction/${projectId}`}
            className="p-2 rounded-xl border border-border hover:bg-slate-50 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-muted-foreground" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Progresso Físico</h1>
                <p className="text-sm text-muted-foreground">{project.name}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-border">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Última atualização:</span>
            <span className="text-sm font-medium">{formatDate(project.updated_at)}</span>
          </div>
        </div>
      </div>

      {/* Main Progress */}
      <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-semibold">Progresso Geral</h2>
            <p className="text-sm text-muted-foreground">Percentagem de conclusão da obra</p>
          </div>
          <div className="text-right">
            <p className="text-4xl font-bold text-blue-600">{progress}%</p>
            <p className="text-sm text-muted-foreground">
              {progress < 100 ? `${100 - progress}% restante` : "Obra concluída!"}
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="h-4 bg-slate-100 rounded-full overflow-hidden mb-4">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-500",
              progress >= 100 ? "bg-emerald-500" : 
              progress >= 75 ? "bg-blue-500" :
              progress >= 50 ? "bg-indigo-500" :
              progress >= 25 ? "bg-amber-500" : "bg-slate-400"
            )}
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Milestones */}
        <div className="grid grid-cols-4 gap-4 mt-6">
          {[
            { label: "Início", value: 0, icon: Clock },
            { label: "Fundações", value: 25, icon: HardHat },
            { label: "Estrutura", value: 50, icon: TrendingUp },
            { label: "Acabamentos", value: 75, icon: CheckCircle2 },
          ].map((milestone) => (
            <div 
              key={milestone.label}
              className={cn(
                "p-3 rounded-xl border text-center transition-colors",
                progress >= milestone.value
                  ? "border-blue-200 bg-blue-50/50"
                  : "border-slate-100 bg-slate-50/30"
              )}
            >
              <milestone.icon className={cn(
                "h-5 w-5 mx-auto mb-2",
                progress >= milestone.value ? "text-blue-600" : "text-slate-300"
              )} />
              <p className={cn(
                "text-xs font-medium",
                progress >= milestone.value ? "text-blue-700" : "text-slate-400"
              )}>
                {milestone.label}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Progress History & Daily Reports */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Progress History */}
        <div className="lg:col-span-2 rounded-2xl border border-border bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Histórico de Progresso</h3>
          {reportsLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-xl" />
              ))}
            </div>
          ) : reports.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Sem relatórios de progresso</p>
              <p className="text-xs mt-1">Os relatórios diários aparecerão aqui</p>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((report, index) => {
                const prevProgress = index < reports.length - 1 ? reports[index + 1].progress_pct : 0;
                const diff = report.progress_pct - prevProgress;

                return (
                  <div 
                    key={report.id}
                    className="flex items-center gap-4 p-3 rounded-xl border border-border hover:bg-slate-50/50 transition-colors"
                  >
                    <div className="h-12 w-12 rounded-xl bg-blue-50 flex items-center justify-center shrink-0">
                      <FileText className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-foreground">{formatDate(report.date)}</p>
                        <span className={cn(
                          "text-[10px] px-1.5 py-0.5 rounded-full",
                          report.status === "APPROVED" ? "bg-emerald-50 text-emerald-600" :
                          report.status === "SUBMITTED" ? "bg-amber-50 text-amber-600" :
                          "bg-slate-50 text-slate-600"
                        )}>
                          {getStatusLabel(report.status)}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-1">{report.summary}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{report.progress_pct}%</p>
                      {diff > 0 && (
                        <p className="text-xs text-emerald-600">+{diff.toFixed(1)}%</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="space-y-4">
          <div className="rounded-2xl border border-border bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Estatísticas</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Relatórios</span>
                <span className="font-medium">{reportsPage?.count || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Último relatório</span>
                <span className="font-medium">
                  {reports[0] ? formatDate(reports[0].date) : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Média/dia</span>
                <span className="font-medium">
                  {reports.length > 0 
                    ? `${(progress / reports.length).toFixed(1)}%` 
                    : "—"}
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Ações</h3>
            <div className="space-y-2">
              <Link
                href="/construction"
                className="flex items-center justify-between p-3 rounded-xl border border-border hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Novo Relatório</span>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </Link>
              <Link
                href={`/construction/${projectId}/gantt`}
                className="flex items-center justify-between p-3 rounded-xl border border-border hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Ver Cronograma</span>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProgressSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10 rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
      </div>
      <Skeleton className="h-48 rounded-2xl" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Skeleton className="h-64 lg:col-span-2 rounded-2xl" />
        <Skeleton className="h-64 rounded-2xl" />
      </div>
    </div>
  );
}
