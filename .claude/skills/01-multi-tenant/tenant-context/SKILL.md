---
name: tenant-context
description: Generate Django code with proper multi-tenant isolation using django-tenants. Auto-load when writing models, views, services, or Celery tasks that access business data.
argument-hint: [model-name] [operation]
allowed-tools: Read, Write, Grep
---

# Tenant Context Pattern — ImoOS

## Core Rule
Every database query on TENANT_APPS models MUST run inside `tenant_context()` when outside the request/response cycle.

## In Django Views (Auto-scoped by Middleware)
```python
# django-tenants middleware sets connection.tenant automatically from subdomain
# Views do NOT need explicit tenant_context — middleware handles it
class UnitViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTenantMember]
    queryset = Unit.objects.all()  # Auto-scoped to active tenant schema
    serializer_class = UnitSerializer
```

## In Celery Tasks (Always Explicit)
```python
from django_tenants.utils import tenant_context
from apps.tenants.models import Client

@shared_task(bind=True, max_retries=3)
def sync_unit_to_marketplace(self, tenant_id: str, unit_id: str):
    """ALWAYS: pass IDs only, never ORM objects. Re-fetch inside task."""
    try:
        tenant = Client.objects.get(id=tenant_id)  # Public schema — OK
        with tenant_context(tenant):
            unit = Unit.objects.get(id=unit_id)    # Tenant schema
            # ... business logic ...
    except Client.DoesNotExist:
        self.retry(exc=Exception(f"Tenant {tenant_id} not found"))
```

## In Management Commands
```python
from django_tenants.utils import tenant_context
from apps.tenants.models import Client

class Command(BaseCommand):
    def handle(self, *args, **options):
        for tenant in Client.objects.filter(is_active=True):
            with tenant_context(tenant):
                # Operates on each tenant's schema
                self.process_tenant(tenant)
```

## In Tests
```python
def test_unit_isolation(tenant_a, tenant_b):
    with tenant_context(tenant_a):
        Unit.objects.create(code='BLK-A-P1-T1', ...)  # Goes to schema_a

    with tenant_context(tenant_b):
        assert Unit.objects.count() == 0  # schema_b is empty — isolation OK
```

## ❌ Anti-Patterns (Never Generate)
```python
# WRONG: Missing tenant_context in Celery task
@shared_task
def bad_task(unit_id):
    unit = Unit.objects.get(id=unit_id)  # Which schema? DANGEROUS!

# WRONG: Passing ORM objects to Celery (serialization issues)
@shared_task
def bad_task(unit):  # ORM object not serializable across workers
    pass

# WRONG: Cross-schema query without explicit context
def get_all_units_admin():
    return Unit.objects.all()  # Only works if middleware set correct schema
```

## Permission Class
```python
# apps/core/permissions.py
class IsTenantMember(BasePermission):
    """Verify JWT tenant_schema matches the active connection schema."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        jwt_schema = request.auth.get('tenant_schema', '')
        active_schema = connection.schema_name
        return jwt_schema == active_schema
```
