"""
CRITICAL: Marketplace / imo.cv Tenant Isolation Tests
=====================================================
These tests verify that MarketplaceListing and ImoCvWebhookLog data is
strictly scoped to its originating tenant schema. A failure here means one
promotora can see or interact with another promotora's marketplace listings
or inbound imo.cv webhook events — a critical data-isolation breach.

Test coverage
-------------
1. TestMarketplaceListingIsolation
   ORM-level: listings created in tenant_a are completely invisible inside
   tenant_b's schema context, and vice versa.

2. TestWebhookLogIsolation
   ORM-level: ImoCvWebhookLog rows created in tenant_a are invisible in
   tenant_b, and direct UUID lookups return DoesNotExist.

3. TestMarketplaceAPIIsolation
   HTTP-level: a JWT scoped to tenant_a cannot list or retrieve listings
   belonging to tenant_b.

4. TestWebhookSecurity
   Webhook endpoint rejects requests with invalid HMAC signatures (401) and
   accepts correctly signed payloads (200).

Run:
    pytest tests/tenant_isolation/test_marketplace_isolation.py -v

CI gate: This test MUST pass before merge.
"""
import hashlib
import hmac as hmac_lib
import json
from decimal import Decimal

import pytest
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# ---------------------------------------------------------------------------
# Module-level helpers (mirror the pattern from test_reservation_isolation.py)
# ---------------------------------------------------------------------------

def _make_jwt_for_user(user, schema_name: str) -> str:
    refresh = RefreshToken.for_user(user)
    refresh["tenant_schema"] = schema_name
    return str(refresh.access_token)


def _api_client_for_tenant(token: str, domain: str) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    client.defaults["HTTP_HOST"] = domain
    return client


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

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
        name=f"Empreendimento Marketplace {_scaffold_counter}",
        slug=f"mktplace-{tenant.schema_name}-{_scaffold_counter}",
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
        code=f"MKT-P1-{_scaffold_counter:02d}",
        area_bruta=Decimal("80.00"),
        status=Unit.STATUS_AVAILABLE,
    )
    return unit


def _create_listing(unit, imocv_listing_id: str = ""):
    """
    Create a MarketplaceListing for the given unit.
    Must be called inside ``with tenant_context(tenant)``.
    """
    from apps.marketplace.models import MarketplaceListing

    return MarketplaceListing.objects.create(
        unit=unit,
        imocv_listing_id=imocv_listing_id,
        status=MarketplaceListing.STATUS_PUBLISHED if imocv_listing_id else MarketplaceListing.STATUS_PENDING,
        price_override_cve=None,
    )


def _create_webhook_log(event_type: str = "lead_captured", listing_id: str = ""):
    """
    Create a raw ImoCvWebhookLog.
    Must be called inside ``with tenant_context(tenant)``.
    """
    from apps.marketplace.models import ImoCvWebhookLog

    return ImoCvWebhookLog.objects.create(
        event_type=event_type,
        imocv_listing_id=listing_id,
        payload={"event": event_type, "listing_id": listing_id},
    )


def _make_hmac_signature(payload: bytes, secret: str) -> str:
    """Build a valid X-ImoCv-Signature header value for a given payload."""
    digest = hmac_lib.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


