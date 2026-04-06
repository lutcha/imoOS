"""
Global pytest fixtures for ImoOS test suite.
"""
import pytest
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient


@pytest.fixture(scope='session', autouse=True)
def fix_cascade_truncate():
    """
    Patch PostgreSQL's sql_flush to always use CASCADE.

    Django's TransactionTestCase teardown calls `flush` (TRUNCATE) to reset
    the DB between tests. With simple-history FK chains (e.g.
    projects_historicalbuilding → users_user) the plain TRUNCATE fails.
    Setting allow_cascade=True generates `TRUNCATE ... CASCADE`, which is
    safe for test teardown.
    """
    from django.db.backends.postgresql.operations import DatabaseOperations

    _original = DatabaseOperations.sql_flush

    def _patched(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        return _original(self, style, tables, reset_sequences=reset_sequences, allow_cascade=True)

    DatabaseOperations.sql_flush = _patched
    yield
    DatabaseOperations.sql_flush = _original


@pytest.fixture
def api_client():
    return APIClient()


def _create_test_tenant(db, schema_name: str, name: str, slug: str, plan: str, domain: str):
    """
    Create a test tenant with proper schema isolation.

    Problem: pytest-django runs `migrate` during test DB setup, which records
    ALL app migrations (including TENANT_APPS) in the public schema's
    django_migrations table. When Client.create_schema() runs migrate_schemas,
    PostgreSQL finds that table via search_path and reports "No migrations to
    apply" — leaving the tenant schema without any tables.

    Fix: pre-create the django_migrations table inside the tenant schema
    BEFORE running migrate_schemas. PostgreSQL's search_path finds it there
    first (not in public), sees it is empty, and correctly applies all
    tenant migrations.
    """
    from unittest.mock import patch
    from django.db import connection
    from django.core.management import call_command
    from apps.tenants.models import Client, Domain

    # Ensure we start from public schema (left-over search_path from prior test)
    connection.set_schema_to_public()

    # 1. Create the PostgreSQL schema and seed its django_migrations table.
    with connection.cursor() as cursor:
        cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
        cursor.execute(f'CREATE SCHEMA "{schema_name}"')
        # Shadow public.django_migrations so migrate_schemas sees this empty
        # table first and correctly applies all pending tenant migrations.
        cursor.execute(f'''
            CREATE TABLE "{schema_name}".django_migrations (
                "id"      bigserial    NOT NULL PRIMARY KEY,
                "app"     varchar(255) NOT NULL,
                "name"    varchar(255) NOT NULL,
                "applied" timestamptz  NOT NULL
            )
        ''')

    # 3. Reset connection to public schema before creating the Client record.
    #    Between transaction=True tests the search_path can be left on the
    #    previous tenant schema, which causes django-tenants to reject the
    #    Client.save() with "Can't create tenant outside the public schema".
    connection.set_schema_to_public()

    # 4. Create the Client DB record WITHOUT triggering auto create_schema
    #    (we already created the schema above).
    with patch.object(Client, 'create_schema', return_value=False):
        tenant = Client.objects.create(
            schema_name=schema_name,
            name=name,
            slug=slug,
            plan=plan,
            is_active=True,
        )
    Domain.objects.create(domain=domain, tenant=tenant, is_primary=True)

    # 3. Apply all tenant-schema migrations.
    #    migrate_schemas now finds the empty django_migrations table in the
    #    tenant schema (not the full one in public) and applies everything.
    call_command('migrate_schemas', schema_name=schema_name, verbosity=0)

    return tenant


@pytest.fixture
def tenant_a(db):
    """Tenant A — first promotora for isolation tests."""
    tenant = _create_test_tenant(
        db,
        schema_name='test_empresa_a',
        name='Empresa A Lda',
        slug='empresa-a',
        plan='pro',
        domain='empresa-a.imos.cv',
    )
    yield tenant
    # Reset to public before TransactionTestCase teardown/flush so that
    # the tenants_client row is properly truncated from the correct schema.
    from django.db import connection
    connection.set_schema_to_public()


@pytest.fixture
def tenant_b(db):
    """Tenant B — second promotora for isolation tests."""
    tenant = _create_test_tenant(
        db,
        schema_name='test_empresa_b',
        name='Empresa B Lda',
        slug='empresa-b',
        plan='starter',
        domain='empresa-b.imos.cv',
    )
    yield tenant
    from django.db import connection
    connection.set_schema_to_public()


@pytest.fixture
def admin_user_a(tenant_a):
    """Admin user in Tenant A."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    with tenant_context(tenant_a):
        user = User.objects.create_user(
            email='admin@empresa-a.cv',
            password='testpass123',
        )
    return user


@pytest.fixture
def api_client_a(tenant_a, admin_user_a, api_client):
    """APIClient authenticated as Tenant A admin."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user_a)
    refresh['tenant_schema'] = tenant_a.schema_name
    api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}',
        HTTP_HOST='empresa-a.imos.cv',
    )
    return api_client


