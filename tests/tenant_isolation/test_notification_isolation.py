"""
Testes de Isolamento: Notificações

Valida que notificações e mensagens estão isoladas por tenant.
"""
import uuid
from decimal import Decimal
from datetime import date

import pytest
from django.utils import timezone
from django_tenants.utils import tenant_context
from rest_framework import status

from apps.crm.models import Lead, WhatsAppTemplate, WhatsAppMessage


pytestmark = [pytest.mark.isolation, pytest.mark.django_db(transaction=True)]


class TestWhatsAppTemplateIsolation:
    """Testar isolamento de templates WhatsApp."""
    
    def test_whatsapp_template_not_visible_across_tenants(
        self, tenant_a, tenant_b
    ):
        """1. Template WhatsApp de tenant A não visível em B."""
        with tenant_context(tenant_a):
            template = WhatsAppTemplate.objects.create(
                name='boas_vindas',
                template_id_meta='template_meta_id_a',
                language='pt_PT',
                variables={'1': 'nome_cliente'},
                is_active=True,
            )
            template_id = template.id
        
        # Verificar não existe em tenant B
        with tenant_context(tenant_b):
            templates = WhatsAppTemplate.objects.filter(id=template_id)
            assert templates.count() == 0
    
    def test_whatsapp_template_same_name_allowed(
        self, tenant_a, tenant_b
    ):
        """2. Mesmo nome de template permitido em tenants diferentes."""
        template_name = 'template_vendas'
        
        with tenant_context(tenant_a):
            template_a = WhatsAppTemplate.objects.create(
                name=template_name,
                template_id_meta='meta_id_a',
                language='pt_PT',
                is_active=True,
            )
        
        with tenant_context(tenant_b):
            template_b = WhatsAppTemplate.objects.create(
                name=template_name,
                template_id_meta='meta_id_b',
                language='pt_PT',
                is_active=True,
            )
            
            assert template_a.id != template_b.id
            assert template_a.template_id_meta != template_b.template_id_meta


class TestWhatsAppMessageIsolation:
    """Testar isolamento de mensagens WhatsApp."""
    
    def test_whatsapp_message_not_visible_across_tenants(
        self, tenant_a, tenant_b
    ):
        """1. Mensagem WhatsApp de tenant A não visível em B."""
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='João',
                last_name='Silva',
                email='joao@a.cv',
                phone='+2389991111',
            )
            
            template = WhatsAppTemplate.objects.create(
                name='mensagem_teste',
                template_id_meta='meta_id',
                language='pt_PT',
            )
            
            message = WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone='+2389991111',
                payload={'text': 'Olá João'},
                status=WhatsAppMessage.STATUS_SENT,
                message_id_meta='wamid.123',
            )
            message_id = message.id
        
        # Verificar não existe em tenant B
        with tenant_context(tenant_b):
            messages = WhatsAppMessage.objects.filter(id=message_id)
            assert messages.count() == 0
    
    def test_whatsapp_message_status_isolated(
        self, tenant_a, tenant_b
    ):
        """2. Status de mensagem é isolado entre tenants."""
        phone_number = '+2389999999'
        
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='Cliente',
                last_name='A',
                email='cliente@a.cv',
                phone=phone_number,
            )
            
            message = WhatsAppMessage.objects.create(
                lead=lead,
                phone=phone_number,
                payload={'text': 'Mensagem A'},
                status=WhatsAppMessage.STATUS_SENT,
            )
        
        with tenant_context(tenant_b):
            lead_b = Lead.objects.create(
                first_name='Cliente',
                last_name='B',
                email='cliente@b.cv',
                phone=phone_number,  # Mesmo número!
            )
            
            message_b = WhatsAppMessage.objects.create(
                lead=lead_b,
                phone=phone_number,
                payload={'text': 'Mensagem B'},
                status=WhatsAppMessage.STATUS_DELIVERED,  # Status diferente
            )
            
            # Mensagens devem ser diferentes
            assert message.id != message_b.id
            assert message_b.status == WhatsAppMessage.STATUS_DELIVERED
        
        # Verificar que mensagem A ainda está SENT
        with tenant_context(tenant_a):
            message.refresh_from_db()
            assert message.status == WhatsAppMessage.STATUS_SENT
    
    def test_whatsapp_message_history_isolated(
        self, tenant_a, tenant_b
    ):
        """3. Histórico de mensagens é isolado entre tenants."""
        phone_number = '+2389998888'
        
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='Lead',
                last_name='A',
                email='lead@a.cv',
                phone=phone_number,
            )
            
            # Criar múltiplas mensagens
            for i in range(5):
                WhatsAppMessage.objects.create(
                    lead=lead,
                    phone=phone_number,
                    payload={'text': f'Mensagem {i}'},
                    status=WhatsAppMessage.STATUS_DELIVERED,
                )
            
            count_a = WhatsAppMessage.objects.filter(lead=lead).count()
            assert count_a == 5
        
        with tenant_context(tenant_b):
            lead_b = Lead.objects.create(
                first_name='Lead',
                last_name='B',
                email='lead@b.cv',
                phone=phone_number,
            )
            
            # Contar mensagens
            count_b = WhatsAppMessage.objects.filter(lead=lead_b).count()
            assert count_b == 0
            
            # Criar mensagens em B
            for i in range(3):
                WhatsAppMessage.objects.create(
                    lead=lead_b,
                    phone=phone_number,
                    payload={'text': f'Mensagem B{i}'},
                    status=WhatsAppMessage.STATUS_SENT,
                )
            
            count_b = WhatsAppMessage.objects.filter(lead=lead_b).count()
            assert count_b == 3


