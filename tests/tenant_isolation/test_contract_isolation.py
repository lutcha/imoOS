"""
CRITICAL: Contract & Payment Tenant Isolation Tests
====================================================
These tests verify that Contract and Payment data is strictly scoped to its
originating tenant schema.  A failure here means one promotora can see,
activate, cancel, or enumerate another promotora's contracts — a catastrophic
data-integrity, commercial, and legal breach.

Test coverage
-------------
1. TestContractTenantIsolation
   ORM-level: contracts created in tenant_a are completely invisible inside
   tenant_b's schema context, and vice versa.

2. TestContractActivateIsolation
   HTTP-level: the activate action correctly enforces tenant boundaries.
   Verifies 404 on cross-tenant UUID lookup, 403 on cross-tenant JWT, and
   correct unit status transition on a valid same-tenant activate.

3. TestPaymentIsolation
   ORM-level: payment rows belong exclusively to the schema where their
   parent contract lives; the other schema sees nothing.

4. TestContractCancelIsolation
   HTTP-level: the cancel action releases the unit only within the correct
   tenant schema and cannot be triggered cross-tenant.

Run:
    pytest tests/tenant_isolation/test_contract_isolation.py -v

CI gate: This test MUST pass before merge.
"""
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# ---------------------------------------------------------------------------
# Module-level helpers  (mirror the pattern from test_reservation_isolation.py)
# ---------------------------------------------------------------------------

def _make_jwt_for_user(user, schema_name: str) -> str:
    """
    Mint a JWT access token carrying a ``tenant_schema`` claim.
    Mirrors CustomTokenObtainPairSerializer used in production.
    """
    refresh = RefreshToken.for_user(user)
    refresh["tenant_schema"] = schema_name
    return str(refresh.access_token)


def _api_client_for_tenant(token: str, domain: str) -> APIClient:
    """
    Return an APIClient pre-configured with a Bearer token and the correct
    Host header so ImoOSTenantMiddleware resolves the right schema.
    """
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    client.defaults["HTTP_HOST"] = domain
    return client


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

# Counter used to generate unique slugs and contract numbers within a single
# test run so that Project.slug (unique=True) and Contract.contract_number
# (unique=True) do not collide when multiple tests call factory helpers.
_scaffold_counter = 0


def _create_unit_scaffold(tenant):
    """
    Create the minimum Project / Building / Floor / UnitType / Unit hierarchy
    required to produce one AVAILABLE unit inside the given tenant's schema.

    Must be called inside ``with tenant_context(tenant)``.
    Returns the Unit instance.
    """
    global _scaffold_counter
    _scaffold_counter += 1

    from apps.projects.models import Building, Floor, Project
    from apps.inventory.models import Unit, UnitType

    project = Project.objects.create(
        name=f"Empreendimento Contrato {_scaffold_counter}",
        slug=f"contrato-{tenant.schema_name}-{_scaffold_counter}",
        status="PLANNING",
    )
    building = Building.objects.create(
        project=project,
        name="Bloco A",
        code="BLK-A",
    )
    floor = Floor.objects.create(building=building, number=1)
    unit_type = UnitType.objects.create(
        name="T2",
        code="T2",
        bedrooms=2,
        bathrooms=1,
    )
    unit = Unit.objects.create(
        floor=floor,
        unit_type=unit_type,
        code="A-P1-01",
        area_bruta=Decimal("75.00"),
        status=Unit.STATUS_AVAILABLE,
    )
    return unit


def _create_lead(tenant):
    """
    Create a minimal Lead inside the given tenant's schema context.
    Must be called inside ``with tenant_context(tenant)``.
    Returns the Lead instance.
    """
    global _scaffold_counter
    _scaffold_counter += 1

    from apps.crm.models import Lead

    return Lead.objects.create(
        first_name="Test",
        last_name="Lead",
        email=f"lead-{_scaffold_counter}@{tenant.schema_name}.cv",
        source=Lead.SOURCE_WEB,
    )


def _expires_at():
    """Return a default expiry 48 h from now (matches RESERVATION_EXPIRY_HOURS)."""
    return timezone.now() + timedelta(hours=48)


def _make_contract_orm(unit, lead, reservation=None):
    """
    Create a Contract directly via ORM (no service layer).
    Use this only in isolation-level tests that do NOT test service logic.
    Supplies all required non-nullable fields.

    Must be called inside ``with tenant_context(tenant)``.
    Returns the Contract instance.
    """
    global _scaffold_counter
    _scaffold_counter += 1

    from apps.contracts.models import Contract

    return Contract.objects.create(
        contract_number=f"ImoOS-2026-{_scaffold_counter:04d}",
        status=Contract.STATUS_DRAFT,
        total_price_cve=Decimal("5000000.00"),
        unit=unit,
        lead=lead,
        reservation=reservation,
    )


