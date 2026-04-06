/**
 * Mobile Hooks — Barrel Export
 * ImoOS Field App
 */

export {
  useConstructionTasksMobile,
  useConstructionTaskMobile,
  useTaskUpdateMutation,
  usePhotoUploadMutation,
} from "./useConstructionTasksMobile";

// Re-export from global hooks for convenience
export { useMobileTasks, useMobileTask } from "@/hooks/useMobileTasks";
export { useOfflineSync, useNetworkStatus } from "@/hooks/useOfflineSync";
