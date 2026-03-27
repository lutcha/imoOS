"""
CRITICAL: Investor Portal Tenant Isolation Tests
=================================================
These tests verify that the investor portal endpoints only return contract
data scoped to the active tenant schema. A failure here means one promotora's
investor can read another promotora's contracts — a critical data-isolation
breach.

Test coverage
-------------
1. TestInvestorPermissions
   Unauthenticated requests and users without investor/admin membership are
   rejected with 401/403.

2. TestInvestorDataIsolation
   An investor from tenant_a cannot see contracts created inside tenant_b.

3. TestInvestorEmailFilter
   An investor user only sees contracts where lead.email == user.email;
   contracts belonging to other leads in the same tenant are not visible.

4. TestAdminSeesAll
   A tenant admin can see all contracts in the tenant, regardless of lead email.

Run:
    pytest tests/tenant_isolation/test_investor_isolation.py -v

CI gate: This test MUST pass before merge.
"""
import pytest
from decimal import Decimal

from django_tenants.utils import tenant_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_jwt(user, schema_name: str) -> str:
    refresh = RefreshToken.for_user(user)
    refresh["tenant_schema"] = schema_name
    return str(refresh.access_token)


def _client(token: str, domain: str) -> APIClient:
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    c.defaults["HTTP_HOST"] = domain
    return c


def _create_membership(user, role: str):
    from apps.memberships.models import TenantMembership
    return TenantMembership.objects.create(user=user, role=role)


def _create_contract(unit, lead, number: str, price=Decimal("5000000.00")):
    from apps.contracts.models import Contract
    return Contract.objects.create(
        unit=unit,
        lead=lead,
        contract_number=number,
        total_price_cve=price,
        status=Contract.STATUS_ACTIVE,
    )


_unit_counter = 0


def _create_minimal_unit(tenant):
    """Create the minimal object graph: Project→Building→Floor→UnitType→Unit."""
    global _unit_counter
    _unit_counter += 1
    seq = _unit_counter

    from django.contrib.auth import get_user_model
    from apps.projects.models import Project, Building, Floor
    from apps.inventory.models import Unit, UnitType

    User = get_user_model()

    user, _ = User.objects.get_or_create(
        email=f"builder@{tenant.schema_name}.cv",
        defaults={"password": "!"},
    )

    project = Project.objects.create(
        name=f"Proj {tenant.schema_name} {seq}",
        slug=f"proj-{tenant.schema_name}-{seq}",
        status=Project.STATUS_PLANNING,
        created_by=user,
    )
    building = Building.objects.create(
        project=project, name=f"Bloco {seq}", code=f"BLK-{seq}",
    )
    floor = Floor.objects.create(building=building, number=1, name="Piso 1")
    unit_type, _ = UnitType.objects.get_or_create(name="T2", code="T2")
    unit = Unit.objects.create(
        floor=floor,
        unit_type=unit_type,
        code=f"U-{seq:04d}",
        area_bruta=Decimal("85.00"),
        created_by=user,
    )
    return unit


def _create_lead(email: str):
    from apps.crm.models import Lead
    return Lead.objects.create(
        first_name="Test",
        last_name="Investor",
        email=email,
        source=Lead.SOURCE_WEB,
    )


