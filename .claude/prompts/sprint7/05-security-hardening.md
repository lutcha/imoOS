# Sprint 7 — Security Hardening

## Contexto

Antes de Go-Live, realizar um **audit de segurança interno**:
1. Rate limiting auditado e testado em todos os endpoints
2. CORS configurado para produção (sem wildcard)
3. Headers de segurança HTTP (HSTS, CSP, X-Frame-Options)
4. Audit de isolamento de tenant (verificar que não há leaks)
5. JWT security (rotação de refresh tokens, blacklist)
6. Secrets management (verificar que zero secrets no código)
7. Dependency scanning (bandit + safety)

**Este prompt deve ser o último do Sprint 7** — audita o sistema completo.

## Pré-requisitos — Ler antes de começar

```
apps/core/throttling.py         → PublicEndpointThrottle (existente)
config/settings/base.py         → CORS, ALLOWED_HOSTS, SESSION_*, CSRF_*
config/settings/production.py   → settings de produção
apps/users/views.py             → TenantTokenObtainPairView
tests/tenant_isolation/         → suite de testes de isolamento
```

```bash
cat apps/core/throttling.py
grep "CORS\|ALLOWED\|CSRF\|SESSION\|SECURE" config/settings/base.py
ls tests/tenant_isolation/
```

## Skills a carregar

```
@.claude/skills/16-security-compliance/webhook-verification/SKILL.md
@.claude/skills/16-security-compliance/jwt-security/SKILL.md
@.claude/skills/16-security-compliance/audit-logging/SKILL.md
@.claude/skills/14-testing/tenant-isolation-tests/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `schema-isolation-auditor` | Audit completo de isolamento cross-tenant |
| `isolation-test-writer` | Tests para marketplace, investors, billing isolation |

---

## Tarefa 1 — Rate limiting por endpoint

**Ler `apps/core/throttling.py` antes de editar.**

```python
# apps/core/throttling.py — expandir throttles existentes:

class AuthEndpointThrottle(AnonRateThrottle):
    """Login/register — mais restritivo para prevenir brute force."""
    rate = '10/hour'

class PublicEndpointThrottle(AnonRateThrottle):
    """Endpoints públicos (lead capture, webhooks)."""
    rate = '100/hour'

class SignatureThrottle(AnonRateThrottle):
    """Endpoint de assinatura electrónica."""
    rate = '20/hour'  # por IP, por token já tem validação única

class ReportGenerationThrottle(UserRateThrottle):
    """Geração de relatórios — heavy operation."""
    rate = '10/hour'

class MarketplaceSyncThrottle(UserRateThrottle):
    """Sync manual para imo.cv."""
    rate = '30/hour'
```

**Aplicar throttles nos ViewSets:**
```python
# apps/users/views.py — TenantTokenObtainPairView:
throttle_classes = [AuthEndpointThrottle]

# apps/crm/views_public.py — LeadCaptureView:
throttle_classes = [PublicEndpointThrottle]

# apps/contracts/views_public.py — SignatureView:
throttle_classes = [SignatureThrottle]

# apps/core/views.py — ReportJobViewSet:
throttle_classes = [ReportGenerationThrottle]
```

---

## Tarefa 2 — Security headers (produção)

**Criar `config/settings/production.py`** (ou verificar se existe):
```python
from .base import *

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS (sem wildcard em produção)
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'https://app.imos.cv',
    'https://*.imos.cv',  # subdomínios de tenant
])
CORS_ALLOW_CREDENTIALS = True

# CSP via django-csp
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", 'https://cdn.jsdelivr.net')
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")  # necessário para Tailwind inline
CSP_IMG_SRC = ("'self'", 'data:', 'https://media.imos.cv')
CSP_CONNECT_SRC = ("'self'", 'https://api.imos.cv', 'https://*.sentry.io')

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'

# Referrer
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

Instalar: `django-csp==3.8` em `requirements/base.txt`.

---

## Tarefa 3 — JWT blacklist (refresh token rotation)

**Verificar `config/settings/base.py` para SIMPLE_JWT config.**

```python
# config/settings/base.py — adicionar a SIMPLE_JWT:
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,      # cada refresh gera novo token
    'BLACKLIST_AFTER_ROTATION': True,   # token antigo é invalidado
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Em INSTALLED_APPS (SHARED_APPS):
'rest_framework_simplejwt.token_blacklist',
```

