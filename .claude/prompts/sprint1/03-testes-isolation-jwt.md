# Sprint 1 — Testes: Expandir Isolation Suite (JWT + CRM + LeadCapture)

## Estado actual

`tests/tenant_isolation/test_core_isolation.py` já tem:
- `TestProjectIsolation` — projecto invisível entre tenants ✓
- `TestUnitIsolation` — unidades isoladas, bulk delete scoped ✓

`tests/conftest.py` tem fixtures: `tenant_a`, `tenant_b`, `api_client_a`

## O que falta (crítico para CI gate)

1. **TestJWTIsolation** — JWT de tenant_a rejeitado em tenant_b
2. **TestAPIViewIsolation** — chamadas de API autenticadas com token errado retornam 403
3. **TestCRMIsolation** — leads de tenant_a não visíveis em tenant_b
4. **TestLeadCaptureIsolation** — endpoint público cria lead no schema correcto

## Skills a carregar

```
@.claude/skills/14-testing/isolation-test-template/SKILL.md
@.claude/skills/14-testing/pytest-tenant-fixtures/SKILL.md
@.claude/skills/01-multi-tenant/jwt-tenant-claims/SKILL.md
@.claude/skills/01-multi-tenant/tenant-permissions/SKILL.md
@.claude/skills/01-multi-tenant/cross-tenant-prevention/SKILL.md
```

## Agent a activar

- Agent: `.claude/agents/03-testing/isolation-test-writer.md`
  - Prompt: "Escreve testes de isolamento para: (1) JWT tenant_schema claim errado retorna 403; (2) Lead criado via LeadCaptureView vai para o schema do tenant activo; (3) LeadViewSet de tenant_a não vê leads de tenant_b. Usa os fixtures existentes em tests/conftest.py"

## Fixtures adicionais necessárias em `tests/conftest.py`

Adicionar aos fixtures existentes:

```python
import pytest
from rest_framework.test import APIClient
from django_tenants.utils import tenant_context

@pytest.fixture
def admin_user_b(tenant_b):
    """Admin user for tenant_b — for cross-tenant attack simulation."""
    from apps.users.models import User
    with tenant_context(tenant_b):
        return User.objects.create_user(
            email='admin@tenant-b.test',
            password='testpass123',
            role='admin'
        )

@pytest.fixture
def api_client_b(tenant_b, admin_user_b):
    """Authenticated API client for tenant_b with correct JWT."""
    from rest_framework_simplejwt.tokens import RefreshToken
    client = APIClient()
    with tenant_context(tenant_b):
        refresh = RefreshToken.for_user(admin_user_b)
        refresh['tenant_schema'] = tenant_b.schema_name
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client

@pytest.fixture
def api_client_a_wrong_tenant(tenant_b, admin_user_a):
    """
    Client com token válido de tenant_a mas a aceder a tenant_b.
    Deve ser rejeitado por IsTenantMember.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user_a)
    refresh['tenant_schema'] = admin_user_a.tenant_schema  # schema de A
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    # Simular middleware a activar schema de tenant_b
    client.tenant = tenant_b
    return client
```

## Testes a criar em `tests/tenant_isolation/test_jwt_isolation.py`

