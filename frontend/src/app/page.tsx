"use client";

import {
  Building,
  Home as HomeIcon,
  Users2,
  ArrowUpRight,
  TrendingUp,
  Clock,
  ArrowRight,
  AlertCircle,
  Banknote,
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { useDashboardStats, activeLeadsCount } from "@/hooks/useDashboardStats";
import { useProjects, featureToProject } from "@/hooks/useProjects";
import { StatCardSkeleton, ProjectRowSkeleton } from "@/components/ui/Skeleton";

// ----- Status display maps -----

const PROJECT_STATUS_LABEL: Record<string, string> = {
  PLANNING: "Planeamento",
  LICENSING: "Licenciamento",
  CONSTRUCTION: "Em Construção",
  COMPLETED: "Concluído",
};

const PROJECT_STATUS_COLOR: Record<string, string> = {
  PLANNING: "text-amber-600 bg-amber-50",
  LICENSING: "text-purple-600 bg-purple-50",
  CONSTRUCTION: "text-blue-600 bg-blue-50",
  COMPLETED: "text-emerald-600 bg-emerald-50",
};

// Pipeline stage labels (in funnel order)
const PIPELINE_STAGES: Array<{ key: string; label: string }> = [
  { key: "new", label: "Novo" },
  { key: "contacted", label: "Contactado" },
  { key: "visit_scheduled", label: "Visita Agend." },
  { key: "proposal_sent", label: "Proposta Env." },
  { key: "negotiation", label: "Negociação" },
  { key: "won", label: "Ganho" },
  { key: "lost", label: "Perdido" },
];

// ----- Sub-components -----

function StatCard({
  label,
  value,
  sub,
  icon: Icon,
  color,
  bg,
}: {
  label: string;
  value: string;
  sub: string;
  icon: React.ElementType;
  color: string;
  bg: string;
}) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-border bg-white p-6 shadow-sm transition-all hover:shadow-md hover:-translate-y-1">
      <div className="flex items-center justify-between">
        <div className={cn("rounded-xl p-2.5", bg)}>
          <Icon className={cn("h-6 w-6", color)} />
        </div>
        <span className="flex items-center text-[10px] font-bold uppercase tracking-widest text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
          <ArrowUpRight className="mr-0.5 h-3 w-3" />
          Live
        </span>
      </div>
      <div className="mt-4">
        <h3 className="text-sm font-medium text-muted-foreground">{label}</h3>
        <p className="mt-1 text-3xl font-bold tracking-tight text-foreground">{value}</p>
        <p className="mt-1 text-xs text-muted-foreground flex items-center">
          <Clock className="mr-1 h-3 w-3 opacity-50" />
          {sub}
        </p>
      </div>
    </div>
  );
}

function PipelineFunnel({ pipeline }: { pipeline: Record<string, number> }) {
  const max = Math.max(...Object.values(pipeline), 1);

  return (
    <div className="space-y-2">
      {PIPELINE_STAGES.map(({ key, label }) => {
        const count = pipeline[key] ?? 0;
        const pct = Math.round((count / max) * 100);
        return (
          <div key={key} className="flex items-center gap-3">
            <span className="w-28 shrink-0 text-xs text-muted-foreground text-right">{label}</span>
            <div className="flex-1 h-5 rounded-full bg-slate-100 overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all duration-500",
                  key === "won"
                    ? "bg-emerald-500"
                    : key === "lost"
                    ? "bg-rose-300"
                    : "bg-blue-400"
                )}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="w-6 shrink-0 text-xs font-bold text-foreground text-right">{count}</span>
          </div>
        );
      })}
    </div>
  );
}

// ----- Page -----

