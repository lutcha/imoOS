# Sprint 3 — Testes: JWT Isolation + Reservas + E2E Playwright

## Contexto actual

### O que existe em testes
- `tests/tenant_isolation/test_core_isolation.py` — Project + Unit isolation ✓
- `tests/conftest.py` — fixtures tenant_a, tenant_b, api_client_a ✓
- `apps/crm/tests/test_filters.py` + `test_tasks.py` ✓
- `apps/inventory/tests/test_filters.py` + `test_tasks.py` ✓

### O que NÃO existe (crítico para CI gate)
- Testes de isolamento JWT — user com JWT de tenant_a rejeitado em tenant_b
- Testes de UnitReservation — anti-double-booking
- E2E Playwright — nenhum fluxo de ponta a ponta testado

## Skills a carregar

```
@.claude/skills/14-testing/isolation-test-template/SKILL.md
@.claude/skills/14-testing/pytest-tenant-fixtures/SKILL.md
@.claude/skills/01-multi-tenant/jwt-tenant-claims/SKILL.md
@.claude/skills/08-module-crm/reservation-lock-mechanism/SKILL.md
@.claude/skills/00-global/security-compliance/SKILL.md
```

## Agent a activar

- Agent: `.claude/agents/03-testing/isolation-test-writer.md`
  - Prompt: "Escreve suites de testes de isolamento para ImoOS. Preciso de 3 suites: (1) JWT cross-tenant — user autenticado em tenant_a não acede API de tenant_b; (2) UnitReservation — anti-double-booking com transações concorrentes; (3) TenantMembership — role admin em tenant_a não dá acesso admin em tenant_b. Usar fixtures existentes em tests/conftest.py: tenant_a, tenant_b, api_client_a."

---

## Suite 1 — `tests/tenant_isolation/test_jwt_isolation.py`

```python
"""
JWT Tenant Isolation Tests
===========================
Verifica que tokens JWT são estritamente vinculados ao tenant que os emitiu.
Um token válido de tenant_a deve ser rejeitado em endpoints de tenant_b.
"""
import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django_tenants.utils import tenant_context


@pytest.mark.isolation
class TestJWTTenantIsolation:

    def test_token_from_tenant_a_rejected_on_tenant_b(
        self, tenant_a, tenant_b, admin_user_a, db
    ):
        """
        Um token emitido no contexto de tenant_a deve ser rejeitado
        quando usado no contexto de tenant_b.
        """
        # 1. Gerar token no contexto de tenant_a
        with tenant_context(tenant_a):
            refresh = RefreshToken.for_user(admin_user_a)
            refresh['tenant_schema'] = tenant_a.schema_name
            token = str(refresh.access_token)

        # 2. Tentar usar esse token no contexto de tenant_b
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        with tenant_context(tenant_b):
            response = client.get('/api/v1/projects/projects/')

        assert response.status_code == 403, (
            f"ISOLATION BREACH: Token from tenant_a accepted in tenant_b! "
            f"Status: {response.status_code}"
        )

    def test_token_without_tenant_schema_rejected(self, tenant_a, db):
        """Token sem claim tenant_schema deve ser rejeitado."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with tenant_context(tenant_a):
            user = User.objects.create_user(
                email='noschema@test.cv', password='pass123'
            )
            # Token sem tenant_schema (como se viesse de um sistema externo)
            refresh = RefreshToken.for_user(user)
            # Não injectar tenant_schema
            token = str(refresh.access_token)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        with tenant_context(tenant_a):
            response = client.get('/api/v1/projects/projects/')

        assert response.status_code == 403

    def test_lead_data_isolated_via_api(
        self, tenant_a, tenant_b, admin_user_a, api_client_a, db
    ):
        """Leads criados em tenant_a não visíveis via API de tenant_b."""
        from apps.crm.models import Lead

        with tenant_context(tenant_a):
            Lead.objects.create(
                first_name='João', last_name='Silva',
                email='joao@test.cv', source='DIRECT',
            )

        # api_client_a está autenticado em tenant_a — tentar aceder tenant_b
        # (IsTenantMember deve bloquear porque o JWT tem tenant_schema=tenant_a
        # mas o contexto activo é tenant_b)
        with tenant_context(tenant_b):
            response = api_client_a.get('/api/v1/crm/leads/')

        assert response.status_code == 403, (
            "ISOLATION BREACH: api_client_a (tenant_a token) accessed tenant_b CRM!"
        )


@pytest.mark.isolation
class TestMembershipRoleIsolation:
    """TenantMembership roles devem ser estritamente per-schema."""

    def test_admin_in_tenant_a_is_not_admin_in_tenant_b(
        self, tenant_a, tenant_b, admin_user_a, db
    ):
        """User que é admin em tenant_a não tem role admin em tenant_b."""
        from apps.memberships.models import TenantMembership

        # Verificar que existe membership em tenant_a
        with tenant_context(tenant_a):
            is_admin_a = TenantMembership.objects.filter(
                user=admin_user_a, role=TenantMembership.ROLE_ADMIN, is_active=True
            ).exists()

        # Verificar que NÃO existe membership em tenant_b
        with tenant_context(tenant_b):
            is_admin_b = TenantMembership.objects.filter(
                user=admin_user_a
            ).exists()

        assert is_admin_a, "Test setup error: admin_user_a should be admin in tenant_a"
        assert not is_admin_b, (
            "ISOLATION BREACH: admin_user_a has membership in tenant_b!"
        )
```

