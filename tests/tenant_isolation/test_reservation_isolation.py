"""
CRITICAL: UnitReservation Tenant Isolation Tests
=================================================
These tests verify that UnitReservation data is strictly scoped to its
originating tenant schema.  A failure here means one promotora can see,
cancel, or double-book against another promotora's reservations — a
catastrophic data-integrity and commercial breach.

Test coverage
-------------
1. TestReservationTenantIsolation
   ORM-level: reservations created in tenant_a are completely invisible
   inside tenant_b's schema context, and vice versa.

2. TestAntiDoubleBooking
   Concurrency guard: two requests to create-reservation for the same unit
   must result in exactly one 201 and one 400.  Uses both sequential and
   threaded variants.  Verifies that the SELECT FOR UPDATE inside
   services.create_reservation() prevents double-booking.

3. TestReservationCancelRestoresUnit
   Cancel workflow: services.cancel_reservation() must atomically set
   UnitReservation.status = CANCELLED and Unit.status = AVAILABLE.
   Also verifies the freed unit can be reserved again, and that cancelling
   an already-cancelled reservation raises a validation error.

4. TestReservationAPIIsolation
   HTTP-level: a JWT scoped to tenant_a cannot list, retrieve, or cancel
   reservations belonging to tenant_b.

Run:
    pytest tests/tenant_isolation/test_reservation_isolation.py -v

CI gate: This test MUST pass before merge.
"""
import threading
from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import close_old_connections
from django.utils import timezone
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# ---------------------------------------------------------------------------
# Module-level helpers  (mirror the pattern from test_jwt_isolation.py)
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

