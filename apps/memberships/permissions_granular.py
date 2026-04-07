"""
Granular Permissions for ImoOS
Maps roles to module permissions
"""
from rest_framework.permissions import BasePermission

# Permission matrix: role -> module -> actions
PERMISSION_MATRIX = {
    "admin": {
        "crm": ["view", "create", "edit", "delete"],
        "projects": ["view", "create", "edit", "delete"],
        "contracts": ["view", "create", "edit", "delete"],
        "construction": ["view", "create", "edit", "delete"],
        "budget": ["view", "create", "edit", "delete"],
        "inventory": ["view", "create", "edit", "delete"],
        "users": ["view", "create", "edit", "delete"],
        "settings": ["view", "edit"],
        "reports": ["view", "export"],
    },
    "gestor": {
        "crm": ["view", "create", "edit"],
        "projects": ["view", "create", "edit"],
        "contracts": ["view", "create", "edit"],
        "construction": ["view", "create", "edit"],
        "budget": ["view", "create", "edit"],
        "inventory": ["view", "create", "edit"],
        "users": ["view"],
        "settings": ["view"],
        "reports": ["view", "export"],
    },
    "vendedor": {
        "crm": ["view", "create", "edit"],
        "projects": ["view"],
        "contracts": ["view", "create"],
        "construction": ["view"],
        "budget": ["view"],
        "inventory": ["view"],
        "users": [],
        "settings": [],
        "reports": ["view"],
    },
    "engenheiro": {
        "crm": ["view"],
        "projects": ["view"],
        "contracts": ["view"],
        "construction": ["view", "create", "edit"],
        "budget": ["view", "create", "edit"],
        "inventory": ["view", "create", "edit"],
        "users": [],
        "settings": [],
        "reports": ["view"],
    },
    "investidor": {
        "crm": [],
        "projects": ["view"],
        "contracts": ["view"],
        "construction": ["view"],
        "budget": ["view"],
        "inventory": ["view"],
        "users": [],
        "settings": [],
        "reports": ["view"],
    },
}


def has_permission(role: str, module: str, action: str) -> bool:
    """Check if role has permission for action in module."""
    if role not in PERMISSION_MATRIX:
        return False
    module_perms = PERMISSION_MATRIX[role].get(module, [])
    return action in module_perms


def get_module_permissions(role: str, module: str) -> list:
    """Get all permissions for a role in a module."""
    return PERMISSION_MATRIX.get(role, {}).get(module, [])


class HasModulePermission(BasePermission):
    """
    DRF Permission class for module-level permissions.
    Usage: permission_classes = [HasModulePermission("crm", "view")]
    """
    
    def __init__(self, module: str, action: str):
        self.module = module
        self.action = action
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check role-based permission
        return has_permission(request.user.role, self.module, self.action)


# Convenience permission classes
class CanViewCRM(HasModulePermission):
    def __init__(self):
        super().__init__("crm", "view")

class CanEditCRM(HasModulePermission):
    def __init__(self):
        super().__init__("crm", "edit")

class CanViewContracts(HasModulePermission):
    def __init__(self):
        super().__init__("contracts", "view")

class CanEditContracts(HasModulePermission):
    def __init__(self):
        super().__init__("contracts", "edit")
