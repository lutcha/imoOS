---
name: rate-limit-ddos-protection
description: Decorator django-ratelimit para limites ao nível da view, configuração de rate limiting upstream no Nginx, regras WAF Cloudflare e throttling por inquilino (ver skill throttle-per-tenant).
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Proteger a API ImoOS contra abuso, DDoS e scraping com camadas múltiplas de rate limiting: Cloudflare na borda, Nginx no upstream e django-ratelimit ao nível da view para granularidade por endpoint.

## Code Pattern

```python
# auth/views.py — proteção de endpoints sensíveis
from django_ratelimit.decorators import ratelimit
from rest_framework.views import APIView

class TokenObtainView(APIView):
    """Login — limite estrito para prevenir brute force."""
    authentication_classes = []

    @ratelimit(key="ip", rate="5/m", method="POST", block=True)
    def post(self, request):
        ...


class LeadCreateView(APIView):
    """Criação de leads — limite por IP para prevenir spam."""

    @ratelimit(key="ip", rate="20/h", method="POST", block=True)
    def post(self, request):
        ...
```

```python
# middleware/tenant_throttle.py — throttling por inquilino via DRF
from rest_framework.throttling import SimpleRateThrottle

class TenantRateThrottle(SimpleRateThrottle):
    """Limita pedidos por inquilino (schema) — independente do utilizador."""
    scope = "tenant"

    def get_cache_key(self, request, view):
        from django.db import connection
        tenant = connection.schema_name
        return self.cache_format % {
            "scope": self.scope,
            "ident": tenant,
        }
```

```python
# settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "middleware.tenant_throttle.TenantRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "tenant": "5000/hour",
    },
}
```

```nginx
# nginx/nginx.conf — rate limiting upstream
http {
    # Zona de limite por IP (10MB = ~160k IPs)
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s;

    # Zona específica para autenticação
    limit_req_zone $binary_remote_addr zone=auth_limit:5m rate=5r/m;

    server {
        location /api/ {
            limit_req zone=api_limit burst=50 nodelay;
            limit_req_status 429;
            proxy_pass http://django;
        }

        location /api/v1/auth/ {
            limit_req zone=auth_limit burst=5 nodelay;
            limit_req_status 429;
            proxy_pass http://django;
        }
    }
}
```

```yaml
# Cloudflare WAF Rules (via API ou dashboard)
# Regra 1: Bloquear IPs com > 1000 pedidos/minuto
expression: cf.threat_score > 50
action: challenge

# Regra 2: Rate limit para endpoint de login
expression: http.request.uri.path matches "^/api/v1/auth/token/"
action: rate_limit
characteristics: ip
threshold: 10
period: 60
```

## Key Rules

- Aplicar rate limiting em múltiplas camadas: Cloudflare → Nginx → Django — cada camada complementa as outras.
- O endpoint de autenticação (`/api/v1/auth/token/`) deve ter limites muito mais restritivos (5/minuto por IP).
- Retornar `HTTP 429 Too Many Requests` com header `Retry-After` para facilitar clientes bem-comportados.
- Os limites por inquilino devem ser configuráveis em `TenantSettings` para planos diferentes.

## Anti-Pattern

```python
# ERRADO: rate limiting apenas em Django sem Nginx — Nginx nunca recebe pedidos se o Django está sobrecarregado
@ratelimit(key="ip", rate="100/m")  # funciona mas não protege o servidor de ficar sem recursos primeiro
```