# Counter used to generate unique slugs within a single test run so that
# Project.slug (unique=True) does not collide when multiple tests in the
# same class call _create_unit_scaffold().
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

    from apps.projects.models import Project, Building, Floor
    from apps.inventory.models import Unit, UnitType

    project = Project.objects.create(
        name=f"Empreendimento Teste {_scaffold_counter}",
        slug=f"empreendimento-{tenant.schema_name}-{_scaffold_counter}",
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


def _make_reservation_orm(unit, lead):
    """
    Create a UnitReservation directly via ORM (no service layer).
    Use this only in isolation-level tests that do NOT test service logic.
    Supplies all required non-nullable fields.
    """
    from apps.crm.models import UnitReservation

    return UnitReservation.objects.create(
        unit=unit,
        lead=lead,
        status=UnitReservation.STATUS_ACTIVE,
        expires_at=_expires_at(),
        deposit_amount_cve=Decimal("100000.00"),
    )


# ---------------------------------------------------------------------------
# Test Class 1 — ORM-level reservation isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestReservationTenantIsolation:
    """
    Direct ORM-level verification that UnitReservation rows created in
    tenant_a's PostgreSQL schema are completely invisible when querying from
    tenant_b, and vice versa.

    These tests validate the schema-per-tenant guarantee at its most
    fundamental level, independent of any HTTP or service layer.
    """

    def test_reservation_from_tenant_a_invisible_in_tenant_b(
        self, tenant_a, tenant_b
    ):
        """
        A UnitReservation created inside tenant_a must not appear when
        querying UnitReservation from within tenant_b's schema context.

        Failure here = one promotora can enumerate another's reservation
        pipeline — a catastrophic data leak.
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            reservation_a = _make_reservation_orm(unit_a, lead_a)
            count_a = UnitReservation.objects.count()

        with tenant_context(tenant_b):
            count_b = UnitReservation.objects.count()
            direct_lookup = UnitReservation.objects.filter(
                id=reservation_a.id
            ).count()

        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} reservation(s) from "
            f"tenant_a. Expected 0."
        )
        assert direct_lookup == 0, (
            f"ISOLATION BREACH: tenant_b can directly look up "
            f"UnitReservation {reservation_a.id} which belongs to tenant_a."
        )
        # Sanity: the row still exists where it was created.
        assert count_a == 1

    def test_reservation_from_tenant_b_invisible_in_tenant_a(
        self, tenant_a, tenant_b
    ):
        """
        Symmetric direction: tenant_b's reservation must not be reachable
        from within tenant_a's schema context (B → A).
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            reservation_b = _make_reservation_orm(unit_b, lead_b)

        with tenant_context(tenant_a):
            count_a = UnitReservation.objects.count()
            direct_lookup = UnitReservation.objects.filter(
                id=reservation_b.id
            ).count()

        assert count_a == 0, (
            f"ISOLATION BREACH: tenant_a sees {count_a} reservation(s) from "
            f"tenant_b. Expected 0."
        )
        assert direct_lookup == 0, (
            f"ISOLATION BREACH: tenant_a can directly look up "
            f"UnitReservation {reservation_b.id} which belongs to tenant_b."
        )

    def test_reservation_counts_are_independent_per_tenant(
        self, tenant_a, tenant_b
    ):
        """
        Creating reservations in both tenants must produce independent counts
        with zero cross-schema contamination in either direction.
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            _make_reservation_orm(unit_a, lead_a)
            count_a = UnitReservation.objects.count()

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            _make_reservation_orm(unit_b, lead_b)
            count_b = UnitReservation.objects.count()

        # Re-read both schemas after both inserts
        with tenant_context(tenant_a):
            assert UnitReservation.objects.count() == count_a == 1, (
                f"ISOLATION BREACH: tenant_a count changed after tenant_b "
                f"insert. Expected 1, got {UnitReservation.objects.count()}."
            )
        with tenant_context(tenant_b):
            assert UnitReservation.objects.count() == count_b == 1, (
                f"ISOLATION BREACH: tenant_b count changed after tenant_a "
                f"insert. Expected 1, got {UnitReservation.objects.count()}."
            )

    def test_bulk_delete_in_tenant_a_does_not_affect_tenant_b(
        self, tenant_a, tenant_b
    ):
        """
        Bulk-deleting all reservations in tenant_a must have zero effect on
        tenant_b's reservation rows.  Catches accidental public-schema or
        cross-schema raw queries.
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            _make_reservation_orm(unit_a, lead_a)

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            _make_reservation_orm(unit_b, lead_b)

        with tenant_context(tenant_a):
            UnitReservation.objects.all().delete()
            assert UnitReservation.objects.count() == 0, (
                "Sanity check: tenant_a should have 0 reservations after delete."
            )

        with tenant_context(tenant_b):
            count_b = UnitReservation.objects.count()

        assert count_b == 1, (
            f"ISOLATION BREACH: bulk delete in tenant_a removed reservations "
            f"from tenant_b. Expected 1, got {count_b}."
        )

    def test_unit_b_id_not_resolvable_via_tenant_a_query(
        self, tenant_a, tenant_b
    ):
        """
        Even if a user from tenant_a constructs a queryset filter using the
        exact UUID of tenant_b's reservation, the result must be empty.
        This mirrors what happens when cross-tenant UUID guessing is attempted.
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            res_b = _make_reservation_orm(unit_b, lead_b)
            known_uuid = res_b.id  # Attacker knows this UUID

        with tenant_context(tenant_a):
            result = UnitReservation.objects.filter(id=known_uuid)
            assert not result.exists(), (
                f"ISOLATION BREACH: filter(id={known_uuid}) inside tenant_a "
                f"schema returned a row that belongs to tenant_b."
            )


# ---------------------------------------------------------------------------
# Test Class 2 — Anti-double-booking (SELECT FOR UPDATE concurrency guard)
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestAntiDoubleBooking:
    """
    Verify that two simultaneous (or back-to-back) calls to
    services.create_reservation() for the same unit result in exactly one
    success and one UnitNotAvailableError / ActiveReservationExistsError.

    At the service layer this is enforced by SELECT FOR UPDATE on the Unit row
    inside an atomic transaction.  A UniqueConstraint on
    UnitReservation(unit, status=ACTIVE) acts as the second safety net.

    Tests here cover:
    - Deterministic sequential path (service layer directly)
    - Deterministic sequential path (via HTTP API)
    - Concurrent threaded path (HTTP API with real threading)
    - DB-level assertion that exactly one ACTIVE row exists after race
    """

    def test_service_sequential_second_call_raises(self, tenant_a, user_tenant_a):
        """
        Calling create_reservation() twice sequentially for the same unit
        must raise UnitNotAvailableError on the second call.

        This is the most direct test of the service-layer business rule.
        """
        from apps.crm.services import create_reservation, UnitNotAvailableError

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)

            # First call must succeed
            reservation = create_reservation(
                unit_id=str(unit.id),
                lead_id=str(lead.id),
                user=user_tenant_a,
                notes="first",
                deposit_cve=Decimal("100000.00"),
            )
            assert reservation.status == "ACTIVE"

            # Second call on the same unit must raise
            with pytest.raises(UnitNotAvailableError):
                create_reservation(
                    unit_id=str(unit.id),
                    lead_id=str(lead.id),
                    user=user_tenant_a,
                    notes="second — must fail",
                    deposit_cve=Decimal("50000.00"),
                )

    def test_service_only_one_active_reservation_after_double_attempt(
        self, tenant_a, user_tenant_a
    ):
        """
        After a successful create_reservation() and a rejected one, the
        database must contain exactly one ACTIVE UnitReservation for that unit.
        """
        from apps.crm.models import UnitReservation
        from apps.crm.services import create_reservation, UnitNotAvailableError

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)

            create_reservation(
                unit_id=str(unit.id),
                lead_id=str(lead.id),
                user=user_tenant_a,
            )
            try:
                create_reservation(
                    unit_id=str(unit.id),
                    lead_id=str(lead.id),
                    user=user_tenant_a,
                )
            except UnitNotAvailableError:
                pass

            active_count = UnitReservation.objects.filter(
                unit=unit,
                status=UnitReservation.STATUS_ACTIVE,
            ).count()

        assert active_count == 1, (
            f"DOUBLE-BOOKING: Expected exactly 1 ACTIVE reservation for unit "
            f"{unit.id}, found {active_count}."
        )

    def test_api_sequential_second_post_returns_400(
        self, tenant_a, user_tenant_a
    ):
        """
        Two sequential POST requests to create-reservation for the same unit
        via the HTTP API must return 201 then 400.

        This is the API-level complement to the service-layer test above.
        """
        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)

        token = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token, "empresa-a.imos.cv")
        payload = {
            "unit_id": str(unit.id),
            "lead_id": str(lead.id),
            "deposit_amount_cve": "100000.00",
            "notes": "sequential test",
        }

        response_1 = client.post(
            "/api/v1/crm/reservations/create-reservation/",
            payload,
            format="json",
        )
        response_2 = client.post(
            "/api/v1/crm/reservations/create-reservation/",
            payload,
            format="json",
        )

        assert response_1.status_code == 201, (
            f"First reservation POST rejected. "
            f"Got {response_1.status_code}: {response_1.data}"
        )
        assert response_2.status_code == 400, (
            f"DOUBLE-BOOKING: Second reservation POST for the same unit was "
            f"accepted. Got {response_2.status_code}. Expected 400. "
            f"Unit {unit.id} is now double-booked."
        )

    def test_api_unit_status_is_reserved_after_successful_booking(
        self, tenant_a, user_tenant_a
    ):
        """
        After a successful create-reservation, Unit.status must transition
        from AVAILABLE to RESERVED.  This is the state-machine invariant that
        the anti-double-booking logic depends on.
        """
        from apps.inventory.models import Unit

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)
            assert unit.status == Unit.STATUS_AVAILABLE

        token = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token, "empresa-a.imos.cv")

        response = client.post(
            "/api/v1/crm/reservations/create-reservation/",
            {
                "unit_id": str(unit.id),
                "lead_id": str(lead.id),
                "deposit_amount_cve": "100000.00",
            },
            format="json",
        )

        assert response.status_code == 201, (
            f"create-reservation rejected valid payload. "
            f"Got {response.status_code}: {response.data}"
        )

        with tenant_context(tenant_a):
            unit.refresh_from_db()
            assert unit.status == Unit.STATUS_RESERVED, (
                f"Unit {unit.id} status not updated after reservation. "
                f"Expected RESERVED, got '{unit.status}'."
            )

    def test_concurrent_threads_only_one_booking_succeeds(
        self, tenant_a, user_tenant_a
    ):
        """
        Two threads fire create-reservation for the same unit at the same time.
        Exactly one must succeed (201) and the other must be rejected (400).

        This validates that the SELECT FOR UPDATE inside create_reservation()
        serialises concurrent requests at the database level.

        Thread results are collected in a thread-safe list and asserted in the
        main thread after both threads complete.
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)

        payload = {
            "unit_id": str(unit.id),
            "lead_id": str(lead.id),
            "deposit_amount_cve": "100000.00",
            "notes": "concurrent test",
        }
        results = []
        lock = threading.Lock()

        def attempt_reservation():
            # Each thread needs a fresh DB connection; close any inherited ones.
            close_old_connections()
            try:
                token = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
                client = _api_client_for_tenant(token, "empresa-a.imos.cv")
                response = client.post(
                    "/api/v1/crm/reservations/create-reservation/",
                    payload,
                    format="json",
                )
                with lock:
                    results.append(response.status_code)
            finally:
                close_old_connections()

        t1 = threading.Thread(target=attempt_reservation)
        t2 = threading.Thread(target=attempt_reservation)

        t1.start()
        t2.start()
        t1.join(timeout=15)
        t2.join(timeout=15)

        assert len(results) == 2, (
            f"Expected 2 thread results, got {len(results)}. "
            f"A thread may have timed out or raised an unhandled exception."
        )

        status_counts = {code: results.count(code) for code in set(results)}

        assert results.count(201) == 1, (
            f"DOUBLE-BOOKING: Expected exactly 1 successful (201) reservation. "
            f"Got status distribution: {status_counts}. "
            f"Unit {unit.id} may be double-booked."
        )
        assert results.count(400) == 1, (
            f"DOUBLE-BOOKING: Expected exactly 1 rejected (400) reservation. "
            f"Got status distribution: {status_counts}."
        )

        with tenant_context(tenant_a):
            active_count = UnitReservation.objects.filter(
                unit=unit,
                status=UnitReservation.STATUS_ACTIVE,
            ).count()

        assert active_count == 1, (
            f"DOUBLE-BOOKING: Database contains {active_count} ACTIVE "
            f"reservations for unit {unit.id} after concurrent attempts. "
            f"Expected exactly 1."
        )


