---
name: jwt-tenant-claims
description: Generate JWT tokens with tenant_schema claim for ImoOS multi-tenant auth. Auto-load when implementing login, token refresh, or auth middleware.
argument-hint: [token-type] [claims]
allowed-tools: Read, Write, Grep
---

# JWT Tenant Claims — ImoOS

## Custom Token Serializer
```python
# apps/users/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Inject tenant_schema from active connection
        from django.db import connection
        token['tenant_schema'] = connection.schema_name
        token['tenant_name'] = connection.tenant.name
        token['user_email'] = user.email
        token['user_role'] = user.role
        return token

# urls.py
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import TenantTokenObtainPairView

urlpatterns = [
    path('auth/token/', TenantTokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
]
```

## Validating Tenant in Permissions
```python
# apps/core/permissions.py
from django.db import connection
from rest_framework.permissions import BasePermission

class IsTenantMember(BasePermission):
    """JWT tenant_schema must match active schema from middleware."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        jwt_schema = request.auth.get('tenant_schema', '')
        return jwt_schema == connection.schema_name
```

## Frontend Token Handling
```typescript
// Decode JWT to get tenant info (never trust for security — only for UX)
import { jwtDecode } from 'jwt-decode';

interface ImoOSToken {
  tenant_schema: string;
  tenant_name: string;
  user_email: string;
  user_role: 'admin' | 'gestor' | 'vendedor' | 'engenheiro' | 'investidor';
  exp: number;
}

const claims = jwtDecode<ImoOSToken>(accessToken);
```

## Key Rules
- `tenant_schema` claim is injected at login — always from `connection.schema_name`
- All business API requests must be validated against active schema
- Access token lifetime: 15 min; Refresh token: 7 days (rotate on use)
- On logout: add refresh token to Redis blacklist for immediate invalidation