class TestEmailNotificationIsolation:
    """Testar isolamento de notificações por email."""
    
    def test_email_notification_model_isolated(
        self, tenant_a, tenant_b
    ):
        """1. Notificações por email são isoladas."""
        from apps.notifications.models import EmailNotification
        
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='Cliente',
                last_name='A',
                email='cliente@a.cv',
            )
            
            notification = EmailNotification.objects.create(
                recipient=lead.email,
                subject='Bem-vindo',
                body='Conteúdo do email A',
                status='SENT',
            )
            notification_id = notification.id
        
        # Verificar não existe em tenant B
        with tenant_context(tenant_b):
            notifications = EmailNotification.objects.filter(id=notification_id)
            assert notifications.count() == 0


class TestPushNotificationIsolation:
    """Testar isolamento de push notifications."""
    
    def test_push_notification_model_isolated(
        self, tenant_a, tenant_b
    ):
        """1. Push notifications são isoladas."""
        from apps.notifications.models import PushNotification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        with tenant_context(tenant_a):
            user = User.objects.create_user(
                email='user@a.cv',
                password='testpass123!',
            )
            
            notification = PushNotification.objects.create(
                user=user,
                title='Nova Tarefa',
                body='Você tem uma nova tarefa A',
                status='SENT',
            )
            notification_id = notification.id
        
        # Verificar não existe em tenant B
        with tenant_context(tenant_b):
            notifications = PushNotification.objects.filter(id=notification_id)
            assert notifications.count() == 0


