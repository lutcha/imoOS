/**
 * Skeleton — ImoOS
 * Pulse-animate placeholder for loading states.
 * Skill: tailwind-design-tokens
 */
import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      aria-hidden="true"
    />
  );
}

/** Full KPI stat card skeleton */
export function StatCardSkeleton() {
  return (
    <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <Skeleton className="h-11 w-11 rounded-xl" />
        <Skeleton className="h-5 w-12 rounded-full" />
      </div>
      <div className="mt-4 space-y-2">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-9 w-20" />
        <Skeleton className="h-3 w-32" />
      </div>
    </div>
  );
}

/** Recent project row skeleton */
export function ProjectRowSkeleton() {
  return (
    <div className="flex items-center p-3 rounded-xl">
      <Skeleton className="h-12 w-12 rounded-lg mr-4 shrink-0" />
      <div className="flex-1 space-y-1.5">
        <Skeleton className="h-4 w-36" />
        <Skeleton className="h-3 w-24" />
      </div>
      <Skeleton className="h-5 w-20 rounded-md ml-2 shrink-0" />
    </div>
  );
}
