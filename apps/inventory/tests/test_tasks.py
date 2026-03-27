"""
Tests for apps/inventory/tasks.py

Coverage:
  1. Valid CSV creates units
  2. Idempotency — re-running same CSV updates, no duplicates
  3. Row with missing required field → error collected, batch continues
  4. Row with unknown floor_id → error collected
  5. Row with invalid area_bruta → error collected
  6. price_cve present → UnitPricing created / updated
  7. Tenant isolation — task only writes to the target schema
"""
import pytest
from decimal import Decimal
from django_tenants.utils import tenant_context


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project_tree(tenant, suffix=''):
    """Create Project → Building → Floor inside the given tenant schema."""
    from apps.projects.models import Building, Floor, Project
    with tenant_context(tenant):
        project = Project.objects.create(
            name=f'Projecto{suffix}',
            slug=f'projecto{suffix.lower().replace(" ", "-")}',
        )
        building = Building.objects.create(project=project, name='Bloco A', code='BLK-A')
        floor = Floor.objects.create(building=building, number=1, name='1º Andar')
    return floor


def _make_unit_type(tenant, code='T2'):
    from apps.inventory.models import UnitType
    with tenant_context(tenant):
        ut, _ = UnitType.objects.get_or_create(
            code=code,
            defaults={'name': code, 'bedrooms': 2, 'bathrooms': 1},
        )
    return ut


def _csv(floor_id, code='BLK-A-P1-T2', unit_type_code='T2',
         area_bruta='85.50', price_cve=''):
    header = 'code,floor_id,unit_type_code,area_bruta,price_cve\n'
    row = f'{code},{floor_id},{unit_type_code},{area_bruta},{price_cve}\n'
    return header + row


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestImportUnitsCsvTask:

    def test_creates_unit_from_valid_csv(self, tenant_a):
        from apps.inventory.models import Unit
        from apps.inventory.tasks import import_units_from_csv

        floor = _make_project_tree(tenant_a)
        _make_unit_type(tenant_a)

        result = import_units_from_csv(
            tenant_schema=tenant_a.schema_name,
            csv_content=_csv(str(floor.id)),
        )

        assert result['created'] == 1
        assert result['updated'] == 0
        assert result['errors'] == []

        with tenant_context(tenant_a):
            assert Unit.objects.filter(code='BLK-A-P1-T2').count() == 1

    def test_idempotency_second_run_updates_not_duplicates(self, tenant_a):
        from apps.inventory.models import Unit
        from apps.inventory.tasks import import_units_from_csv

        floor = _make_project_tree(tenant_a, suffix='Idem')
        _make_unit_type(tenant_a)
        csv_content = _csv(str(floor.id))

        import_units_from_csv(tenant_schema=tenant_a.schema_name, csv_content=csv_content)
        result = import_units_from_csv(tenant_schema=tenant_a.schema_name, csv_content=csv_content)

        assert result['created'] == 0
        assert result['updated'] == 1
        assert result['errors'] == []

        with tenant_context(tenant_a):
            assert Unit.objects.filter(code='BLK-A-P1-T2').count() == 1

    def test_missing_area_bruta_adds_error_batch_continues(self, tenant_a):
        from apps.inventory.models import Unit
        from apps.inventory.tasks import import_units_from_csv

        floor = _make_project_tree(tenant_a, suffix='Batch')
        _make_unit_type(tenant_a)

        csv_content = (
            'code,floor_id,unit_type_code,area_bruta\n'
            f'BAD-CODE,{floor.id},T2,\n'         # missing area_bruta — row 2
            f'GOOD-CODE,{floor.id},T2,90.00\n'   # valid — row 3
        )

        result = import_units_from_csv(tenant_schema=tenant_a.schema_name, csv_content=csv_content)

        assert result['created'] == 1
        assert len(result['errors']) == 1
        assert result['errors'][0]['row'] == 2
        assert 'area_bruta' in result['errors'][0]['error']

        with tenant_context(tenant_a):
            assert Unit.objects.filter(code='GOOD-CODE').exists()
            assert not Unit.objects.filter(code='BAD-CODE').exists()

    def test_unknown_floor_id_adds_error(self, tenant_a):
        from apps.inventory.tasks import import_units_from_csv

        _make_unit_type(tenant_a)

        result = import_units_from_csv(
            tenant_schema=tenant_a.schema_name,
            csv_content=_csv('00000000-0000-0000-0000-000000000000'),
        )

        assert result['created'] == 0
        assert len(result['errors']) == 1
        assert 'Floor not found' in result['errors'][0]['error']

    def test_invalid_area_bruta_adds_error(self, tenant_a):
        from apps.inventory.tasks import import_units_from_csv

        floor = _make_project_tree(tenant_a, suffix='InvalidArea')
        _make_unit_type(tenant_a)

        result = import_units_from_csv(
            tenant_schema=tenant_a.schema_name,
            csv_content=_csv(str(floor.id), area_bruta='not-a-number'),
        )

        assert result['created'] == 0
        assert len(result['errors']) == 1
        assert 'area_bruta' in result['errors'][0]['error']

    def test_creates_unit_pricing_when_price_cve_present(self, tenant_a):
        from apps.inventory.models import Unit, UnitPricing
        from apps.inventory.tasks import import_units_from_csv

        floor = _make_project_tree(tenant_a, suffix='Pricing')
        _make_unit_type(tenant_a)

        result = import_units_from_csv(
            tenant_schema=tenant_a.schema_name,
            csv_content=_csv(str(floor.id), price_cve='12000000'),
        )

        assert result['created'] == 1
        assert result['errors'] == []

        with tenant_context(tenant_a):
            unit = Unit.objects.get(code='BLK-A-P1-T2')
            assert UnitPricing.objects.filter(unit=unit).exists()
            assert unit.pricing.price_cve == Decimal('12000000')

    def test_tenant_isolation_does_not_write_to_other_schema(self, tenant_a, tenant_b):
        from apps.inventory.models import Unit
        from apps.inventory.tasks import import_units_from_csv

        floor_a = _make_project_tree(tenant_a, suffix='IsoA')
        _make_unit_type(tenant_a)

        import_units_from_csv(
            tenant_schema=tenant_a.schema_name,
            csv_content=_csv(str(floor_a.id)),
        )

        with tenant_context(tenant_b):
            assert Unit.objects.filter(code='BLK-A-P1-T2').count() == 0
