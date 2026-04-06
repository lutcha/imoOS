"""
Fixtures específicas para testes de isolamento de tenant.
"""
import pytest


@pytest.fixture
def tenant_context_fixture():
    """Fixture para operações em contexto de tenant."""
    from django_tenants.utils import tenant_context
    return tenant_context
