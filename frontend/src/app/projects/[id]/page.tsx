"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Building2, MapPin, CalendarClock, Layers, Building, BookmarkPlus, Box, FileImage } from "lucide-react";
import { cn } from "@/lib/utils";
import { useProject, featureToProject } from "@/hooks/useProjects";
import { useUnits } from "@/hooks/useUnits";
import { useBuildings } from "@/hooks/useBuildings";
import { ProjectStatusBadge, UnitStatusBadge } from "@/components/ui/StatusBadge";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate, formatArea, formatCve, formatEur } from "@/lib/format";
import { UnitReservationModal } from "@/components/crm/UnitReservationModal";
import type { Unit } from "@/hooks/useUnits";

type Tab = "overview" | "units" | "buildings" | "bim";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Visão Geral" },
  { id: "units", label: "Unidades" },
  { id: "buildings", label: "Edifícios" },
  { id: "bim", label: "BIM" },
];

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("overview");
  const [reservingUnit, setReservingUnit] = useState<Unit | null>(null);

  const { data: feature, isLoading, isError } = useProject(id);
  const project = feature ? featureToProject(feature) : null;

  // Buildings for this project
  const { data: buildings = [], isLoading: buildingsLoading } = useBuildings(id);

  // Units for this project
  const { data: unitsPage, isLoading: unitsLoading } = useUnits({
    project: id,
    page_size: 100,
  });
  const units = unitsPage?.results ?? [];

  // ----- Loading -----
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Skeleton className="h-14 w-14 rounded-2xl" />
          <div className="space-y-2">
            <Skeleton className="h-7 w-64" />
            <Skeleton className="h-5 w-40" />
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-white p-8 space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
    );
  }

  if (isError || !project) {
    return (
      <div className="flex flex-col items-center justify-center py-32 text-center">
        <div className="h-16 w-16 rounded-full bg-red-50 flex items-center justify-center mb-4">
          <Building2 className="h-8 w-8 text-red-500" />
        </div>
        <h2 className="text-lg font-bold text-foreground">Projecto não encontrado</h2>
        <p className="text-muted-foreground mt-1 text-sm">O projecto que procura não existe ou foi removido.</p>
        <button onClick={() => router.back()} className="mt-6 flex items-center text-sm font-bold text-primary hover:underline">
          <ArrowLeft className="h-4 w-4 mr-1.5" />
          Voltar aos projectos
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div>
        <button
          onClick={() => router.back()}
          className="flex items-center text-xs font-bold text-muted-foreground hover:text-primary mb-4 transition-colors uppercase tracking-widest"
        >
          <ArrowLeft className="h-3.5 w-3.5 mr-1.5" />
          Projectos
        </button>

        <div className="flex items-start justify-between flex-wrap gap-6">
          <div className="flex items-center space-x-5">
            <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0 border border-primary/10">
              <Building2 className="h-9 w-9 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground">{project.name}</h1>
              <div className="flex items-center space-x-3 mt-1.5">
                <span className="flex items-center text-sm text-muted-foreground font-medium">
                  <MapPin className="h-3.5 w-3.5 mr-1.5 text-primary/60" />
                  {project.city}{project.island ? `, ${project.island}` : ""}
                </span>
                <ProjectStatusBadge status={project.status} />
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* BIM Buttons */}
            <button
              onClick={() => router.push(`/projects/${id}/plans`)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium transition-colors"
            >
              <FileImage className="h-4 w-4" />
              Plantas 2D
            </button>
            <button
              onClick={() => router.push(`/projects/${id}/bim`)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-100 hover:bg-blue-200 text-blue-700 text-sm font-medium transition-colors"
            >
              <Box className="h-4 w-4" />
              BIM 3D
            </button>
            
            <div className="w-px h-8 bg-border" />
            
            {project.start_date && (
              <div className="flex flex-col items-end">
                <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-bold">Início</span>
                <span className="flex items-center text-sm font-bold text-foreground mt-0.5">
                  <CalendarClock className="h-3.5 w-3.5 mr-1.5 text-primary/60" />
                  {formatDate(project.start_date)}
                </span>
              </div>
            )}
            {project.expected_delivery_date && (
              <div className="flex flex-col items-end">
                <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-bold">Entrega</span>
                <span className="flex items-center text-sm font-bold text-foreground mt-0.5">
                  <CalendarClock className="h-3.5 w-3.5 mr-1.5 text-primary/60" />
                  {formatDate(project.expected_delivery_date)}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border space-x-8">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              "px-1 py-4 text-sm font-bold border-b-2 transition-all relative",
              tab === t.id
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
            )}
          >
            {t.label}
            {tab === t.id && (
              <span className="absolute -bottom-[2px] left-0 right-0 h-0.5 bg-primary rounded-full shadow-[0_0_8px_rgba(59,130,246,0.5)]"></span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content Area */}
      <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
        {/* Tab: Visão Geral */}
        {tab === "overview" && (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Description */}
            <div className="lg:col-span-2 rounded-2xl border border-border bg-white p-8 shadow-sm space-y-6">
              <div>
                <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4">Sobre o Projecto</h2>
                {project.description ? (
                  <p className="text-sm text-foreground leading-relaxed font-medium">{project.description}</p>
                ) : (
                  <p className="text-sm text-muted-foreground italic">Sem descrição disponível para este projecto.</p>
                )}
              </div>

              {project.address && (
                <div className="pt-6 border-t border-border">
                  <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-3">Localização</h2>
                  <div className="flex items-start space-x-2">
                    <MapPin className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                    <p className="text-sm text-foreground font-medium">{project.address}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Stats sidebar */}
            <div className="space-y-4">
              {[
                { label: "Total de Unidades", value: project.total_units != null ? String(project.total_units) : "—", color: "bg-blue-50" },
                { label: "Área Total", value: formatArea(project.total_area), color: "bg-emerald-50" },
                { label: "Cidade", value: project.city || "—", color: "bg-slate-50" },
                { label: "Ilha", value: project.island || "—", color: "bg-slate-50" },
              ].map(({ label, value, color }) => (
                <div key={label} className={cn("rounded-2xl border border-border p-5 shadow-sm bg-white")}>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold mb-2">{label}</p>
                  <p className="text-xl font-black text-foreground">{value}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab: Unidades */}
        {tab === "units" && (
          <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
            <div className="px-8 py-5 border-b border-border flex items-center justify-between bg-slate-50/50">
              <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Lista de Unidades</h2>
              <span className="rounded-full bg-white px-3 py-1 text-[11px] font-bold text-primary border border-primary/10 shadow-sm">
                {units.length} Unidades
              </span>
            </div>
            {unitsLoading ? (
              <div className="p-8 space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-14 w-full rounded-xl" />
                ))}
              </div>
            ) : units.length === 0 ? (
              <div className="p-20 text-center flex flex-col items-center">
                <div className="h-16 w-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
                  <Building className="h-8 w-8 text-muted-foreground/40" />
                </div>
                <p className="text-sm text-muted-foreground font-bold">Sem unidades registadas neste projecto.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border bg-slate-50/30">
                      {["Código", "Tipologia", "Piso", "Área Bruta", "Preço CVE", "Estado", ""].map((h) => (
                        <th key={h} className="px-6 py-4 text-left text-[10px] font-bold text-muted-foreground uppercase tracking-widest whitespace-nowrap">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {units.map((unit) => (
                      <tr key={unit.id} className="hover:bg-slate-50/80 transition-colors group">
                        <td className="px-6 py-4 font-mono font-bold text-foreground group-hover:text-primary transition-colors">
                          {unit.code}
                        </td>
                        <td className="px-6 py-4 text-muted-foreground font-medium">{unit.unit_type_detail?.name ?? "—"}</td>
                        <td className="px-6 py-4 text-muted-foreground font-medium">{unit.floor_number}º</td>
                        <td className="px-6 py-4 text-muted-foreground font-bold">{formatArea(unit.area_bruta)}</td>
                        <td className="px-6 py-4 font-black">
                          {unit.pricing ? formatCve(unit.pricing.final_price_cve) : "—"}
                        </td>
                        <td className="px-6 py-4">
                          <UnitStatusBadge status={unit.status} />
                        </td>
                        <td className="px-6 py-4 text-right">
                          {unit.status === "AVAILABLE" && (
                            <button
                              onClick={() => setReservingUnit(unit)}
                              className="inline-flex items-center gap-1.5 rounded-lg border border-primary/20 bg-primary/5 px-3 py-1.5 text-xs font-bold text-primary hover:bg-primary hover:text-white transition-all active:scale-95"
                            >
                              <BookmarkPlus className="h-3.5 w-3.5" />
                              Reservar
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Tab: Edifícios */}
        {tab === "buildings" && (
          <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
            <div className="px-8 py-5 border-b border-border bg-slate-50/50">
              <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Edifícios e Blocos</h2>
            </div>
            {buildingsLoading ? (
              <div className="p-8 space-y-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <Skeleton key={i} className="h-20 w-full rounded-xl" />
                ))}
              </div>
            ) : buildings.length > 0 ? (
              <div className="divide-y divide-border">
                {buildings.map((b) => (
                  <div key={b.id} className="px-8 py-6 flex items-center justify-between hover:bg-slate-50/80 transition-colors group">
                    <div className="flex items-center space-x-5">
                      <div className="h-12 w-12 rounded-xl bg-slate-100 flex items-center justify-center shrink-0 border border-slate-200 group-hover:bg-primary/10 group-hover:border-primary/10 transition-colors">
                        <Layers className="h-6 w-6 text-slate-500 group-hover:text-primary transition-colors" />
                      </div>
                      <div>
                        <p className="font-bold text-foreground text-lg">{b.name}</p>
                        <p className="text-xs text-muted-foreground font-medium">
                          Código: <span className="font-mono text-foreground/70">{b.code}</span> · {b.floors_count} piso{b.floors_count !== 1 ? "s" : ""}
                        </p>
                      </div>
                    </div>
                    <button className="px-4 py-2 rounded-lg bg-muted text-xs font-bold text-foreground hover:bg-border transition-all opacity-0 group-hover:opacity-100">
                      Gerir Blocos
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-20 text-center flex flex-col items-center">
                <div className="h-16 w-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
                  <Layers className="h-8 w-8 text-muted-foreground/40" />
                </div>
                <p className="text-sm text-muted-foreground font-bold">Sem edifícios registados neste projecto.</p>
              </div>
            )}
          </div>
        )}

        {/* Tab: BIM */}
        {tab === "bim" && (
          <div className="space-y-6">
            {/* BIM Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card 
                icon={<Box className="h-8 w-8 text-blue-600" />}
                title="Modelo BIM 3D"
                description="Visualize o modelo 3D do projeto, navegue pelos elementos e associe-os a tarefas."
                action="Abrir Viewer 3D"
                onAction={() => router.push(`/projects/${id}/bim`)}
              />
              <Card 
                icon={<FileImage className="h-8 w-8 text-emerald-600" />}
                title="Plantas 2D"
                description="Consulte as plantas arquitetónicas, cortes e outras representações 2D."
                action="Ver Plantas"
                onAction={() => router.push(`/projects/${id}/plans`)}
              />
              <Card 
                icon={<Layers className="h-8 w-8 text-violet-600" />}
                title="Elementos"
                description="Lista completa de elementos BIM: paredes, portas, janelas, etc."
                action="Explorar"
                onAction={() => router.push(`/projects/${id}/bim`)}
              />
            </div>

            {/* Quick Info */}
            <div className="rounded-2xl border border-border bg-white p-8 shadow-sm">
              <h2 className="text-lg font-bold text-foreground mb-4">Sobre o Módulo BIM</h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                O módulo BIM (Building Information Modeling) permite visualizar e gerir o modelo digital 
                da construção. Associe elementos 3D a tarefas de obra e unidades habitacionais para 
                um acompanhamento integrado do projeto.
              </p>
              <div className="mt-6 flex gap-4">
                <button
                  onClick={() => router.push(`/projects/${id}/bim`)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium"
                >
                  <Box className="h-4 w-4" />
                  Abrir Modelo 3D
                </button>
                <button
                  onClick={() => router.push(`/projects/${id}/plans`)}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-border text-foreground rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  <FileImage className="h-4 w-4" />
                  Ver Plantas 2D
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Reservation modal — unit-first flow */}
      <UnitReservationModal
        unit={reservingUnit}
        onClose={() => setReservingUnit(null)}
        onSuccess={() => setReservingUnit(null)}
      />
    </div>
  );
}

// BIM Card Component
interface CardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action: string;
  onAction: () => void;
}

function Card({ icon, title, description, action, onAction }: CardProps) {
  return (
    <div className="rounded-2xl border border-border bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="h-12 w-12 rounded-xl bg-gray-50 flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="font-bold text-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground mb-4">{description}</p>
      <button
        onClick={onAction}
        className="text-sm font-bold text-primary hover:text-primary/80 transition-colors"
      >
        {action} →
      </button>
    </div>
  );
}