# ---------------------------------------------------------------------------
# Test Class 3 — Cancel reservation restores unit status
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestReservationCancelRestoresUnit:
    """
    Verify that services.cancel_reservation() atomically executes both sides
    of the state-machine transition inside a single transaction:

      UnitReservation.status  →  CANCELLED
      Unit.status             →  AVAILABLE

    If the unit is not restored to AVAILABLE it is permanently locked out of
    the sales pipeline — a direct revenue loss for the promotora.

    Tests call the service layer directly (unit tests) and through the HTTP
    API (integration tests) to cover both paths.
    """

    def test_service_cancel_sets_reservation_cancelled(
        self, tenant_a, user_tenant_a
    ):
        """
        services.cancel_reservation() must set reservation.status = CANCELLED.
        """
        from apps.crm.models import UnitReservation
        from apps.crm.services import cancel_reservation

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)
            reservation = _make_reservation_orm(unit, lead)
            # Reflect the real state the unit would be in
            from apps.inventory.models import Unit
            unit.status = Unit.STATUS_RESERVED
            unit.save(update_fields=["status", "updated_at"])

            cancel_reservation(str(reservation.id), user_tenant_a)

            reservation.refresh_from_db()
            assert reservation.status == UnitReservation.STATUS_CANCELLED, (
                f"Reservation {reservation.id} status is '{reservation.status}' "
                f"after cancel. Expected CANCELLED."
            )

    def test_service_cancel_restores_unit_to_available(
        self, tenant_a, user_tenant_a
    ):
        """
        services.cancel_reservation() must set unit.status = AVAILABLE.

        This is the critical revenue-protecting business rule: a cancelled
        reservation must free the unit back into the sales pipeline.
        """
        from apps.crm.services import cancel_reservation
        from apps.inventory.models import Unit

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)
            reservation = _make_reservation_orm(unit, lead)
            unit.status = Unit.STATUS_RESERVED
            unit.save(update_fields=["status", "updated_at"])
            unit_id = unit.id

            cancel_reservation(str(reservation.id), user_tenant_a)

            unit = Unit.objects.get(id=unit_id)
            assert unit.status == Unit.STATUS_AVAILABLE, (
                f"UNIT STUCK: Unit {unit_id} status is '{unit.status}' after "
                f"cancel_reservation(). Expected AVAILABLE. "
                f"The unit is permanently locked out of the sales pipeline."
            )

    def test_service_cancel_non_active_reservation_raises(
        self, tenant_a, user_tenant_a
    ):
        """
        Attempting to cancel an already-CANCELLED reservation via the service
        must raise a ValidationError.

        This prevents double-cancel races from triggering spurious unit-status
        flips (AVAILABLE → AVAILABLE is harmless, but two concurrent cancels
        could flip a unit that was already re-reserved back to AVAILABLE).
        """
        from apps.crm.models import UnitReservation
        from apps.crm.services import cancel_reservation
        from rest_framework.exceptions import ValidationError

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)
            reservation = UnitReservation.objects.create(
                unit=unit,
                lead=lead,
                status=UnitReservation.STATUS_CANCELLED,
                expires_at=_expires_at(),
                deposit_amount_cve=Decimal("0.00"),
            )

            with pytest.raises(ValidationError):
                cancel_reservation(str(reservation.id), user_tenant_a)

    def test_api_cancel_returns_200_and_updates_statuses(
        self, tenant_a, user_tenant_a
    ):
        """
        POST /api/v1/crm/reservations/{id}/cancel/ for an ACTIVE reservation
        must return 200 and the response must reflect the CANCELLED status.
        Unit.status must be AVAILABLE in the DB afterwards.
        """
        from apps.crm.models import UnitReservation
        from apps.inventory.models import Unit

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)
            reservation = _make_reservation_orm(unit, lead)
            unit.status = Unit.STATUS_RESERVED
            unit.save(update_fields=["status", "updated_at"])
            reservation_id = reservation.id
            unit_id = unit.id

        token = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token, "empresa-a.imos.cv")

        response = client.post(
            f"/api/v1/crm/reservations/{reservation_id}/cancel/",
            format="json",
        )

        assert response.status_code == 200, (
            f"Cancel endpoint rejected valid request. "
            f"Got {response.status_code}: {getattr(response, 'data', '')}"
        )
        assert response.data["status"] == UnitReservation.STATUS_CANCELLED, (
            f"Response body status is '{response.data['status']}'. "
            f"Expected 'CANCELLED'."
        )

        with tenant_context(tenant_a):
            unit = Unit.objects.get(id=unit_id)
            assert unit.status == Unit.STATUS_AVAILABLE, (
                f"UNIT STUCK: Unit {unit_id} is '{unit.status}' after API "
                f"cancel. Expected AVAILABLE."
            )

    def test_api_cancel_already_cancelled_returns_400(
        self, tenant_a, user_tenant_a
    ):
        """
        POST cancel/ on a CANCELLED reservation must return 400 — not 200.
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead = _create_lead(tenant_a)
            reservation = UnitReservation.objects.create(
                unit=unit,
                lead=lead,
                status=UnitReservation.STATUS_CANCELLED,
                expires_at=_expires_at(),
                deposit_amount_cve=Decimal("0.00"),
            )
            reservation_id = reservation.id

        token = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token, "empresa-a.imos.cv")

        response = client.post(
            f"/api/v1/crm/reservations/{reservation_id}/cancel/",
            format="json",
        )

        assert response.status_code == 400, (
            f"Double-cancel was accepted. Got {response.status_code}, "
            f"expected 400. This can cause spurious unit-status flips."
        )

    def test_cancelled_unit_can_be_reserved_again(
        self, tenant_a, user_tenant_a
    ):
        """
        After cancel_reservation(), the same unit must be reservable by a
        different lead via create_reservation().  This is the end-to-end proof
        that the unit was genuinely freed back into the pipeline.
        """
        from apps.crm.models import UnitReservation
        from apps.crm.services import cancel_reservation, create_reservation
        from apps.inventory.models import Unit

        with tenant_context(tenant_a):
            unit = _create_unit_scaffold(tenant_a)
            lead_1 = _create_lead(tenant_a)
            lead_2 = _create_lead(tenant_a)

            # Create and then cancel a reservation for lead_1
            res_1 = create_reservation(
                unit_id=str(unit.id),
                lead_id=str(lead_1.id),
                user=user_tenant_a,
                deposit_cve=Decimal("100000.00"),
            )
            assert res_1.status == UnitReservation.STATUS_ACTIVE

            cancel_reservation(str(res_1.id), user_tenant_a)

            # The unit must now be available again
            unit.refresh_from_db()
            assert unit.status == Unit.STATUS_AVAILABLE, (
                f"Unit {unit.id} not restored to AVAILABLE after cancel. "
                f"Cannot re-reserve."
            )

            # Re-reserve for lead_2 — must succeed
            res_2 = create_reservation(
                unit_id=str(unit.id),
                lead_id=str(lead_2.id),
                user=user_tenant_a,
                deposit_cve=Decimal("120000.00"),
            )
            assert res_2.status == UnitReservation.STATUS_ACTIVE, (
                f"Unit {unit.id} could not be re-reserved after cancel. "
                f"The cancel workflow did not properly free the unit."
            )


# ---------------------------------------------------------------------------
# Test Class 4 — HTTP-level API isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestReservationAPIIsolation:
    """
    HTTP-level verification that a JWT scoped to tenant_a cannot list,
    retrieve, or cancel reservations belonging to tenant_b.

    ImoOSTenantMiddleware sets the active DB schema from the Host header.
    IsTenantMember then compares the JWT's ``tenant_schema`` claim against
    the active schema.  Any mismatch must yield 403.

    Within the correct tenant, the queryset filter (schema isolation) ensures
    that cross-tenant UUID lookups return 404, not 200.

    Expected HTTP codes:
      Cross-tenant JWT to wrong domain  →  403
      Same-domain UUID of other tenant  →  404
      Cancel other tenant's reservation →  403 or 404
      Unauthenticated request           →  401
      Correct credentials, own data     →  200 / 201
    """

    def test_tenant_a_jwt_on_tenant_b_reservations_list_returns_403(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        GET /api/v1/crm/reservations/ with tenant_a JWT routed to tenant_b
        domain must return 403.  IsTenantMember detects the schema mismatch.
        """
        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            _make_reservation_orm(unit_b, lead_b)

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-b.imos.cv")

        response = client.get("/api/v1/crm/reservations/")

        assert response.status_code == 403, (
            f"JWT ISOLATION BREACH: tenant_a JWT accepted by tenant_b "
            f"reservations list. Got {response.status_code}, expected 403."
        )

    def test_tenant_b_jwt_on_tenant_a_reservations_list_returns_403(
        self, tenant_a, tenant_b, user_tenant_b
    ):
        """
        Symmetric direction: tenant_b JWT routed to tenant_a domain must
        return 403 on the reservations list endpoint.
        """
        token_b = _make_jwt_for_user(user_tenant_b, tenant_b.schema_name)
        client = _api_client_for_tenant(token_b, "empresa-a.imos.cv")

        response = client.get("/api/v1/crm/reservations/")

        assert response.status_code == 403, (
            f"JWT ISOLATION BREACH: tenant_b JWT accepted by tenant_a "
            f"reservations list. Got {response.status_code}, expected 403."
        )

    def test_tenant_a_direct_uuid_lookup_of_tenant_b_reservation_returns_404(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        A user from tenant_a who knows the UUID of tenant_b's reservation
        and queries their own domain must receive 404 — the row does not
        exist in tenant_a's PostgreSQL schema.

        404 (not forbidden) is the correct response because schema isolation
        makes the row invisible, not access-controlled.
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            res_b = _make_reservation_orm(unit_b, lead_b)
            res_b_id = res_b.id

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.get(f"/api/v1/crm/reservations/{res_b_id}/")

        assert response.status_code == 404, (
            f"ISOLATION BREACH: tenant_a user can retrieve reservation "
            f"{res_b_id} from tenant_b via direct UUID lookup. "
            f"Got {response.status_code}, expected 404."
        )

    def test_tenant_a_cannot_cancel_tenant_b_reservation(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        POST /api/v1/crm/reservations/{id}/cancel/ with tenant_a credentials
        targeting tenant_b's reservation must be rejected (403 or 404).

        A 200 here means tenant_a can destroy tenant_b's commercial pipeline
        — a severe multi-tenant security breach with direct business impact.

        After the request, tenant_b's reservation must still be ACTIVE.
        """
        from apps.crm.models import UnitReservation
        from apps.inventory.models import Unit

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            res_b = _make_reservation_orm(unit_b, lead_b)
            unit_b.status = Unit.STATUS_RESERVED
            unit_b.save(update_fields=["status", "updated_at"])
            res_b_id = res_b.id

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.post(
            f"/api/v1/crm/reservations/{res_b_id}/cancel/",
            format="json",
        )

        assert response.status_code in (403, 404), (
            f"ISOLATION BREACH: tenant_a user was able to cancel reservation "
            f"{res_b_id} from tenant_b. "
            f"Got {response.status_code}, expected 403 or 404."
        )

        # Verify the reservation was NOT mutated
        with tenant_context(tenant_b):
            res_b.refresh_from_db()
            assert res_b.status == UnitReservation.STATUS_ACTIVE, (
                f"CRITICAL: tenant_a cancel request mutated tenant_b's "
                f"reservation {res_b_id}. Status is now '{res_b.status}', "
                f"expected ACTIVE."
            )

    def test_reservations_list_excludes_other_tenant_ids_from_response_body(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        GET /api/v1/crm/reservations/ for an authenticated tenant_a user must
        not contain any UUID that belongs to tenant_b.

        This is a defence-in-depth serialiser-level check: even if the
        queryset filter were bypassed, the response body must not leak
        cross-tenant identifiers.
        """
        from apps.crm.models import UnitReservation

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            lead_b = _create_lead(tenant_b)
            res_b = _make_reservation_orm(unit_b, lead_b)
        tenant_b_uuid = str(res_b.id)

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            _make_reservation_orm(unit_a, lead_a)

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.get("/api/v1/crm/reservations/")

        assert response.status_code == 200, (
            f"Reservations list rejected valid tenant_a request. "
            f"Got {response.status_code}."
        )
        response_text = str(response.data)
        assert tenant_b_uuid not in response_text, (
            f"ISOLATION BREACH: tenant_a reservations list response contains "
            f"UUID {tenant_b_uuid} that belongs to tenant_b."
        )

    def test_unauthenticated_reservations_list_returns_401(self, tenant_a):
        """
        An unauthenticated GET to the reservations list must return 401.

        Positive control: distinguishes missing credentials (401) from
        wrong-tenant credentials (403).  If this returns 200 the endpoint
        is missing authentication entirely.
        """
        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get("/api/v1/crm/reservations/")

        assert response.status_code == 401, (
            f"Unauthenticated request returned {response.status_code}, "
            f"expected 401."
        )

    def test_correct_tenant_user_can_list_own_reservations(
        self, tenant_a, user_tenant_a
    ):
        """
        Positive control: a correctly scoped JWT must be able to list its own
        tenant's reservations and receive 200.

        If this fails, IsTenantMember or the JWT configuration is broken.
        """
        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            lead_a = _create_lead(tenant_a)
            _make_reservation_orm(unit_a, lead_a)

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.get("/api/v1/crm/reservations/")

        assert response.status_code == 200, (
            f"Correctly scoped JWT was rejected on own domain. "
            f"Got {response.status_code}, expected 200. "
            f"This indicates IsTenantMember or JWT config is broken."
        )
        results = response.data.get("results", response.data)
        assert len(results) >= 1, (
            "Reservations list returned 0 results even though tenant_a has 1 "
            "reservation. The queryset filter may be too aggressive."
        )