class TestNotificationAPICrossTenantAccess:
    """Testar acesso cross-tenant via API de notificações."""
    
    def test_api_cannot_access_messages_from_other_tenant(
        self, api_client_tenant_a, tenant_b
    ):
        """1. API não pode aceder mensagens de outro tenant."""
        with tenant_context(tenant_b):
            lead = Lead.objects.create(
                first_name='Lead',
                last_name='B',
                email='lead@b.cv',
                phone='+2389997777',
            )
            
            message = WhatsAppMessage.objects.create(
                lead=lead,
                phone=lead.phone,
                payload={'text': 'Mensagem B'},
                status=WhatsAppMessage.STATUS_SENT,
            )
            message_id = message.id
        
        # Tentar aceder via API de tenant A
        response = api_client_tenant_a.get(
            f'/api/v1/crm/whatsapp/messages/{message_id}/'
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_api_cannot_list_other_tenant_messages(
        self, api_client_tenant_b, tenant_a
    ):
        """2. API não pode listar mensagens de outro tenant."""
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='Lead',
                last_name='A',
                email='lead@a.cv',
                phone='+2389996666',
            )
            
            for i in range(10):
                WhatsAppMessage.objects.create(
                    lead=lead,
                    phone=lead.phone,
                    payload={'text': f'Mensagem {i}'},
                    status=WhatsAppMessage.STATUS_SENT,
                )
        
        # Listar mensagens via API de tenant B
        response = api_client_tenant_b.get('/api/v1/crm/whatsapp/messages/')
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                messages = data['results']
            else:
                messages = data
            
            # Não deve conter mensagens do tenant A
            for msg in messages:
                assert 'Mensagem ' not in str(msg.get('payload', ''))


class TestWebhookIsolation:
    """Testar isolamento de webhooks de notificação."""
    
    def test_webhook_update_isolated(
        self, tenant_a, tenant_b
    ):
        """1. Webhook de status só atualiza mensagem do próprio tenant."""
        message_id_meta = 'wamid.test123'
        
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='Lead',
                last_name='A',
                email='lead@a.cv',
                phone='+2389995555',
            )
            
            message_a = WhatsAppMessage.objects.create(
                lead=lead,
                phone=lead.phone,
                payload={'text': 'Mensagem A'},
                status=WhatsAppMessage.STATUS_SENT,
                message_id_meta=message_id_meta,
            )
        
        with tenant_context(tenant_b):
            lead_b = Lead.objects.create(
                first_name='Lead',
                last_name='B',
                email='lead@b.cv',
                phone='+2389994444',
            )
            
            message_b = WhatsAppMessage.objects.create(
                lead=lead_b,
                phone=lead_b.phone,
                payload={'text': 'Mensagem B'},
                status=WhatsAppMessage.STATUS_SENT,
                message_id_meta=message_id_meta,  # Mesmo ID meta!
            )
        
        # Simular webhook de entrega
        with tenant_context(tenant_a):
            # Atualizar mensagem A
            message_a.status = WhatsAppMessage.STATUS_DELIVERED
            message_a.delivered_at = timezone.now()
            message_a.save()
        
        # Verificar isolamento
        with tenant_context(tenant_a):
            message_a.refresh_from_db()
            assert message_a.status == WhatsAppMessage.STATUS_DELIVERED
        
        with tenant_context(tenant_b):
            message_b.refresh_from_db()
            # Mensagem B ainda deve estar SENT
            assert message_b.status == WhatsAppMessage.STATUS_SENT


class TestNotificationTemplateVariables:
    """Testar isolamento de variáveis em templates."""
    
    def test_template_variables_isolated(
        self, tenant_a, tenant_b
    ):
        """1. Variáveis de template são isoladas."""
        with tenant_context(tenant_a):
            template_a = WhatsAppTemplate.objects.create(
                name='personalizado',
                template_id_meta='meta_a',
                language='pt_PT',
                variables={
                    '1': 'nome_cliente',
                    '2': 'nome_vendedor',
                    '3': 'valor_proposta',
                },
            )
        
        with tenant_context(tenant_b):
            template_b = WhatsAppTemplate.objects.create(
                name='personalizado',
                template_id_meta='meta_b',
                language='pt_PT',
                variables={
                    '1': 'nome_cliente',
                    '2': 'numero_contrato',  # Variável diferente!
                },
            )
            
            # Variáveis devem ser diferentes
            assert 'nome_vendedor' in template_a.variables.values()
            assert 'nome_vendedor' not in template_b.variables.values()
            assert 'numero_contrato' in template_b.variables.values()
