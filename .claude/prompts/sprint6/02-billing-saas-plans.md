# Sprint 6 — Billing / Planos SaaS

## Contexto

`Client` já tem `plan` (STARTER/PRO/ENTERPRISE) e `TenantSettings` tem limites
(`max_projects`, `max_units`, `max_users`). Este módulo adiciona:
1. **Enforcement** dos limites por plano antes de criar recursos
2. **Billing events** (log auditável de mudanças de plano)
3. **Admin UI** para gerir planos e ver consumo por tenant
4. **Upgrade flow** no frontend (self-service ou contacto comercial)

Não integra gateway de pagamento neste sprint — o foco é a infra de limites e
o painel de administração do SaaS.

## Pré-requisitos — Ler antes de começar

```
apps/tenants/models.py          → Client.plan, TenantSettings (limites)
apps/projects/models.py         → Project (count para limite)
apps/inventory/models.py        → Unit (count para limite)
apps/memberships/models.py      → TenantMembership (count para limite users)
config/settings/base.py         → SHARED_APPS (billing vive no schema público)
```

```bash
grep "max_projects\|max_units\|max_users\|PLAN_" apps/tenants/models.py
grep "SHARED_APPS\|TENANT_APPS" config/settings/base.py
```

## Skills a carregar

```
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `model-architect` | PlanLimitEvent (log de mudanças de plano) |
| `drf-viewset-builder` | UsageViewSet + PlanAdminViewSet |
| `celery-task-specialist` | Task: enviar alertas de limite próximo |
| `react-component-builder` | Página /settings/billing + upgrade banner |

---

## Tarefa 1 — Enforcement de limites (service layer)

Criar `apps/tenants/limits.py`:

```python
"""
Enforcement de limites de plano. Chamar antes de criar recursos.
Vive no schema público — acede a TenantSettings (público) e
faz queries cross-schema com tenant_context() quando necessário.
"""
from dataclasses import dataclass
from django.db import connection

from apps.tenants.models import TenantSettings


@dataclass
class LimitCheck:
    allowed: bool
    current: int
    limit: int
    resource: str

    @property
    def message(self) -> str:
        if self.allowed:
            return ''
        return (
            f'Limite de {self.resource} atingido: {self.current}/{self.limit}. '
            f'Actualize o seu plano para continuar.'
        )


def check_project_limit(tenant_settings: TenantSettings) -> LimitCheck:
    """Verifica se o tenant pode criar mais projectos."""
    from apps.projects.models import Project
    count = Project.objects.filter(is_active=True).count()
    return LimitCheck(
        allowed=count < tenant_settings.max_projects,
        current=count,
        limit=tenant_settings.max_projects,
        resource='projectos',
    )


def check_unit_limit(tenant_settings: TenantSettings) -> LimitCheck:
    from apps.inventory.models import Unit
    count = Unit.objects.count()
    return LimitCheck(
        allowed=count < tenant_settings.max_units,
        current=count,
        limit=tenant_settings.max_units,
        resource='unidades',
    )


def check_user_limit(tenant_settings: TenantSettings) -> LimitCheck:
    from apps.memberships.models import TenantMembership
    count = TenantMembership.objects.filter(is_active=True).count()
    return LimitCheck(
        allowed=count < tenant_settings.max_users,
        current=count,
        limit=tenant_settings.max_users,
        resource='utilizadores',
    )
```

**Integrar nos ViewSets existentes** — chamar `check_*_limit()` no `perform_create()`:
```python
# apps/projects/views.py — ProjectViewSet.perform_create()
def perform_create(self, serializer):
    settings = TenantSettings.objects.get(tenant__schema_name=connection.schema_name)
    check = check_project_limit(settings)
    if not check.allowed:
        raise ValidationError({'non_field_errors': [check.message]})
    serializer.save()