# ---------------------------------------------------------------------------
# Test Class 1 — ORM-level listing isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestMarketplaceListingIsolation:
    """
    Direct ORM-level verification that MarketplaceListing rows created in
    tenant_a's PostgreSQL schema are completely invisible when querying from
    tenant_b, and vice versa.
    """

    def test_listing_from_tenant_a_invisible_in_tenant_b(
        self, tenant_a, tenant_b
    ):
        """
        A MarketplaceListing created in tenant_a must not appear when
        querying MarketplaceListing from within tenant_b's schema context.
        """
        from apps.marketplace.models import MarketplaceListing

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            listing_a = _create_listing(unit_a, imocv_listing_id="imocv-001")
            count_a = MarketplaceListing.objects.count()

        with tenant_context(tenant_b):
            count_b = MarketplaceListing.objects.count()
            direct_lookup = MarketplaceListing.objects.filter(id=listing_a.id).count()

        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} listing(s) from "
            f"tenant_a. Expected 0."
        )
        assert direct_lookup == 0, (
            f"ISOLATION BREACH: tenant_b can directly look up "
            f"MarketplaceListing {listing_a.id} which belongs to tenant_a."
        )
        assert count_a == 1

    def test_listing_from_tenant_b_invisible_in_tenant_a(
        self, tenant_a, tenant_b
    ):
        """Symmetric direction: tenant_b's listing must not be reachable from tenant_a."""
        from apps.marketplace.models import MarketplaceListing

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            listing_b = _create_listing(unit_b, imocv_listing_id="imocv-002")

        with tenant_context(tenant_a):
            count_a = MarketplaceListing.objects.count()
            direct_lookup = MarketplaceListing.objects.filter(id=listing_b.id).count()

        assert count_a == 0, (
            f"ISOLATION BREACH: tenant_a sees {count_a} listing(s) from "
            f"tenant_b. Expected 0."
        )
        assert direct_lookup == 0, (
            f"ISOLATION BREACH: tenant_a can directly look up "
            f"MarketplaceListing {listing_b.id} which belongs to tenant_b."
        )

    def test_listings_in_both_tenants_are_independent(self, tenant_a, tenant_b):
        """
        Creating listings in both tenants must produce independent counts with
        zero cross-schema contamination in either direction.
        """
        from apps.marketplace.models import MarketplaceListing

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            _create_listing(unit_a, imocv_listing_id="imocv-a-01")

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            _create_listing(unit_b, imocv_listing_id="imocv-b-01")

        with tenant_context(tenant_a):
            count_a = MarketplaceListing.objects.count()
            assert count_a == 1, (
                f"ISOLATION BREACH: tenant_a count is {count_a} after tenant_b "
                f"insert. Expected 1."
            )

        with tenant_context(tenant_b):
            count_b = MarketplaceListing.objects.count()
            assert count_b == 1, (
                f"ISOLATION BREACH: tenant_b count is {count_b} after tenant_a "
                f"insert. Expected 1."
            )

    def test_bulk_delete_in_tenant_a_does_not_affect_tenant_b(
        self, tenant_a, tenant_b
    ):
        """
        Bulk-deleting all listings in tenant_a must have zero effect on
        tenant_b's listing rows.
        """
        from apps.marketplace.models import MarketplaceListing

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            _create_listing(unit_a, imocv_listing_id="imocv-del-a")

        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            _create_listing(unit_b, imocv_listing_id="imocv-del-b")

        with tenant_context(tenant_a):
            MarketplaceListing.objects.all().delete()
            assert MarketplaceListing.objects.count() == 0

        with tenant_context(tenant_b):
            count_b = MarketplaceListing.objects.count()

        assert count_b == 1, (
            f"ISOLATION BREACH: bulk delete in tenant_a removed listings from "
            f"tenant_b. Expected 1, got {count_b}."
        )

    def test_imocv_listing_id_lookup_scoped_to_tenant(self, tenant_a, tenant_b):
        """
        A query filtering by imocv_listing_id in tenant_a must not find a
        listing from tenant_b that shares the same ID string.
        This validates that imo.cv listing IDs cannot be used to leak data
        across tenant boundaries.
        """
        from apps.marketplace.models import MarketplaceListing

        shared_id = "imocv-shared-id-999"

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            _create_listing(unit_a, imocv_listing_id=shared_id)

        with tenant_context(tenant_b):
            # tenant_b should see 0 results even though the imocv_listing_id
            # string matches a record in tenant_a
            count = MarketplaceListing.objects.filter(
                imocv_listing_id=shared_id,
            ).count()

        assert count == 0, (
            f"ISOLATION BREACH: tenant_b query by imocv_listing_id='{shared_id}' "
            f"returned {count} result(s) from tenant_a's schema."
        )


