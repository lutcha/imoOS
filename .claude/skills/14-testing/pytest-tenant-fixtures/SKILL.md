---
name: pytest-tenant-fixtures
description: Generate pytest fixtures for ImoOS tenant testing — tenant creation, authenticated API clients, user factories with tenant context. Auto-load when writing any test file.
argument-hint: [module] [test-type]
allowed-tools: Read, Write, Grep
---

# ImoOS Pytest Tenant Fixtures

## Core Fixtures (tests/conftest.py)

```python
import pytest
from django_tenants.utils import tenant_context, schema_context
from apps.tenants.models import Client, Domain
from apps.users.models import User

@pytest.fixture
def tenant_a(db):
    """Create Tenant A with its schema."""
    tenant = Client.objects.create(
        schema_name='empresa_a',
        name='Empresa A Lda',
        plan='starter',
        is_active=True,
    )
    Domain.objects.create(
        domain='empresa-a.imos.cv',
        tenant=tenant,
        is_primary=True,
    )
    return tenant

@pytest.fixture
def tenant_b(db):
    """Create Tenant B — for isolation tests."""
    tenant = Client.objects.create(
        schema_name='empresa_b',
        name='Empresa B Lda',
        plan='starter',
        is_active=True,
    )
    Domain.objects.create(
        domain='empresa-b.imos.cv',
        tenant=tenant,
        is_primary=True,
    )
    return tenant

@pytest.fixture
def admin_user_a(tenant_a):
    """Admin user belonging to Tenant A."""
    with tenant_context(tenant_a):
        user = User.objects.create_user(
            email='admin@empresa-a.cv',
            password='testpass123',
            role='admin',
        )
    return user

@pytest.fixture
def api_client_a(tenant_a, admin_user_a, api_client):
    """DRF APIClient authenticated as Tenant A admin."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user_a)
    # Inject tenant claim
    refresh['tenant_schema'] = tenant_a.schema_name
    api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}',
        HTTP_HOST='empresa-a.imos.cv',
    )
    return api_client
```

## Factory Boy Factories

```python
# tests/factories.py
import factory
from django_tenants.utils import tenant_context
from apps.tenants.models import Client
from apps.projects.models import Project

class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f'Projecto Residencial {n}')
    status = 'PLANNING'
    location = factory.LazyFunction(
        lambda: {'type': 'Point', 'coordinates': [-23.5170, 14.9177]}
    )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Factories must be called inside tenant_context externally
        return super()._create(model_class, *args, **kwargs)
```

## Usage in Tests

```python
def test_project_list(api_client_a, tenant_a):
    with tenant_context(tenant_a):
        ProjectFactory.create_batch(3)

    response = api_client_a.get('/api/v1/projects/')
    assert response.status_code == 200
    assert response.data['count'] == 3

def test_isolation(tenant_a, tenant_b):
    """Tenant A data must NOT be visible to Tenant B."""
    with tenant_context(tenant_a):
        ProjectFactory()  # 1 project in schema_a

    with tenant_context(tenant_b):
        count = Project.objects.count()

    assert count == 0, f"ISOLATION BREACH: Tenant B saw {count} projects from Tenant A!"
```

## pytest.ini Configuration

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --reuse-db --no-migrations -x
markers =
    isolation: marks tests that verify tenant data isolation (deselect with -m "not isolation")
    slow: marks tests as slow (deselect with -m "not slow")
```
