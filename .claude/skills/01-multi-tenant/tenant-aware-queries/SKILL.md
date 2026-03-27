---
name: tenant-aware-queries
description: Safe QuerySet patterns for multi-tenant ImoOS — select_related, prefetch, annotations that stay within tenant schema. Auto-load when writing complex queries or optimizing N+1 issues.
argument-hint: [model] [query-type]
allowed-tools: Read, Write, Grep
---

# Tenant-Aware Query Patterns — ImoOS

## Safe QuerySet Optimization
```python
# All queries auto-scoped by django-tenants middleware in views
# Optimize with select_related and prefetch_related

class UnitViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return (
            Unit.objects
            .select_related('floor__building__project', 'unit_type', 'pricing')
            .prefetch_related('media_files')
            .filter(is_deleted=False)
            .order_by('code')
        )
```

## Aggregation Within Tenant
```python
from django.db.models import Count, Sum, Avg, Q

# Project dashboard KPIs — all scoped to active tenant
def get_project_kpis(project_id):
    units = Unit.objects.filter(floor__building__project_id=project_id)
    return units.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status='AVAILABLE')),
        reserved=Count('id', filter=Q(status='RESERVED')),
        sold=Count('id', filter=Q(status='SOLD')),
        total_revenue=Sum('pricing__price_cve', filter=Q(status='SOLD')),
    )
```

## Cross-Tenant Query (Only for Super Admin)
```python
# NEVER in regular views — only in management commands with explicit context
from django_tenants.utils import schema_context

def aggregate_platform_stats():
    """Platform-level stats — super admin only."""
    results = {}
    for tenant in Client.objects.filter(is_active=True):
        with schema_context(tenant.schema_name):
            results[tenant.slug] = Unit.objects.count()
    return results
```

## Avoiding N+1
```python
# BAD: N+1 in serializer
class UnitSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    def get_project_name(self, obj):
        return obj.floor.building.project.name  # 3 queries per unit!

# GOOD: use select_related in queryset
queryset = Unit.objects.select_related('floor__building__project')
# Then obj.floor.building.project.name hits no extra queries
```

## Key Rules
- Always define `get_queryset()` in ViewSets — never use class-level `queryset =` for tenant models
- Use `select_related` for FK chains, `prefetch_related` for reverse FK/M2M
- Annotate instead of computing in Python when possible (database is faster)
- Index frequently-filtered fields: `status`, `project_id`, `created_at`
