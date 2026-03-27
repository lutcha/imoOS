from django.db import connection
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication


class IsTenantMember(BasePermission):
    """
    JWT tenant_schema must match active schema from connection (set by middleware).
    Mandatory for multi-tenant isolation.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # If it's a superuser, they might need access across tenants 
        # but for business data, they should still belong to a schema context.
        # For now, follow the strict rule in DEFENSIVE.md
        
        # request.auth is the validated token object if using JWTAuthentication
        if not request.auth:
            return False
            
        token_schema = request.auth.get('tenant_schema')
        active_schema = connection.schema_name
        
        # Business endpoints must never run in the public schema.
        # If connection.schema_name == 'public' it means a request arrived on
        # the platform domain (no tenant resolved) — block it here so views
        # are never executed without a real tenant context.
        if active_schema == 'public':
            return False

        return token_schema == active_schema


class IsInvestor(BasePermission):
    """
    Grants access only to users whose TenantMembership role is 'investidor'.
    Must be combined with IsTenantMember.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from apps.memberships.models import TenantMembership
        return TenantMembership.objects.filter(
            user=request.user,
            role=TenantMembership.ROLE_INVESTIDOR,
            is_active=True,
        ).exists()


class IsInvestorOrAdmin(BasePermission):
    """
    Grants access to users with role 'investidor' OR 'admin' in the active tenant.
    Must be combined with IsTenantMember.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from apps.memberships.models import TenantMembership
        return TenantMembership.objects.filter(
            user=request.user,
            role__in=[TenantMembership.ROLE_INVESTIDOR, TenantMembership.ROLE_ADMIN],
            is_active=True,
        ).exists()
