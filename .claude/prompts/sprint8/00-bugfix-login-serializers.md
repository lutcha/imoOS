# Sprint 8 — Prompt 00: Bugfix Login + Serializers

## Contexto

Este prompt resolve os bugs críticos identificados durante a sessão de dev:

### Bug 1 — Login 404 no Docker (Turbopack + TENANT_DOMAIN)
**Root cause**: Next.js 16 com Turbopack em Docker retorna 404 para route handlers
(`/api/auth/login`, `/api/auth/refresh`) quando:
1. O `.next` cache estava corrompido (Turbopack internal error)
2. O `TENANT_DOMAIN` env var não estava definido → Host header enviado ao Django era
   `localhost` em vez de `demo.localhost` → Django não encontrava o tenant

**Status actual**: `middleware.ts` foi renomeado para `proxy.ts` (Next.js 16 convention).
O frontend local corre na porta 3002 com `API_URL=http://localhost:8001` e
`TENANT_DOMAIN=demo.localhost`. Login funciona localmente.

### Bug 2 — `ProjectSerializer` campo `total_area` inexistente
**Root cause**: `apps/projects/serializers.py` lista `total_area` mas o modelo
`Project` não tem esse campo → HTTP 500 em `/api/v1/projects/projects/`.

### Bug 3 — Dashboard stats endpoint não encontrado
**Root cause**: `/api/v1/dashboard/stats/` pode não estar registado em `config/urls.py`.

## Pré-requisitos — Ler antes de começar

```
frontend/src/proxy.ts                       → auth gate (renomeado de middleware.ts)
frontend/src/app/api/auth/login/route.ts    → login proxy (fix TENANT_DOMAIN já aplicado)
frontend/src/app/api/auth/refresh/route.ts  → refresh proxy (fix TENANT_DOMAIN já aplicado)
frontend/.env.local                         → API_URL + TENANT_DOMAIN (local dev)
docker-compose.dev.yml                      → TENANT_DOMAIN=demo.localhost (Docker)
apps/projects/serializers.py                → remover total_area
config/urls.py                              → verificar dashboard URL
```

## Skills a carregar

```
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/02-backend-django/drf-serializers/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `nextjs-tenant-routing` | Fix permanente do Docker login (Dockerfile + env vars) |
| `drf-viewset-builder` | Fix ProjectSerializer + verificar dashboard endpoint |

---

## Tarefa 1 — Fix permanente do Docker login

### 1a. Dockerfile.dev do frontend — passar TENANT_DOMAIN como ARG

**Ler `frontend/Dockerfile.dev` antes de editar.**

O problema é que `TENANT_DOMAIN` precisa de ser passado como env var em runtime,
não como build arg. O `docker-compose.dev.yml` já tem:
```yaml
environment:
  - TENANT_DOMAIN=demo.localhost
```
Verificar que este env var está a ser lido pela route handler.

### 1b. Fix do proxy.ts para Next.js 16

**Ler `frontend/src/proxy.ts` antes de editar.**

Verificar que:
1. O export é `export function proxy(request: NextRequest)` (não `middleware`)
2. O matcher exclui correctamente `/api/auth/*`
3. A config está correcta

### 1c. Fix do Turbopack em Docker

O problema do Turbopack corrupted cache em Docker pode ser evitado com:
```yaml
# docker-compose.dev.yml — frontend service
environment:
  - NEXT_TELEMETRY_DISABLED=1
  - TURBOPACK_CACHE_DISABLED=1  # evitar cache corruption
volumes:
  - ./frontend:/app
  - /app/node_modules
  # NÃO montar /app/.next — deixar Turbopack gerir o cache em memória
  # (remover a linha "- /app/.next" do volumes)
```

Remover o volume anónimo `/app/.next` do `docker-compose.dev.yml` para que o
Turbopack use o `.next` montado do host (sempre sincronizado).

### 1d. Variável TENANT_DOMAIN em produção

Em produção, cada tenant tem o seu próprio subdomínio (ex: `empresa-a.imos.cv`).
O login route deve extrair o subdomínio do `Host` header automaticamente.
Para staging: `TENANT_DOMAIN=demo.imos.cv`.

---

## Tarefa 2 — Fix ProjectSerializer

**Ler `apps/projects/serializers.py` antes de editar.**

```python
# Remover 'total_area' da lista de fields — campo não existe no modelo
class ProjectSerializer(GeoFeatureModelSerializer):
    buildings = BuildingSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        geo_field = 'location'
        fields = (
            'id', 'name', 'description', 'status', 'start_date', 'end_date',
            'address', 'city',
            # 'total_area',  ← REMOVER — não existe no modelo
            'total_units',
            'buildings',
            'created_at', 'updated_at',
        )
```

Verificar o modelo `Project` e adicionar o campo se realmente é necessário:
```bash
grep -n "area\|units\|field" apps/projects/models.py
```

---

## Tarefa 3 — Verificar dashboard endpoint

```bash
grep -r "dashboard\|stats" config/urls.py apps/core/dashboard_urls.py 2>/dev/null
curl -s http://localhost:8001/api/v1/dashboard/stats/ -H "Authorization: Bearer $TOKEN"
```

Se o URL não estiver registado, adicionar a `config/urls.py`:
```python
from apps.core.dashboard_urls import urlpatterns as dashboard_urls
# ou
path('api/v1/dashboard/', include('apps.core.dashboard_urls')),
```

---

## Tarefa 4 — Teste de regressão completo

```bash
# 1. Login funciona via Docker
curl -s http://demo.localhost:3001/api/auth/login \
  -X POST -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.cv","password":"ImoOS2026!"}' | jq .tenant_schema

# 2. Projects carregam sem 500
TOKEN=<access_token>
curl -s http://localhost:8001/api/v1/projects/projects/ \
  -H "Authorization: Bearer $TOKEN" | jq '.count'

# 3. Dashboard stats carregam
curl -s http://localhost:8001/api/v1/dashboard/stats/ \
  -H "Authorization: Bearer $TOKEN" | jq '.inventory'

# 4. Todos os outros módulos
for ep in inventory/units crm/leads construction/daily-reports contracts/contracts; do
  echo "$ep: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/api/v1/$ep/ -H "Authorization: Bearer $TOKEN")"
done
```

## Verificação final

- [ ] `POST http://demo.localhost:3001/api/auth/login` → 200 + access_token (via Docker)
- [ ] `GET http://localhost:3001/login` → 200
- [ ] `GET /api/v1/projects/projects/` → 200 (sem 500 de total_area)
- [ ] `GET /api/v1/dashboard/stats/` → 200
- [ ] Página Dashboard no browser mostra KPIs (não "Erro ao carregar estatísticas")
- [ ] Página Projectos mostra "Residencial Praia Norte" (não "Erro ao carregar")
- [ ] `proxy.ts` renomeado correctamente e auth gate funcional
