/**
 * StatusBadge — ImoOS
 * Unit status + Project status coloured pill badges.
 * Skill: unit-status-workflow, tailwind-design-tokens
 */
import { cn } from "@/lib/utils";
import type { UnitStatus } from "@/hooks/useUnits";
import type { ProjectStatus } from "@/hooks/useProjects";

// ----- Unit -----

const UNIT_CONFIG: Record<UnitStatus, { label: string; className: string }> = {
  AVAILABLE: { label: "Disponível", className: "text-emerald-700 bg-emerald-50 border-emerald-200" },
  RESERVED: { label: "Reservado", className: "text-amber-700  bg-amber-50  border-amber-200" },
  CONTRACT: { label: "Contrato", className: "text-violet-700 bg-violet-50 border-violet-200" },
  SOLD: { label: "Vendido", className: "text-red-700    bg-red-50    border-red-200" },
  MAINTENANCE: { label: "Manutenção", className: "text-slate-600  bg-slate-100 border-slate-200" },
};

interface UnitStatusBadgeProps {
  status: UnitStatus;
  className?: string;
}

export function UnitStatusBadge({ status, className }: UnitStatusBadgeProps) {
  const cfg = UNIT_CONFIG[status] ?? { label: status, className: "text-slate-600 bg-slate-100 border-slate-200" };
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold leading-none", cfg.className, className)}>
      {cfg.label}
    </span>
  );
}

// ----- Project -----

const PROJECT_CONFIG: Record<ProjectStatus, { label: string; className: string }> = {
  PLANNING: { label: "Planeamento", className: "text-amber-700  bg-amber-50  border-amber-200" },
  LICENSING: { label: "Licenciamento", className: "text-purple-700 bg-purple-50 border-purple-200" },
  CONSTRUCTION: { label: "Em Construção", className: "text-blue-700   bg-blue-50   border-blue-200" },
  COMPLETED: { label: "Concluído", className: "text-emerald-700 bg-emerald-50 border-emerald-200" },
};

interface ProjectStatusBadgeProps {
  status: ProjectStatus;
  className?: string;
}

export function ProjectStatusBadge({ status, className }: ProjectStatusBadgeProps) {
  const cfg = PROJECT_CONFIG[status] ?? { label: status, className: "text-slate-600 bg-slate-100 border-slate-200" };
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold leading-none", cfg.className, className)}>
      {cfg.label}
    </span>
  );
}

// ----- Lead status -----

type LeadStatusKey =
  | "NEW"
  | "CONTACTED"
  | "VISIT_SCHEDULED"
  | "PROPOSAL_SENT"
  | "NEGOTIATION"
  | "WON"
  | "LOST";

const LEAD_CONFIG: Record<LeadStatusKey, { label: string; className: string }> = {
  NEW: { label: "Novo", className: "text-slate-700 bg-slate-50 border-slate-200" },
  CONTACTED: { label: "Contactado", className: "text-blue-700  bg-blue-50  border-blue-200" },
  VISIT_SCHEDULED: { label: "Visita Agendada", className: "text-indigo-700 bg-indigo-50 border-indigo-200" },
  PROPOSAL_SENT: { label: "Proposta Enviada", className: "text-amber-700  bg-amber-50  border-amber-200" },
  NEGOTIATION: { label: "Em Negociação", className: "text-orange-700 bg-orange-50 border-orange-200" },
  WON: { label: "Ganho", className: "text-emerald-700 bg-emerald-50 border-emerald-200" },
  LOST: { label: "Perdido", className: "text-slate-600  bg-slate-100 border-slate-200" },
};

interface LeadStatusBadgeProps {
  status: string; // Keep it string to allow for dynamic data but Typed internally
  className?: string;
}


export function LeadStatusBadge({ status, className }: LeadStatusBadgeProps) {
  const cfg = LEAD_CONFIG[status as LeadStatusKey] ?? { label: status, className: "text-slate-600 bg-slate-100 border-slate-200" };
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold leading-none", cfg.className, className)}>
      {cfg.label}
    </span>
  );
}

/**
 * Generic StatusBadge
 * Resolves status string to Unit, Project or Lead styling.
 */
export function StatusBadge({ status, className }: { status: string; className?: string }) {
  // If it matches a Unit status
  if (status in UNIT_CONFIG) return <UnitStatusBadge status={status as UnitStatus} className={className} />;
  // If it matches a Project status
  if (status in PROJECT_CONFIG) return <ProjectStatusBadge status={status as ProjectStatus} className={className} />;
  // Default to Lead/Generic styling
  return <LeadStatusBadge status={status} className={className} />;
}