# ---------------------------------------------------------------------------
# JWT isolation fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user_tenant_a(tenant_a):
    """
    A regular gestor user created inside tenant_a's schema.

    The user is created with tenant_context so the INSERT lands in the correct
    PostgreSQL schema.  Used by JWT isolation tests to mint tokens that carry
    ``tenant_schema = tenant_a.schema_name``.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    with tenant_context(tenant_a):
        user = User.objects.create_user(
            email='gestor@empresa-a.cv',
            password='testpass123!',
            role='gestor',
        )
    return user


@pytest.fixture
def user_tenant_b(tenant_b):
    """
    A regular gestor user created inside tenant_b's schema.

    Symmetric counterpart to ``user_tenant_a``.  Used to mint JWT tokens
    scoped to tenant_b.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    with tenant_context(tenant_b):
        user = User.objects.create_user(
            email='gestor@empresa-b.cv',
            password='testpass123!',
            role='gestor',
        )
    return user


@pytest.fixture
def api_client_tenant_a(tenant_a, user_tenant_a):
    """
    APIClient pre-configured with a JWT token scoped to tenant_a and the
    correct Host header for tenant_a's domain.

    Use this fixture when you need an authenticated client for tenant_a without
    manually constructing the token in each test.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user_tenant_a)
    refresh['tenant_schema'] = tenant_a.schema_name
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    client.defaults['HTTP_HOST'] = 'empresa-a.imos.cv'
    return client


@pytest.fixture
def api_client_tenant_b(tenant_b, user_tenant_b):
    """
    APIClient pre-configured with a JWT token scoped to tenant_b and the
    correct Host header for tenant_b's domain.

    Symmetric counterpart to ``api_client_tenant_a``.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user_tenant_b)
    refresh['tenant_schema'] = tenant_b.schema_name
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    client.defaults['HTTP_HOST'] = 'empresa-b.imos.cv'
    return client


# ---------------------------------------------------------------------------
# Workflow fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tenant_context():
    """
    Fixture that returns a context manager for tenant operations.
    
    Usage:
        def test_something(tenant_context, tenant_a):
            with tenant_context(tenant_a):
                # operations in tenant_a schema
                pass
    """
    from contextlib import contextmanager
    
    @contextmanager
    def _context(tenant):
        from django.db import connection
        from django_tenants.utils import tenant_context as _tenant_context
        
        with _tenant_context(tenant):
            yield tenant, tenant.schema_name
    
    return _context


@pytest.fixture
def lead_factory():
    """Factory for creating Lead instances."""
    def factory(**kwargs):
        from apps.crm.models import Lead
        defaults = {
            'first_name': 'Test',
            'last_name': 'Lead',
            'email': 'test@example.com',
            'phone': '+2389999999',
            'status': Lead.STATUS_NEW,
        }
        defaults.update(kwargs)
        return Lead.objects.create(**defaults)
    return factory


@pytest.fixture
def unit_factory():
    """Factory for creating Unit instances."""
    def factory(**kwargs):
        from apps.inventory.models import Unit, Floor, Building, Project
        from apps.projects.models import Project as ProjectModel
        
        # Create project if not provided
        if 'floor' not in kwargs:
            project = ProjectModel.objects.create(
                name='Test Project',
                slug='test-project',
                city='Praia',
                island='Santiago'
            )
            building = Building.objects.create(
                project=project,
                name='Bloco A',
                code='BLK-A'
            )
            floor = Floor.objects.create(
                building=building,
                number=1,
                name='1º Andar'
            )
            kwargs['floor'] = floor
        
        defaults = {
            'code': 'T1-A-01',
            'status': Unit.STATUS_AVAILABLE,
            'area_bruta': 100.00,
        }
        defaults.update(kwargs)
        return Unit.objects.create(**defaults)
    return factory


