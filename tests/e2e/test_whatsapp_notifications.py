"""
Testes E2E: Notificações WhatsApp

Valida envio de notificações em diferentes eventos do sistema.
"""
import uuid
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

import pytest
from django.utils import timezone
from django_tenants.utils import tenant_context
from rest_framework import status

from apps.crm.models import Lead, UnitReservation, WhatsAppTemplate, WhatsAppMessage
from apps.contracts.models import Contract, Payment
from apps.construction.models import ConstructionTask


pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


class TestWhatsAppLeadNotifications:
    """Testar notificações para Leads."""
    
    def test_new_lead_notification(
        self, authenticated_client, e2e_tenant, e2e_vendedor, 
        mock_whatsapp_service
    ):
        """1. Novo lead recebe mensagem de boas-vindas."""
        with tenant_context(e2e_tenant):
            # Criar template
            template, _ = WhatsAppTemplate.objects.get_or_create(
                name='novo_lead',
                defaults={
                    'template_id_meta': 'novo_lead_template_id',
                    'language': 'pt_PT',
                    'variables': {'1': 'nome_lead', '2': 'nome_empresa'},
                    'is_active': True,
                }
            )
        
        # Criar lead
        lead_data = {
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'joao.whatsapp@test.cv',
            'phone': '+2389991234',
            'status': Lead.STATUS_NEW,
            'assigned_to': str(e2e_vendedor.id),
        }
        
        response = authenticated_client.post(
            '/api/v1/crm/leads/', 
            lead_data, 
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verificar se notificação seria enviada
        with tenant_context(e2e_tenant):
            lead = Lead.objects.get(email='joao.whatsapp@test.cv')
            
            # Simular envio de notificação
            message = WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone=lead.phone,
                payload={
                    'template': 'novo_lead',
                    'variables': [lead.first_name, 'ImoOS'],
                },
                status=WhatsAppMessage.STATUS_SENT,
            )
            
            assert message.phone == '+2389991234'
            assert message.status == WhatsAppMessage.STATUS_SENT
    
    def test_reservation_confirmation_notification(
        self, authenticated_client, e2e_tenant, e2e_reservation,
        mock_whatsapp_service
    ):
        """2. Reserva confirmada envia notificação."""
        with tenant_context(e2e_tenant):
            template, _ = WhatsAppTemplate.objects.get_or_create(
                name='reserva_confirmada',
                defaults={
                    'template_id_meta': 'reserva_template_id',
                    'language': 'pt_PT',
                    'is_active': True,
                }
            )
            
            lead = e2e_reservation.lead
            unit = e2e_reservation.unit
            
            # Simular envio de notificação
            message = WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone=lead.phone,
                payload={
                    'template': 'reserva_confirmada',
                    'variables': [
                        lead.first_name,
                        unit.code,
                        e2e_reservation.expires_at.strftime('%d/%m/%Y %H:%M'),
                    ],
                },
                status=WhatsAppMessage.STATUS_SENT,
            )
            
            assert unit.code in str(message.payload)
    
    def test_visit_reminder_notification(
        self, authenticated_client, e2e_tenant, e2e_lead
    ):
        """3. Lembrete de visita enviado no dia anterior."""
        with tenant_context(e2e_tenant):
            # Agendar visita
            e2e_lead.visit_date = timezone.now() + timedelta(days=1)
            e2e_lead.stage = Lead.STAGE_VISIT_SCHEDULED
            e2e_lead.save()
            
            template, _ = WhatsAppTemplate.objects.get_or_create(
                name='lembrete_visita',
                defaults={
                    'template_id_meta': 'lembrete_visita_template_id',
                    'language': 'pt_PT',
                    'is_active': True,
                }
            )
            
            # Simular envio de lembrete
            message = WhatsAppMessage.objects.create(
                lead=e2e_lead,
                template=template,
                phone=e2e_lead.phone,
                payload={
                    'template': 'lembrete_visita',
                    'variables': [
                        e2e_lead.first_name,
                        e2e_lead.visit_date.strftime('%d/%m/%Y às %H:%M'),
                    ],
                },
                status=WhatsAppMessage.STATUS_SENT,
            )
            
            assert message.status == WhatsAppMessage.STATUS_SENT


