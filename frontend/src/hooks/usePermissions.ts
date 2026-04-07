/**
 * usePermissions — Hook for granular permission checking
 */
import { useAuth } from "@/contexts/AuthContext";

// Permission matrix matching backend
const PERMISSION_MATRIX: Record<string, Record<string, string[]>> = {
  admin: {
    crm: ["view", "create", "edit", "delete"],
    projects: ["view", "create", "edit", "delete"],
    contracts: ["view", "create", "edit", "delete"],
    construction: ["view", "create", "edit", "delete"],
    budget: ["view", "create", "edit", "delete"],
    inventory: ["view", "create", "edit", "delete"],
    users: ["view", "create", "edit", "delete"],
    settings: ["view", "edit"],
    reports: ["view", "export"],
  },
  gestor: {
    crm: ["view", "create", "edit"],
    projects: ["view", "create", "edit"],
    contracts: ["view", "create", "edit"],
    construction: ["view", "create", "edit"],
    budget: ["view", "create", "edit"],
    inventory: ["view", "create", "edit"],
    users: ["view"],
    settings: ["view"],
    reports: ["view", "export"],
  },
  vendedor: {
    crm: ["view", "create", "edit"],
    projects: ["view"],
    contracts: ["view", "create"],
    construction: ["view"],
    budget: ["view"],
    inventory: ["view"],
    users: [],
    settings: [],
    reports: ["view"],
  },
  engenheiro: {
    crm: ["view"],
    projects: ["view"],
    contracts: ["view"],
    construction: ["view", "create", "edit"],
    budget: ["view", "create", "edit"],
    inventory: ["view", "create", "edit"],
    users: [],
    settings: [],
    reports: ["view"],
  },
  investidor: {
    crm: [],
    projects: ["view"],
    contracts: ["view"],
    construction: ["view"],
    budget: ["view"],
    inventory: ["view"],
    users: [],
    settings: [],
    reports: ["view"],
  },
};

export type Module = "crm" | "projects" | "contracts" | "construction" | "budget" | "inventory" | "users" | "settings" | "reports";
export type Action = "view" | "create" | "edit" | "delete" | "export";

export function usePermissions() {
  const { user } = useAuth();
  const role = user?.role || "investidor";

  const hasPermission = (module: Module, action: Action): boolean => {
    const modulePerms = PERMISSION_MATRIX[role]?.[module] || [];
    return modulePerms.includes(action);
  };

  const canView = (module: Module) => hasPermission(module, "view");
  const canCreate = (module: Module) => hasPermission(module, "create");
  const canEdit = (module: Module) => hasPermission(module, "edit");
  const canDelete = (module: Module) => hasPermission(module, "delete");

  // Module-specific shortcuts
  const permissions = {
    crm: { view: canView("crm"), create: canCreate("crm"), edit: canEdit("crm"), delete: canDelete("crm") },
    contracts: { view: canView("contracts"), create: canCreate("contracts"), edit: canEdit("contracts"), delete: canDelete("contracts") },
    construction: { view: canView("construction"), create: canCreate("construction"), edit: canEdit("construction"), delete: canDelete("construction") },
    budget: { view: canView("budget"), create: canCreate("budget"), edit: canEdit("budget"), delete: canDelete("budget") },
    users: { view: canView("users"), create: canCreate("users"), edit: canEdit("users"), delete: canDelete("users") },
    settings: { view: canView("settings"), edit: canEdit("settings") },
  };

  return {
    hasPermission,
    canView,
    canCreate,
    canEdit,
    canDelete,
    permissions,
    role,
    isAdmin: role === "admin",
    isManager: role === "gestor",
  };
}

// Component wrapper for permission-based rendering
export function PermissionGuard({ 
  module, 
  action, 
  children, 
  fallback = null 
}: { 
  module: Module; 
  action: Action; 
  children: React.ReactNode; 
  fallback?: React.ReactNode;
}) {
  const { hasPermission } = usePermissions();
  return hasPermission(module, action) ? <>{children}</> : <>{fallback}</>;
}
