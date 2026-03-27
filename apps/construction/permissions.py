from rest_framework.permissions import BasePermission


class IsEngineerOrAdmin(BasePermission):
    """Allow admin, gestor, or engenheiro roles (from TenantMembership)."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        from apps.memberships.models import TenantMembership

        try:
            m = TenantMembership.objects.get(user=request.user)
            return m.is_active and m.role in (
                TenantMembership.ROLE_ADMIN,
                TenantMembership.ROLE_GESTOR,
                TenantMembership.ROLE_ENGENHEIRO,
            )
        except TenantMembership.DoesNotExist:
            return False
