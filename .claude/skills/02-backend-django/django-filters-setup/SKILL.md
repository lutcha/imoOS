---
name: django-filters-setup
description: Configure django-filter FilterSets for ImoOS APIs — price ranges, status enums, date ranges. Auto-load when adding filtering to any ViewSet.
argument-hint: [ModelName] [filter-fields]
allowed-tools: Read, Write, Grep
---

# Django Filter Setup — ImoOS

## Standard FilterSet Pattern
```python
# apps/inventory/filters.py
import django_filters
from apps.inventory.models import Unit

class UnitFilter(django_filters.FilterSet):
    # Enum filter
    status = django_filters.MultipleChoiceFilter(choices=Unit.STATUS_CHOICES)

    # Price range
    min_price = django_filters.NumberFilter(field_name='pricing__price_cve', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='pricing__price_cve', lookup_expr='lte')

    # Area range
    min_area = django_filters.NumberFilter(field_name='area_bruta', lookup_expr='gte')
    max_area = django_filters.NumberFilter(field_name='area_bruta', lookup_expr='lte')

    # Related model filter
    project = django_filters.UUIDFilter(field_name='floor__building__project__id')
    building = django_filters.UUIDFilter(field_name='floor__building__id')
    unit_type = django_filters.CharFilter(field_name='unit_type__code', lookup_expr='iexact')

    # Date range
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = Unit
        fields = ['status', 'unit_type', 'project', 'building']
```

## ViewSet Registration
```python
class UnitViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UnitFilter
    search_fields = ['code', 'floor__building__project__name']
    ordering_fields = ['created_at', 'code', 'pricing__price_cve', 'area_bruta']
    ordering = ['code']
```

## Usage (API calls)
```
GET /api/v1/units/?status=AVAILABLE&min_price=5000000&project=<uuid>
GET /api/v1/units/?unit_type=T2&min_area=60&max_area=100
GET /api/v1/units/?search=BLK-A&ordering=-pricing__price_cve
```

## Key Rules
- Always document filter params in API schema (`drf-spectacular` picks these up automatically)
- Use `MultipleChoiceFilter` for status — clients often filter by multiple statuses
- Price filters use `pricing__price_cve` — never EUR (CVE is the canonical price)
- Index filtered fields in the database: `status`, `project`, `created_at`
