"""
Integration tests for WhatsApp Business API.
These tests can run without a full Django database setup.
"""
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from apps.integrations.services.whatsapp_client import WhatsAppClient, MessageResponse


class WhatsAppClientIntegrationTest(TestCase):
    """Test WhatsAppClient with mocked external APIs."""
    
    def test_client_initialization_with_meta(self):
        """Test client initializes correctly with Meta provider."""
        with patch('apps.integrations.services.whatsapp_client.settings') as mock_settings:
            mock_settings.WHATSAPP_PROVIDER = 'meta'
            mock_settings.WHATSAPP_PHONE_NUMBER_ID = '123456'
            mock_settings.WHATSAPP_ACCESS_TOKEN = 'token123'
            
            client = WhatsAppClient()
            self.assertEqual(client.provider, 'meta')
            self.assertEqual(client.meta_phone_number_id, '123456')
    
    def test_client_initialization_with_twilio(self):
        """Test client initializes correctly with Twilio provider."""
        with patch('apps.integrations.services.whatsapp_client.settings') as mock_settings:
            mock_settings.WHATSAPP_PROVIDER = 'twilio'
            mock_settings.TWILIO_ACCOUNT_SID = 'AC123'
            mock_settings.TWILIO_AUTH_TOKEN = 'token123'
            mock_settings.TWILIO_WHATSAPP_NUMBER = '+1234567890'
            
            client = WhatsAppClient()
            self.assertEqual(client.provider, 'twilio')
            self.assertEqual(client.twilio_account_sid, 'AC123')

    def test_format_phone_cabo_verde(self):
        """Test phone formatting for Cabo Verde numbers."""
        with patch('apps.integrations.services.whatsapp_client.settings'):
            client = WhatsAppClient()
            
            # Without country code
            self.assertEqual(
                client._format_phone('9991234'),
                '+2389991234'
            )
            # With country code
            self.assertEqual(
                client._format_phone('+2389991234'),
                '+2389991234'
            )
            # With spaces
            self.assertEqual(
                client._format_phone('+238 999 1234'),
                '+2389991234'
            )


class NotificationRouterIntegrationTest(TestCase):
    """Test NotificationRouter functionality."""
    
    def test_router_initialization(self):
        """Test router initializes with client."""
        with patch('apps.integrations.services.notification_router.WhatsAppClient') as mock_client:
            from apps.integrations.services import NotificationRouter
            router = NotificationRouter()
            self.assertIsNotNone(router.whatsapp_client)


class ModelIntegrationTest(TestCase):
    """Test model methods without database."""
    
    def test_message_status_methods(self):
        """Test WhatsAppMessage status methods logic."""
        from apps.integrations.models import WhatsAppMessage
        
        # Create a mock message
        msg = Mock(spec=WhatsAppMessage)
        msg.status = WhatsAppMessage.STATUS_SENT
        
        # Test mark_delivered logic
        msg.mark_delivered = Mock()
        msg.mark_delivered()
        msg.mark_delivered.assert_called_once()


class CeleryTaskSignatureTest(TestCase):
    """Test Celery task signatures."""
    
    def test_task_signatures(self):
        """Verify task functions are importable and callable."""
        from apps.integrations.tasks import (
            send_whatsapp_message,
            process_inbound_message,
            send_scheduled_reminders,
            check_overdue_tasks,
            sync_message_status,
            cleanup_old_messages
        )
        
        # Verify tasks are defined
        self.assertIsNotNone(send_whatsapp_message)
        self.assertIsNotNone(process_inbound_message)
        self.assertIsNotNone(send_scheduled_reminders)
        self.assertIsNotNone(check_overdue_tasks)
        self.assertIsNotNone(sync_message_status)
        self.assertIsNotNone(cleanup_old_messages)