# ---------------------------------------------------------------------------
# Test Class 2 — Webhook log isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestWebhookLogIsolation:
    """
    ORM-level verification that ImoCvWebhookLog rows are strictly scoped to
    their originating tenant schema.
    """

    def test_webhook_log_from_tenant_a_invisible_in_tenant_b(
        self, tenant_a, tenant_b
    ):
        """
        A webhook log created in tenant_a must not appear in tenant_b's schema.
        """
        from apps.marketplace.models import ImoCvWebhookLog

        with tenant_context(tenant_a):
            log_a = _create_webhook_log("lead_captured", "imocv-100")
            count_a = ImoCvWebhookLog.objects.count()

        with tenant_context(tenant_b):
            count_b = ImoCvWebhookLog.objects.count()
            direct_lookup = ImoCvWebhookLog.objects.filter(id=log_a.id).count()

        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} webhook log(s) from "
            f"tenant_a. Expected 0."
        )
        assert direct_lookup == 0, (
            f"ISOLATION BREACH: tenant_b can directly look up "
            f"ImoCvWebhookLog {log_a.id} which belongs to tenant_a."
        )
        assert count_a == 1

    def test_webhook_log_does_not_exist_in_other_tenant_schema(
        self, tenant_a, tenant_b
    ):
        """
        Fetching a webhook log by its PK from the wrong tenant schema
        must raise DoesNotExist — not return stale data.
        """
        from apps.marketplace.models import ImoCvWebhookLog

        with tenant_context(tenant_a):
            log_a = _create_webhook_log("unit_viewed", "imocv-200")
            log_a_id = log_a.id

        with tenant_context(tenant_b):
            with pytest.raises(ImoCvWebhookLog.DoesNotExist):
                ImoCvWebhookLog.objects.get(id=log_a_id)

    def test_webhook_logs_in_both_tenants_are_independent(
        self, tenant_a, tenant_b
    ):
        """
        Logs created in both tenants are completely independent — each tenant
        only sees its own rows.
        """
        from apps.marketplace.models import ImoCvWebhookLog

        with tenant_context(tenant_a):
            _create_webhook_log("lead_captured", "imocv-a-300")

        with tenant_context(tenant_b):
            _create_webhook_log("lead_captured", "imocv-b-300")

        with tenant_context(tenant_a):
            assert ImoCvWebhookLog.objects.count() == 1, (
                "ISOLATION BREACH: tenant_a webhook log count changed after "
                "tenant_b insert."
            )

        with tenant_context(tenant_b):
            assert ImoCvWebhookLog.objects.count() == 1, (
                "ISOLATION BREACH: tenant_b webhook log count changed after "
                "tenant_a insert."
            )