export default function DashboardPage() {
  const { user, tenant } = useAuth();
  const { data: stats, isLoading: statsLoading, isError: statsError } = useDashboardStats();
  const { data: projectsPage, isLoading: projectsLoading, isError: projectsError } = useProjects({ page_size: 5 });

  const projects = (projectsPage?.results ?? []).map(featureToProject);

  const greeting = user?.fullName ? `Bem-vindo, ${user.fullName.split(" ")[0]}.` : "Bem-vindo de volta.";
  const subtitle = tenant?.name ? `${tenant.name} — resumo da operação.` : "Resumo da operação.";

  const v = (val: number | undefined) =>
    statsLoading ? "…" : !stats || statsError ? "—" : String(val ?? 0);

  const formatCve = (raw: string | undefined) => {
    if (!raw || statsLoading) return "…";
    if (statsError) return "—";
    const n = parseFloat(raw);
    if (isNaN(n)) return "—";
    return new Intl.NumberFormat("pt-CV", { style: "currency", currency: "CVE", maximumFractionDigits: 0 }).format(n);
  };

  const statCards = [
    {
      label: "Unidades Disponíveis",
      value: v(stats?.inventory.available),
      sub: statsLoading
        ? "A carregar…"
        : stats
        ? `${stats.inventory.total ? Math.round((stats.inventory.available / stats.inventory.total) * 100) : 0}% do stock`
        : "—",
      icon: HomeIcon,
      color: "text-amber-600",
      bg: "bg-amber-50",
    },
    {
      label: "Receita Confirmada",
      value: formatCve(stats?.revenue_cve),
      sub: statsLoading ? "A carregar…" : "Contratos activos + concluídos",
      icon: Banknote,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
    },
    {
      label: "Leads Activos",
      value: statsLoading ? "…" : !stats || statsError ? "—" : String(activeLeadsCount(stats.pipeline)),
      sub: statsLoading ? "A carregar…" : "Excluindo ganhos e perdidos",
      icon: Users2,
      color: "text-indigo-600",
      bg: "bg-indigo-50",
    },
    {
      label: "Contratos Activos",
      value: v(stats?.contracts["ACTIVE"]),
      sub: statsLoading ? "A carregar…" : `${stats?.contracts["DRAFT"] ?? 0} em rascunho`,
      icon: TrendingUp,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard Geral</h1>
          <p className="text-muted-foreground mt-1 text-lg">{greeting} {subtitle}</p>
        </div>
        <button className="flex items-center space-x-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white transition-all hover:bg-primary/90 hover:scale-105 active:scale-95 shadow-md shadow-primary/20">
          <span>Gerar Relatório</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </header>

      {/* Expiring reservations alert */}
      {!statsLoading && !statsError && stats && stats.reservations_expiring_soon > 0 && (
        <div className="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-amber-500 shrink-0" />
          <p className="text-sm font-bold text-amber-800">
            {stats.reservations_expiring_soon} reserva(s) a expirar nas próximas 24h
          </p>
          <Link href="/crm" className="ml-auto text-xs font-bold text-amber-700 hover:underline">
            Ver CRM →
          </Link>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statsLoading
          ? Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)
          : statCards.map((card, i) => <StatCard key={i} {...card} />)}
      </div>

      {/* Stats error banner */}
      {statsError && (
        <div className="flex items-center space-x-2 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>Não foi possível carregar as estatísticas. Verifique a ligação à API.</span>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        {/* Sales Chart */}
        <div className="rounded-2xl border border-border bg-white p-6 shadow-sm flex flex-col h-96">
          <div className="mb-4">
            <h2 className="text-lg font-bold">Evolução de Vendas</h2>
            <p className="text-sm text-muted-foreground">Volume financeiro (CVE) nos últimos 6 meses</p>
          </div>
          <div className="flex-1 w-full relative">
            {statsLoading ? (
               <div className="absolute inset-0 flex items-center justify-center text-muted-foreground text-sm">A carregar gráfico...</div>
            ) : (!stats?.sales_chart || stats.sales_chart.length === 0) ? (
               <div className="absolute inset-0 flex items-center justify-center text-muted-foreground text-sm">Sem dados suficientes.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats.sales_chart} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fontSize: 12, fill: '#64748b' }} 
                    tickFormatter={(value) => value >= 1000000 ? `${(value / 1000000).toFixed(1)}M` : value}
                    dx={-10}
                    width={80}
                  />
                  <Tooltip 
                    formatter={(value: number) => [new Intl.NumberFormat("pt-CV", { style: "currency", currency: "CVE", maximumFractionDigits: 0 }).format(value), "Faturação"]}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)' }}
                  />
                  <Area type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Leads Chart */}
        <div className="rounded-2xl border border-border bg-white p-6 shadow-sm flex flex-col h-96">
          <div className="mb-4">
            <h2 className="text-lg font-bold">Captação de Leads</h2>
            <p className="text-sm text-muted-foreground">Novos contactos gerados nos últimos 6 meses</p>
          </div>
          <div className="flex-1 w-full relative">
            {statsLoading ? (
               <div className="absolute inset-0 flex items-center justify-center text-muted-foreground text-sm">A carregar gráfico...</div>
            ) : (!stats?.leads_chart || stats.leads_chart.length === 0) ? (
               <div className="absolute inset-0 flex items-center justify-center text-muted-foreground text-sm">Sem dados suficientes.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.leads_chart} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fontSize: 12, fill: '#64748b' }}
                    allowDecimals={false} 
                    dx={-10}
                    width={40}
                  />
                  <Tooltip 
                    cursor={{ fill: '#f1f5f9' }}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)' }}
                  />
                  <Bar dataKey="count" name="Novos Leads" fill="#4f46e5" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* CRM Pipeline funnel */}
        <div className="lg:col-span-2 rounded-2xl border border-border bg-white p-6 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold">Funil de Pipeline CRM</h2>
              {!statsLoading && stats && (
                <p className="text-sm text-muted-foreground mt-0.5">
                  {activeLeadsCount(stats.pipeline)} leads activos
                </p>
              )}
            </div>
          </div>

          {statsLoading && (
            <div className="flex-1 flex items-center justify-center">
              <p className="text-sm text-muted-foreground">A carregar pipeline…</p>
            </div>
          )}

          {!statsLoading && stats && (
            <PipelineFunnel pipeline={stats.pipeline} />
          )}

          {/* Inventory status bar */}
          {!statsLoading && stats && stats.inventory.total > 0 && (
            <div className="mt-6 pt-6 border-t border-border">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Inventário</p>
              <div className="flex rounded-full overflow-hidden h-3 bg-slate-100">
                <div
                  title={`Vendidas: ${stats.inventory.sold}`}
                  className="bg-emerald-500 transition-all duration-700"
                  style={{ width: `${(stats.inventory.sold / stats.inventory.total) * 100}%` }}
                />
                <div
                  title={`Contrato: ${stats.inventory.contract}`}
                  className="bg-blue-400 transition-all duration-700"
                  style={{ width: `${(stats.inventory.contract / stats.inventory.total) * 100}%` }}
                />
                <div
                  title={`Reservadas: ${stats.inventory.reserved}`}
                  className="bg-amber-400 transition-all duration-700"
                  style={{ width: `${(stats.inventory.reserved / stats.inventory.total) * 100}%` }}
                />
                <div
                  title={`Disponíveis: ${stats.inventory.available}`}
                  className="bg-blue-200 transition-all duration-700"
                  style={{ width: `${(stats.inventory.available / stats.inventory.total) * 100}%` }}
                />
              </div>
              <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
                {[
                  { label: "Vendidas", count: stats.inventory.sold, color: "bg-emerald-500" },
                  { label: "Contrato", count: stats.inventory.contract, color: "bg-blue-400" },
                  { label: "Reservadas", count: stats.inventory.reserved, color: "bg-amber-400" },
                  { label: "Disponíveis", count: stats.inventory.available, color: "bg-blue-200" },
                ].map(({ label, count, color }) => (
                  <span key={label} className="flex items-center text-[11px] text-muted-foreground">
                    <span className={cn("inline-block w-2 h-2 rounded-full mr-1.5", color)} />
                    {label} {count}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Recent Projects */}
        <div className="rounded-2xl border border-border bg-white p-6 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold">Projectos Recentes</h2>
            {projectsPage && (
              <span className="text-xs text-muted-foreground font-medium bg-muted px-2 py-0.5 rounded-full">
                {projectsPage.count}
              </span>
            )}
          </div>

          {projectsLoading && (
            <div className="space-y-1">
              {Array.from({ length: 4 }).map((_, i) => <ProjectRowSkeleton key={i} />)}
            </div>
          )}

          {projectsError && (
            <div className="flex-1 flex items-center justify-center">
              <p className="text-sm text-muted-foreground text-center px-4">
                Erro ao carregar projectos.
              </p>
            </div>
          )}

          {!projectsLoading && !projectsError && projects.length === 0 && (
            <div className="flex-1 flex items-center justify-center">
              <p className="text-sm text-muted-foreground text-center">Ainda não há projectos.</p>
            </div>
          )}

          {!projectsLoading && projects.length > 0 && (
            <div className="space-y-1 flex-1">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className="flex items-center p-3 rounded-xl hover:bg-muted/50 border border-transparent hover:border-border transition-all cursor-pointer group"
                >
                  <div className="h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center mr-4 group-hover:scale-110 transition-transform shrink-0">
                    <Building className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-bold text-sm truncate">{project.name}</h4>
                    <p className="text-xs text-muted-foreground truncate">
                      {project.city}{project.island ? `, ${project.island}` : ""}
                    </p>
                  </div>
                  <div className="shrink-0 ml-2">
                    <span className={cn(
                      "text-[10px] font-bold px-2 py-0.5 rounded-md",
                      PROJECT_STATUS_COLOR[project.status] ?? "text-slate-500 bg-slate-100"
                    )}>
                      {PROJECT_STATUS_LABEL[project.status] ?? project.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <button className="mt-6 w-full py-2.5 rounded-lg border border-border text-sm font-semibold hover:bg-muted transition-colors">
            Ver Todos os Projectos
          </button>
        </div>
      </div>
    </div>
  );
}
