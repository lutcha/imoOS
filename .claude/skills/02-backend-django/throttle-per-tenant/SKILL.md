---
name: throttle-per-tenant
description: Rate limiting scoped per tenant in ImoOS using SimpleRateThrottle. Auto-load when adding rate limiting to any endpoint.
argument-hint: [rate] [scope]
allowed-tools: Read, Write
---

# Per-Tenant Rate Limiting — ImoOS

## Custom Throttle Class
```python
# apps/core/throttling.py
from rest_framework.throttling import SimpleRateThrottle
from django.db import connection

class TenantScopedThrottle(SimpleRateThrottle):
    """Rate limit per tenant + user combination."""
    scope = 'tenant_user'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            tenant_schema = getattr(connection, 'schema_name', 'public')
            ident = f'{tenant_schema}:{request.user.id}'
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}

class PublicEndpointThrottle(SimpleRateThrottle):
    """For public endpoints like webhooks and lead capture forms."""
    scope = 'public'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }
```

## Settings
```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': ['apps.core.throttling.TenantScopedThrottle'],
    'DEFAULT_THROTTLE_RATES': {
        'tenant_user': '1000/hour',   # Authenticated per-tenant user
        'public': '100/hour',          # Anonymous/public endpoints
        'webhook': '500/hour',         # Webhook receivers
        'login': '20/minute',          # Auth endpoints (brute force protection)
    }
}
```

## Per-View Override
```python
class LoginView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]  # Stricter for auth

class WebhookView(APIView):
    throttle_classes = [WebhookThrottle]
    authentication_classes = []  # No auth for webhooks
```

## Key Rules
- All public endpoints must have throttling — no exceptions
- Auth endpoints use stricter rate (20/minute) to prevent brute force
- Throttle keys include tenant_schema to avoid cross-tenant rate sharing
- On `429 Too Many Requests`, return Retry-After header