def _make_active_reservation(tenant, user):
    """
    Full pre-condition scaffold for HTTP activate/cancel tests.

    Inside tenant_context(tenant):
      1. Creates unit scaffold + lead.
      2. Creates an ACTIVE UnitReservation with a valid expires_at.
      3. Sets unit.status = RESERVED.
      4. Creates a DRAFT Contract linked to the reservation.

    Returns (unit, lead, reservation, contract) — all within tenant schema.
    Must be called outside any tenant_context; it opens its own.
    """
    from apps.crm.models import UnitReservation
    from apps.inventory.models import Unit

    with tenant_context(tenant):
        unit = _create_unit_scaffold(tenant)
        lead = _create_lead(tenant)

        reservation = UnitReservation.objects.create(
            unit=unit,
            lead=lead,
            status=UnitReservation.STATUS_ACTIVE,
            expires_at=_expires_at(),
            deposit_amount_cve=Decimal("100000.00"),
        )

        unit.status = Unit.STATUS_RESERVED
        unit.save(update_fields=["status", "updated_at"])

        contract = _make_contract_orm(unit, lead, reservation=reservation)

    return unit, lead, reservation, contract


def _grant_tenant_admin(user, tenant):
    """
    Create a TenantMembership row granting the user admin role inside tenant.

    The ContractViewSet activate/cancel actions are protected by IsTenantAdmin,
    which queries TenantMembership in the active schema.  Without this row the
    test user receives 403 even on their own tenant.

    Must be called inside ``with tenant_context(tenant)``.
    """
    from apps.memberships.models import TenantMembership

    TenantMembership.objects.get_or_create(
        user=user,
        defaults={"role": TenantMembership.ROLE_ADMIN, "is_active": True},
    )


# ---------------------------------------------------------------------------
# Test Class 1 — ORM-level contract isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestContractTenantIsolation:
    """
    Direct ORM-level verification that Contract rows created in tenant_a's
    PostgreSQL schema are completely invisible when querying from tenant_b,
    and vice versa.

    These tests validate the schema-per-tenant guarantee at its most
    fundamental level, independent of any HTTP or service layer.
    """

    def test_contract_from_tenant_a_invisible_in_tenant_b(
        self, tenant_a, tenant_b
    ):
        """
        A Contract created inside tenant_a must not appear when querying
        Contract from within tenant_b's schema context.

        Failure here = one promotora can enumerate another's contract pipeline
        — a catastrophic data and commercial leak.
        """
        from apps.contracts.models import Contract

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            contract_a = _make_contract_orm(unit_a, lead_a)
            count_a = Contract.objects.count()

        with tenant_context(tenant_b):
            count_b = Contract.objects.count()
            direct_lookup = Contract.objects.filter(id=contract_a.id).count()

        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} contract(s) from "
            f"tenant_a. Expected 0."
        )
        assert direct_lookup == 0, (
            f"ISOLATION BREACH: tenant_b can directly look up "
            f"Contract {contract_a.id} which belongs to tenant_a."
        )
        # Sanity: the row still exists where it was created.
        assert count_a == 1

    def test_contract_from_tenant_b_invisible_in_tenant_a(
        self, tenant_a, tenant_b
    ):
        """
        Symmetric direction: tenant_b's contract must not be reachable from
        within tenant_a's schema context (B → A).
        """
        from apps.contracts.models import Contract

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            contract_b = _make_contract_orm(unit_b, lead_b)

        with tenant_context(tenant_a):
            count_a = Contract.objects.count()
            direct_lookup = Contract.objects.filter(id=contract_b.id).count()

        assert count_a == 0, (
            f"ISOLATION BREACH: tenant_a sees {count_a} contract(s) from "
            f"tenant_b. Expected 0."
        )
        assert direct_lookup == 0, (
            f"ISOLATION BREACH: tenant_a can directly look up "
            f"Contract {contract_b.id} which belongs to tenant_b."
        )

    def test_contract_counts_independent_per_tenant(self, tenant_a, tenant_b):
        """
        Creating contracts in both tenants must produce independent counts
        with zero cross-schema contamination in either direction.
        """
        from apps.contracts.models import Contract

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            _make_contract_orm(unit_a, lead_a)
            count_a = Contract.objects.count()

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            _make_contract_orm(unit_b, lead_b)
            count_b = Contract.objects.count()

        # Re-read both schemas after both inserts.
        with tenant_context(tenant_a):
            assert Contract.objects.count() == count_a == 1, (
                f"ISOLATION BREACH: tenant_a count changed after tenant_b "
                f"insert. Expected 1, got {Contract.objects.count()}."
            )
        with tenant_context(tenant_b):
            assert Contract.objects.count() == count_b == 1, (
                f"ISOLATION BREACH: tenant_b count changed after tenant_a "
                f"insert. Expected 1, got {Contract.objects.count()}."
            )

    def test_contract_uuid_not_resolvable_cross_tenant(
        self, tenant_a, tenant_b
    ):
        """
        Even if a user from tenant_a constructs a queryset filter using the
        exact UUID of tenant_b's contract, the result must be empty.

        This mirrors what happens when cross-tenant UUID guessing is attempted
        — the attacker knows the ID but the schema boundary blocks the lookup.
        """
        from apps.contracts.models import Contract

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            contract_b = _make_contract_orm(unit_b, lead_b)
            known_uuid = contract_b.id  # Attacker knows this UUID

        with tenant_context(tenant_a):
            result = Contract.objects.filter(id=known_uuid)
            assert not result.exists(), (
                f"ISOLATION BREACH: filter(id={known_uuid}) inside tenant_a "
                f"schema returned a row that belongs to tenant_b."
            )


