"""
CRITICAL: JWT Tenant Isolation Tests
=====================================
These tests verify that JWT tokens are strictly scoped to the tenant schema
they were issued for. A failure here means authentication credentials from
Tenant A can be used to access Tenant B's data — a catastrophic security breach.

Test coverage:
  1. JWT issued for tenant_a is rejected when presented to tenant_b endpoints
  2. LeadCaptureView (public, AllowAny) creates leads in the correct schema
  3. Lead data from tenant_a is completely invisible when querying from tenant_b

Run: pytest tests/tenant_isolation/test_jwt_isolation.py -v

CI gate: This test MUST pass before merge.
"""
import pytest
from django.db import connection
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_jwt_for_user(user, schema_name: str) -> str:
    """
    Mint a JWT access token that carries a ``tenant_schema`` claim matching
    the given schema.  This mirrors the token produced by
    CustomTokenObtainPairSerializer in production.
    """
    refresh = RefreshToken.for_user(user)
    refresh["tenant_schema"] = schema_name
    return str(refresh.access_token)


def _api_client_for_tenant(token: str, domain: str) -> APIClient:
    """
    Return an APIClient pre-configured with a Bearer token and the correct
    Host header so that ImoOSTenantMiddleware resolves the right schema.
    """
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    client.defaults["HTTP_HOST"] = domain
    return client


