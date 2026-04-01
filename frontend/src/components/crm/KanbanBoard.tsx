"use client";

import { useState } from "react";
import {
    DndContext,
    DragOverlay,
    pointerWithin,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    type DragEndEvent,
    type DragStartEvent,
} from "@dnd-kit/core";
import { sortableKeyboardCoordinates } from "@dnd-kit/sortable";
import { useLeadsByStage, useMoveLeadStage, type Lead, type LeadStatus } from "@/hooks/useLeads";
import { KanbanColumn } from "./KanbanColumn";
import { LeadCard } from "./LeadCard";
import { ReservationModal } from "./ReservationModal";
import { Skeleton } from "@/components/ui/Skeleton";

const STAGES: LeadStatus[] = [
    "NEW",
    "CONTACTED",
    "VISIT_SCHEDULED",
    "PROPOSAL_SENT",
    "NEGOTIATION",
    "WON",
    "LOST",
];

export function KanbanBoard() {
    const { data: pipeline, isLoading } = useLeadsByStage();
    const { mutate: moveStage } = useMoveLeadStage();

    const [activeLead, setActiveLead] = useState<Lead | null>(null);
    const [selectedLeadForReservation, setSelectedLeadForReservation] = useState<Lead | null>(null);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        }),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    function handleDragStart(event: DragStartEvent) {
        const { active } = event;
        setActiveLead(active.data.current?.lead as Lead);
    }

    function handleDragEnd(event: DragEndEvent) {
        const { active, over } = event;

        if (over && active.id !== over.id) {
            const leadId = active.id as string;
            const newStage = over.id as LeadStatus;

            // Optimistic update would require local state management for the whole board
            // Here we rely on React Query invalidation in useMoveLeadStage
            moveStage({ id: leadId, stage: newStage });
        }

        setActiveLead(null);
    }

    if (isLoading || !pipeline) {
        return (
            <div className="flex space-x-6 overflow-x-auto pb-4 px-1 min-h-[600px]">
                {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="w-72 shrink-0 space-y-4">
                        <Skeleton className="h-6 w-32" />
                        <Skeleton className="h-[400px] w-full rounded-2xl" />
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className="relative">
            <DndContext
                sensors={sensors}
                collisionDetection={pointerWithin}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
            >
                <div className="flex space-x-6 overflow-x-auto pb-8 px-1 scrollbar-hide min-h-[calc(100vh-16rem)]">
                    {STAGES.map((id) => (
                        <KanbanColumn
                            key={id}
                            id={id}
                            column={pipeline![id]}
                            onReserve={(lead) => setSelectedLeadForReservation(lead)}
                        />
                    ))}
                </div>

                <DragOverlay>
                    {activeLead ? (
                        <div className="w-72 shadow-2xl rotate-3">
                            <LeadCard lead={activeLead} />
                        </div>
                    ) : null}
                </DragOverlay>
            </DndContext>

            {selectedLeadForReservation && (
                <ReservationModal
                    lead={selectedLeadForReservation}
                    onClose={() => setSelectedLeadForReservation(null)}
                    onSuccess={() => {
                        setSelectedLeadForReservation(null);
                        // Invalidate units query if needed, or rely on mutation's success
                    }}
                />
            )}
        </div>
    );
}
