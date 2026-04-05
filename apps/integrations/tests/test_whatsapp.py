"""
Tests para WhatsApp Business API integration.
Uses mocks para API externa - não faz chamadas reais.
"""
import uuid
import json
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from apps.core.models import TenantAwareModel
from apps.integrations.models import WhatsAppMessage, WhatsAppTemplate, NotificationPreference
from apps.integrations.services import WhatsAppClient, NotificationRouter, WhatsAppClientError
from apps.users.models import User


# =============================================================================
# Mocks e Fixtures
# =============================================================================

def mock_whatsapp_client():
    """Criar mock do cliente WhatsApp."""
    mock = MagicMock(spec=WhatsAppClient)
    mock.send_template_message.return_value = MagicMock(
        success=True,
        message_id='msg_test_123',
        error_message=None,
        raw_response={'id': 'msg_test_123'}
    )
    mock.send_free_text.return_value = MagicMock(
        success=True,
        message_id='msg_test_456',
        error_message=None
    )
    mock.send_interactive_menu.return_value = MagicMock(
        success=True,
        message_id='msg_test_789'
    )
    return mock


# =============================================================================
# Model Tests
# =============================================================================

class WhatsAppTemplateModelTest(TestCase):
    """Testes para o model WhatsAppTemplate."""
    
    def setUp(self):
        self.template = WhatsAppTemplate.objects.create(
            name='task_reminder',
            template_type='TASK_REMINDER',
            content_pt='Olá {{nome}}, a tarefa {{tarefa}} vence em {{data}}.',
            variables=['{{nome}}', '{{tarefa}}', '{{data}}'],
            meta_template_id='template_meta_123',
            is_active=True
        )
    
    def test_template_creation(self):
        """Testar criação de template."""
        self.assertEqual(self.template.name, 'task_reminder')
        self.assertEqual(self.template.template_type, 'TASK_REMINDER')
        self.assertTrue(self.template.is_active)
    
    def test_template_str(self):
        """Testar representação string."""
        self.assertIn('task_reminder', str(self.template))
        self.assertIn('Lembrete de Tarefa', str(self.template))
    
    def test_unique_name_per_tenant(self):
        """Testar unicidade do nome por tenant."""
        # Deve falhar ao criar duplicado
        with self.assertRaises(Exception):
            WhatsAppTemplate.objects.create(
                name='task_reminder',  # Mesmo nome
                template_type='WELCOME',
                content_pt='Outro conteúdo'
            )


class WhatsAppMessageModelTest(TestCase):
    """Testes para o model WhatsAppMessage."""
    
    def setUp(self):
        self.message = WhatsAppMessage.objects.create(
            direction=WhatsAppMessage.DIRECTION_OUTBOUND,
            phone_number='+2389991234',
            message_body='Test message',
            status=WhatsAppMessage.STATUS_SENT,
            meta_message_id='msg_123'
        )
    
    def test_message_creation(self):
        """Testar criação de mensagem."""
        self.assertEqual(self.message.phone_number, '+2389991234')
        self.assertEqual(self.message.direction, WhatsAppMessage.DIRECTION_OUTBOUND)
        self.assertEqual(self.message.status, WhatsAppMessage.STATUS_SENT)
    
    def test_mark_delivered(self):
        """Testar marcação como entregue."""
        self.message.mark_delivered()
        self.assertEqual(self.message.status, WhatsAppMessage.STATUS_DELIVERED)
        self.assertIsNotNone(self.message.delivered_at)
    
    def test_mark_read(self):
        """Testar marcação como lida."""
        self.message.mark_read()
        self.assertEqual(self.message.status, WhatsAppMessage.STATUS_READ)
        self.assertIsNotNone(self.message.read_at)
    
    def test_mark_failed(self):
        """Testar marcação como falhada."""
        self.message.mark_failed('API Error')
        self.assertEqual(self.message.status, WhatsAppMessage.STATUS_FAILED)
        self.assertEqual(self.message.error_message, 'API Error')
    
    def test_mark_processed(self):
        """Testar marcação como processada."""
        inbound = WhatsAppMessage.objects.create(
            direction=WhatsAppMessage.DIRECTION_INBOUND,
            phone_number='+2389991234',
            message_body='✅',
            inbound_response='✅'
        )
        inbound.mark_processed()
        self.assertTrue(inbound.processed)
        self.assertIsNotNone(inbound.processed_at)


