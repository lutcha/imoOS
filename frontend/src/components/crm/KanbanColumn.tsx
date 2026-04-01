"use client";

import { useDroppable } from "@dnd-kit/core";
import { cn } from "@/lib/utils";
import type { Lead, LeadStatus, PipelineColumn } from "@/hooks/useLeads";
import { LeadCard } from "./LeadCard";

interface KanbanColumnProps {
    id: LeadStatus;
    column: PipelineColumn;
    onReserve?: (lead: Lead) => void;
    onView?: (lead: Lead) => void;
}

export function KanbanColumn({ id, column, onReserve, onView }: KanbanColumnProps) {
    const { setNodeRef, isOver } = useDroppable({
        id,
    });

    return (
        <div className="flex flex-col w-72 shrink-0 h-full">
            <div className="flex items-center justify-between mb-4 px-1">
                <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-bold text-foreground">{column.label}</h3>
                    <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-bold text-muted-foreground border border-border">
                        {column.count}
                    </span>
                </div>
            </div>

            <div
                ref={setNodeRef}
                className={cn(
                    "flex-1 rounded-2xl p-2 transition-colors space-y-3 overflow-y-auto min-h-[500px]",
                    isOver ? "bg-primary/5 ring-2 ring-primary/10" : "bg-slate-50/50"
                )}
            >
                {column.leads.map((lead) => (
                    <LeadCard
                        key={lead.id}
                        lead={lead}
                        onReserve={onReserve}
                        onView={onView}
                    />
                ))}
                {column.leads.length === 0 && !isOver && (
                    <div className="flex flex-col items-center justify-center py-12 px-4 border-2 border-dashed border-slate-200 rounded-xl">
                        <p className="text-[11px] text-muted-foreground text-center">Nenhum lead nesta etapa</p>
                    </div>
                )}
            </div>
        </div>
    );
}