# ---------------------------------------------------------------------------
# Test Class 2 — HTTP-level activate action isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestContractActivateIsolation:
    """
    HTTP-level verification that the activate action on ContractViewSet
    correctly enforces tenant boundaries.

    ImoOSTenantMiddleware sets the active DB schema from the Host header.
    IsTenantMember then compares the JWT's ``tenant_schema`` claim against
    the active schema.  IsTenantAdmin additionally requires a TenantMembership
    row with role='admin' in that schema.

    Expected HTTP codes:
      Cross-tenant UUID on own domain              → 404
      Cross-tenant JWT sent to wrong domain        → 403
      Correct admin credentials on own DRAFT        → 200, unit CONTRACT
    """

    def test_tenant_a_cannot_activate_tenant_b_contract(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        A user from tenant_a who knows the UUID of tenant_b's contract and
        sends an activate request to tenant_a's domain must receive 404.

        The schema boundary makes the row invisible inside tenant_a — the
        router cannot resolve the pk, so DRF returns 404, not 403.
        """
        _, _, _, contract_b = _make_active_reservation(tenant_b, user_tenant_a)

        with tenant_context(tenant_a):
            _grant_tenant_admin(user_tenant_a, tenant_a)

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        with patch("apps.contracts.tasks.generate_contract_pdf.delay"):
            response = client.post(
                f"/api/v1/contracts/contracts/{contract_b.id}/activate/",
                format="json",
            )

        assert response.status_code == 404, (
            f"ISOLATION BREACH: tenant_a user received {response.status_code} "
            f"when targeting tenant_b's contract UUID on tenant_a's domain. "
            f"Expected 404 — the UUID must be invisible in tenant_a's schema."
        )

    def test_cross_tenant_jwt_on_activate_returns_403(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        A tenant_a JWT routed to tenant_b's domain (via Host header) must be
        rejected with 403.  IsTenantMember detects the schema mismatch between
        the JWT claim (tenant_a) and the active schema (tenant_b).

        This prevents token-reuse attacks where a user exports their JWT and
        replays it against a different tenant's subdomain.
        """
        _, _, _, contract_b = _make_active_reservation(tenant_b, user_tenant_a)

        # Mint a token scoped to tenant_a but route it to tenant_b's domain.
        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-b.imos.cv")

        with patch("apps.contracts.tasks.generate_contract_pdf.delay"):
            response = client.post(
                f"/api/v1/contracts/contracts/{contract_b.id}/activate/",
                format="json",
            )

        assert response.status_code == 403, (
            f"JWT ISOLATION BREACH: tenant_a JWT was accepted by tenant_b's "
            f"activate endpoint. Got {response.status_code}, expected 403. "
            f"IsTenantMember must reject the schema mismatch."
        )

    def test_activate_correct_tenant_unit_status_becomes_contract(
        self, tenant_a, user_tenant_a
    ):
        """
        A tenant_a admin activating their own DRAFT contract must receive 200
        and the linked Unit's status must transition to STATUS_CONTRACT inside
        tenant_a's schema.

        The activate view calls convert_reservation() which is responsible for
        setting unit.status = CONTRACT.  The PDF generation task is mocked to
        avoid Celery/S3 dependencies.
        """
        from apps.inventory.models import Unit

        unit, _, _, contract = _make_active_reservation(tenant_a, user_tenant_a)

        with tenant_context(tenant_a):
            _grant_tenant_admin(user_tenant_a, tenant_a)
            unit_id = unit.id
            contract_id = contract.id

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        with patch("apps.contracts.tasks.generate_contract_pdf.delay") as mock_pdf:
            response = client.post(
                f"/api/v1/contracts/contracts/{contract_id}/activate/",
                format="json",
            )

        assert response.status_code == 200, (
            f"activate rejected a valid DRAFT contract by tenant_a admin. "
            f"Got {response.status_code}: {getattr(response, 'data', '')}"
        )

        # PDF task must have been enqueued (or the bare except swallowed it —
        # we verify the mock was called to confirm the code path was reached).
        mock_pdf.assert_called_once()

        with tenant_context(tenant_a):
            unit_after = Unit.objects.get(id=unit_id)
            assert unit_after.status == Unit.STATUS_CONTRACT, (
                f"Unit {unit_id} status is '{unit_after.status}' after "
                f"contract activation. Expected STATUS_CONTRACT. "
                f"convert_reservation() may not have updated the unit status."
            )


# ---------------------------------------------------------------------------
# Test Class 3 — ORM-level payment isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestPaymentIsolation:
    """
    Direct ORM-level verification that Payment rows created in tenant_a's
    schema are completely invisible when querying from tenant_b, and vice
    versa.

    Payments inherit tenant isolation implicitly through their FK to Contract,
    but we assert it explicitly here because a misconfigured shared-schema
    migration or raw-SQL query could bypass the ORM-level enforcement.
    """

    def test_payment_from_tenant_a_invisible_in_tenant_b(
        self, tenant_a, tenant_b
    ):
        """
        A Payment created inside tenant_a (linked to a tenant_a Contract) must
        not appear when querying Payment from within tenant_b's schema context.

        Failure here = financial payment records leaking across promotoras — a
        severe LGPD / Lei n.o 133/V/2019 violation and commercial breach.
        """
        from apps.contracts.models import Payment

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            contract_a = _make_contract_orm(unit_a, lead_a)
            Payment.objects.create(
                contract=contract_a,
                payment_type=Payment.PAYMENT_DEPOSIT,
                amount_cve=Decimal("500000.00"),
                due_date=timezone.now().date(),
                status=Payment.STATUS_PENDING,
            )
            count_a = Payment.objects.count()

        with tenant_context(tenant_b):
            count_b = Payment.objects.count()

        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} payment(s) from "
            f"tenant_a. Expected 0."
        )
        # Sanity: the row still exists where it was created.
        assert count_a == 1

    def test_payment_registered_in_correct_schema(self, tenant_a, tenant_b):
        """
        A Payment created inside tenant_a persists correctly within that
        schema and remains retrievable by its own id.

        This is a positive control: it verifies that schema isolation does
        not accidentally prevent writes within the correct schema, and that
        a cross-tenant sanity check (zero payments in tenant_b) still holds.
        """
        from apps.contracts.models import Payment

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            contract_a = _make_contract_orm(unit_a, lead_a)
            payment_a = Payment.objects.create(
                contract=contract_a,
                payment_type=Payment.PAYMENT_INSTALLMENT,
                amount_cve=Decimal("250000.00"),
                due_date=timezone.now().date() + timedelta(days=30),
                status=Payment.STATUS_PENDING,
            )
            payment_a_id = payment_a.id

        # Verify the payment resolves within tenant_a.
        with tenant_context(tenant_a):
            assert Payment.objects.filter(id=payment_a_id).exists(), (
                f"Payment {payment_a_id} is not retrievable within tenant_a. "
                f"Schema write may have been routed to the wrong schema."
            )
            assert Payment.objects.count() == 1

        # Verify tenant_b sees nothing.
        with tenant_context(tenant_b):
            assert Payment.objects.filter(id=payment_a_id).count() == 0, (
                f"ISOLATION BREACH: tenant_b can look up Payment {payment_a_id} "
                f"which belongs to tenant_a."
            )
            assert Payment.objects.count() == 0


