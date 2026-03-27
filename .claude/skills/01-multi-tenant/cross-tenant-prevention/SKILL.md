---
name: cross-tenant-prevention
description: Patterns and tests that prevent cross-tenant data access in ImoOS. Auto-load when reviewing security-sensitive code or writing models/views that could leak data.
argument-hint: [model] [risk-level]
allowed-tools: Read, Write, Grep
---

# Cross-Tenant Prevention — ImoOS

## Middleware Protection (Automatic)
django-tenants sets `connection.schema_name` from the subdomain on every request.
All ORM queries on TENANT_APPS models automatically hit the correct schema.

**But this only works inside request/response cycle.** See tenant-context skill for tasks.

## The Three Attack Vectors to Guard Against

### 1. Insecure Direct Object Reference (IDOR)
```python
# VULNERABLE: UUID from URL could belong to another tenant if schemas got mixed
class UnitViewSet(viewsets.ModelViewSet):
    def get_object(self):
        # django-tenants already scopes this to active schema — safe
        return get_object_or_404(Unit, pk=self.kwargs['pk'])

# VERIFY with test:
def test_no_idor(api_client_a, tenant_b):
    with tenant_context(tenant_b):
        unit_b = UnitFactory()
    response = api_client_a.get(f'/api/v1/units/{unit_b.id}/')
    assert response.status_code == 404  # Not 200!
```

### 2. Celery Task Without tenant_context
```python
# VULNERABLE: task processes without schema switch
@shared_task
def process_unit(unit_id):
    unit = Unit.objects.get(id=unit_id)  # Which schema?!

# SAFE: always pass and re-fetch tenant
@shared_task
def process_unit(tenant_id, unit_id):
    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        unit = Unit.objects.get(id=unit_id)
```

### 3. Shared Cache Without Tenant Key
```python
# VULNERABLE: cache key without tenant scoping
cache.set('dashboard_kpis', data)  # Any tenant can read this!

# SAFE: prefix cache keys with tenant schema
schema = connection.schema_name
cache.set(f'{schema}:dashboard_kpis', data, timeout=300)
```

## Automated Prevention in CI
```python
# tests/tenant_isolation/test_cross_tenant.py
# This test MUST stay in the CI gate (see isolation-test-template skill)
@pytest.mark.isolation
def test_all_business_models_isolated(tenant_a, tenant_b):
    """Auto-discover all TENANT_APPS models and verify isolation."""
    from django.apps import apps
    from django.conf import settings

    for app_label in settings.TENANT_APPS:
        for model in apps.get_app_config(app_label.split('.')[-1]).get_models():
            with tenant_context(tenant_a):
                obj = model.objects.first()
                if obj:
                    obj_id = obj.pk
            with tenant_context(tenant_b):
                assert not model.objects.filter(pk=obj_id).exists(), \
                    f"ISOLATION BREACH: {model.__name__} leaks between tenants!"
```