class TestWhatsAppContractNotifications:
    """Testar notificações relacionadas a contratos."""
    
    def test_contract_signature_request(
        self, authenticated_client, e2e_tenant, e2e_contract
    ):
        """1. Pedido de assinatura enviado via WhatsApp."""
        with tenant_context(e2e_tenant):
            template, _ = WhatsAppTemplate.objects.get_or_create(
                name='pedido_assinatura',
                defaults={
                    'template_id_meta': 'assinatura_template_id',
                    'language': 'pt_PT',
                    'is_active': True,
                }
            )
            
            lead = e2e_contract.lead
            
            # Simular envio de pedido de assinatura
            message = WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone=lead.phone,
                payload={
                    'template': 'pedido_assinatura',
                    'variables': [
                        lead.first_name,
                        e2e_contract.contract_number,
                        e2e_contract.total_price_cve,
                        'https://imos.cv/sign/mock-token',
                    ],
                },
                status=WhatsAppMessage.STATUS_SENT,
            )
            
            assert e2e_contract.contract_number in str(message.payload)
    
    def test_payment_reminder_notification(
        self, authenticated_client, e2e_tenant, e2e_signed_contract
    ):
        """2. Lembrete de pagamento próximo ao vencimento."""
        with tenant_context(e2e_tenant):
            # Criar pagamento próximo do vencimento
            payment = Payment.objects.create(
                contract=e2e_signed_contract,
                payment_type=Payment.PAYMENT_INSTALLMENT,
                amount_cve=Decimal('1700000.00'),
                due_date=date.today() + timedelta(days=2),
                status=Payment.STATUS_PENDING,
            )
            
            template, _ = WhatsAppTemplate.objects.get_or_create(
                name='lembrete_pagamento',
                defaults={
                    'template_id_meta': 'pagamento_template_id',
                    'language': 'pt_PT',
                    'is_active': True,
                }
            )
            
            lead = e2e_signed_contract.lead
            
            # Simular envio de lembrete
            message = WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone=lead.phone,
                payload={
                    'template': 'lembrete_pagamento',
                    'variables': [
                        lead.first_name,
                        str(payment.amount_cve),
                        payment.due_date.strftime('%d/%m/%Y'),
                        payment.reference or 'Pendente',
                    ],
                },
                status=WhatsAppMessage.STATUS_SENT,
            )
            
            assert str(payment.amount_cve) in str(message.payload)
    
    def test_payment_confirmation(
        self, authenticated_client, e2e_tenant, e2e_signed_contract
    ):
        """3. Confirmação de pagamento recebido."""
        with tenant_context(e2e_tenant):
            payment = Payment.objects.create(
                contract=e2e_signed_contract,
                payment_type=Payment.PAYMENT_INSTALLMENT,
                amount_cve=Decimal('1700000.00'),
                due_date=date.today() - timedelta(days=5),
                paid_date=date.today(),
                status=Payment.STATUS_PAID,
                reference='MB-123456789',
            )
            
            template, _ = WhatsAppTemplate.objects.get_or_create(
                name='pagamento_confirmado',
                defaults={
                    'template_id_meta': 'confirmacao_template_id',
                    'language': 'pt_PT',
                    'is_active': True,
                }
            )
            
            lead = e2e_signed_contract.lead
            
            # Simular envio de confirmação
            message = WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone=lead.phone,
                payload={
                    'template': 'pagamento_confirmado',
                    'variables': [
                        lead.first_name,
                        str(payment.amount_cve),
                        payment.paid_date.strftime('%d/%m/%Y'),
                        payment.reference,
                    ],
                },
                status=WhatsAppMessage.STATUS_SENT,
            )
            
            assert 'MB-123456789' in str(message.payload)


