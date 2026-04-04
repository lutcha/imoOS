"""
Tests for tenant provision API — Sprint 9 P02.
POST /api/v1/superadmin/tenants/provision/

Covers:
  - test_provision_creates_tenant_and_schema
  - test_provision_idempotent
  - test_provision_rejects_invalid_schema_name
  - test_provision_requires_staff
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

PROVISION_URL = '/api/v1/superadmin/tenants/provision/'
PLATFORM_HOST = 'proptech.cv'

User = get_user_model()


@pytest.fixture
def staff_client(db):
    """APIClient authenticated as a staff user in the public schema."""
    from apps.tenants.models import Client, Domain
    # Ensure a public/platform domain exists for routing
    try:
        public_tenant = Client.objects.get(schema_name='public')
    except Client.DoesNotExist:
        pytest.skip('Public tenant not set up — run ensure_public_tenant first')

    user = User.objects.create_user(
        email='superadmin@proptech.cv',
        password='SuperSecret123!',
        is_staff=True,
    )
    refresh = RefreshToken.for_user(user)
    refresh['is_staff'] = True
    refresh['tenant_schema'] = 'public'

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    client.defaults['HTTP_HOST'] = PLATFORM_HOST
    return client


@pytest.fixture
def regular_client(db):
    """APIClient authenticated as a non-staff user."""
    from apps.tenants.models import Client
    try:
        Client.objects.get(schema_name='public')
    except Client.DoesNotExist:
        pytest.skip('Public tenant not set up')

    user = User.objects.create_user(
        email='regular@proptech.cv',
        password='Regular123!',
        is_staff=False,
    )
    refresh = RefreshToken.for_user(user)
    refresh['tenant_schema'] = 'public'

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    client.defaults['HTTP_HOST'] = PLATFORM_HOST
    return client


VALID_PAYLOAD = {
    'schema_name': 'test_nova_empresa',
    'name': 'Nova Empresa Lda',
    'domain': 'nova-empresa.proptech.cv',
    'plan': 'starter',
    'contact_email': 'admin@nova-empresa.cv',
    'country': 'CV',
}


@pytest.mark.django_db(transaction=True)
def test_provision_creates_tenant_and_schema(staff_client):
    """Successful provision returns 201 with tenant_id and schema_name."""
    with patch('apps.tenants.views.call_command', return_value='created') as mock_cmd:
        # Also mock Client.objects.get to return a fake tenant after 'creation'
        from apps.tenants.models import Client, Domain, TenantSettings
        import uuid

        fake_tenant = MagicMock(spec=Client)
        fake_tenant.id = uuid.uuid4()
        fake_tenant.schema_name = VALID_PAYLOAD['schema_name']
        fake_tenant.name = VALID_PAYLOAD['name']
        fake_tenant.plan = VALID_PAYLOAD['plan']

        with patch.object(Client.objects, 'get', return_value=fake_tenant):
            resp = staff_client.post(PROVISION_URL, VALID_PAYLOAD, format='json')

    assert resp.status_code == 201
    data = resp.json()
    assert data['schema_name'] == VALID_PAYLOAD['schema_name']
    assert data['status'] == 'created'
    assert 'tenant_id' in data

    mock_cmd.assert_called_once_with(
        'provision_tenant',
        schema=VALID_PAYLOAD['schema_name'],
        name=VALID_PAYLOAD['name'],
        domain=VALID_PAYLOAD['domain'],
        plan=VALID_PAYLOAD['plan'],
        contact_email=VALID_PAYLOAD['contact_email'],
        country=VALID_PAYLOAD['country'],
        stdout=mock_cmd.call_args.kwargs['stdout'],
        stderr=mock_cmd.call_args.kwargs['stderr'],
    )


@pytest.mark.django_db(transaction=True)
def test_provision_idempotent(staff_client):
    """Second call for an existing tenant returns 200 with already_exists."""
    from apps.tenants.models import Client
    import uuid

    fake_tenant = MagicMock(spec=Client)
    fake_tenant.id = uuid.uuid4()
    fake_tenant.schema_name = VALID_PAYLOAD['schema_name']
    fake_tenant.name = VALID_PAYLOAD['name']
    fake_tenant.plan = VALID_PAYLOAD['plan']

    with patch('apps.tenants.views.call_command', return_value='already_exists'):
        with patch.object(Client.objects, 'get', return_value=fake_tenant):
            resp = staff_client.post(PROVISION_URL, VALID_PAYLOAD, format='json')

    assert resp.status_code == 200
    assert resp.json()['status'] == 'already_exists'


@pytest.mark.django_db
def test_provision_rejects_invalid_schema_name(staff_client):
    """Schema names with uppercase, spaces, or leading digits are rejected."""
    bad_names = [
        'UpperCase',
        'has space',
        '1starts_with_digit',
        'ab',            # too short (< 3 chars)
        'a' * 51,        # too long (> 50 chars)
        'has-hyphen',
    ]
    for bad in bad_names:
        payload = {**VALID_PAYLOAD, 'schema_name': bad}
        resp = staff_client.post(PROVISION_URL, payload, format='json')
        assert resp.status_code == 400, f"Expected 400 for schema_name={bad!r}, got {resp.status_code}"
        assert 'schema_name' in resp.json(), f"Expected schema_name error for {bad!r}"


@pytest.mark.django_db
def test_provision_requires_staff(regular_client):
    """Non-staff users receive 403."""
    resp = regular_client.post(PROVISION_URL, VALID_PAYLOAD, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_provision_requires_auth():
    """Unauthenticated requests receive 401."""
    client = APIClient()
    client.defaults['HTTP_HOST'] = PLATFORM_HOST
    resp = client.post(PROVISION_URL, VALID_PAYLOAD, format='json')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_provision_rejects_base_domain(staff_client):
    """Provisioning with domain == TENANT_BASE_DOMAIN is rejected."""
    from django.conf import settings
    base = getattr(settings, 'TENANT_BASE_DOMAIN', 'proptech.cv')
    payload = {**VALID_PAYLOAD, 'domain': base}

    with patch('apps.tenants.views.call_command', return_value='created'):
        resp = staff_client.post(PROVISION_URL, payload, format='json')

    assert resp.status_code == 400
    assert 'domain' in resp.json()
