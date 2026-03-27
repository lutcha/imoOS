# Sprint 7 — Admin Backoffice (Super-Admin)

## Contexto

O super-admin do ImoOS (a equipa ImoOS, não as promotoras) precisa de:
1. Ver todos os tenants, estados, consumo de plano
2. Criar/suspender tenants
3. Ver logs de erros e eventos de plano
4. Monitorizar tasks Celery falhadas
5. Aceder a Django Admin para debug

A interface pode ser **Django Admin customizado** (rápido de implementar) com uma
página React dedicada em `/admin/` (diferente do `/admin/` Django — prefixo `/superadmin/`).

## Pré-requisitos — Ler antes de começar

```
apps/tenants/models.py          → Client, TenantSettings, PlanEvent
apps/users/models.py            → User (is_staff para super-admin)
config/settings/base.py         → INSTALLED_APPS, MIDDLEWARE
apps/core/health.py             → HealthCheckView (sprint 7 prompt 00)
```

```bash
grep "admin\|is_staff\|superuser" apps/users/models.py
cat config/settings/base.py | grep "INSTALLED_APPS" -A 30
```

## Skills a carregar

```
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `drf-viewset-builder` | SuperAdminViewSet — lê schema público (todos os tenants) |
| `react-component-builder` | Página /superadmin/ com tabela de tenants e métricas |

---

## Tarefa 1 — Django Admin customizado

Criar `apps/tenants/admin.py` (ou actualizar existente):
```python
from django.contrib import admin
from django.utils.html import format_html
from .models import Client, TenantSettings, PlanEvent


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'schema_name', 'plan', 'is_active', 'created_at', 'tenant_health']
    list_filter = ['plan', 'is_active', 'country']
    search_fields = ['name', 'schema_name', 'slug']
    readonly_fields = ['schema_name', 'slug', 'created_at', 'updated_at']
    actions = ['suspend_tenants', 'activate_tenants']

    def tenant_health(self, obj):
        settings = TenantSettings.objects.filter(tenant=obj).first()
        if not settings:
            return format_html('<span style="color:red">⚠ Sem settings</span>')
        return format_html('<span style="color:green">✓</span>')
    tenant_health.short_description = 'Health'

    @admin.action(description='Suspender tenants seleccionados')
    def suspend_tenants(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} tenant(s) suspenso(s).')

    @admin.action(description='Activar tenants seleccionados')
    def activate_tenants(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} tenant(s) activado(s).')


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'max_projects', 'max_units', 'max_users', 'imocv_enabled']
    list_filter = ['imocv_enabled']
    search_fields = ['tenant__name']


@admin.register(PlanEvent)
class PlanEventAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'event_type', 'from_plan', 'to_plan', 'created_at']
    list_filter = ['event_type']
    readonly_fields = ['tenant', 'event_type', 'from_plan', 'to_plan', 'metadata', 'created_at']
    # Imutável — sem edição
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
```

Em `config/settings/base.py`:
```python
DJANGO_SUPERADMIN_URL = env('DJANGO_SUPERADMIN_URL', default='django-admin/')
```

Em `config/urls.py` (substituir `admin/`):
```python
from django.conf import settings
path(settings.DJANGO_SUPERADMIN_URL, admin.site.urls),
```

---

## Tarefa 2 — SuperAdmin API (schema público)

Prompt para `drf-viewset-builder`:
> "Cria `SuperAdminTenantViewSet` em `apps/tenants/views.py`. Permission: `IsAdminUser` (is_staff=True). Sem tenant middleware — usa sempre o schema público. Actions: `list` (todos os tenants com count de users por schema — usar `schema_context`), `suspend`, `activate`, `usage_summary` (agregado de todos os tenants). Endpoint: `GET /api/v1/superadmin/tenants/`."

```python
class SuperAdminTenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de super-admin — schema público, todos os tenants.
    ATENÇÃO: nunca filtrar por tenant_context aqui.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Client.objects.select_related().prefetch_related('domains', 'settings')
    serializer_class = TenantAdminSerializer

    @action(detail=False, methods=['get'])
    def platform_summary(self, request):
        """Métricas agregadas da plataforma (sem dados cross-tenant)."""
        return Response({
            'total_tenants': Client.objects.filter(is_active=True).count(),
            'total_tenants_by_plan': dict(
                Client.objects.filter(is_active=True)
                .values_list('plan')
                .annotate(count=Count('id'))
                .values_list('plan', 'count')
            ),
        })
```

---

## Tarefa 3 — Frontend /superadmin/

Criar `frontend/src/app/superadmin/layout.tsx`:
```typescript
// Layout diferente: apenas acessível a is_staff=True
// Verificar no AuthContext: se !user.is_staff → redirect para /
// Sidebar ultra-simples: Tenants | Eventos | Health | Django Admin
```

Criar `frontend/src/app/superadmin/page.tsx`:
```typescript
// Dashboard super-admin:
// Linha 1 — KPIs: Total Tenants | Tenants Activos | Plano Starter/Pro/Enterprise
// Linha 2 — Tabela de tenants:
//   Empresa | Schema | Plano | Activo | Data criação | Acções (suspender/activar)
// Linha 3 — Eventos recentes (PlanEvent):
//   Tenant | Tipo | Plano anterior | Plano novo | Data
// Linha 4 — Health status (de /health/detailed/)
```

---

## Tarefa 4 — Superuser de plataforma

Management command para criar o utilizador super-admin da plataforma:
```bash
python manage.py createsuperuser --email=superadmin@imos.cv
# is_staff=True permite acesso ao Django Admin
# is_superuser=True não necessário — apenas is_staff
```

Ou via shell:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.create_user(email='superadmin@imos.cv', password='...')
u.is_staff = True
u.save()
# Nota: este utilizador existe no schema PUBLIC (não num tenant)
```

---

## Verificação final

- [ ] Django Admin acessível em `DJANGO_SUPERADMIN_URL` (env configurável)
- [ ] Django Admin mostra todos os tenants com filtro por plano
- [ ] `suspend_tenants` admin action → `Client.is_active=False`
- [ ] `GET /api/v1/superadmin/tenants/` com is_staff=True → 200
- [ ] `GET /api/v1/superadmin/tenants/` com utilizador normal → 403
- [ ] `/superadmin/` no frontend acessível apenas a is_staff
- [ ] Utilizador normal na `/superadmin/` → redirect para /
- [ ] `platform_summary` mostra counts correctos por plano