# ---------------------------------------------------------------------------
# Test Class 4 — HTTP-level cancel action isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestContractCancelIsolation:
    """
    HTTP-level verification that the cancel action on ContractViewSet releases
    the unit only within the correct tenant schema and cannot be triggered
    cross-tenant.

    A successful cross-tenant cancel would allow one promotora to destroy
    another's active sales contracts — a severe commercial and data breach.
    """

    def test_cancel_correct_tenant_releases_unit(
        self, tenant_a, user_tenant_a
    ):
        """
        Cancelling an ACTIVE contract in tenant_a via a valid admin JWT must:
          - return 200 with the updated contract in the response body,
          - set Unit.status = AVAILABLE inside tenant_a's schema.

        This validates the full cancel → unit-release state machine within
        the correct schema boundary.
        """
        from apps.contracts.models import Contract
        from apps.inventory.models import Unit

        # Build an ACTIVE contract (we go through the activate path via ORM
        # to keep this test focused on cancel behaviour, not activate).
        unit, _, _, contract = _make_active_reservation(tenant_a, user_tenant_a)

        with tenant_context(tenant_a):
            _grant_tenant_admin(user_tenant_a, tenant_a)
            # Manually promote to ACTIVE so we can test cancel directly.
            contract.status = Contract.STATUS_ACTIVE
            contract.signed_at = timezone.now()
            contract.save(update_fields=["status", "signed_at", "updated_at"])
            # Reflect the unit state that activate() would set.
            unit.status = Unit.STATUS_CONTRACT
            unit.save(update_fields=["status", "updated_at"])
            contract_id = contract.id
            unit_id = unit.id

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.post(
            f"/api/v1/contracts/contracts/{contract_id}/cancel/",
            format="json",
        )

        assert response.status_code == 200, (
            f"cancel rejected a valid ACTIVE contract by tenant_a admin. "
            f"Got {response.status_code}: {getattr(response, 'data', '')}"
        )
        assert response.data["status"] == Contract.STATUS_CANCELLED, (
            f"Response body status is '{response.data['status']}'. "
            f"Expected 'CANCELLED'."
        )

        with tenant_context(tenant_a):
            unit_after = Unit.objects.get(id=unit_id)
            assert unit_after.status == Unit.STATUS_AVAILABLE, (
                f"UNIT STUCK: Unit {unit_id} status is '{unit_after.status}' "
                f"after contract cancel. Expected AVAILABLE. "
                f"The unit is permanently locked out of the sales pipeline."
            )

    def test_cancel_does_not_affect_other_tenant_contract(
        self, tenant_a, tenant_b, user_tenant_a, user_tenant_b
    ):
        """
        A cancel attempt by tenant_a targeting tenant_b's ACTIVE contract
        must be rejected (403 or 404) and tenant_b's contract must remain
        ACTIVE afterwards.

        We test the own-domain path (404 — UUID invisible in tenant_a's schema)
        since IsTenantMember would already reject a cross-domain JWT with 403
        (covered in TestContractActivateIsolation).

        A 200 here means tenant_a can destroy tenant_b's live contracts —
        a catastrophic cross-tenant mutation that constitutes both a data
        integrity failure and a direct commercial attack vector.
        """
        from apps.contracts.models import Contract

        # Build an ACTIVE contract in tenant_b.
        unit_b, _, _, contract_b = _make_active_reservation(
            tenant_b, user_tenant_b
        )

        with tenant_context(tenant_b):
            contract_b.status = Contract.STATUS_ACTIVE
            contract_b.signed_at = timezone.now()
            contract_b.save(update_fields=["status", "signed_at", "updated_at"])
            from apps.inventory.models import Unit as _Unit
            unit_b.status = _Unit.STATUS_CONTRACT
            unit_b.save(update_fields=["status", "updated_at"])
            contract_b_id = contract_b.id

        # Give tenant_a user admin rights in tenant_a (not in tenant_b).
        with tenant_context(tenant_a):
            _grant_tenant_admin(user_tenant_a, tenant_a)

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.post(
            f"/api/v1/contracts/contracts/{contract_b_id}/cancel/",
            format="json",
        )

        assert response.status_code in (403, 404), (
            f"ISOLATION BREACH: tenant_a user was able to cancel contract "
            f"{contract_b_id} from tenant_b. "
            f"Got {response.status_code}, expected 403 or 404. "
            f"This is a cross-tenant mutation — a critical security failure."
        )

        # Verify the contract was NOT mutated in tenant_b.
        with tenant_context(tenant_b):
            contract_b.refresh_from_db()
            assert contract_b.status == Contract.STATUS_ACTIVE, (
                f"CRITICAL: tenant_a cancel request mutated tenant_b's "
                f"contract {contract_b_id}. "
                f"Status is now '{contract_b.status}', expected ACTIVE."
            )
