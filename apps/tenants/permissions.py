from rest_framework.permissions import BasePermission
from apps.users.permissions import IsTenantMember


class IsTenantAdmin(BasePermission):
    """
    User must be authenticated, pass IsTenantMember, and hold an active
    'admin' TenantMembership row in the current tenant's schema.

    Role is stored in TenantMembership (TENANT_APP) — per-schema — so a
    user who is admin in Tenant A has no elevated access in Tenant B.
    Previously relied on User.role (SHARED_APP), which was a global flag.
    """
    message = 'Tenant admin role required.'

    def has_permission(self, request, view):
        if not IsTenantMember().has_permission(request, view):
            return False
        # Lazy import avoids circular dependency at module load time and
        # ensures the query runs only when the permission is actually checked.
        from apps.memberships.models import TenantMembership
        return TenantMembership.objects.filter(
            user=request.user,
            role=TenantMembership.ROLE_ADMIN,
            is_active=True,
        ).exists()
