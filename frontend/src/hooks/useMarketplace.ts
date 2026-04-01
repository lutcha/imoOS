/**
 * useMarketplace — ImoOS
 * API path: api/v1/marketplace/listings/
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";

// ----- Types -----

export type ListingStatus = "PENDING_SYNC" | "PUBLISHED" | "PAUSED" | "REMOVED";

export interface MarketplaceListing {
  id: string;
  unit: string;
  unit_code: string;
  project_name: string;
  imocv_listing_id: string;
  status: ListingStatus;
  last_synced_at: string | null;
  sync_error_display: string | null;
  price_override_cve: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MarketplaceListingsPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: MarketplaceListing[];
}

// ----- Query keys -----

export const marketplaceKeys = {
  all: (schema: string) => ["marketplace-listings", schema] as const,
  list: (schema: string) =>
    ["marketplace-listings", schema, "list"] as const,
};

// ----- Hooks -----

export function useMarketplaceListings() {
  const { schema } = useTenant();

  return useQuery<MarketplaceListingsPage>({
    queryKey: marketplaceKeys.list(schema),
    queryFn: () =>
      apiClient
        .get<MarketplaceListingsPage>("/marketplace/listings/")
        .then((r) => r.data),
    staleTime: 30_000,
    enabled: !!schema,
  });
}

export function useSyncListing() {
  const queryClient = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (listingId: string) =>
      apiClient
        .post(`/marketplace/listings/${listingId}/sync/`)
        .then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: marketplaceKeys.all(schema) });
    },
  });
}

export function useSyncAllListings() {
  const queryClient = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: () =>
      apiClient
        .post("/marketplace/listings/sync_all/")
        .then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: marketplaceKeys.all(schema) });
    },
  });
}

export function useUpdateListing() {
  const queryClient = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: ListingStatus }) =>
      apiClient
        .patch<MarketplaceListing>(`/marketplace/listings/${id}/`, { status })
        .then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: marketplaceKeys.all(schema) });
    },
  });
}