---

## Suite 2 — `tests/tenant_isolation/test_reservation_isolation.py`

```python
"""
Reservation Anti-Double-Booking + Isolation Tests
==================================================
Garante que:
1. Duas reservas simultâneas para a mesma unidade resultam em apenas uma com sucesso
2. Reservas são isoladas por schema — tenant_b não vê reservas de tenant_a
"""
import pytest
import threading
from django_tenants.utils import tenant_context


@pytest.mark.isolation
class TestReservationIsolation:

    def test_reservation_invisible_across_tenants(
        self, tenant_a, tenant_b, db
    ):
        """UnitReservation de tenant_a não visível em tenant_b."""
        from apps.crm.models import UnitReservation
        # ... criar reserva em tenant_a, verificar count=0 em tenant_b

    def test_cancel_reservation_scoped_to_tenant(
        self, tenant_a, tenant_b, db
    ):
        """Cancelar todas as reservas em tenant_a não afecta tenant_b."""
        # ... criar reservas em ambos, cancelar em tenant_a, verificar tenant_b intacto


@pytest.mark.isolation
class TestAntiDoubleBooking:

    def test_concurrent_reservations_only_one_succeeds(
        self, tenant_a, db
    ):
        """
        Simula dois requests simultâneos para reservar a mesma unidade.
        Apenas um deve ter sucesso — o outro deve receber um erro adequado.

        Usa threading para simular concorrência real.
        """
        from apps.crm.models import UnitReservation
        from apps.inventory.models import Unit
        # ... usar threads para chamar create_reservation em simultâneo
        # verificar: UnitReservation.objects.filter(unit=unit, status='ACTIVE').count() == 1
```

---

## Suite 3 — E2E Playwright `tests/e2e/`

### Setup

```bash
# Criar directório e instalar Playwright para Python (ou usar o frontend)
mkdir -p tests/e2e
pip install playwright pytest-playwright
playwright install chromium
```

**`tests/e2e/conftest.py`:**
```python
import pytest
from playwright.sync_api import Page, BrowserContext

STAGING_URL = "https://imoos-staging.ondigitalocean.app"
# ou LOCAL_URL = "http://localhost:3000"
BASE_URL = STAGING_URL

@pytest.fixture
def page_with_auth(page: Page):
    """Fixture que faz login antes do teste."""
    page.goto(f"{BASE_URL}/auth/login")
    page.fill('[type=email]', 'admin@empresa-demo.cv')
    page.fill('[type=password]', 'demo123')
    page.click('[type=submit]')
    page.wait_for_url(f"{BASE_URL}/")
    return page
```

**`tests/e2e/test_auth_flow.py`:**
```python
def test_login_redirect_and_logout(page):
    """Aceder rota protegida → redirect login → login → dashboard."""
    page.goto(f"{BASE_URL}/inventory")
    assert "/auth/login" in page.url
    page.fill('[type=email]', 'admin@empresa-demo.cv')
    page.fill('[type=password]', 'demo123')
    page.click('[type=submit]')
    page.wait_for_url(f"{BASE_URL}/inventory")  # redirect para destino original
    assert page.title() == "ImoOS — Sistema de Gestão Imobiliária"

def test_invalid_credentials_show_error(page):
    page.goto(f"{BASE_URL}/auth/login")
    page.fill('[type=email]', 'wrong@test.cv')
    page.fill('[type=password]', 'wrongpass')
    page.click('[type=submit]')
    # Deve mostrar mensagem de erro em pt-PT
    assert page.locator("text=Credenciais inválidas").is_visible()
```

**`tests/e2e/test_inventory_flow.py`:**
```python
def test_inventory_table_loads(page_with_auth):
    page_with_auth.goto(f"{BASE_URL}/inventory")
    page_with_auth.wait_for_selector('table')
    # Verificar que a tabela tem pelo menos um header
    assert page_with_auth.locator('th:has-text("Código")').is_visible()

def test_status_filter_updates_table(page_with_auth):
    page_with_auth.goto(f"{BASE_URL}/inventory")
    page_with_auth.click('button:has-text("Disponível")')
    page_with_auth.wait_for_load_state('networkidle')
    # Todos os badges visíveis devem ser "Disponível"
    badges = page_with_auth.locator('[data-status="AVAILABLE"]').all()
    # ... verificar que não há badges de outros status
```

---

## Integrar E2E no CI

**`.github/workflows/ci.yml`** — ler o ficheiro existente, adicionar job:

```yaml
  e2e-tests:
    needs: [deploy-staging]  # só corre após staging estar up
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install playwright pytest-playwright
      - run: playwright install chromium --with-deps
      - run: pytest tests/e2e/ -v --base-url=${{ vars.STAGING_URL }}
    env:
      STAGING_URL: ${{ vars.STAGING_URL }}
```

## Verificação final

- [ ] `pytest tests/tenant_isolation/ -v --tb=short` — todos passing (incluindo novas suites)
- [ ] `pytest tests/tenant_isolation/test_jwt_isolation.py -v` — 100% passing
- [ ] `pytest tests/tenant_isolation/test_reservation_isolation.py -v` — 100% passing
- [ ] `pytest tests/e2e/ -v` — login + inventário + filtros passing em staging
- [ ] CI `isolation-tests` job continua a passar (não regredir)
- [ ] Coverage nas apps core ≥ 80%: `pytest --cov=apps --cov-report=term-missing`