@pytest.fixture
def user_factory():
    """Factory for creating User instances."""
    def factory(**kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        defaults = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
        defaults.update(kwargs)
        
        if 'password' not in defaults:
            user = User.objects.create_user(**defaults)
        else:
            password = defaults.pop('password')
            user = User.objects.create_user(password=password, **defaults)
        
        return user
    return factory


@pytest.fixture
def contract_factory():
    """Factory for creating Contract instances."""
    def factory(**kwargs):
        from apps.contracts.models import Contract
        from apps.crm.models import Lead
        from apps.inventory.models import Unit
        
        # Create dependencies if not provided
        if 'lead' not in kwargs:
            from apps.crm.models import Lead
            kwargs['lead'] = Lead.objects.create(
                first_name='Test',
                last_name='Client',
                email='client@example.com'
            )
        
        if 'unit' not in kwargs:
            from apps.inventory.models import Unit, Floor, Building
            from apps.projects.models import Project
            
            project = Project.objects.create(
                name='Test Project',
                slug='test-project'
            )
            building = Building.objects.create(
                project=project,
                name='Bloco A',
                code='BLK-A'
            )
            floor = Floor.objects.create(
                building=building,
                number=1
            )
            kwargs['unit'] = Unit.objects.create(
                floor=floor,
                code='T1-01',
                area_bruta=100
            )
        
        defaults = {
            'contract_number': 'IMO-2026-0001',
            'total_price_cve': 5000000,
            'status': Contract.STATUS_DRAFT,
        }
        defaults.update(kwargs)
        return Contract.objects.create(**defaults)
    return factory


@pytest.fixture
def reservation_factory():
    """Factory for creating UnitReservation instances."""
    def factory(**kwargs):
        from apps.crm.models import UnitReservation
        from datetime import timedelta
        from django.utils import timezone
        
        defaults = {
            'status': UnitReservation.STATUS_ACTIVE,
            'expires_at': timezone.now() + timedelta(hours=48),
            'deposit_amount_cve': 0,
        }
        defaults.update(kwargs)
        return UnitReservation.objects.create(**defaults)
    return factory


@pytest.fixture
def signature_request_factory():
    """Factory for creating SignatureRequest instances."""
    def factory(**kwargs):
        from apps.contracts.models import SignatureRequest
        from datetime import timedelta
        from django.utils import timezone
        
        defaults = {
            'status': SignatureRequest.STATUS_PENDING,
            'expires_at': timezone.now() + timedelta(hours=72),
        }
        defaults.update(kwargs)
        return SignatureRequest.objects.create(**defaults)
    return factory


@pytest.fixture
def task_factory():
    """Factory for creating ConstructionTask instances."""
    def factory(**kwargs):
        from apps.construction.models import ConstructionTask, ConstructionTask
        from apps.projects.models import Project
        from datetime import date
        
        # Create project if not provided
        if 'project' not in kwargs:
            kwargs['project'] = Project.objects.create(
                name='Test Project',
                slug='test-project'
            )
        
        defaults = {
            'name': 'Test Task',
            'wbs_code': '1.1',
            'status': ConstructionTask.STATUS_PENDING,
            'due_date': date(2026, 12, 31),
        }
        defaults.update(kwargs)
        return ConstructionTask.objects.create(**defaults)
    return factory


@pytest.fixture
def phase_factory():
    """Factory for creating ConstructionPhase instances."""
    def factory(**kwargs):
        from apps.construction.models import ConstructionPhase
        from apps.projects.models import Project
        from datetime import date
        
        # Create project if not provided
        if 'project' not in kwargs:
            kwargs['project'] = Project.objects.create(
                name='Test Project',
                slug='test-project'
            )
        
        defaults = {
            'name': 'Test Phase',
            'phase_type': 'FOUNDATION',
            'status': ConstructionPhase.STATUS_NOT_STARTED,
            'start_planned': date(2026, 6, 1),
            'end_planned': date(2026, 7, 1),
        }
        defaults.update(kwargs)
        return ConstructionPhase.objects.create(**defaults)
    return factory


@pytest.fixture
def payment_factory():
    """Factory for creating Payment instances."""
    def factory(**kwargs):
        from apps.contracts.models import Payment
        from datetime import date
        
        defaults = {
            'payment_type': Payment.PAYMENT_INSTALLMENT,
            'amount_cve': 100000,
            'due_date': date(2026, 7, 1),
            'status': Payment.STATUS_PENDING,
        }
        defaults.update(kwargs)
        return Payment.objects.create(**defaults)
    return factory
