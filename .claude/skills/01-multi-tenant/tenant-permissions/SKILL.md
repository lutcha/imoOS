---
name: tenant-permissions
description: RBAC permissions for ImoOS using django-guardian. Roles: Admin, Gestor, Vendedor, Engenheiro, Investidor. Auto-load when implementing access control on any model or view.
argument-hint: [role] [model]
allowed-tools: Read, Write, Grep
---

# Tenant Permissions (RBAC) — ImoOS

## Role Definitions
```python
# apps/users/models.py
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_ADMIN = 'admin'
    ROLE_GESTOR = 'gestor'          # Project manager
    ROLE_VENDEDOR = 'vendedor'      # Sales agent
    ROLE_ENGENHEIRO = 'engenheiro'  # Site engineer (mobile app)
    ROLE_INVESTIDOR = 'investidor'  # Read-only investor portal
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_GESTOR, 'Gestor de Projecto'),
        (ROLE_VENDEDOR, 'Vendedor'),
        (ROLE_ENGENHEIRO, 'Engenheiro de Obra'),
        (ROLE_INVESTIDOR, 'Investidor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VENDEDOR)
```

## Role-Based ViewSet Permissions
```python
# apps/core/permissions.py
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsGestorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'gestor']

class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']

# ViewSet usage
class ProjectViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsGestorOrAdmin()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsTenantMember()]
```

## Object-Level Permissions (django-guardian)
```python
# Grant specific user permission on a single object
from guardian.shortcuts import assign_perm, remove_perm

# Only this vendedor can edit this specific lead
assign_perm('crm.change_lead', vendedor_user, lead_instance)

# Check in view
from guardian.shortcuts import get_objects_for_user
my_leads = get_objects_for_user(request.user, 'crm.change_lead', Lead)
```

## Permission Matrix
| Action | Admin | Gestor | Vendedor | Engenheiro | Investidor |
|--------|-------|--------|----------|------------|------------|
| Manage tenants | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create/Edit projects | ✅ | ✅ | ❌ | ❌ | ❌ |
| View all units | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reserve unit | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit daily log | ✅ | ✅ | ❌ | ✅ | ❌ |
| View financials | ✅ | ✅ | ❌ | ❌ | ✅ (own) |