```bash
# Após adicionar:
python manage.py migrate_schemas --shared
```

**No endpoint de logout** (verificar `apps/users/views.py`):
```python
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Sessão terminada.'})
        except TokenError:
            return Response({'detail': 'Token inválido.'}, status=400)
```

---

## Tarefa 4 — Audit de isolamento tenant

Prompt para `schema-isolation-auditor`:
> "Audita o código ImoOS em c:\Dev\imos para detectar possíveis leaks de dados cross-tenant. Verificar especificamente:
> 1. ViewSets que não têm `get_queryset()` definido (usam `queryset =` ao nível da classe)
> 2. Serializers que acedem a FKs cross-schema sem `select_related` explícito
> 3. Celery tasks que não usam `tenant_context()` antes de ORM queries
> 4. Endpoints que usam `Model.objects.all()` sem filtro
> 5. `InvestorPortalViewSet` — verifica que o filtro `lead__email=request.user.email` é correcto
> Reportar cada issue com ficheiro, linha e nível de risco (CRÍTICO/ALTO/MÉDIO)."

---

## Tarefa 5 — Testes de isolamento para módulos Sprint 6

Prompt para `isolation-test-writer`:
> "Cria testes de isolamento em `tests/tenant_isolation/`:
> - `test_marketplace_isolation.py`: Tenant B não vê MarketplaceListing de Tenant A; ImoCvWebhookLog isolado
> - `test_investor_isolation.py`: Investidor de Tenant A não vê contratos de Tenant B via /api/v1/investors/portal/
> - `test_whatsapp_isolation.py`: WhatsAppMessage e WhatsAppTemplate isolados por schema
> - `test_signature_isolation.py`: SignatureRequest token de Tenant A não acessível pelo Tenant B"

---

## Tarefa 6 — Secrets scan

```bash
# Verificar se há secrets hardcoded no código:
make security    # bandit + safety

# Verificar .gitignore protege .env:
cat .gitignore | grep ".env"

# Verificar que nenhum secret está no código:
grep -r "password\|secret\|api_key\|token" apps/ --include="*.py" \
  | grep -v "settings\|env\|test\|migration\|comment" \
  | grep -v "#"
```

**Checklist de secrets**:
- [ ] `WHATSAPP_ACCESS_TOKEN` → env var ✓
- [ ] `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` → env var ✓
- [ ] `SECRET_KEY` (Django) → env var ✓
- [ ] `SENTRY_DSN` → env var ✓
- [ ] `IMO_CV_API_KEY` (por tenant em TenantSettings) ✓

---

## Tarefa 7 — Penetration test básico

Testar manualmente os cenários críticos antes do Go-Live:

```bash
# 1. JWT sem token → 401
curl http://localhost:8000/api/v1/crm/leads/ -H "Host: demo.localhost"

# 2. JWT de Tenant A a aceder a Tenant B → deve retornar 404 (não 403)
# (schema_name no token ≠ schema_name do host)

# 3. SQL injection na pesquisa de leads
curl "http://localhost:8000/api/v1/crm/leads/?search='; DROP TABLE crm_lead; --" \
  -H "Authorization: Bearer $TOKEN" -H "Host: demo.localhost"

# 4. Rate limiting no login (>10 tentativas/hora)
for i in $(seq 1 12); do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/users/auth/token/ \
    -H "Host: demo.localhost" -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"brute@force.com","password":"wrong"}'
done
# Deve retornar 429 a partir da 11ª tentativa

# 5. IDOR no endpoint de assinatura
# Token de Tenant A não deve ser acessível a partir de Tenant B
```

---

## Verificação final

- [ ] `make security` passa (bandit + safety sem erros críticos)
- [ ] `pytest tests/tenant_isolation/ -v` → 100% passing
- [ ] Rate limiting: login retorna 429 após 10 tentativas por hora
- [ ] JWT rotation: refresh token antigo rejeitado após rotação
- [ ] `/sign/{token}` com token de outro tenant → 404
- [ ] Django Admin apenas acessível a is_staff
- [ ] CORS em produção sem wildcard
- [ ] HSTS configurado em `production.py`
- [ ] Nenhum secret hardcoded no código (grep clean)
- [ ] `pytest tests/tenant_isolation/test_marketplace_isolation.py -v` passa
