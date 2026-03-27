"""
Unit tests for apps/inventory/filters.py
Tests UnitFilter price range (CVE) filtering.
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


def _build_project_with_units(pricing_map: dict):
    """
    Helper: creates Project → Building → Floor → N Units with UnitPricing.
    pricing_map: {unit_code: price_cve}
    Returns list of created Unit instances.
    """
    from apps.projects.models import Project, Building, Floor
    from apps.inventory.models import Unit, UnitType, UnitPricing

    project = Project.objects.create(name="Teste Filtros", slug="teste-filtros")
    building = Building.objects.create(project=project, name="Bloco A", code="BLK-A")
    floor = Floor.objects.create(building=building, number=1)
    unit_type = UnitType.objects.create(name="T2", code="T2", bedrooms=2, bathrooms=1)

    units = []
    for code, price in pricing_map.items():
        unit = Unit.objects.create(
            floor=floor,
            unit_type=unit_type,
            code=code,
            area_bruta=Decimal("80.00"),
        )
        UnitPricing.objects.create(unit=unit, price_cve=Decimal(str(price)))
        units.append(unit)
    return units


@pytest.mark.django_db
class TestUnitFilterPriceCVE:
    """UnitFilter price_cve_min / price_cve_max range filtering."""

    def test_price_cve_min_filters_out_cheaper_units(self, tenant_a, user_tenant_a):
        with tenant_context(tenant_a):
            _build_project_with_units({
                "U-CHEAP": 5_000_000,
                "U-MID":   10_000_000,
                "U-EXP":   20_000_000,
            })

        token = _make_token(user_tenant_a, tenant_a.schema_name)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get("/api/v1/inventory/units/", {"price_cve_min": 10_000_000})

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        codes = {u["code"] for u in results}

        assert "U-CHEAP" not in codes, "Unit below price_cve_min must be excluded"
        assert "U-MID" in codes
        assert "U-EXP" in codes

    def test_price_cve_max_filters_out_expensive_units(self, tenant_a, user_tenant_a):
        with tenant_context(tenant_a):
            _build_project_with_units({
                "U-CHEAP": 5_000_000,
                "U-MID":   10_000_000,
                "U-EXP":   20_000_000,
            })

        token = _make_token(user_tenant_a, tenant_a.schema_name)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get("/api/v1/inventory/units/", {"price_cve_max": 10_000_000})

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        codes = {u["code"] for u in results}

        assert "U-EXP" not in codes, "Unit above price_cve_max must be excluded"
        assert "U-CHEAP" in codes
        assert "U-MID" in codes

    def test_price_cve_range_returns_only_matching_units(self, tenant_a, user_tenant_a):
        with tenant_context(tenant_a):
            _build_project_with_units({
                "U-LOW":    3_000_000,
                "U-TARGET": 8_000_000,
                "U-HIGH":  15_000_000,
            })

        token = _make_token(user_tenant_a, tenant_a.schema_name)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get(
            "/api/v1/inventory/units/",
            {"price_cve_min": 5_000_000, "price_cve_max": 10_000_000},
        )

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        codes = {u["code"] for u in results}

        assert codes == {"U-TARGET"}, (
            f"Expected only U-TARGET in range, got {codes}"
        )

    def test_price_cve_min_exact_boundary_is_inclusive(self, tenant_a, user_tenant_a):
        """Boundary value: price == min must be included (gte, not gt)."""
        with tenant_context(tenant_a):
            _build_project_with_units({"U-EXACT": 7_500_000})

        token = _make_token(user_tenant_a, tenant_a.schema_name)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get("/api/v1/inventory/units/", {"price_cve_min": 7_500_000})

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        codes = {u["code"] for u in results}
        assert "U-EXACT" in codes, "Exact boundary value must be included (gte)"

    def test_price_cve_max_exact_boundary_is_inclusive(self, tenant_a, user_tenant_a):
        """Boundary value: price == max must be included (lte, not lt)."""
        with tenant_context(tenant_a):
            _build_project_with_units({"U-EXACT": 7_500_000})

        token = _make_token(user_tenant_a, tenant_a.schema_name)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get("/api/v1/inventory/units/", {"price_cve_max": 7_500_000})

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        codes = {u["code"] for u in results}
        assert "U-EXACT" in codes, "Exact boundary value must be included (lte)"

    def test_no_price_filter_returns_all_units(self, tenant_a, user_tenant_a):
        """Omitting price filters must not exclude any unit."""
        with tenant_context(tenant_a):
            _build_project_with_units({
                "U-A": 1_000_000,
                "U-B": 50_000_000,
            })

        token = _make_token(user_tenant_a, tenant_a.schema_name)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        client.defaults["HTTP_HOST"] = "empresa-a.imos.cv"

        response = client.get("/api/v1/inventory/units/")

        assert response.status_code == 200
        results = response.data.get("results", response.data)
        codes = {u["code"] for u in results}
        assert {"U-A", "U-B"}.issubset(codes)