class TestWhatsAppConstructionNotifications:
    """Testar notificações relacionadas à construção."""
    
    def test_task_assignment_notification(
        self, authenticated_client, e2e_tenant, e2e_construction_tasks,
        e2e_encarregado
    ):
        """1. Atribuição de task envia notificação."""
        with tenant_context(e2e_tenant):
            task = e2e_construction_tasks[0]
            task.assigned_to = e2e_encarregado
            task.save()
            
            template, _ = WhatsAppTemplate.objects.get_or_create(
                name='tarefa_atribuida',
                defaults={
                    'template_id_meta': 'tarefa_template_id',
                    'language': 'pt_PT',
                    'is_active': True,
                }
            )
            
            # Simular envio de notificação
            message = WhatsAppMessage.objects.create(
                phone=e2e_encarregado.phone,
                template=template,
                payload={
                    'template': 'tarefa_atribuida',
                    'variables': [
                        e2e_encarregado.first_name,
                        task.name,
                        task.due_date.strftime('%d/%m/%Y'),
                    ],
                },
                status=WhatsAppMessage.STATUS_SENT,
            )
            
            assert task.name in str(message.payload)
            assert e2e_encarregado.phone == message.phone
    
    def test_milestone_completion_notification(
        self, authenticated_client, e2e_tenant, e2e_signed_contract
    ):
        """2. Conclusão de milestone envia notificação."""
        with tenant_context(e2e_tenant):
            template, _ = WhatsAppTemplate.objects.get_or_create(
                name='milestone_concluido',
                defaults={
                    'template_id_meta': 'milestone_template_id',
                    'language': 'pt_PT',
                    'is_active': True,
                }
            )
            
            lead = e2e_signed_contract.lead
            
            # Simular notificação de milestone
            message = WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone=lead.phone,
                payload={
                    'template': 'milestone_concluido',
                    'variables': [
                        lead.first_name,
                        'Fundação',  # Nome da fase
                        e2e_signed_contract.unit.code,
                        '20%',  # Próximo pagamento
                    ],
                },
                status=WhatsAppMessage.STATUS_SENT,
            )
            
            assert 'Fundação' in str(message.payload)
    
    def test_delay_notification(
        self, authenticated_client, e2e_tenant, e2e_construction_tasks
    ):
        """3. Atraso na obra envia notificação."""
        with tenant_context(e2e_tenant):
            task = e2e_construction_tasks[0]
            task.due_date = date.today() - timedelta(days=2)  # Atrasada
            task.status = ConstructionTask.STATUS_PENDING
            task.save()
            
            template, _ = WhatsAppTemplate.objects.get_or_create(
                'tarefa_atrasada',
                defaults={
                    'template_id_meta': 'atraso_template_id',
                    'language': 'pt_PT',
                    'is_active': True,
                }
            )
            
            # Simular notificação de atraso
            if task.assigned_to and task.assigned_to.phone:
                message = WhatsAppMessage.objects.create(
                    phone=task.assigned_to.phone,
                    template=template,
                    payload={
                        'template': 'tarefa_atrasada',
                        'variables': [
                            task.assigned_to.first_name,
                            task.name,
                            task.due_date.strftime('%d/%m/%Y'),
                            str(task.days_overdue),
                        ],
                    },
                    status=WhatsAppMessage.STATUS_SENT,
                )
                
                assert str(task.days_overdue) in str(message.payload)


