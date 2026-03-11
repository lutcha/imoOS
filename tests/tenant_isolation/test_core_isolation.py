"""
CRITICAL: Tenant Isolation Tests
=================================
These tests MUST pass before ANY merge to main/develop.
A failure here means data is leaking between tenant schemas.

Run: pytest tests/tenant_isolation/ -v
"""
import pytest
from django_tenants.utils import tenant_context


@pytest.mark.isolation
class TestProjectIsolation:
    """Projects must be fully isolated per tenant schema."""

    def test_project_invisible_across_tenants(self, tenant_a, tenant_b, db):
        """Tenant B cannot see Tenant A's projects."""
        from apps.projects.models import Project

        with tenant_context(tenant_a):
            Project.objects.create(name='Residencial A', slug='residencial-a', status='PLANNING')

        with tenant_context(tenant_b):
            count = Project.objects.count()

        assert count == 0, (
            f"ISOLATION BREACH: Tenant B sees {count} projects from Tenant A!"
        )

    def test_project_id_not_accessible_cross_tenant(self, tenant_a, tenant_b, db):
        """Direct UUID lookup cannot cross tenant boundary."""
        from apps.projects.models import Project

        with tenant_context(tenant_a):
            project = Project.objects.create(name='Residencial A', slug='residencial-a')
            project_id = project.id

        with tenant_context(tenant_b):
            exists = Project.objects.filter(id=project_id).exists()

        assert not exists, (
            f"ISOLATION BREACH: Tenant B can directly access Project {project_id} from Tenant A!"
        )


@pytest.mark.isolation
class TestUnitIsolation:
    """Units (Frações) must be fully isolated per tenant schema."""

    def test_units_isolated_between_tenants(self, tenant_a, tenant_b, db):
        """Bulk of units in Tenant A not visible in Tenant B."""
        from apps.projects.models import Project, Building, Floor
        from apps.inventory.models import Unit, UnitType

        with tenant_context(tenant_a):
            project = Project.objects.create(name='P1', slug='p1')
            building = Building.objects.create(project=project, name='Bloco A', code='BLK-A')
            floor = Floor.objects.create(building=building, number=1)
            unit_type = UnitType.objects.create(name='T2', code='T2', bedrooms=2, bathrooms=1)
            Unit.objects.bulk_create([
                Unit(floor=floor, unit_type=unit_type, code=f'A-P1-{i:02d}', area_bruta=75)
                for i in range(10)
            ])

        with tenant_context(tenant_b):
            count = Unit.objects.count()

        assert count == 0, (
            f"ISOLATION BREACH: Tenant B sees {count} units from Tenant A!"
        )

    def test_bulk_delete_scoped_to_tenant(self, tenant_a, tenant_b, db):
        """Deleting all units in Tenant A must not affect Tenant B."""
        from apps.projects.models import Project, Building, Floor
        from apps.inventory.models import Unit, UnitType

        # Create units in both tenants
        for tenant, slug_prefix in [(tenant_a, 'a'), (tenant_b, 'b')]:
            with tenant_context(tenant):
                project = Project.objects.create(name=f'P-{slug_prefix}', slug=f'p-{slug_prefix}')
                building = Building.objects.create(project=project, name='Bloco A', code='BLK-A')
                floor = Floor.objects.create(building=building, number=1)
                unit_type = UnitType.objects.create(name='T2', code='T2', bedrooms=2, bathrooms=1)
                Unit.objects.create(floor=floor, unit_type=unit_type, code='A-P1-01', area_bruta=75)

        # Delete all in Tenant A
        with tenant_context(tenant_a):
            Unit.objects.all().delete()

        # Tenant B must still have its unit
        with tenant_context(tenant_b):
            count = Unit.objects.count()

        assert count == 1, (
            f"ISOLATION BREACH: Bulk delete in Tenant A affected Tenant B! Expected 1, got {count}"
        )
