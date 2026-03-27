from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class PublicEndpointThrottle(AnonRateThrottle):
    """100 req/hour per IP for all public endpoints (CLAUDE.md security rule)."""
    rate = '100/hour'


class AuthenticatedUserThrottle(UserRateThrottle):
    """500 req/hour per authenticated user."""
    rate = '500/hour'


class TenantScopedThrottle(UserRateThrottle):
    """
    1000 req/hour per authenticated user, scoped per tenant schema.
    Cache key includes the tenant schema so limits are isolated between tenants.
    """
    rate = '1000/hour'

    def get_cache_key(self, request, view):
        key = super().get_cache_key(request, view)
        if key is None:
            return None
        from django.db import connection
        schema = getattr(connection, 'schema_name', 'public')
        return f'{schema}_{key}'
