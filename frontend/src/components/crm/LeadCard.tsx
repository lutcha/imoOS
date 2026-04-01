"use client";

import { useDraggable } from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import { MoreHorizontal, Calendar, CreditCard, Building } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Lead } from "@/hooks/useLeads";
import { formatCve } from "@/lib/format";

interface LeadCardProps {
    lead: Lead;
    onReserve?: (lead: Lead) => void;
    onView?: (lead: Lead) => void;
}

export function LeadCard({ lead, onReserve, onView }: LeadCardProps) {
    const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
        id: lead.id,
        data: { lead },
    });

    const style = {
        transform: CSS.Translate.toString(transform),
        opacity: isDragging ? 0.3 : 1,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className={cn(
                "group relative rounded-xl border border-border bg-white p-4 shadow-sm transition-all hover:shadow-md",
                isDragging ? "z-50 ring-2 ring-primary/20" : "cursor-grab active:cursor-grabbing"
            )}
        >
            <div className="flex items-start justify-between mb-2">
                <span className="inline-flex items-center rounded-full bg-slate-50 px-2 py-0.5 text-[10px] font-medium text-slate-600 border border-slate-100 uppercase tracking-tight">
                    {lead.source.toLowerCase()}
                </span>
                <button
                    className="rounded-lg p-1 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                    {...attributes}
                    {...listeners}
                >
                    <MoreHorizontal className="h-4 w-4" />
                </button>
            </div>

            <div className="space-y-3">
                <div>
                    <h3 className="text-sm font-bold text-foreground leading-tight">
                        {lead.first_name} {lead.last_name}
                    </h3>
                    {lead.project_name && (
                        <div className="flex items-center text-[11px] text-muted-foreground mt-1">
                            <Building className="h-3 w-3 mr-1" />
                            {lead.project_name} {lead.unit_number && `— ${lead.unit_number}`}
                        </div>
                    )}
                </div>

                <div className="flex items-center justify-between text-[11px]">
                    <div className="flex items-center text-muted-foreground">
                        <CreditCard className="h-3 w-3 mr-1" />
                        {lead.budget ? formatCve(lead.budget) : "Sem orçamento"}
                    </div>
                    <div className="flex items-center text-muted-foreground">
                        <Calendar className="h-3 w-3 mr-1" />
                        0d
                    </div>
                </div>

                <div className="pt-3 border-t border-border flex items-center space-x-2">
                    <button
                        onClick={() => onView?.(lead)}
                        className="flex-1 rounded-lg bg-muted px-2 py-1.5 text-[11px] font-semibold text-foreground hover:bg-muted/80 transition-colors"
                    >
                        Ver
                    </button>
                    <button
                        onClick={() => onReserve?.(lead)}
                        className="flex-[1.5] rounded-lg bg-primary/10 px-2 py-1.5 text-[11px] font-semibold text-primary hover:bg-primary/20 transition-colors"
                    >
                        Reservar
                    </button>
                </div>
            </div>
        </div>
    );
}
