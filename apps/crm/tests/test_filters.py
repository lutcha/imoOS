"""
Unit tests for apps/crm/filters.py and apps/crm/views_public.py
Covers:
  - LeadFilter budget range
  - PublicLeadSerializer field restrictions (no assigned_to / interested_unit)
  - Throttle class wiring on LeadCaptureView
"""
import pytest
from decimal import Decimal
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def _make_token(user, schema_name):
    refresh = RefreshToken.for_user(user)
    refresh["tenant_schema"] = schema_name
    return str(refresh.access_token)


def _create_lead(tenant, **kwargs):
    from apps.crm.models import Lead
    with tenant_context(tenant):
        return Lead.objects.create(**kwargs)


_BASE_LEAD = dict(first_name="Test", last_name="Lead", email="t@example.com", source="WEB")


# ---------------------------------------------------------------------------
# LeadFilter — budget range
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLeadFilterBudget:
    """LeadFilter budget_min / budget_max filtering."""

    def _auth_client(self, user, schema_name, domain):
        token = _make_token(user, schema_name)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        client.defaults["HTTP_HOST"] = domain
        return client

    def _setup_leads(self, tenant):
        from apps.crm.models import Lead
        with tenant_context(tenant):
            Lead.objects.create(
                first_name="Low", last_name="Budget",
                email="low@t.cv", source="WEB",
                budget=Decimal("2000000"),
            )
            Lead.objects.create(
                first_name="Mid", last_name="Budget",
                email="mid@t.cv", source="WEB",
                budget=Decimal("5000000"),
            )
            Lead.objects.create(
                first_name="High", last_name="Budget",
                email="high@t.cv", source="WEB",
                budget=Decimal("10000000"),
            )
            Lead.objects.create(
                first_name="No", last_name="Budget",
                email="none@t.cv", source="WEB",
                budget=None,
            )

    def test_budget_min_excludes_cheaper_leads(self, tenant_a, user_tenant_a):
        self._setup_leads(tenant_a)
        client = self._auth_client(user_tenant_a, tenant_a.schema_name, "empresa-a.imos.cv")

        response = client.get("/api/v1/crm/leads/", {"budget_min": 5_000_000})

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        emails = {r["email"] for r in results}

        assert "low@t.cv" not in emails, "Lead below budget_min must be excluded"
        assert "mid@t.cv" in emails
        assert "high@t.cv" in emails

    def test_budget_max_excludes_expensive_leads(self, tenant_a, user_tenant_a):
        self._setup_leads(tenant_a)
        client = self._auth_client(user_tenant_a, tenant_a.schema_name, "empresa-a.imos.cv")

        response = client.get("/api/v1/crm/leads/", {"budget_max": 5_000_000})

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        emails = {r["email"] for r in results}

        assert "high@t.cv" not in emails, "Lead above budget_max must be excluded"
        assert "low@t.cv" in emails
        assert "mid@t.cv" in emails

    def test_budget_range_returns_only_matching_leads(self, tenant_a, user_tenant_a):
        self._setup_leads(tenant_a)
        client = self._auth_client(user_tenant_a, tenant_a.schema_name, "empresa-a.imos.cv")

        response = client.get(
            "/api/v1/crm/leads/",
            {"budget_min": 3_000_000, "budget_max": 7_000_000},
        )

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        emails = {r["email"] for r in results}

        assert emails == {"mid@t.cv"}, f"Expected only mid@t.cv in range, got {emails}"

    def test_budget_min_exact_boundary_inclusive(self, tenant_a, user_tenant_a):
        from apps.crm.models import Lead
        with tenant_context(tenant_a):
            Lead.objects.create(
                first_name="Exact", last_name="B",
                email="exact@t.cv", source="WEB",
                budget=Decimal("4000000"),
            )
        client = self._auth_client(user_tenant_a, tenant_a.schema_name, "empresa-a.imos.cv")
        response = client.get("/api/v1/crm/leads/", {"budget_min": 4_000_000})
        results = response.data.get("results", response.data)
        assert any(r["email"] == "exact@t.cv" for r in results), "Exact boundary must be included (gte)"

    def test_budget_max_exact_boundary_inclusive(self, tenant_a, user_tenant_a):
        from apps.crm.models import Lead
        with tenant_context(tenant_a):
            Lead.objects.create(
                first_name="Exact", last_name="B",
                email="exact2@t.cv", source="WEB",
                budget=Decimal("4000000"),
            )
        client = self._auth_client(user_tenant_a, tenant_a.schema_name, "empresa-a.imos.cv")
        response = client.get("/api/v1/crm/leads/", {"budget_max": 4_000_000})
        results = response.data.get("results", response.data)
        assert any(r["email"] == "exact2@t.cv" for r in results), "Exact boundary must be included (lte)"


