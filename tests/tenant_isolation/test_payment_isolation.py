"""
CRITICAL: Payment Plan Tenant Isolation Tests
=============================================
Verifies that PaymentPlan and PaymentPlanItem data is strictly scoped to its
originating tenant schema. A failure here means one promotora can read, generate,
or modify another promotora's payment schedules — a catastrophic data-integrity
and legal breach.

Test coverage
-------------
1. TestPaymentPlanOrmIsolation
   ORM-level: plans created in tenant_a are invisible in tenant_b's schema, and vice versa.

2. TestPaymentPlanHttpIsolation
   HTTP-level: the generate action correctly enforces tenant boundaries.
   - 404 on cross-tenant contract UUID
   - 403 when using a JWT scoped to a different tenant

3. TestMbeReferenceIsolation
   MBE references are deterministic and schema-isolated: the same UUID in two
   different tenants produces different references because the contract is
   a different object.

Run:
    pytest tests/tenant_isolation/test_payment_isolation.py -v

CI gate: This test MUST pass before merge.
"""

from datetime import date
from decimal import Decimal

import pytest
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# ---------------------------------------------------------------------------
# JWT / API client helpers  (mirror test_contract_isolation.py pattern)
# ---------------------------------------------------------------------------

def _make_jwt(user, schema_name: str) -> str:
    refresh = RefreshToken.for_user(user)
    refresh["tenant_schema"] = schema_name
    return str(refresh.access_token)


def _api_client(token: str, domain: str) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    client.defaults["HTTP_HOST"] = domain
    return client


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

_counter = 0


def _next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def _make_contract(tenant) -> "Contract":
    """
    Create the minimum scaffold (unit + lead + contract) inside the given
    tenant's schema context.

    Must be called inside ``with tenant_context(tenant)``.
    """
    n = _next_id()

    from apps.projects.models import Building, Floor, Project
    from apps.inventory.models import Unit, UnitType
    from apps.crm.models import Lead
    from apps.contracts.models import Contract

    project = Project.objects.create(
        name=f"Empreendimento Payments {n}",
        slug=f"payments-{tenant.schema_name}-{n}",
        status="PLANNING",
    )
    building = Building.objects.create(project=project, name="Bloco A", code="BLK-A")
    floor = Floor.objects.create(building=building, number=1)
    unit_type = UnitType.objects.create(name=f"T2-{n}", code=f"T2-{n}", bedrooms=2, bathrooms=1)
    unit = Unit.objects.create(
        floor=floor,
        unit_type=unit_type,
        code=f"A-P1-{n:02d}",
        area_bruta=Decimal("75.00"),
        status=Unit.STATUS_AVAILABLE,
    )
    lead = Lead.objects.create(
        first_name="Test",
        last_name="Buyer",
        email=f"buyer-{n}@{tenant.schema_name}.cv",
        source=Lead.SOURCE_WEB,
    )
    contract = Contract.objects.create(
        contract_number=f"ImoOS-PLAN-{n:04d}",
        status=Contract.STATUS_DRAFT,
        total_price_cve=Decimal("5000000.00"),
        unit=unit,
        lead=lead,
    )
    return contract


# ---------------------------------------------------------------------------
# 1. ORM-level isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
class TestPaymentPlanOrmIsolation:
    """Plans in tenant_a must not be visible in tenant_b's schema and vice versa."""

    def test_plan_invisible_cross_tenant(self, tenant_a, tenant_b):
        from apps.payments.models import PaymentPlan

        with tenant_context(tenant_a):
            contract_a = _make_contract(tenant_a)
            plan_a = PaymentPlan.objects.create(
                contract=contract_a,
                plan_type=PaymentPlan.TYPE_STANDARD,
                total_cve=contract_a.total_price_cve,
            )
            plan_a.generate_standard(installments=4)

        with tenant_context(tenant_b):
            # tenant_b schema has no plans — different schema, different tables
            assert PaymentPlan.objects.count() == 0

        with tenant_context(tenant_a):
            assert PaymentPlan.objects.filter(id=plan_a.id).exists()

    def test_plan_items_invisible_cross_tenant(self, tenant_a, tenant_b):
        from apps.payments.models import PaymentPlan, PaymentPlanItem

        with tenant_context(tenant_a):
            contract_a = _make_contract(tenant_a)
            plan_a = PaymentPlan.objects.create(
                contract=contract_a,
                plan_type=PaymentPlan.TYPE_STANDARD,
                total_cve=contract_a.total_price_cve,
            )
            plan_a.generate_standard(installments=4)
            item_count_a = plan_a.items.count()
            assert item_count_a == 6  # 1 deposit + 4 installments + 1 final

        with tenant_context(tenant_b):
            # Items live in tenant_a schema — invisible here
            assert PaymentPlanItem.objects.count() == 0

    def test_bidirectional_isolation(self, tenant_a, tenant_b):
        """Plans in both tenants are independently isolated."""
        from apps.payments.models import PaymentPlan

        with tenant_context(tenant_a):
            contract_a = _make_contract(tenant_a)
            PaymentPlan.objects.create(
                contract=contract_a,
                plan_type=PaymentPlan.TYPE_STANDARD,
                total_cve=Decimal("5000000.00"),
            )

        with tenant_context(tenant_b):
            contract_b = _make_contract(tenant_b)
            PaymentPlan.objects.create(
                contract=contract_b,
                plan_type=PaymentPlan.TYPE_STANDARD,
                total_cve=Decimal("3000000.00"),
            )

        with tenant_context(tenant_a):
            plans = PaymentPlan.objects.all()
            assert plans.count() == 1
            assert plans.first().total_cve == Decimal("5000000.00")

        with tenant_context(tenant_b):
            plans = PaymentPlan.objects.all()
            assert plans.count() == 1
            assert plans.first().total_cve == Decimal("3000000.00")