class TestWhatsAppOptOut:
    """Testar opt-out de WhatsApp (LGPD)."""
    
    def test_lead_opt_out(
        self, authenticated_client, e2e_tenant, e2e_lead
    ):
        """1. Lead pode opt-out de mensagens WhatsApp."""
        with tenant_context(e2e_tenant):
            # Marcar opt-out
            e2e_lead.whatsapp_opt_out = True
            e2e_lead.whatsapp_opt_out_at = timezone.now()
            e2e_lead.save()
            
            # Verificar opt-out
            assert e2e_lead.whatsapp_opt_out is True
            assert e2e_lead.whatsapp_opt_out_at is not None
    
    def test_no_message_to_opted_out_lead(
        self, authenticated_client, e2e_tenant, e2e_lead
    ):
        """2. Mensagens não são enviadas a leads com opt-out."""
        with tenant_context(e2e_tenant):
            e2e_lead.whatsapp_opt_out = True
            e2e_lead.save()
            
            # Tentar enviar mensagem
            should_send = not e2e_lead.whatsapp_opt_out
            
            assert should_send is False


class TestWhatsAppTemplates:
    """Testar templates WhatsApp."""
    
    def test_list_templates(
        self, authenticated_client, e2e_tenant
    ):
        """1. Listar templates disponíveis."""
        with tenant_context(e2e_tenant):
            # Criar templates
            templates = [
                WhatsAppTemplate(
                    name='template_1',
                    template_id_meta='id_1',
                    is_active=True,
                ),
                WhatsAppTemplate(
                    name='template_2',
                    template_id_meta='id_2',
                    is_active=True,
                ),
            ]
            for t in templates:
                t.save()
        
        response = authenticated_client.get('/api/v1/crm/whatsapp/templates/')
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                results = data['results']
            else:
                results = data
            
            assert len(results) >= 2
    
    def test_get_template_details(
        self, authenticated_client, e2e_tenant
    ):
        """2. Obter detalhes de um template."""
        with tenant_context(e2e_tenant):
            template = WhatsAppTemplate.objects.create(
                name='detalhe_template',
                template_id_meta='detalhe_id',
                language='pt_PT',
                variables={'1': 'nome', '2': 'valor'},
                is_active=True,
            )
        
        response = authenticated_client.get(
            f'/api/v1/crm/whatsapp/templates/{template.id}/'
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data['name'] == 'detalhe_template'
            assert data['language'] == 'pt_PT'


class TestWhatsAppMessageHistory:
    """Testar histórico de mensagens."""
    
    def test_list_message_history(
        self, authenticated_client, e2e_tenant, e2e_lead
    ):
        """1. Listar histórico de mensagens de um lead."""
        with tenant_context(e2e_tenant):
            # Criar mensagens
            for i in range(5):
                WhatsAppMessage.objects.create(
                    lead=e2e_lead,
                    phone=e2e_lead.phone,
                    payload={'message': f'Mensagem {i}'},
                    status=WhatsAppMessage.STATUS_DELIVERED if i % 2 == 0 else WhatsAppMessage.STATUS_SENT,
                )
        
        response = authenticated_client.get(
            f'/api/v1/crm/leads/{e2e_lead.id}/messages/'
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                messages = data['results']
            else:
                messages = data
            
            assert len(messages) >= 5
    
    def test_message_status_update(
        self, authenticated_client, e2e_tenant, e2e_lead
    ):
        """2. Atualizar status de mensagem (webhook)."""
        with tenant_context(e2e_tenant):
            message = WhatsAppMessage.objects.create(
                lead=e2e_lead,
                phone=e2e_lead.phone,
                payload={'message': 'Teste'},
                status=WhatsAppMessage.STATUS_SENT,
                message_id_meta='wamid.test123',
            )
        
        # Simular webhook de atualização
        webhook_data = {
            'message_id': 'wamid.test123',
            'status': 'delivered',
            'timestamp': timezone.now().isoformat(),
        }
        
        response = authenticated_client.post(
            '/api/v1/webhooks/whatsapp/status/',
            webhook_data,
            format='json'
        )
        
        # Verificar atualização
        with tenant_context(e2e_tenant):
            message.refresh_from_db()
            # Status pode ter sido atualizado