# ---------------------------------------------------------------------------
# 1. TestInvestorPermissions
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
class TestInvestorPermissions:
    """Unauthenticated and unauthorised access is rejected."""

    def test_unauthenticated_returns_401(self, tenant_a):
        client = APIClient()
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"
        resp = client.get("/api/v1/investors/portal/")
        assert resp.status_code == 401

    def test_no_membership_returns_403(self, tenant_a):
        """A user with a valid JWT but no TenantMembership is rejected."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with tenant_context(tenant_a):
            user = User.objects.create_user(
                email="nobody@empresa-a.cv", password="pass123"
            )

        token = _make_jwt(user, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/")
        assert resp.status_code == 403

    def test_vendedor_role_returns_403(self, tenant_a):
        """A vendedor (non-investor, non-admin) cannot access the investor portal."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with tenant_context(tenant_a):
            user = User.objects.create_user(
                email="vendedor@empresa-a.cv", password="pass123"
            )
            _create_membership(user, "vendedor")

        token = _make_jwt(user, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/")
        assert resp.status_code == 403

    def test_investor_role_returns_200(self, tenant_a):
        """A user with investidor membership gets 200."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with tenant_context(tenant_a):
            user = User.objects.create_user(
                email="inv@empresa-a.cv", password="pass123"
            )
            _create_membership(user, "investidor")

        token = _make_jwt(user, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 2. TestInvestorDataIsolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
class TestInvestorDataIsolation:
    """Investor from tenant_a cannot access tenant_b contracts via API."""

    def test_investor_a_cannot_list_tenant_b_contracts(self, tenant_a, tenant_b):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        investor_email = "cross@empresa-a.cv"

        with tenant_context(tenant_a):
            user_a = User.objects.create_user(email=investor_email, password="pass")
            _create_membership(user_a, "investidor")

        # Create a contract in tenant_b using the same email.
        with tenant_context(tenant_b):
            unit_b = _create_minimal_unit(tenant_b)
            lead_b = _create_lead(investor_email)
            _create_contract(unit_b, lead_b, "CVB-2026-001")

        # Request from tenant_a endpoint — should return 0 contracts (schema isolation).
        token = _make_jwt(user_a, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/")
        assert resp.status_code == 200
        assert len(resp.json()) == 0, "Investor A must not see Tenant B contracts"

    def test_jwt_for_tenant_a_rejected_on_tenant_b_endpoint(self, tenant_a, tenant_b):
        """A JWT scoped to tenant_a is rejected when used against tenant_b's domain."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with tenant_context(tenant_a):
            user_a = User.objects.create_user(email="inv2@empresa-a.cv", password="p")
            _create_membership(user_a, "investidor")

        token = _make_jwt(user_a, tenant_a.schema_name)
        c = _client(token, "empresa-b.imos.cv")  # wrong tenant domain
        resp = c.get("/api/v1/investors/portal/")
        assert resp.status_code == 403, "JWT from tenant_a must be rejected on tenant_b"

    def test_summary_does_not_leak_cross_tenant_totals(self, tenant_a, tenant_b):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        inv_email = "inv3@empresa-a.cv"

        with tenant_context(tenant_a):
            user_a = User.objects.create_user(email=inv_email, password="p")
            _create_membership(user_a, "investidor")

        # Large contract in tenant_b.
        with tenant_context(tenant_b):
            unit_b = _create_minimal_unit(tenant_b)
            lead_b = _create_lead(inv_email)
            _create_contract(unit_b, lead_b, "CVB-2026-BIG", price=Decimal("99000000.00"))

        token = _make_jwt(user_a, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/my_summary/")
        assert resp.status_code == 200
        data = resp.json()
        # tenant_a has no contracts → total must be 0
        assert Decimal(data["total_invested_cve"]) == Decimal("0"), (
            "Summary must not include contracts from another tenant"
        )


# ---------------------------------------------------------------------------
# 3. TestInvestorEmailFilter
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
class TestInvestorEmailFilter:
    """Investor only sees contracts where lead.email matches their own email."""

    def test_investor_only_sees_own_contracts(self, tenant_a):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        inv_email = "owner@empresa-a.cv"
        other_email = "other@empresa-a.cv"

        with tenant_context(tenant_a):
            user = User.objects.create_user(email=inv_email, password="p")
            _create_membership(user, "investidor")

            unit = _create_minimal_unit(tenant_a)

            # Own contract
            own_lead = _create_lead(inv_email)
            _create_contract(unit, own_lead, "CVA-2026-OWN")

            # Another investor's contract (same tenant, different email)
            other_unit = _create_minimal_unit(tenant_a)
            other_lead = _create_lead(other_email)
            _create_contract(other_unit, other_lead, "CVA-2026-OTHER")

        token = _make_jwt(user, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1, "Investor must only see their own contract"
        assert data[0]["contract_number"] == "CVA-2026-OWN"

    def test_my_documents_only_returns_own_pdfs(self, tenant_a):
        from django.contrib.auth import get_user_model
        from apps.contracts.models import Contract
        User = get_user_model()

        inv_email = "docowner@empresa-a.cv"

        with tenant_context(tenant_a):
            user = User.objects.create_user(email=inv_email, password="p")
            _create_membership(user, "investidor")

            unit = _create_minimal_unit(tenant_a)
            lead = _create_lead(inv_email)
            contract = _create_contract(unit, lead, "CVA-2026-DOC")
            contract.pdf_s3_key = f"tenants/empresa-a/contracts/{contract.contract_number}.pdf"
            contract.save()

            # Another lead's contract with PDF
            other_unit = _create_minimal_unit(tenant_a)
            other_lead = _create_lead("nodoc@empresa-a.cv")
            other_contract = _create_contract(other_unit, other_lead, "CVA-2026-NODOC")
            other_contract.pdf_s3_key = "tenants/empresa-a/contracts/other.pdf"
            other_contract.save()

        token = _make_jwt(user, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/my_documents/")
        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) == 1
        assert "CVA-2026-DOC" in docs[0]["contract_number"]


# ---------------------------------------------------------------------------
# 4. TestAdminSeesAll
# ---------------------------------------------------------------------------

@pytest.mark.django_db(transaction=True)
class TestAdminSeesAll:
    """Tenant admin can see all contracts, not just their own."""

    def test_admin_lists_all_contracts(self, tenant_a):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        admin_email = "admin@empresa-a.cv"

        with tenant_context(tenant_a):
            admin = User.objects.create_user(email=admin_email, password="p")
            _create_membership(admin, "admin")

            unit1 = _create_minimal_unit(tenant_a)
            lead1 = _create_lead("buyer1@cv.cv")
            _create_contract(unit1, lead1, "CVA-ADMIN-001")

            unit2 = _create_minimal_unit(tenant_a)
            lead2 = _create_lead("buyer2@cv.cv")
            _create_contract(unit2, lead2, "CVA-ADMIN-002")

        token = _make_jwt(admin, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2, "Admin must see all contracts in the tenant"

    def test_admin_summary_totals_all_contracts(self, tenant_a):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with tenant_context(tenant_a):
            admin = User.objects.create_user(email="admin2@empresa-a.cv", password="p")
            _create_membership(admin, "admin")

            unit = _create_minimal_unit(tenant_a)
            lead = _create_lead("buyer3@cv.cv")
            _create_contract(unit, lead, "CVA-ADMIN-003", price=Decimal("10000000.00"))

        token = _make_jwt(admin, tenant_a.schema_name)
        c = _client(token, "empresa-a.imos.cv")
        resp = c.get("/api/v1/investors/portal/my_summary/")
        assert resp.status_code == 200
        data = resp.json()
        assert Decimal(data["total_invested_cve"]) == Decimal("10000000.00")