```

---

## Tarefa 2 — Modelo de log de eventos de plano

Prompt para `model-architect`:
> "Cria `PlanEvent` em `apps/tenants/models.py` (ou `apps/billing/models.py` em SHARED_APPS). Campos: `tenant` (FK Client), `event_type` (PLAN_UPGRADED/PLAN_DOWNGRADED/LIMIT_HIT/TRIAL_STARTED/TRIAL_ENDED), `from_plan` (CharField nullable), `to_plan` (CharField nullable), `metadata` (JSONField, ex: {resource: 'projects', current: 5, limit: 5}), `created_at`, `created_by` (User nullable). Sem HistoricalRecords (já é um log)."

```python
class PlanEvent(models.Model):
    EVENT_PLAN_UPGRADED   = 'PLAN_UPGRADED'
    EVENT_PLAN_DOWNGRADED = 'PLAN_DOWNGRADED'
    EVENT_LIMIT_HIT       = 'LIMIT_HIT'
    EVENT_TRIAL_STARTED   = 'TRIAL_STARTED'
    EVENT_TRIAL_ENDED     = 'TRIAL_ENDED'

    tenant = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='plan_events')
    event_type = models.CharField(max_length=25, choices=EVENT_CHOICES)
    from_plan = models.CharField(max_length=20, blank=True)
    to_plan = models.CharField(max_length=20, blank=True)
    metadata = models.JSONField(default=dict)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

---

## Tarefa 3 — UsageViewSet (consumo actual)

Prompt para `drf-viewset-builder`:
> "Cria `UsageView` (APIView, não ViewSet) em `apps/tenants/views.py`. Permission: IsTenantMember. `GET /api/v1/tenants/usage/`: retorna JSON com `projects`, `units`, `users` — cada um com `{current, limit, pct_used}`. Lê `TenantSettings` do tenant actual. Não passa dados de outros tenants."

```json
// Resposta esperada:
{
  "plan": "starter",
  "projects": {"current": 3, "limit": 5, "pct_used": 60},
  "units":    {"current": 120, "limit": 500, "pct_used": 24},
  "users":    {"current": 8, "limit": 20, "pct_used": 40}
}
```

---

## Tarefa 4 — Celery task: alerta de limite próximo

Prompt para `celery-task-specialist`:
> "Cria `apps/tenants/tasks.py` (ou adiciona a existente) com `check_plan_limits`. Corre diariamente por tenant. Dentro de `tenant_context`: verifica `pct_used >= 80%` para projectos/unidades/utilizadores. Se atingido, regista `PlanEvent(LIMIT_HIT)` e envia WhatsApp ao admin do tenant (via `whatsapp_phone_id`). Cache key `{schema}:limit_alert:{resource}:{date}` para não repetir no mesmo dia."

---

## Tarefa 5 — Frontend: /settings/billing

Criar `frontend/src/app/settings/billing/page.tsx`:

```typescript
// Secção: Plano Actual
//   - Badge do plano (STARTER/PRO/ENTERPRISE) com cor
//   - Data de renovação (mockado por agora)
//   - Botão "Upgrade" → abre modal ou link para contacto comercial

// Secção: Consumo
//   - 3 progress bars: Projectos | Unidades | Utilizadores
//   - Cor: verde <60%, amarelo 60-80%, vermelho >80%
//   - Usa GET /api/v1/tenants/usage/

// Secção: Histórico de eventos
//   - Tabela simples: Data | Evento | Plano anterior | Plano novo
```

**Upgrade banner** em `frontend/src/components/layout/Sidebar.tsx`:
```typescript
// Se pct_used >= 80% em qualquer recurso:
// Mostrar banner amarelo no fundo da sidebar: "⚠ Limite próximo — Upgrade"
// Link para /settings/billing
```

---

## Tarefa 6 — Limites por plano (configuração)

Definir limites padrão em `config/settings/base.py`:
```python
PLAN_LIMITS = {
    'starter':    {'max_projects': 3,  'max_units': 100,  'max_users': 5},
    'pro':        {'max_projects': 15, 'max_units': 1000, 'max_users': 50},
    'enterprise': {'max_projects': 999, 'max_units': 9999, 'max_users': 999},
}
```

Management command `set_plan_limits` para actualizar `TenantSettings` existentes:
```bash
python manage.py set_plan_limits --plan=starter  # actualiza todos os tenants starter
```

---

## Verificação final

- [ ] `POST /api/v1/projects/projects/` quando `current >= limit` → 400 com mensagem clara
- [ ] `GET /api/v1/tenants/usage/` → JSON correcto por tenant
- [ ] Tenant A não vê consumo de Tenant B
- [ ] `PlanEvent` criado ao atingir 80% de limite
- [ ] `/settings/billing` mostra progress bars correctas
- [ ] Banner de upgrade aparece quando pct_used >= 80%
