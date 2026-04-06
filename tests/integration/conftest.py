"""
Fixtures específicas para testes de integração.
"""
import pytest


@pytest.fixture(scope='module')
def integration_test_data():
    """Dados compartilhados entre testes de integração."""
    return {}