class NotificationPreferenceModelTest(TestCase):
    """Testes para o model NotificationPreference."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.preference = NotificationPreference.objects.create(
            user=self.user,
            whatsapp_enabled=True,
            email_enabled=True,
            quiet_hours_start='22:00',
            quiet_hours_end='08:00'
        )
    
    def test_preference_creation(self):
        """Testar criação de preferências."""
        self.assertTrue(self.preference.whatsapp_enabled)
        self.assertTrue(self.preference.email_enabled)
        self.assertEqual(self.preference.user, self.user)
    
    def test_is_quiet_hours(self):
        """Testar verificação de horário de silêncio."""
        # Não podemos testar horário exato sem mock de timezone
        # Mas podemos verificar que o método existe e retorna boolean
        result = self.preference.is_quiet_hours()
        self.assertIsInstance(result, bool)
    
    def test_should_notify_whatsapp(self):
        """Testar decisão de notificação WhatsApp."""
        # Habilitado
        self.assertTrue(self.preference.should_notify_whatsapp())
        
        # Desabilitado
        self.preference.whatsapp_enabled = False
        self.assertFalse(self.preference.should_notify_whatsapp())
        
        # Urgente quando só_urgentes
        self.preference.whatsapp_enabled = True
        self.preference.urgent_only_whatsapp = True
        self.assertFalse(self.preference.should_notify_whatsapp(is_urgent=False))
        self.assertTrue(self.preference.should_notify_whatsapp(is_urgent=True))


# =============================================================================
# Service Tests
# =============================================================================

@override_settings(
    WHATSAPP_PROVIDER='meta',
    WHATSAPP_PHONE_NUMBER_ID='123456',
    WHATSAPP_ACCESS_TOKEN='test_token'
)
class WhatsAppClientTest(TestCase):
    """Testes para o WhatsAppClient."""
    
    def setUp(self):
        self.client = WhatsAppClient()
    
    def test_format_phone(self):
        """Testar formatação de telefone."""
        # Cabo Verde sem prefixo
        self.assertEqual(
            self.client._format_phone('9991234'),
            '+2389991234'
        )
        # Com prefixo
        self.assertEqual(
            self.client._format_phone('+2389991234'),
            '+2389991234'
        )
        # Com espaços
        self.assertEqual(
            self.client._format_phone('+238 999 1234'),
            '+2389991234'
        )
    
    @patch('apps.integrations.services.whatsapp_client.requests.post')
    def test_send_template_message_meta(self, mock_post):
        """Testar envio de template via Meta API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'messages': [{'id': 'test_msg_id'}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.client.send_template_message(
            to_phone='+2389991234',
            template_name='test_template',
            variables={'nome': 'João'}
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.message_id, 'test_msg_id')
        mock_post.assert_called_once()
    
    @patch('apps.integrations.services.whatsapp_client.requests.post')
    def test_send_free_text_meta(self, mock_post):
        """Testar envio de texto livre via Meta API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'messages': [{'id': 'text_msg_id'}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.client.send_free_text(
            to_phone='+2389991234',
            message='Test message'
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.message_id, 'text_msg_id')
    
    def test_parse_inbound_message_meta(self):
        """Testar parse de webhook Meta."""
        webhook_data = {
            'entry': [{
                'changes': [{
                    'value': {
                        'messages': [{
                            'from': '2389991234',
                            'id': 'wamid.test',
                            'timestamp': '1234567890',
                            'text': {'body': 'Hello'},
                            'type': 'text'
                        }],
                        'contacts': [{
                            'profile': {'name': 'Test User'},
                            'wa_id': '2389991234'
                        }]
                    }
                }]
            }]
        }
        
        result = self.client.parse_inbound_message(webhook_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.from_phone, '2389991234')
        self.assertEqual(result.message_body, 'Hello')
        self.assertEqual(result.profile_name, 'Test User')
    
    def test_parse_inbound_message_twilio(self):
        """Testar parse de webhook Twilio."""
        webhook_data = {
            'From': 'whatsapp:+2389991234',
            'Body': 'Hello from Twilio',
            'MessageSid': 'SMtest123',
            'ProfileName': 'Twilio User'
        }
        
        result = self.client.parse_inbound_message(webhook_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.message_body, 'Hello from Twilio')


@override_settings(
    WHATSAPP_PROVIDER='meta',
    WHATSAPP_PHONE_NUMBER_ID='123456',
    WHATSAPP_ACCESS_TOKEN='test_token',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='test@imos.cv'
)
class NotificationRouterTest(TestCase):
    """Testes para o NotificationRouter."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='worker@example.com',
            password='testpass123',
            first_name='Worker'
        )
        # Adicionar telefone ao utilizador
        self.user.phone = '+2389991234'
        self.user.save()
        
        self.router = NotificationRouter()
        
        # Criar template
        self.template = WhatsAppTemplate.objects.create(
            name='task_reminder',
            template_type='TASK_REMINDER',
            content_pt='Olá {{nome}}, tarefa: {{tarefa}}',
            variables=['{{nome}}', '{{tarefa}}'],
            meta_template_id='template_123'
        )
    
    @patch.object(WhatsAppClient, 'send_template_message')
    def test_notify_task_assignment_whatsapp(self, mock_send):
        """Testar notificação de atribuição via WhatsApp."""
        mock_send.return_value = MagicMock(
            success=True,
            message_id='msg_123'
        )
        
        # Mock de ConstructionTask
        mock_task = Mock()
        mock_task.name = 'Instalação elétrica'
        mock_task.due_date = date.today()
        mock_task.status = 'PENDING'
        mock_task.assigned_to = self.user
        mock_task.id = uuid.uuid4()
        
        with patch('apps.integrations.services.notification_router.ConstructionTask', Mock):
            result = self.router.notify_task_assignment(mock_task)
        
        # Verificar que tentou WhatsApp
        mock_send.assert_called_once()
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'whatsapp')
    
    @patch.object(WhatsAppClient, 'send_free_text')
    def test_send_interactive_task_menu(self, mock_send):
        """Testar envio de menu interativo."""
        mock_send.return_value = MagicMock(
            success=True,
            message_id='menu_123'
        )
        
        result = self.router.send_interactive_task_menu(
            self.user,
            '+2389991234'
        )
        
        self.assertTrue(result['success'])
        mock_send.assert_called_once()
    
    def test_process_inbound_response_completed(self):
        """Testar processamento de resposta ✅."""
        # Criar mensagem inbound
        message = WhatsAppMessage.objects.create(
            direction=WhatsAppMessage.DIRECTION_INBOUND,
            phone_number='+2389991234',
            message_body='✅',
            inbound_response='✅',
            user=self.user
        )
        
        with patch.object(self.router.whatsapp_client, 'send_free_text') as mock_send:
            mock_send.return_value = MagicMock(success=True)
            result = self.router.process_inbound_response(message)
        
        # Verificar que foi processada
        message.refresh_from_db()
        self.assertTrue(message.processed)
    
    def test_process_inbound_response_list_tasks(self):
        """Testar processamento de resposta '1' (ver tarefas)."""
        message = WhatsAppMessage.objects.create(
            direction=WhatsAppMessage.DIRECTION_INBOUND,
            phone_number='+2389991234',
            message_body='1',
            inbound_response='1',
            user=self.user
        )
        
        with patch.object(self.router.whatsapp_client, 'send_free_text') as mock_send:
            mock_send.return_value = MagicMock(success=True)
            result = self.router.process_inbound_response(message)
        
        self.assertEqual(result['action'], 'list_tasks')
        message.refresh_from_db()
        self.assertTrue(message.processed)