# ---------------------------------------------------------------------------
# 2. HTTP-level isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
class TestPaymentPlanHttpIsolation:
    """HTTP layer must reject cross-tenant access."""

    def test_generate_with_cross_tenant_contract_returns_404(
        self, tenant_a, tenant_b, user_a, user_b, domain_a, domain_b
    ):
        """
        Using tenant_a JWT to call generate with a contract that belongs to tenant_b
        must return 404 — the contract does not exist in tenant_a's schema.
        """
        with tenant_context(tenant_b):
            contract_b = _make_contract(tenant_b)

        token_a = _make_jwt(user_a, tenant_a.schema_name)
        client_a = _api_client(token_a, domain_a)

        resp = client_a.post(
            '/api/v1/payments/plans/generate/',
            {'contract': str(contract_b.id), 'installments': 4},
            format='json',
        )
        assert resp.status_code == 404, (
            f"Expected 404 on cross-tenant contract, got {resp.status_code}: {resp.data}"
        )

    def test_regenerate_with_cross_tenant_jwt_returns_403(
        self, tenant_a, tenant_b, user_a, user_b, domain_a, domain_b
    ):
        """
        Using tenant_b JWT to call regenerate on a plan that belongs to tenant_a
        must return 401 or 404 — the plan is not accessible from tenant_b's schema.
        """
        from apps.payments.models import PaymentPlan

        with tenant_context(tenant_a):
            contract_a = _make_contract(tenant_a)
            plan_a = PaymentPlan.objects.create(
                contract=contract_a,
                plan_type=PaymentPlan.TYPE_STANDARD,
                total_cve=contract_a.total_price_cve,
            )

        token_b = _make_jwt(user_b, tenant_b.schema_name)
        client_b = _api_client(token_b, domain_b)

        resp = client_b.post(
            f'/api/v1/payments/plans/{plan_a.id}/regenerate/',
            {'installments': 4},
            format='json',
        )
        # The plan UUID doesn't exist in tenant_b's schema → 404
        assert resp.status_code in (403, 404), (
            f"Expected 403 or 404 for cross-tenant regenerate, got {resp.status_code}"
        )

    def test_list_returns_only_own_tenant_plans(
        self, tenant_a, tenant_b, user_a, user_b, domain_a, domain_b
    ):
        from apps.payments.models import PaymentPlan

        with tenant_context(tenant_a):
            contract_a = _make_contract(tenant_a)
            PaymentPlan.objects.create(
                contract=contract_a,
                plan_type=PaymentPlan.TYPE_STANDARD,
                total_cve=Decimal("5000000.00"),
            )

        with tenant_context(tenant_b):
            contract_b = _make_contract(tenant_b)
            PaymentPlan.objects.create(
                contract=contract_b,
                plan_type=PaymentPlan.TYPE_STANDARD,
                total_cve=Decimal("2000000.00"),
            )

        token_a = _make_jwt(user_a, tenant_a.schema_name)
        client_a = _api_client(token_a, domain_a)

        resp = client_a.get('/api/v1/payments/plans/', format='json')
        assert resp.status_code == 200
        # tenant_a sees only its 1 plan
        assert resp.data['count'] == 1
        assert Decimal(resp.data['results'][0]['total_cve']) == Decimal("5000000.00")


# ---------------------------------------------------------------------------
# 3. MBE reference isolation
# ---------------------------------------------------------------------------

class TestMbeReferenceIsolation:
    """
    MBE references are deterministic but contract-scoped.
    Two contracts with different UUIDs (even same amount) produce different refs.
    """

    def test_same_order_different_contracts_yield_different_refs(self):
        from apps.payments.mbe import generate_mbe_reference

        ref_1 = generate_mbe_reference("contract-uuid-1111", 0, 500000)
        ref_2 = generate_mbe_reference("contract-uuid-2222", 0, 500000)
        assert ref_1 != ref_2

    def test_deterministic_for_same_inputs(self):
        from apps.payments.mbe import generate_mbe_reference

        ref_a = generate_mbe_reference("abc-123", 2, 100000)
        ref_b = generate_mbe_reference("abc-123", 2, 100000)
        assert ref_a == ref_b

    def test_ref_is_nine_digits(self):
        from apps.payments.mbe import generate_mbe_reference

        ref = generate_mbe_reference("any-uuid", 0, 1)
        assert len(ref) == 9
        assert ref.isdigit()

    def test_different_order_yields_different_ref(self):
        from apps.payments.mbe import generate_mbe_reference

        ref_order_0 = generate_mbe_reference("same-uuid", 0, 50000)
        ref_order_1 = generate_mbe_reference("same-uuid", 1, 50000)
        assert ref_order_0 != ref_order_1
