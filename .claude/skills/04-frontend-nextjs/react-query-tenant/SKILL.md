---
name: react-query-tenant
description: TanStack Query patterns for ImoOS with tenant-scoped cache keys, invalidation on mutations, and optimistic updates. Auto-load when writing data-fetching hooks.
argument-hint: [model] [operations]
allowed-tools: Read, Write
---

# React Query with Tenant Scoping — ImoOS

## Query Key Convention
```typescript
// ALWAYS include tenant schema in cache keys to prevent cross-tenant contamination
const queryKeys = {
  units: (schema: string) => ['units', schema] as const,
  unit: (schema: string, id: string) => ['units', schema, id] as const,
  unitsFiltered: (schema: string, filters: object) => ['units', schema, filters] as const,
};
```

## Standard Data Hook
```typescript
// hooks/useUnits.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTenant } from '@/contexts/TenantContext';
import apiClient from '@/lib/api-client';

export function useUnits(filters: UnitFilters = {}) {
  const { schema } = useTenant();
  return useQuery({
    queryKey: queryKeys.unitsFiltered(schema, filters),
    queryFn: () => apiClient.get('/api/v1/units/', { params: filters }).then(r => r.data),
    staleTime: 30_000,    // 30s — balance freshness vs requests
    gcTime: 5 * 60_000,   // 5min cache retention
  });
}

export function useUpdateUnitStatus() {
  const queryClient = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      apiClient.patch(`/api/v1/units/${id}/`, { status }).then(r => r.data),

    // Optimistic update
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.units(schema) });
      const prev = queryClient.getQueryData(queryKeys.unit(schema, id));
      queryClient.setQueryData(queryKeys.unit(schema, id), (old: any) => ({ ...old, status }));
      return { prev };
    },
    onError: (err, vars, ctx) => {
      queryClient.setQueryData(queryKeys.unit(schema, vars.id), ctx?.prev);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.units(schema) });
    },
  });
}
```

## Key Rules
- Tenant schema MUST be first element in queryKey arrays (enables selective invalidation)
- Invalidate parent query on mutation settlement — always use `onSettled` not `onSuccess`
- `staleTime: 30_000` is the default — adjust per sensitivity (dashboard: 60s, reservations: 5s)
- Never share QueryClient across tenants — create per-tenant client if doing SSR
