from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class PublicEndpointThrottle(AnonRateThrottle):
    """100 req/hour per IP for all public endpoints (CLAUDE.md security rule)."""
    rate = '100/hour'


class AuthenticatedUserThrottle(UserRateThrottle):
    """500 req/hour per authenticated user."""
    rate = '500/hour'
