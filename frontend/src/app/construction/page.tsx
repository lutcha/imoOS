"use client";

import { useState } from "react";
import {
  HardHat,
  Search,
  Plus,
  Camera,
  Clock,
  CheckCircle2,
  XCircle,
  FileEdit,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  useDailyReports,
  useCreateDailyReport,
  type ReportStatus,
  type WeatherCondition,
  type CreateDailyReportPayload,
} from "@/hooks/useConstruction";
import { useProjects, featureToProject } from "@/hooks/useProjects";
import { useBuildings } from "@/hooks/useBuildings";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate } from "@/lib/format";

// ----- Status config -----

const STATUS_CONFIG: Record<
  ReportStatus,
  { label: string; className: string; icon: React.ElementType }
> = {
  DRAFT:     { label: "Rascunho",   className: "bg-slate-100 text-slate-600 border-slate-200",      icon: FileEdit },
  SUBMITTED: { label: "Submetido",  className: "bg-amber-50 text-amber-700 border-amber-200",        icon: Clock },
  APPROVED:  { label: "Aprovado",   className: "bg-emerald-50 text-emerald-700 border-emerald-200",  icon: CheckCircle2 },
  REJECTED:  { label: "Rejeitado",  className: "bg-red-50 text-red-600 border-red-200",              icon: XCircle },
};

function ReportStatusBadge({ status }: { status: ReportStatus }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.DRAFT;
  const Icon = cfg.icon;
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-bold", cfg.className)}>
      <Icon className="h-3 w-3" />
      {cfg.label}
    </span>
  );
}

const STATUS_FILTERS: { value: ReportStatus | "ALL"; label: string }[] = [
  { value: "ALL",       label: "Todos" },
  { value: "DRAFT",     label: "Rascunho" },
  { value: "SUBMITTED", label: "Submetidos" },
  { value: "APPROVED",  label: "Aprovados" },
];

const WEATHER_LABELS: Record<WeatherCondition, string> = {
  SUNNY:   "Soalheiro",
  CLOUDY:  "Nublado",
  RAINY:   "Chuvoso",
  STORMY:  "Tempestuoso",
  WINDY:   "Ventoso",
};

// ----- Daily Report Form -----

function DailyReportForm({
  onSuccess,
  onClose,
}: {
  onSuccess: () => void;
  onClose: () => void;
}) {
  const today = new Date().toISOString().slice(0, 10);

  const [projectId, setProjectId] = useState("");
  const [buildingId, setBuildingId] = useState("");
  const [date, setDate] = useState(today);
  const [summary, setSummary] = useState("");
  const [progress, setProgress] = useState(0);
  const [weather, setWeather] = useState<WeatherCondition | "">("");
  const [workers, setWorkers] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);

  const { data: projectsPage } = useProjects({ page_size: 100 });
  const projects = projectsPage?.results.map(featureToProject) ?? [];

  const { data: buildings = [] } = useBuildings(projectId);

  const { mutate, isPending } = useCreateDailyReport();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!projectId || !date || !summary) {
      setError("Projecto, data e resumo são obrigatórios.");
      return;
    }
    const payload: CreateDailyReportPayload = {
      project: projectId,
      building: buildingId || null,
      date,
      summary,
      progress_pct: progress,
      weather: (weather as WeatherCondition) || null,
      workers_count: workers === "" ? null : Number(workers),
    };
    mutate(payload, {
      onSuccess: () => onSuccess(),
      onError: () => setError("Erro ao criar relatório. Tente novamente."),
    });
  }

  const labelCls = "block text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1";
  const inputCls = "w-full rounded-xl border border-border px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all bg-white";

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-bold text-foreground">Novo Relatório Diário</h2>
        <button type="button" onClick={onClose} className="rounded-lg p-1.5 hover:bg-muted transition-colors">
          <X className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>

      {error && (
        <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-2.5 text-sm text-red-600">
          {error}
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="sm:col-span-2">
          <label className={labelCls}>Projecto *</label>
          <select
            className={inputCls}
            value={projectId}
            onChange={(e) => { setProjectId(e.target.value); setBuildingId(""); }}
            required
          >
            <option value="">Seleccionar projecto…</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        <div className="sm:col-span-2">
          <label className={labelCls}>Edifício</label>
          <select
            className={cn(inputCls, !projectId && "opacity-50 cursor-not-allowed")}
            value={buildingId}
            onChange={(e) => setBuildingId(e.target.value)}
            disabled={!projectId}
          >
            <option value="">Todos os edifícios</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className={labelCls}>Data *</label>
          <input
            type="date"
            className={inputCls}
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>

        <div>
          <label className={labelCls}>Nº Trabalhadores</label>
          <input
            type="number"
            min={0}
            className={inputCls}
            value={workers}
            onChange={(e) => setWorkers(e.target.value === "" ? "" : Number(e.target.value))}
            placeholder="0"
          />
        </div>
      </div>

      <div>
        <label className={labelCls}>Resumo *</label>
        <textarea
          className={cn(inputCls, "resize-none")}
          rows={3}
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          placeholder="Descreva o trabalho realizado hoje…"
          required
        />
      </div>

      <div>
        <label className={labelCls}>Progresso — {progress}%</label>
        <input
          type="range"
          min={0}
          max={100}
          value={progress}
          onChange={(e) => setProgress(Number(e.target.value))}
          className="w-full accent-primary"
        />
      </div>

      <div>
        <label className={labelCls}>Condição Meteorológica</label>
        <select
          className={inputCls}
          value={weather}
          onChange={(e) => setWeather(e.target.value as WeatherCondition | "")}
        >
          <option value="">Não especificado</option>
          {(Object.keys(WEATHER_LABELS) as WeatherCondition[]).map((w) => (
            <option key={w} value={w}>{WEATHER_LABELS[w]}</option>
          ))}
        </select>
      </div>

      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={onClose}
          className="rounded-xl border border-border px-5 py-2.5 text-sm font-bold text-muted-foreground hover:text-foreground transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isPending}
          className="rounded-xl bg-primary px-6 py-2.5 text-sm font-bold text-white shadow-md shadow-primary/20 hover:opacity-90 transition-opacity disabled:opacity-60"
        >
          {isPending ? "A guardar…" : "Criar Relatório"}
        </button>
      </div>
    </form>
  );
}