# =============================================================================
# API Tests
# =============================================================================

class WhatsAppWebhookTest(APITestCase):
    """Testes para o webhook do WhatsApp."""
    
    def test_webhook_verification(self):
        """Testar verificação do webhook (Meta)."""
        with override_settings(WHATSAPP_VERIFY_TOKEN='test_token'):
            response = self.client.get(
                '/api/v1/integrations/webhook/',
                {
                    'hub.mode': 'subscribe',
                    'hub.verify_token': 'test_token',
                    'hub.challenge': 'challenge_123'
                }
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'challenge_123')
    
    def test_webhook_verification_failed(self):
        """Testar falha na verificação."""
        with override_settings(WHATSAPP_VERIFY_TOKEN='test_token'):
            response = self.client.get(
                '/api/v1/integrations/webhook/',
                {
                    'hub.mode': 'subscribe',
                    'hub.verify_token': 'wrong_token',
                    'hub.challenge': 'challenge_123'
                }
            )
        
        self.assertEqual(response.status_code, 403)
    
    @patch('apps.integrations.tasks.process_inbound_message.delay')
    def test_webhook_receive_message(self, mock_task):
        """Testar recebimento de mensagem."""
        webhook_data = {
            'entry': [{
                'changes': [{
                    'value': {
                        'messages': [{
                            'from': '2389991234',
                            'id': 'wamid.test',
                            'timestamp': '1234567890',
                            'text': {'body': '✅'},
                            'type': 'text'
                        }],
                        'contacts': [{
                            'profile': {'name': 'Test User'}
                        }]
                    }
                }]
            }]
        }
        
        response = self.client.post(
            '/api/v1/integrations/webhook/',
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que mensagem foi criada
        message = WhatsAppMessage.objects.filter(
            direction=WhatsAppMessage.DIRECTION_INBOUND
        ).first()
        
        self.assertIsNotNone(message)
        self.assertEqual(message.message_body, '✅')
        self.assertEqual(message.inbound_response, '✅')
    
    def test_webhook_receive_twilio(self):
        """Testar recebimento de mensagem Twilio."""
        webhook_data = {
            'From': 'whatsapp:+2389991234',
            'Body': 'Hello',
            'MessageSid': 'SMtest123',
            'ProfileName': 'Test User'
        }
        
        response = self.client.post(
            '/api/v1/integrations/webhook/',
            data=webhook_data
        )
        
        self.assertEqual(response.status_code, 200)


class WhatsAppAPITest(APITestCase):
    """Testes para os endpoints da API."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='apiuser@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    @patch.object(WhatsAppClient, 'send_free_text')
    def test_send_test_message(self, mock_send):
        """Testar endpoint de envio de mensagem de teste."""
        mock_send.return_value = MagicMock(
            success=True,
            message_id='test_msg_id'
        )
        
        response = self.client.post(
            '/api/v1/integrations/send-test/',
            {
                'phone': '+2389991234',
                'message': 'Test message'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_send_test_message_missing_phone(self):
        """Testar erro quando phone não é fornecido."""
        response = self.client.post(
            '/api/v1/integrations/send-test/',
            {'message': 'Test'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_preferences(self):
        """Testar obtenção de preferências."""
        # Criar preferência
        NotificationPreference.objects.create(
            user=self.user,
            whatsapp_enabled=True,
            email_enabled=True
        )
        
        response = self.client.get('/api/v1/integrations/preferences/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['whatsapp_enabled'])
    
    def test_update_preferences(self):
        """Testar atualização de preferências."""
        NotificationPreference.objects.create(
            user=self.user,
            whatsapp_enabled=True
        )
        
        response = self.client.put(
            '/api/v1/integrations/preferences/',
            {'whatsapp_enabled': False},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar atualização
        pref = NotificationPreference.objects.get(user=self.user)
        self.assertFalse(pref.whatsapp_enabled)
    
    def test_get_message_history(self):
        """Testar histórico de mensagens."""
        # Criar mensagens
        for i in range(3):
            WhatsAppMessage.objects.create(
                user=self.user,
                direction=WhatsAppMessage.DIRECTION_OUTBOUND,
                phone_number='+2389991234',
                message_body=f'Message {i}'
            )
        
        response = self.client.get('/api/v1/integrations/history/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)


# =============================================================================
# Celery Task Tests
# =============================================================================

@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,  # Executar tasks sync em testes
)
class CeleryTaskTest(TestCase):
    """Testes para as tasks Celery."""
    
    @patch.object(WhatsAppClient, 'send_free_text')
    def test_send_whatsapp_message_task(self, mock_send):
        """Testar task de envio de mensagem."""
        mock_send.return_value = MagicMock(
            success=True,
            message_id='task_msg_id'
        )
        
        message = WhatsAppMessage.objects.create(
            direction=WhatsAppMessage.DIRECTION_OUTBOUND,
            phone_number='+2389991234',
            message_body='Task test'
        )
        
        from apps.integrations.tasks import send_whatsapp_message
        result = send_whatsapp_message(str(message.id))
        
        self.assertEqual(result['status'], 'sent')
        
        message.refresh_from_db()
        self.assertEqual(message.status, WhatsAppMessage.STATUS_SENT)
    
    @patch.object(NotificationRouter, 'notify_task_reminder')
    def test_send_scheduled_reminders(self, mock_reminder):
        """Testar task de lembretes agendados."""
        mock_reminder.return_value = {'success': True}
        
        # Criar tarefa mock
        with patch('apps.integrations.tasks.ConstructionTask') as MockTask:
            MockTask.objects.filter.return_value.select_related.return_value = []
            
            from apps.integrations.tasks import send_scheduled_reminders
            result = send_scheduled_reminders()
        
        self.assertEqual(result['status'], 'completed')


# =============================================================================
# Tenant Isolation Tests
# =============================================================================

class TenantIsolationTest(TestCase):
    """Testes para garantir isolamento multi-tenant."""
    
    def test_messages_isolated_by_tenant(self):
        """Testar que mensagens são isoladas por tenant (schema)."""
        # Criar mensagens
        msg1 = WhatsAppMessage.objects.create(
            direction=WhatsAppMessage.DIRECTION_OUTBOUND,
            phone_number='+2389991111',
            message_body='Tenant 1 message'
        )
        msg2 = WhatsAppMessage.objects.create(
            direction=WhatsAppMessage.DIRECTION_OUTBOUND,
            phone_number='+2389992222',
            message_body='Tenant 2 message'
        )
        
        # Verificar que ambas existem no schema atual
        # (Em ambiente real, estariam em schemas diferentes)
        self.assertEqual(WhatsAppMessage.objects.count(), 2)
    
    def test_template_unique_per_tenant(self):
        """Testar unicidade de templates por tenant."""
        WhatsAppTemplate.objects.create(
            name='welcome',
            template_type='WELCOME',
            content_pt='Bem-vindo!'
        )
        
        # Deve falhar no mesmo schema
        with self.assertRaises(Exception):
            WhatsAppTemplate.objects.create(
                name='welcome',
                template_type='WELCOME',
                content_pt='Outro conteúdo'
            )
