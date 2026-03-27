"""
Tests for apps/crm/tasks.py

Coverage:
  1. Task skips when WHATSAPP_ENABLED=False
  2. Task sends message and returns sent=True when enabled
  3. Message body contains lead name and typology
  4. Task returns lead_not_found when lead does not exist
  5. Task calls self.retry() on requests.RequestException
  6. LeadCaptureView triggers the task after successful lead creation
"""
import pytest
from unittest.mock import MagicMock, patch

import requests as req
from django_tenants.utils import tenant_context


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_lead(tenant, **kwargs):
    from apps.crm.models import Lead
    defaults = dict(first_name='Ana', last_name='Gomes', email='ana@test.cv', source='WEB')
    defaults.update(kwargs)
    with tenant_context(tenant):
        return Lead.objects.create(**defaults)


def _whatsapp_settings(settings):
    settings.WHATSAPP_ENABLED = True
    settings.WHATSAPP_API_URL = 'https://api.whatsapp.test/send'
    settings.WHATSAPP_API_TOKEN = 'test-token'
    settings.WHATSAPP_SALES_NUMBER = '+2389XXXXXXXX'


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestNotifyWhatsappNewLead:

    def test_skips_when_whatsapp_disabled(self, tenant_a, settings):
        from apps.crm.tasks import notify_whatsapp_new_lead

        settings.WHATSAPP_ENABLED = False
        lead = _create_lead(tenant_a)

        result = notify_whatsapp_new_lead(
            tenant_schema=tenant_a.schema_name,
            lead_id=str(lead.id),
        )

        assert result == {'skipped': True}

    def test_sends_message_and_returns_sent(self, tenant_a, settings):
        from apps.crm.tasks import notify_whatsapp_new_lead

        _whatsapp_settings(settings)
        lead = _create_lead(tenant_a)

        with patch('apps.crm.tasks.requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            result = notify_whatsapp_new_lead(
                tenant_schema=tenant_a.schema_name,
                lead_id=str(lead.id),
            )

        assert result == {'sent': True, 'lead_id': str(lead.id)}
        mock_post.assert_called_once()

    def test_message_body_contains_lead_details(self, tenant_a, settings):
        from apps.crm.tasks import notify_whatsapp_new_lead

        _whatsapp_settings(settings)
        lead = _create_lead(
            tenant_a,
            first_name='João',
            last_name='Silva',
            phone='+2389111222',
            preferred_typology='T3',
            budget=15000000,
        )

        with patch('apps.crm.tasks.requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            notify_whatsapp_new_lead(
                tenant_schema=tenant_a.schema_name,
                lead_id=str(lead.id),
            )

        body = mock_post.call_args.kwargs['json']['body']
        assert 'João' in body
        assert 'T3' in body
        assert '+2389111222' in body
        assert '15' in body  # budget in message

    def test_returns_lead_not_found_for_missing_lead(self, tenant_a, settings):
        import uuid
        from apps.crm.tasks import notify_whatsapp_new_lead

        _whatsapp_settings(settings)

        result = notify_whatsapp_new_lead(
            tenant_schema=tenant_a.schema_name,
            lead_id=str(uuid.uuid4()),
        )

        assert result == {'error': 'lead_not_found'}

    def test_calls_retry_on_connection_error(self, tenant_a, settings):
        from celery.exceptions import Retry as CeleryRetry

        from apps.crm.tasks import notify_whatsapp_new_lead

        _whatsapp_settings(settings)
        lead = _create_lead(tenant_a)

        with patch('apps.crm.tasks.requests.post', side_effect=req.ConnectionError('timeout')):
            # Patch self.retry so it raises CeleryRetry immediately (avoids 5 real retries)
            with patch.object(
                notify_whatsapp_new_lead,
                'retry',
                side_effect=CeleryRetry(),
            ) as mock_retry:
                with pytest.raises(CeleryRetry):
                    notify_whatsapp_new_lead(
                        tenant_schema=tenant_a.schema_name,
                        lead_id=str(lead.id),
                    )

        mock_retry.assert_called_once()
        # Verify countdown uses exponential back-off
        assert mock_retry.call_args.kwargs.get('countdown', 0) >= 30


@pytest.mark.django_db
class TestLeadCaptureViewTriggersTask:

    def test_task_is_queued_after_lead_capture(self, tenant_a):
        from rest_framework.test import APIClient

        client = APIClient()
        client.defaults['HTTP_HOST'] = 'empresa-a.imos.cv'

        with patch('apps.crm.tasks.notify_whatsapp_new_lead.delay') as mock_delay:
            response = client.post(
                '/api/v1/crm/lead-capture/',
                {
                    'first_name': 'Maria',
                    'last_name': 'Ferreira',
                    'email': 'maria@test.cv',
                    'source': 'WEB',
                },
                format='json',
            )

        assert response.status_code == 201
        mock_delay.assert_called_once()

        kwargs = mock_delay.call_args.kwargs
        assert kwargs['tenant_schema'] == tenant_a.schema_name
        assert 'lead_id' in kwargs

    def test_lead_id_in_task_matches_created_lead(self, tenant_a):
        from apps.crm.models import Lead
        from rest_framework.test import APIClient

        client = APIClient()
        client.defaults['HTTP_HOST'] = 'empresa-a.imos.cv'

        with patch('apps.crm.tasks.notify_whatsapp_new_lead.delay') as mock_delay:
            client.post(
                '/api/v1/crm/lead-capture/',
                {'first_name': 'Carlos', 'last_name': 'Veiga', 'email': 'cv@test.cv', 'source': 'INSTAGRAM'},
                format='json',
            )

        lead_id = mock_delay.call_args.kwargs['lead_id']
        with tenant_context(tenant_a):
            assert Lead.objects.filter(id=lead_id).exists()