// ----- Page -----

export default function ConstructionPage() {
  const [search, setSearch] = useState("");
  const [projectFilter, setProjectFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState<ReportStatus | "ALL">("ALL");
  const [showForm, setShowForm] = useState(false);

  const { data: projectsPage } = useProjects({ page_size: 100 });
  const projects = projectsPage?.results.map(featureToProject) ?? [];

  const { data, isLoading, isError } = useDailyReports({
    project: projectFilter || undefined,
    status: statusFilter === "ALL" ? undefined : statusFilter,
    ordering: "-date",
    page_size: 50,
  });

  const reports = data?.results ?? [];
  const filtered = search
    ? reports.filter(
        (r) =>
          r.project_name.toLowerCase().includes(search.toLowerCase()) ||
          (r.author_name ?? "").toLowerCase().includes(search.toLowerCase())
      )
    : reports;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div className="flex items-center space-x-4">
          <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/10">
            <HardHat className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">Obra</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              {data?.count != null ? `${data.count} relatório${data.count !== 1 ? "s" : ""}` : "A carregar…"}
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-primary/20 hover:opacity-90 transition-opacity"
        >
          <Plus className="h-4 w-4" />
          Novo Relatório
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 flex-wrap">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <input
            type="search"
            placeholder="Pesquisar relatórios…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-border bg-white pl-10 pr-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all"
          />
        </div>

        <select
          value={projectFilter}
          onChange={(e) => setProjectFilter(e.target.value)}
          className="rounded-xl border border-border bg-white px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 transition-all"
        >
          <option value="">Todos os projectos</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>

        <div className="flex items-center gap-1.5 flex-wrap">
          {STATUS_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setStatusFilter(f.value)}
              className={cn(
                "rounded-lg px-3.5 py-2 text-xs font-bold transition-all",
                statusFilter === f.value
                  ? "bg-primary text-white shadow-md shadow-primary/20"
                  : "bg-white border border-border text-muted-foreground hover:text-foreground hover:border-primary/30"
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 space-y-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full rounded-xl" />
            ))}
          </div>
        ) : isError ? (
          <div className="p-20 text-center">
            <p className="text-sm font-bold text-red-600">Erro ao carregar relatórios.</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-20 flex flex-col items-center text-center">
            <div className="h-16 w-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
              <HardHat className="h-8 w-8 text-muted-foreground/40" />
            </div>
            <p className="text-sm font-bold text-foreground">Nenhum relatório encontrado</p>
            <p className="text-xs text-muted-foreground mt-1">
              {search || statusFilter !== "ALL" || projectFilter
                ? "Tente ajustar os filtros."
                : "Os relatórios diários aparecerão aqui quando forem criados."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-slate-50/50">
                  {["Data", "Projecto", "Edifício", "Progresso", "Autor", "Estado", "Fotos"].map((h) => (
                    <th
                      key={h}
                      className="px-6 py-4 text-left text-[10px] font-bold text-muted-foreground uppercase tracking-widest whitespace-nowrap"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/70 transition-colors group">
                    <td className="px-6 py-4 font-medium text-foreground whitespace-nowrap">
                      {formatDate(r.date)}
                    </td>
                    <td className="px-6 py-4 font-medium text-foreground">
                      {r.project_name}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground text-xs">
                      {r.building_name ?? <span className="opacity-40">—</span>}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            style={{ width: `${r.progress_pct}%` }}
                            className="h-2 rounded-full bg-primary transition-all"
                          />
                        </div>
                        <span className="text-xs font-bold text-muted-foreground whitespace-nowrap">
                          {r.progress_pct}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground text-xs">
                      {r.author_name ?? <span className="opacity-40">—</span>}
                    </td>
                    <td className="px-6 py-4">
                      <ReportStatusBadge status={r.status} />
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                        <Camera className="h-3.5 w-3.5" />
                        {r.photos_count}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* New Report Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <DailyReportForm
              onSuccess={() => setShowForm(false)}
              onClose={() => setShowForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