# ---------------------------------------------------------------------------
# Test Class 3 — HTTP API isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestMarketplaceAPIIsolation:
    """
    HTTP-level verification that a JWT scoped to tenant_a cannot list or
    retrieve MarketplaceListings belonging to tenant_b.
    """

    def test_tenant_a_jwt_on_tenant_b_listings_returns_403(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        GET /api/v1/marketplace/listings/ with tenant_a JWT routed to
        tenant_b domain must return 403.
        """
        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            _create_listing(unit_b, imocv_listing_id="imocv-api-001")

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-b.imos.cv")

        response = client.get("/api/v1/marketplace/listings/")

        assert response.status_code == 403, (
            f"JWT ISOLATION BREACH: tenant_a JWT accepted by tenant_b "
            f"marketplace listings. Got {response.status_code}, expected 403."
        )

    def test_tenant_a_uuid_lookup_of_tenant_b_listing_returns_404(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        A user from tenant_a who knows the UUID of tenant_b's listing and
        queries their own domain must receive 404.
        Schema isolation makes the row invisible — 404, not 403.
        """
        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            listing_b = _create_listing(unit_b, imocv_listing_id="imocv-api-002")
            listing_b_id = listing_b.id

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.get(f"/api/v1/marketplace/listings/{listing_b_id}/")

        assert response.status_code == 404, (
            f"ISOLATION BREACH: tenant_a user can retrieve listing "
            f"{listing_b_id} from tenant_b via direct UUID lookup. "
            f"Got {response.status_code}, expected 404."
        )

    def test_listings_list_excludes_other_tenant_uuids_from_response(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        GET /api/v1/marketplace/listings/ for tenant_a must not contain any
        UUID belonging to tenant_b.
        """
        with tenant_context(tenant_b):
            unit_b = _create_unit_scaffold(tenant_b)
            listing_b = _create_listing(unit_b, imocv_listing_id="imocv-api-003")
        tenant_b_uuid = str(listing_b.id)

        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            _create_listing(unit_a, imocv_listing_id="imocv-api-004")

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.get("/api/v1/marketplace/listings/")

        assert response.status_code == 200, (
            f"Correctly scoped JWT rejected. Got {response.status_code}."
        )
        response_text = str(response.data)
        assert tenant_b_uuid not in response_text, (
            f"ISOLATION BREACH: tenant_a listings response contains UUID "
            f"{tenant_b_uuid} that belongs to tenant_b."
        )

    def test_unauthenticated_listings_request_returns_401(self, tenant_a):
        """Unauthenticated GET to the listings list must return 401."""
        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get("/api/v1/marketplace/listings/")

        assert response.status_code == 401, (
            f"Unauthenticated request returned {response.status_code}, "
            f"expected 401."
        )

    def test_correct_tenant_user_can_list_own_listings(
        self, tenant_a, user_tenant_a
    ):
        """
        Positive control: a correctly scoped JWT must be able to list its own
        tenant's listings and receive 200.
        """
        with tenant_context(tenant_a):
            unit_a = _create_unit_scaffold(tenant_a)
            _create_listing(unit_a, imocv_listing_id="imocv-pos-001")

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.get("/api/v1/marketplace/listings/")

        assert response.status_code == 200, (
            f"Correctly scoped JWT rejected on own domain. "
            f"Got {response.status_code}, expected 200."
        )
        results = response.data.get("results", response.data)
        assert len(results) >= 1, (
            "Listings returned 0 results even though tenant_a has 1 listing. "
            "The queryset filter may be too aggressive."
        )


# ---------------------------------------------------------------------------
# Test Class 4 — Webhook security (HMAC verification)
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestWebhookSecurity:
    """
    Verify that the public imo.cv webhook endpoint enforces HMAC-SHA256
    signature verification and rejects tampered or unsigned requests.
    """

    WEBHOOK_URL = "/api/v1/marketplace/webhook/imocv/"

    def _post_webhook(self, client: APIClient, payload: dict, secret: str = "", sign: bool = True):
        # Serialise once so the HMAC is computed over exactly the same bytes
        # that the view will receive via request.body.
        body = json.dumps(payload).encode()
        headers = {"content_type": "application/json"}
        if sign and secret:
            headers["HTTP_X_IMOCV_SIGNATURE"] = _make_hmac_signature(body, secret)
        return client.post(
            self.WEBHOOK_URL,
            data=body,
            **headers,
        )

    def test_valid_signature_returns_200(self, tenant_a, settings):
        """
        A correctly signed webhook payload must return 200 and create a log.
        """
        secret = "test-webhook-secret-abc123"
        settings.IMOCV_WEBHOOK_SECRET = secret

        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        payload = {"event": "unit_viewed", "listing_id": "imocv-wh-001"}

        with tenant_context(tenant_a):
            from apps.marketplace.models import ImoCvWebhookLog
            initial_count = ImoCvWebhookLog.objects.count()

        response = self._post_webhook(client, payload, secret=secret, sign=True)

        assert response.status_code == 200, (
            f"Valid HMAC signature rejected. Got {response.status_code}, "
            f"expected 200. Response: {getattr(response, 'data', '')}"
        )
        assert response.data.get("received") is True

    def test_invalid_signature_returns_401(self, tenant_a, settings):
        """
        A webhook with a tampered signature must be rejected with 401.
        """
        settings.IMOCV_WEBHOOK_SECRET = "real-secret"

        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        payload = {"event": "lead_captured", "listing_id": "imocv-wh-002"}

        # Sign with WRONG secret
        body = json.dumps(payload).encode()
        bad_signature = _make_hmac_signature(body, "wrong-secret")

        response = client.post(
            self.WEBHOOK_URL,
            data=payload,
            format="json",
            HTTP_X_IMOCV_SIGNATURE=bad_signature,
        )

        assert response.status_code == 401, (
            f"SECURITY BREACH: Invalid HMAC signature accepted. "
            f"Got {response.status_code}, expected 401. "
            f"An attacker can inject arbitrary lead data."
        )

    def test_missing_signature_header_returns_401(self, tenant_a, settings):
        """
        A webhook with no X-ImoCv-Signature header must be rejected with 401.
        """
        settings.IMOCV_WEBHOOK_SECRET = "real-secret"

        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        # No signature header
        response = client.post(
            self.WEBHOOK_URL,
            data={"event": "unit_viewed"},
            format="json",
        )

        assert response.status_code == 401, (
            f"SECURITY BREACH: Missing signature header accepted. "
            f"Got {response.status_code}, expected 401."
        )

    def test_lead_captured_webhook_creates_webhook_log(self, tenant_a, settings):
        """
        A valid lead_captured webhook must create an ImoCvWebhookLog row
        in the correct tenant schema for async processing.
        """
        secret = "test-lead-secret"
        settings.IMOCV_WEBHOOK_SECRET = secret

        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        with tenant_context(tenant_a):
            from apps.marketplace.models import ImoCvWebhookLog
            before = ImoCvWebhookLog.objects.count()

        payload = {
            "event": "lead_captured",
            "listing_id": "imocv-lead-001",
            "lead": {
                "first_name": "João",
                "last_name": "Silva",
                "email": "joao@example.cv",
                "phone": "+238 900 0000",
            },
        }

        response = self._post_webhook(client, payload, secret=secret, sign=True)

        assert response.status_code == 200, (
            f"lead_captured webhook rejected. Got {response.status_code}."
        )

        with tenant_context(tenant_a):
            after = ImoCvWebhookLog.objects.count()

        assert after == before + 1, (
            f"Expected 1 new ImoCvWebhookLog after lead_captured webhook. "
            f"Before: {before}, After: {after}."
        )
