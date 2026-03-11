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
        
        # Public schema access is usually reserved for shared apps (Tenants, etc.)
        # Business apps (TENANT_APPS) should always have a specific schema.
        
        return token_schema == active_schema
