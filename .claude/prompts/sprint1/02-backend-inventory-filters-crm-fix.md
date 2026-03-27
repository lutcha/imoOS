# Sprint 1 — Backend: Inventory Filters + Fix CRM

## Estado actual

### Bug crítico no CRM (corrigir PRIMEIRO)

`apps/crm/models.py` linha 4:
```python
from apps.units.models import Unit   # ← ERRADO — esta app não existe
```
Deve ser:
```python
from apps.inventory.models import Unit   # ← CORRECTO
```
Esta linha impede que o servidor Django arranque. **Corrigir antes de qualquer outra coisa.**

### O que existe e está correcto
- `apps/inventory/models.py` — Unit, UnitType, UnitPricing (completos)
- `apps/inventory/views.py` — UnitViewSet com `IsTenantMember` ✓
- `apps/inventory/serializers.py` — UnitSerializer com pricing nested ✓
- `apps/crm/models.py` — Lead, Interaction (bons, excepto o import acima)
- `apps/crm/views.py` — LeadViewSet com pipeline action ✓
- `apps/crm/views_public.py` — LeadCaptureView (público, AllowAny) ✓
- `apps/crm/urls.py` — inclui `lead-capture/` + router ✓

### O que falta
- `apps/inventory/filters.py` — filtros avançados para Unit (status, preço, tipologia)
- `apps/crm/filters.py` — filtros para Lead (fonte, status, data, orçamento)
- `apps/crm/views_public.py` — falta rate limiting (100 req/h por IP — obrigatório por CLAUDE.md)

## Skills a carregar

```
@.claude/skills/02-backend-django/django-filters-setup/SKILL.md
@.claude/skills/07-module-inventory/unit-status-workflow/SKILL.md
@.claude/skills/07-module-inventory/unit-pricing-currency/SKILL.md
@.claude/skills/08-module-crm/lead-source-tracking/SKILL.md
@.claude/skills/02-backend-django/throttle-per-tenant/SKILL.md
@.claude/skills/00-global/coding-standards/SKILL.md
```

## Agent a activar para validação

Após criar os filtros, pedir ao agent para verificar isolamento:
- Agent: `.claude/agents/00-architecture/tenant-expert.md`
  - Prompt: "Audita `apps/crm/views_public.py` — verifica se LeadCaptureView cria leads no schema correcto do tenant activo sem quebrar isolamento"

## Tarefas

### 1. Fix urgente — `apps/crm/models.py`

```python
# Linha 4: mudar
from apps.units.models import Unit
# para:
from apps.inventory.models import Unit
```

### 2. Criar `apps/inventory/filters.py`

```python
import django_filters
from .models import Unit

class UnitFilter(django_filters.FilterSet):
    # Filtro de range de preço em CVE
    price_min = django_filters.NumberFilter(
        field_name='pricing__price_cve', lookup_expr='gte'
    )
    price_max = django_filters.NumberFilter(
        field_name='pricing__price_cve', lookup_expr='lte'
    )
    # Filtro de range de área
    area_min = django_filters.NumberFilter(field_name='area_bruta', lookup_expr='gte')
    area_max = django_filters.NumberFilter(field_name='area_bruta', lookup_expr='lte')
    # Filtros exactos
    project = django_filters.UUIDFilter(field_name='floor__building__project__id')
    building = django_filters.UUIDFilter(field_name='floor__building__id')

    class Meta:
        model = Unit
        fields = ['status', 'unit_type', 'floor', 'project', 'building',
                  'price_min', 'price_max', 'area_min', 'area_max']
```

Depois, actualizar `apps/inventory/views.py` para usar `UnitFilter`:
```python
from .filters import UnitFilter
# No UnitViewSet:
filterset_class = UnitFilter  # substituir filterset_fields
```

### 3. Criar `apps/crm/filters.py`

```python
import django_filters
from .models import Lead

class LeadFilter(django_filters.FilterSet):
    budget_min = django_filters.NumberFilter(field_name='budget', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='budget', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Lead
        fields = ['status', 'source', 'assigned_to', 'interested_unit',
                  'budget_min', 'budget_max', 'created_after', 'created_before']
```

Actualizar `apps/crm/views.py` para usar `LeadFilter`.

### 4. Rate limiting em `views_public.py`

`LeadCaptureView` é público (`AllowAny`). CLAUDE.md exige 100 req/h por IP.
Adicionar throttle class de `apps/core/throttling.py`:

```python
from apps.core.throttling import PublicEndpointThrottle

class LeadCaptureView(generics.CreateAPIView):
    throttle_classes = [PublicEndpointThrottle]
    # ...
```

### 5. Verificar migration de CRM

Após o fix do import, confirmar que as migrations existem ou criar:
```bash
python manage.py makemigrations crm
python manage.py migrate_schemas
```

## Verificação final

- [ ] `python manage.py check` sem erros
- [ ] `pytest tests/ -k crm` passa
- [ ] Endpoint `GET /api/v1/inventory/units/?price_min=5000000&price_max=10000000` retorna resultados filtrados
- [ ] Endpoint `GET /api/v1/crm/leads/?status=NEW&source=INSTAGRAM` funciona
- [ ] `POST /api/v1/crm/lead-capture/` com 101 requests em rápida sucessão retorna 429 na 101ª
