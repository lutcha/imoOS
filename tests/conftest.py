"""
Global pytest fixtures for ImoOS test suite.
"""
import pytest
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def tenant_a(db):
    """Tenant A — first promotora for isolation tests."""
    from apps.tenants.models import Client, Domain
    tenant = Client.objects.create(
        schema_name='test_empresa_a',
        name='Empresa A Lda',
        slug='empresa-a',
        plan='pro',
        is_active=True,
    )
    Domain.objects.create(domain='empresa-a.imos.cv', tenant=tenant, is_primary=True)
    return tenant


@pytest.fixture
def tenant_b(db):
    """Tenant B — second promotora for isolation tests."""
    from apps.tenants.models import Client, Domain
    tenant = Client.objects.create(
        schema_name='test_empresa_b',
        name='Empresa B Lda',
        slug='empresa-b',
        plan='starter',
        is_active=True,
    )
    Domain.objects.create(domain='empresa-b.imos.cv', tenant=tenant, is_primary=True)
    return tenant


@pytest.fixture
def admin_user_a(tenant_a):
    """Admin user in Tenant A."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    with tenant_context(tenant_a):
        user = User.objects.create_user(
            email='admin@empresa-a.cv',
            password='testpass123',
        )
    return user


@pytest.fixture
def api_client_a(tenant_a, admin_user_a, api_client):
    """APIClient authenticated as Tenant A admin."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user_a)
    refresh['tenant_schema'] = tenant_a.schema_name
    api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}',
        HTTP_HOST='empresa-a.imos.cv',
    )
    return api_client


# ---------------------------------------------------------------------------
# JWT isolation fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user_tenant_a(tenant_a):
    """
    A regular gestor user created inside tenant_a's schema.

    The user is created with tenant_context so the INSERT lands in the correct
    PostgreSQL schema.  Used by JWT isolation tests to mint tokens that carry
    ``tenant_schema = tenant_a.schema_name``.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    with tenant_context(tenant_a):
        user = User.objects.create_user(
            email='gestor@empresa-a.cv',
            password='testpass123!',
            role='gestor',
        )
    return user


@pytest.fixture
def user_tenant_b(tenant_b):
    """
    A regular gestor user created inside tenant_b's schema.

    Symmetric counterpart to ``user_tenant_a``.  Used to mint JWT tokens
    scoped to tenant_b.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    with tenant_context(tenant_b):
        user = User.objects.create_user(
            email='gestor@empresa-b.cv',
            password='testpass123!',
            role='gestor',
        )
    return user


@pytest.fixture
def api_client_tenant_a(tenant_a, user_tenant_a):
    """
    APIClient pre-configured with a JWT token scoped to tenant_a and the
    correct Host header for tenant_a's domain.

    Use this fixture when you need an authenticated client for tenant_a without
    manually constructing the token in each test.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user_tenant_a)
    refresh['tenant_schema'] = tenant_a.schema_name
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    client.defaults['HTTP_HOST'] = 'empresa-a.imos.cv'
    return client


@pytest.fixture
def api_client_tenant_b(tenant_b, user_tenant_b):
    """
    APIClient pre-configured with a JWT token scoped to tenant_b and the
    correct Host header for tenant_b's domain.

    Symmetric counterpart to ``api_client_tenant_a``.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user_tenant_b)
    refresh['tenant_schema'] = tenant_b.schema_name
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    client.defaults['HTTP_HOST'] = 'empresa-b.imos.cv'
    return client