# ---------------------------------------------------------------------------
# PublicLeadSerializer — field restrictions
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLeadCaptureViewSerializer:
    """PublicLeadSerializer must not expose or accept assigned_to/interested_unit."""

    _url = "/api/v1/crm/lead-capture/"
    _payload = {
        "first_name": "Maria",
        "last_name": "Fonseca",
        "email": "maria@cv.cv",
        "phone": "+238991234567",
        "source": "WEB",
        "budget": "3500000",
        "preferred_typology": "T2",
        "notes": "Prefere sul",
    }

    def _anon_client(self, domain):
        client = APIClient()
        client.defaults["HTTP_HOST"] = domain
        return client

    def test_lead_capture_201_on_valid_payload(self, tenant_a):
        client = self._anon_client("empresa-a.imos.cv")
        response = client.post(self._url, self._payload, format="json")
        assert response.status_code == 201, response.data

    def test_response_does_not_include_assigned_to(self, tenant_a):
        client = self._anon_client("empresa-a.imos.cv")
        response = client.post(self._url, self._payload, format="json")
        assert response.status_code == 201
        assert "assigned_to" not in response.data, (
            "assigned_to must not be present in PublicLeadSerializer response"
        )

    def test_response_does_not_include_interested_unit(self, tenant_a):
        client = self._anon_client("empresa-a.imos.cv")
        response = client.post(self._url, self._payload, format="json")
        assert response.status_code == 201
        assert "interested_unit" not in response.data, (
            "interested_unit must not be present in PublicLeadSerializer response"
        )

    def test_status_field_not_writable_on_capture(self, tenant_a):
        """Anonymous caller must not be able to set lead status."""
        from apps.crm.models import Lead
        payload = {**self._payload, "email": "status_test@cv.cv", "status": "CONVERTED"}
        client = self._anon_client("empresa-a.imos.cv")
        response = client.post(self._url, payload, format="json")
        assert response.status_code == 201
        with tenant_context(tenant_a):
            lead = Lead.objects.get(email="status_test@cv.cv")
        assert lead.status == Lead.STATUS_NEW, (
            f"Anonymous caller must not override status. Got: {lead.status}"
        )

    def test_assigned_to_field_ignored_on_capture(self, tenant_a, user_tenant_a):
        """Passing assigned_to UUID must be silently ignored, not raise 400."""
        payload = {
            **self._payload,
            "email": "assign_test@cv.cv",
            "assigned_to": str(user_tenant_a.id),
        }
        client = self._anon_client("empresa-a.imos.cv")
        response = client.post(self._url, payload, format="json")
        # Must not 400 (field not in serializer = quietly ignored)
        assert response.status_code == 201, (
            f"Extra field assigned_to caused unexpected error: {response.data}"
        )
        from apps.crm.models import Lead
        with tenant_context(tenant_a):
            lead = Lead.objects.get(email="assign_test@cv.cv")
        assert lead.assigned_to is None, "assigned_to must remain null on public capture"

    def test_required_fields_missing_returns_400(self, tenant_a):
        client = self._anon_client("empresa-a.imos.cv")
        response = client.post(self._url, {"phone": "+238991111111"}, format="json")
        assert response.status_code == 400

    def test_response_contains_expected_public_fields(self, tenant_a):
        client = self._anon_client("empresa-a.imos.cv")
        response = client.post(self._url, self._payload, format="json")
        assert response.status_code == 201
        for field in ("id", "first_name", "last_name", "email", "source", "created_at"):
            assert field in response.data, f"Expected field '{field}' in response"


# ---------------------------------------------------------------------------
# LeadCaptureView — throttle wiring
# ---------------------------------------------------------------------------

class TestLeadCaptureViewThrottle:
    """Verify PublicEndpointThrottle is wired to LeadCaptureView."""

    def test_throttle_classes_contains_public_endpoint_throttle(self):
        from apps.crm.views_public import LeadCaptureView
        from apps.core.throttling import PublicEndpointThrottle

        throttle_classes = LeadCaptureView.throttle_classes
        assert PublicEndpointThrottle in throttle_classes, (
            f"PublicEndpointThrottle not found in LeadCaptureView.throttle_classes: "
            f"{throttle_classes}"
        )

    def test_throttle_rate_is_100_per_hour(self):
        from apps.core.throttling import PublicEndpointThrottle
        assert PublicEndpointThrottle.rate == "100/hour", (
            f"Expected '100/hour', got '{PublicEndpointThrottle.rate}'"
        )