# ---------------------------------------------------------------------------
# Test Class 1 — JWT cross-tenant rejection
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestJWTCrossTenantRejection:
    """
    A JWT token carries a ``tenant_schema`` claim that encodes the schema the
    user belongs to.  IsTenantMember compares that claim against the active
    ``connection.schema_name`` set by the tenant middleware.  Any mismatch
    must result in a 403 Forbidden — never a 200.
    """

    def test_tenant_a_jwt_rejected_on_tenant_b_leads_list(
        self, tenant_a, tenant_b, user_tenant_a, user_tenant_b
    ):
        """
        Token minted for tenant_a schema presented to tenant_b domain must
        return 403, not 200 or 401.

        A 200 here would mean IsTenantMember is not enforcing the schema claim,
        allowing full cross-tenant data access.
        """
        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        # Deliberately route to tenant_b's domain with tenant_a's token
        client = _api_client_for_tenant(token_a, "empresa-b.imos.cv")

        response = client.get("/api/crm/leads/")

        assert response.status_code == 403, (
            f"JWT ISOLATION BREACH: tenant_a JWT accepted by tenant_b endpoint. "
            f"Got {response.status_code}, expected 403. "
            f"Token schema='{tenant_a.schema_name}', "
            f"Active schema='{tenant_b.schema_name}'."
        )

    def test_tenant_b_jwt_rejected_on_tenant_a_leads_list(
        self, tenant_a, tenant_b, user_tenant_a, user_tenant_b
    ):
        """
        Symmetric test: token minted for tenant_b rejected on tenant_a endpoint.
        Both directions must be tested — A→B and B→A.
        """
        token_b = _make_jwt_for_user(user_tenant_b, tenant_b.schema_name)
        # Route to tenant_a's domain with tenant_b's token
        client = _api_client_for_tenant(token_b, "empresa-a.imos.cv")

        response = client.get("/api/crm/leads/")

        assert response.status_code == 403, (
            f"JWT ISOLATION BREACH: tenant_b JWT accepted by tenant_a endpoint. "
            f"Got {response.status_code}, expected 403. "
            f"Token schema='{tenant_b.schema_name}', "
            f"Active schema='{tenant_a.schema_name}'."
        )

    def test_tenant_a_jwt_rejected_on_tenant_b_pipeline_action(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        The ``/api/crm/leads/pipeline/`` custom action also uses IsTenantMember.
        Cross-tenant tokens must be rejected there too, not just the list view.
        """
        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-b.imos.cv")

        response = client.get("/api/crm/leads/pipeline/")

        assert response.status_code == 403, (
            f"JWT ISOLATION BREACH: tenant_a JWT accepted by tenant_b pipeline action. "
            f"Got {response.status_code}, expected 403."
        )

    def test_tenant_a_jwt_rejected_on_tenant_b_interactions(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        The ``/api/crm/interactions/`` endpoint is protected by IsTenantMember.
        Cross-schema tokens must be rejected.
        """
        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-b.imos.cv")

        response = client.get("/api/crm/interactions/")

        assert response.status_code == 403, (
            f"JWT ISOLATION BREACH: tenant_a JWT accepted by tenant_b interactions endpoint. "
            f"Got {response.status_code}, expected 403."
        )

    def test_valid_tenant_jwt_accepted_on_own_domain(
        self, tenant_a, user_tenant_a
    ):
        """
        Positive control: a correctly scoped JWT must succeed on its own domain.
        If this fails the IsTenantMember implementation is broken, not just the
        isolation guard.
        """
        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client.get("/api/crm/leads/")

        assert response.status_code == 200, (
            f"Correctly scoped JWT was rejected on own domain. "
            f"Got {response.status_code}, expected 200. "
            f"This indicates IsTenantMember is misconfigured."
        )

    def test_no_token_returns_401_not_403(self, tenant_a):
        """
        Unauthenticated requests must return 401, not 403.
        Distinguishing 401 (missing credentials) from 403 (wrong tenant) is
        important for security auditing.
        """
        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get("/api/crm/leads/")

        assert response.status_code == 401, (
            f"Unauthenticated request returned {response.status_code}, expected 401."
        )

    def test_tampered_tenant_schema_claim_rejected(self, tenant_a, tenant_b, user_tenant_a):
        """
        A token where the ``tenant_schema`` claim has been set to tenant_b's
        schema but the signature was issued for user_tenant_a must be rejected
        when routed to tenant_b because the user does not exist in that schema.

        This test verifies that schema claim manipulation cannot bootstrap
        cross-tenant access.
        """
        # Mint a token where claim says tenant_b but signer is user from tenant_a
        refresh = RefreshToken.for_user(user_tenant_a)
        refresh["tenant_schema"] = tenant_b.schema_name  # Tampered claim
        tampered_token = str(refresh.access_token)

        client = _api_client_for_tenant(tampered_token, "empresa-b.imos.cv")
        response = client.get("/api/crm/leads/")

        # The schema claim matches the domain so IsTenantMember passes, but the
        # user does not exist in tenant_b's schema → 401 or 403 are both acceptable.
        assert response.status_code in (401, 403), (
            f"Tampered schema claim was accepted on tenant_b endpoint. "
            f"Got {response.status_code}, expected 401 or 403."
        )


# ---------------------------------------------------------------------------
# Test Class 2 — LeadCaptureView schema correctness
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestLeadCaptureViewSchemaCorrectness:
    """
    LeadCaptureView uses AllowAny so it has no JWT gate.  Isolation is
    enforced purely by the tenant middleware routing the request to the
    correct PostgreSQL schema based on the HTTP Host header.

    A lead submitted to empresa-a.imos.cv must land in the empresa_a schema,
    never in empresa_b.
    """

    _lead_payload = {
        "first_name": "Maria",
        "last_name": "Fonseca",
        "email": "maria.fonseca@example.com",
        "phone": "+238991234567",
        "source": "WEB",
    }

    def test_lead_capture_creates_in_correct_tenant_schema(self, tenant_a, tenant_b):
        """
        POST to tenant_a's lead-capture endpoint creates the lead exclusively
        in tenant_a's schema.  Zero leads must exist in tenant_b afterwards.
        """
        from apps.crm.models import Lead

        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.post("/api/crm/lead-capture/", self._lead_payload, format="json")

        assert response.status_code == 201, (
            f"LeadCaptureView rejected valid payload. "
            f"Got {response.status_code}: {response.data}"
        )

        # Must exist in tenant_a
        with tenant_context(tenant_a):
            count_a = Lead.objects.filter(email=self._lead_payload["email"]).count()

        # Must NOT exist in tenant_b
        with tenant_context(tenant_b):
            count_b = Lead.objects.filter(email=self._lead_payload["email"]).count()

        assert count_a == 1, (
            f"Lead was not created in tenant_a schema. Found {count_a} leads."
        )
        assert count_b == 0, (
            f"ISOLATION BREACH: Lead created via tenant_a endpoint leaked into "
            f"tenant_b schema. Found {count_b} leads."
        )

    def test_lead_capture_on_tenant_b_does_not_appear_in_tenant_a(self, tenant_a, tenant_b):
        """
        POST to tenant_b's lead-capture endpoint must not create any data in
        tenant_a.  Symmetric test of the above.
        """
        from apps.crm.models import Lead

        payload = {**self._lead_payload, "email": "joao.silva@example.com"}

        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-b.imos.cv"

        response = client.post("/api/crm/lead-capture/", payload, format="json")

        assert response.status_code == 201, (
            f"LeadCaptureView on tenant_b rejected valid payload. "
            f"Got {response.status_code}: {response.data}"
        )

        with tenant_context(tenant_b):
            count_b = Lead.objects.filter(email=payload["email"]).count()

        with tenant_context(tenant_a):
            count_a = Lead.objects.filter(email=payload["email"]).count()

        assert count_b == 1, (
            f"Lead was not created in tenant_b schema. Found {count_b} leads."
        )
        assert count_a == 0, (
            f"ISOLATION BREACH: Lead created via tenant_b endpoint leaked into "
            f"tenant_a schema. Found {count_a} leads."
        )

    def test_concurrent_lead_captures_go_to_correct_schemas(self, tenant_a, tenant_b):
        """
        Simulate back-to-back lead captures on different tenant endpoints.
        Each lead must reside exclusively in the schema of its originating
        domain.  This guards against connection schema bleed-through.
        """
        from apps.crm.models import Lead

        client_a = APIClient()
        client_a.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        client_b = APIClient()
        client_b.defaults["HTTP_HOST"] = "empresa-b.imos.cv"

        payload_a = {**self._lead_payload, "email": "lead.a@example.com"}
        payload_b = {**self._lead_payload, "email": "lead.b@example.com"}

        r_a = client_a.post("/api/crm/lead-capture/", payload_a, format="json")
        r_b = client_b.post("/api/crm/lead-capture/", payload_b, format="json")

        assert r_a.status_code == 201
        assert r_b.status_code == 201

        with tenant_context(tenant_a):
            assert Lead.objects.filter(email="lead.a@example.com").exists(), (
                "Lead A missing from tenant_a schema."
            )
            assert not Lead.objects.filter(email="lead.b@example.com").exists(), (
                "ISOLATION BREACH: Lead B (tenant_b) leaked into tenant_a schema."
            )

        with tenant_context(tenant_b):
            assert Lead.objects.filter(email="lead.b@example.com").exists(), (
                "Lead B missing from tenant_b schema."
            )
            assert not Lead.objects.filter(email="lead.a@example.com").exists(), (
                "ISOLATION BREACH: Lead A (tenant_a) leaked into tenant_b schema."
            )

    def test_lead_capture_response_contains_no_cross_tenant_data(self, tenant_a, tenant_b):
        """
        The 201 response body from a lead capture must not include identifiers
        that could be used to enumerate leads from another tenant.  This is a
        defence-in-depth check for information leakage in the serializer.
        """
        from apps.crm.models import Lead

        # Create a lead in tenant_b first
        with tenant_context(tenant_b):
            existing_lead = Lead.objects.create(
                first_name="Pre",
                last_name="Existing",
                email="pre.existing@example.com",
                source="WEB",
            )
        tenant_b_lead_id = str(existing_lead.id)

        # Now capture a lead through tenant_a's endpoint
        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"
        response = client.post(
            "/api/crm/lead-capture/",
            {**self._lead_payload, "email": "new.lead@example.com"},
            format="json",
        )

        assert response.status_code == 201
        response_text = str(response.data)

        assert tenant_b_lead_id not in response_text, (
            f"ISOLATION BREACH: Response from tenant_a lead-capture contains "
            f"an ID belonging to tenant_b: {tenant_b_lead_id}"
        )


# ---------------------------------------------------------------------------
# Test Class 3 — Lead data invisibility across tenants
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
@pytest.mark.isolation
class TestLeadDataIsolation:
    """
    Direct ORM-level isolation verification.  Even without any HTTP layer,
    switching the active schema via tenant_context must ensure that Lead
    querysets are completely segregated between tenants.

    These tests verify the schema-per-tenant PostgreSQL guarantee and catch
    any accidental cross-schema query (e.g. a raw SQL query missing a schema
    prefix, or a misconfigured manager).
    """

    def test_leads_from_tenant_a_invisible_in_tenant_b(self, tenant_a, tenant_b):
        """
        Leads created in tenant_a schema must return zero results when the
        same query runs inside tenant_b context.
        """
        from apps.crm.models import Lead

        with tenant_context(tenant_a):
            lead_a = Lead.objects.create(
                first_name="Ana",
                last_name="Borges",
                email="ana.borges@empresa-a.cv",
                source="WEB",
            )
            count_a_before = Lead.objects.count()

        with tenant_context(tenant_b):
            count_b = Lead.objects.count()

        assert count_b == 0, (
            f"ISOLATION BREACH: tenant_b sees {count_b} lead(s) from tenant_a. "
            f"Expected 0."
        )

        # Confirm the lead still exists in tenant_a (not accidentally deleted)
        with tenant_context(tenant_a):
            assert Lead.objects.filter(id=lead_a.id).exists(), (
                "Lead from tenant_a vanished after tenant_b context switch — "
                "possible schema confusion."
            )

    def test_leads_from_tenant_b_invisible_in_tenant_a(self, tenant_a, tenant_b):
        """
        Symmetric test: leads in tenant_b must not be visible from tenant_a.
        """
        from apps.crm.models import Lead

        with tenant_context(tenant_b):
            lead_b = Lead.objects.create(
                first_name="Bruno",
                last_name="Carvalho",
                email="bruno.carvalho@empresa-b.cv",
                source="REFERRAL",
            )

        with tenant_context(tenant_a):
            count_a = Lead.objects.count()
            direct_lookup = Lead.objects.filter(id=lead_b.id).count()

        assert count_a == 0, (
            f"ISOLATION BREACH: tenant_a sees {count_a} lead(s) from tenant_b."
        )
        assert direct_lookup == 0, (
            f"ISOLATION BREACH: tenant_a can directly look up Lead {lead_b.id} "
            f"which belongs to tenant_b."
        )

    def test_lead_counts_are_independent_per_tenant(self, tenant_a, tenant_b):
        """
        Creating leads in both tenants independently must result in accurate,
        independent counts.  Neither tenant must see the other's records.
        """
        from apps.crm.models import Lead

        with tenant_context(tenant_a):
            Lead.objects.create(
                first_name="Carlos", last_name="Dias",
                email="c.dias@empresa-a.cv", source="WEB",
            )
            Lead.objects.create(
                first_name="Diana", last_name="Évora",
                email="d.evora@empresa-a.cv", source="INSTAGRAM",
            )
            count_a = Lead.objects.count()

        with tenant_context(tenant_b):
            Lead.objects.create(
                first_name="Eduardo", last_name="Ferreira",
                email="e.ferreira@empresa-b.cv", source="FACEBOOK",
            )
            count_b = Lead.objects.count()

        # Verify no cross-tenant contamination
        with tenant_context(tenant_a):
            assert Lead.objects.count() == count_a == 2, (
                f"ISOLATION BREACH: tenant_a count changed after tenant_b insert. "
                f"Expected 2, got {Lead.objects.count()}."
            )

        with tenant_context(tenant_b):
            assert Lead.objects.count() == count_b == 1, (
                f"ISOLATION BREACH: tenant_b count changed after tenant_a inserts. "
                f"Expected 1, got {Lead.objects.count()}."
            )

    def test_delete_in_tenant_a_does_not_affect_tenant_b(self, tenant_a, tenant_b):
        """
        Bulk-deleting all leads in tenant_a must have zero effect on leads in
        tenant_b.  This catches cases where a delete query accidentally targets
        the public schema or uses a raw query without a schema filter.
        """
        from apps.crm.models import Lead

        with tenant_context(tenant_a):
            Lead.objects.create(
                first_name="Fátima", last_name="Gomes",
                email="f.gomes@empresa-a.cv", source="WEB",
            )

        with tenant_context(tenant_b):
            Lead.objects.create(
                first_name="Gonçalo", last_name="Henriques",
                email="g.henriques@empresa-b.cv", source="WEB",
            )

        # Wipe all leads in tenant_a
        with tenant_context(tenant_a):
            Lead.objects.all().delete()
            assert Lead.objects.count() == 0

        # tenant_b must be unaffected
        with tenant_context(tenant_b):
            count_b = Lead.objects.count()

        assert count_b == 1, (
            f"ISOLATION BREACH: bulk delete in tenant_a removed leads from tenant_b. "
            f"Expected 1, got {count_b}."
        )

    def test_api_lead_list_only_returns_own_tenant_leads(
        self, tenant_a, tenant_b, user_tenant_a, user_tenant_b
    ):
        """
        An authenticated GET /api/crm/leads/ must only return leads belonging
        to the requesting user's tenant.  This is the API-level complement to
        the ORM-level isolation tests above.
        """
        from apps.crm.models import Lead

        with tenant_context(tenant_a):
            lead_a = Lead.objects.create(
                first_name="Inês", last_name="Jesus",
                email="i.jesus@empresa-a.cv", source="WEB",
            )

        with tenant_context(tenant_b):
            lead_b = Lead.objects.create(
                first_name="Jorge", last_name="Lopes",
                email="j.lopes@empresa-b.cv", source="WEB",
            )

        # Query from tenant_a
        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client_a = _api_client_for_tenant(token_a, "empresa-a.imos.cv")
        response_a = client_a.get("/api/crm/leads/")

        assert response_a.status_code == 200
        returned_ids_a = {item["id"] for item in response_a.data.get("results", response_a.data)}

        assert str(lead_a.id) in returned_ids_a, (
            "tenant_a's own lead is missing from the API response."
        )
        assert str(lead_b.id) not in returned_ids_a, (
            f"ISOLATION BREACH: tenant_a API response includes lead "
            f"{lead_b.id} from tenant_b."
        )

        # Query from tenant_b
        token_b = _make_jwt_for_user(user_tenant_b, tenant_b.schema_name)
        client_b = _api_client_for_tenant(token_b, "empresa-b.imos.cv")
        response_b = client_b.get("/api/crm/leads/")

        assert response_b.status_code == 200
        returned_ids_b = {item["id"] for item in response_b.data.get("results", response_b.data)}

        assert str(lead_b.id) in returned_ids_b, (
            "tenant_b's own lead is missing from the API response."
        )
        assert str(lead_a.id) not in returned_ids_b, (
            f"ISOLATION BREACH: tenant_b API response includes lead "
            f"{lead_a.id} from tenant_a."
        )

    def test_api_direct_uuid_access_cross_tenant_returns_404(
        self, tenant_a, tenant_b, user_tenant_a
    ):
        """
        A user from tenant_a who somehow knows the UUID of a lead in tenant_b
        must receive 404, not 200 or 403.

        404 (not found) is the correct response because the lead genuinely does
        not exist in the tenant_a schema — the schema filter makes it invisible,
        not forbidden.
        """
        from apps.crm.models import Lead

        with tenant_context(tenant_b):
            lead_b = Lead.objects.create(
                first_name="Luisa", last_name="Monteiro",
                email="l.monteiro@empresa-b.cv", source="REFERRAL",
            )

        token_a = _make_jwt_for_user(user_tenant_a, tenant_a.schema_name)
        client_a = _api_client_for_tenant(token_a, "empresa-a.imos.cv")

        response = client_a.get(f"/api/crm/leads/{lead_b.id}/")

        assert response.status_code == 404, (
            f"ISOLATION BREACH: tenant_a user can access lead {lead_b.id} from "
            f"tenant_b via direct UUID lookup. Got {response.status_code}, expected 404."
        )