```python
"""
JWT Tenant Isolation Tests
==========================
Verifica que tokens JWT de um tenant são rejeitados noutro tenant.
Isto protege contra ataques de token replay cross-tenant.
"""
import pytest
from django_tenants.utils import tenant_context
from django.test import RequestFactory
from django.db import connection

@pytest.mark.isolation
class TestJWTIsolation:

    def test_token_with_wrong_schema_rejected(self, tenant_a, tenant_b,
                                               admin_user_a, api_client_a_wrong_tenant, db):
        """
        Token com tenant_schema='tenant_a' é rejeitado quando o middleware
        activa o schema de tenant_b. IsTenantMember deve retornar 403.
        """
        # api_client_a_wrong_tenant tem token de tenant_a
        # mas a request vai para o contexto de tenant_b
        with tenant_context(tenant_b):
            # Forçar connection.schema_name = tenant_b.schema_name
            response = api_client_a_wrong_tenant.get('/api/v1/projects/projects/')

        assert response.status_code == 403, (
            f"SECURITY BREACH: Token de tenant_a aceite em tenant_b! "
            f"Status: {response.status_code}"
        )

    def test_valid_token_accepted_in_correct_tenant(self, tenant_a, api_client_a, db):
        """Token correcto aceite no tenant correcto."""
        with tenant_context(tenant_a):
            response = api_client_a.get('/api/v1/projects/projects/')
        assert response.status_code in [200, 404]  # 404 = sem projectos, mas autenticado

    def test_no_token_rejected(self, tenant_a, db):
        """Request sem token rejeitada."""
        from rest_framework.test import APIClient
        client = APIClient()
        with tenant_context(tenant_a):
            response = client.get('/api/v1/projects/projects/')
        assert response.status_code == 401


@pytest.mark.isolation
class TestCRMIsolation:

    def test_leads_isolated_between_tenants(self, tenant_a, tenant_b, db):
        """Leads de tenant_a não visíveis em tenant_b."""
        from apps.crm.models import Lead

        with tenant_context(tenant_a):
            Lead.objects.create(
                first_name='João', last_name='Silva',
                email='joao@test.cv', status='NEW', source='WEB'
            )

        with tenant_context(tenant_b):
            count = Lead.objects.count()

        assert count == 0, (
            f"ISOLATION BREACH: Tenant B vê {count} leads de Tenant A!"
        )

    def test_lead_capture_creates_in_active_schema(self, tenant_a, db):
        """
        LeadCaptureView público deve criar o Lead no schema do tenant activo,
        não no schema público.
        """
        from apps.crm.models import Lead
        from rest_framework.test import APIClient

        client = APIClient()
        payload = {
            'first_name': 'Maria', 'last_name': 'Santos',
            'email': 'maria@test.cv', 'source': 'INSTAGRAM'
        }

        with tenant_context(tenant_a):
            # Simular request ao tenant_a domain
            response = client.post('/api/v1/crm/lead-capture/', payload, format='json')
            count = Lead.objects.count()

        assert response.status_code == 201, f"Esperado 201, got {response.status_code}"
        assert count == 1, f"Lead deve ser criado no schema de tenant_a, got {count}"

    def test_lead_capture_not_visible_in_other_tenant(self, tenant_a, tenant_b, db):
        """Lead capturado em tenant_a não aparece em tenant_b."""
        from apps.crm.models import Lead
        from rest_framework.test import APIClient

        client = APIClient()

        with tenant_context(tenant_a):
            client.post('/api/v1/crm/lead-capture/', {
                'first_name': 'Carlos', 'last_name': 'Monteiro',
                'email': 'carlos@test.cv', 'source': 'WEB'
            }, format='json')

        with tenant_context(tenant_b):
            count = Lead.objects.count()

        assert count == 0, (
            f"ISOLATION BREACH: Lead de tenant_a visível em tenant_b!"
        )
```

## Como correr

```bash
# Correr apenas isolation tests (gate obrigatório)
pytest tests/tenant_isolation/ -v -m isolation

# Com coverage
pytest tests/tenant_isolation/ --cov=apps --cov-report=term-missing

# Correr o novo ficheiro especificamente
pytest tests/tenant_isolation/test_jwt_isolation.py -v
```

## Verificação final (gate CI)

- [ ] `pytest tests/tenant_isolation/ -v` — 100% passing (zero falhas = zero merges bloqueados)
- [ ] `TestJWTIsolation::test_token_with_wrong_schema_rejected` PASS
- [ ] `TestCRMIsolation::test_leads_isolated_between_tenants` PASS
- [ ] `TestCRMIsolation::test_lead_capture_creates_in_active_schema` PASS
- [ ] Coverage `apps/` ≥ 60% (meta Sprint 1, alvo 80% no Release 1)
