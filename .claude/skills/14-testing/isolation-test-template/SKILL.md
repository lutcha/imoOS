---
name: isolation-test-template
description: Generate tenant isolation tests that MUST pass before any merge. Template for verifying that Tenant A data never leaks to Tenant B. Auto-load when writing tests for any model or API.
argument-hint: [model-name] [operation]
user-invocable: true
---

# Tenant Isolation Test Template

## The Golden Rule
**If this test fails, the build FAILS. No exceptions.**
A query from Tenant B must NEVER return data belonging to Tenant A.

## Standard Isolation Test Pattern

```python
# tests/tenant_isolation/test_<module>_isolation.py
import pytest
from django_tenants.utils import tenant_context
from apps.<module>.models import <Model>
from tests.factories import <Model>Factory

@pytest.mark.isolation
class Test<Model>Isolation:
    """
    CRITICAL: These tests verify that <Model> data is fully isolated between tenants.
    All tests in this class must pass before any merge to main.
    """

    def test_tenant_a_data_invisible_to_tenant_b(self, tenant_a, tenant_b):
        """Core isolation: Tenant B cannot see Tenant A's records."""
        # Arrange: Create data in Tenant A
        with tenant_context(tenant_a):
            obj = <Model>Factory()
            tenant_a_id = obj.id

        # Act: Query from Tenant B context
        with tenant_context(tenant_b):
            count = <Model>.objects.count()
            exists = <Model>.objects.filter(id=tenant_a_id).exists()

        # Assert: Tenant B sees nothing
        assert count == 0, (
            f"ISOLATION BREACH: Tenant B ({tenant_b.schema_name}) "
            f"can see {count} <Model> records from Tenant A ({tenant_a.schema_name})!"
        )
        assert not exists, (
            f"ISOLATION BREACH: Tenant B can directly access "
            f"<Model> id={tenant_a_id} from Tenant A!"
        )

    def test_api_cross_tenant_access_denied(self, api_client_a, tenant_b):
        """API: Authenticated Tenant A user cannot access Tenant B resources."""
        with tenant_context(tenant_b):
            obj = <Model>Factory()

        # api_client_a is authenticated for tenant_a but requests tenant_b host
        response = api_client_a.get(
            f'/api/v1/<model-plural>/{obj.id}/',
            HTTP_HOST='empresa-b.imos.cv',
        )
        assert response.status_code in [403, 404], (
            f"SECURITY: Tenant A user accessed Tenant B resource! "
            f"Got {response.status_code}"
        )

    def test_bulk_operation_stays_within_tenant(self, tenant_a, tenant_b):
        """Bulk operations (import, update) must not affect other tenants."""
        with tenant_context(tenant_a):
            <Model>Factory.create_batch(5)

        with tenant_context(tenant_b):
            <Model>Factory.create_batch(3)

        # Bulk delete in Tenant A
        with tenant_context(tenant_a):
            <Model>.objects.all().delete()

        # Tenant B data untouched
        with tenant_context(tenant_b):
            count = <Model>.objects.count()

        assert count == 3, (
            f"ISOLATION BREACH: Bulk delete in Tenant A affected Tenant B! "
            f"Expected 3, got {count}"
        )

    def test_celery_task_scoped_to_tenant(self, tenant_a, tenant_b, mocker):
        """Async tasks must only operate on the specified tenant's data."""
        with tenant_context(tenant_a):
            obj_a = <Model>Factory()

        with tenant_context(tenant_b):
            obj_b = <Model>Factory()

        # Run task scoped to Tenant A
        from apps.<module>.tasks import process_<model>
        process_<model>(tenant_id=tenant_a.id, <model>_id=obj_a.id)

        # Verify Tenant B object untouched
        with tenant_context(tenant_b):
            refreshed = <Model>.objects.get(id=obj_b.id)
            # Assert no unexpected changes
```

## CI Gate — Required in GitHub Actions

```yaml
# .github/workflows/ci.yml
- name: Run isolation tests (MANDATORY)
  run: pytest tests/tenant_isolation/ -v --tb=short -m isolation
  # This step MUST pass for CI to be green
  # Failure here blocks ALL merges
```

## Quick Isolation Check (run before every PR)

```bash
make test-isolation
# Equivalent to:
# pytest tests/tenant_isolation/ -v --tb=long
```
