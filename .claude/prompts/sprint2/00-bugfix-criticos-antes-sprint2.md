# Sprint 2 — Dia 0: Corrigir Bugs Críticos (antes de qualquer feature nova)

> **Regra defensiva:** Ler cada ficheiro antes de editar. Não alterar nada fora do escopo dos bugs listados.

## Diagnóstico — 4 bugs que impedem o sistema de funcionar

---

### BUG 1 — JWT claims: nomes errados (backend ↔ frontend dessincronizados)

**Ficheiro:** `apps/users/serializers.py`

**Problema:** O `TenantTokenObtainPairSerializer` injeta os claims com nomes errados.
O `AuthContext.tsx` (frontend) espera estes nomes exactos:

| Frontend espera | Backend injeta actualmente | Correcto? |
|----------------|---------------------------|-----------|
| `email` | `user_email` | ❌ |
| `role` | `user_role` | ❌ |
| `full_name` | *(não injetado)* | ❌ |
| `user_id` | *(simplejwt injeta automaticamente)* | ✅ |
| `tenant_schema` | `tenant_schema` | ✅ |
| `tenant_name` | `tenant_name` | ✅ |

**Fix:**
```python
# apps/users/serializers.py — método get_token
token['tenant_schema'] = connection.schema_name
token['tenant_name'] = getattr(connection.tenant, 'name', 'Public')
token['email'] = user.email                          # era user_email
token['role'] = user.role                            # era user_role
token['full_name'] = user.get_full_name() or user.email  # novo — necessário pelo AuthContext
```

---

### BUG 2 — Frontend API routes: URLs erradas para o Django

**Ficheiros:** `frontend/src/app/api/auth/login/route.ts`, `refresh/route.ts`, `logout/route.ts`

**Problema:** As rotas chamam caminhos que não existem em `config/urls.py`.

`config/urls.py` define:
```python
path('api/v1/users/', include('apps.users.urls'))
# → apps/users/urls.py:  path('auth/token/', ...)
# URL final: /api/v1/users/auth/token/
```

| Ficheiro | URL actual (errada) | URL correcta |
|---------|---------------------|--------------|
| `login/route.ts:14` | `/api/v1/auth/token/` | `/api/v1/users/auth/token/` |
| `refresh/route.ts:20` | `/api/v1/auth/token/refresh/` | `/api/v1/users/auth/token/refresh/` |
| `logout/route.ts:17` | `/api/v1/auth/token/blacklist/` | `/api/v1/users/auth/token/blacklist/` |

**Fix:** Actualizar os 3 ficheiros com as URLs correctas.

---

### BUG 3 — Token refresh não devolve `tenant_schema`

**Ficheiro:** `frontend/src/app/api/auth/refresh/route.ts`

**Problema:** A route espera `tenant_schema` no body da resposta do refresh endpoint:
```typescript
const { access, tenant_schema } = await djangoResp.json();  // linha 36
```
Mas o endpoint simplejwt `/token/refresh/` só devolve `{ access }` — não devolve `tenant_schema`.

O `tenant_schema` está **dentro** do novo access token (claim JWT). A solução é decodificar o token no servidor para extrair o claim.

**Fix em `refresh/route.ts`:**
```typescript
import { jwtDecode } from "jwt-decode";  // ou Buffer/atob no servidor

const { access } = await djangoResp.json();

// Extrair tenant_schema do payload do token sem verificação de assinatura
// (o Django já verificou — aqui só precisamos ler o claim)
const payload = JSON.parse(
  Buffer.from(access.split('.')[1], 'base64').toString()
);
const tenant_schema = payload.tenant_schema ?? null;

return NextResponse.json({ access_token: access, tenant_schema });
```

---

### BUG 4 — `apps/tenants/middleware.py`: `Http404` não importado

**Ficheiro:** `apps/tenants/middleware.py`

**Problema:** Linha 24 usa `Http404` mas não está importado:
```python
raise Http404("Tenant não encontrado")  # ← NameError em runtime
```

**Fix:** Adicionar o import em falta:
```python
from django.http import Http404, JsonResponse  # adicionar Http404
```

---

### BUG 5 (menor) — `views_public.py` usa `LeadSerializer` em vez de `PublicLeadSerializer`

**Ficheiro:** `apps/crm/views_public.py`

**Problema:** O `PublicLeadSerializer` foi criado especificamente para este endpoint (campos mínimos, sem FKs internas) mas o view ainda usa o `LeadSerializer` completo.

**Fix:**
```python
from .serializers import PublicLeadSerializer  # era LeadSerializer

class LeadCaptureView(generics.CreateAPIView):
    serializer_class = PublicLeadSerializer    # era LeadSerializer
```

---

## Skills a carregar

```
@.claude/skills/01-multi-tenant/jwt-tenant-claims/SKILL.md
@.claude/skills/00-global/coding-standards/SKILL.md
```

## Agent de validação pós-fix

Após corrigir, invocar:
- Agent: `.claude/agents/00-architecture/tenant-expert.md`
  - Prompt: "Verifica se os JWT claims em `apps/users/serializers.py` estão correctos e alinhados com o que o `AuthContext.tsx` espera. Confirma também que `IsTenantMember` continua a funcionar."

## Verificação final

- [ ] `python manage.py check` sem erros (BUG 4 corrigido)
- [ ] Login via frontend retorna token com `email`, `role`, `full_name` correctos
- [ ] Refresh de sessão funciona sem erros 500
- [ ] `POST /api/v1/crm/lead-capture/` com payload mínimo retorna 201
- [ ] `npm run build` sem erros TypeScript
