"""
Notification Workflow — Centralização de Notificações

Este módulo centraliza todas as notificações da plataforma,
decidindo o canal (WhatsApp, Email, Push) baseado em preferências
e contexto.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class NotificationWorkflow:
    """
    Centralizar todas as notificações da plataforma ImoOS.
    """
    
    # Canais de notificação
    CHANNEL_WHATSAPP = 'whatsapp'
    CHANNEL_EMAIL = 'email'
    CHANNEL_PUSH = 'push'
    CHANNEL_SMS = 'sms'
    
    # Templates de notificação por evento
    NOTIFICATION_TEMPLATES = {
        # Task events
        'task_assigned': {
            'whatsapp': 'task_assigned',
            'email': 'task_assigned',
            'push': True,
        },
        'task_overdue': {
            'whatsapp': 'task_overdue',
            'email': 'task_overdue',
            'push': True,
        },
        'task_completed': {
            'whatsapp': 'task_completed',
            'email': None,
            'push': False,
        },
        # Payment events
        'payment_due': {
            'whatsapp': 'lembrete_pagamento',
            'email': 'payment_reminder',
            'push': True,
        },
        'payment_received': {
            'whatsapp': 'pagamento_confirmado',
            'email': 'payment_confirmed',
            'push': True,
        },
        'payment_overdue': {
            'whatsapp': 'pagamento_atraso',
            'email': 'payment_overdue',
            'push': True,
        },
        # Contract events
        'contract_created': {
            'whatsapp': 'contrato_criado',
            'email': 'contract_created',
            'push': True,
        },
        'contract_signed': {
            'whatsapp': 'contrato_assinado',
            'email': 'contract_signed',
            'push': True,
        },
        'signature_requested': {
            'whatsapp': 'assinatura_solicitada',
            'email': 'signature_requested',
            'push': True,
        },
        # Reservation events
        'reservation_created': {
            'whatsapp': 'reserva_confirmada',
            'email': 'reservation_confirmed',
            'push': True,
        },
        'reservation_expiring': {
            'whatsapp': 'reserva_expirando',
            'email': 'reservation_expiring',
            'push': True,
        },
        # Project events
        'project_initialized': {
            'whatsapp': 'obra_iniciada',
            'email': 'project_started',
            'push': True,
        },
        'milestone_reached': {
            'whatsapp': 'milestone_alcancado',
            'email': 'milestone_reached',
            'push': True,
        },
        # Payment milestones
        'payment_milestone': {
            'whatsapp': 'prestacao_gerada',
            'email': 'installment_generated',
            'push': True,
        },
    }
    
    @classmethod
    def notify(
        cls,
        event_type: str,
        recipient_id: str,
        recipient_type: str = 'lead',
        data: dict = None,
        channels: List[str] = None,
    ) -> dict:
        """
        Enviar notificação genérica.
        
        Args:
            event_type: Tipo do evento (key de NOTIFICATION_TEMPLATES)
            recipient_id: UUID do destinatário
            recipient_type: 'lead' ou 'user'
            data: Dados para o template
            channels: Lista de canais específicos (None = auto)
            
        Returns:
            dict com status de cada canal
        """
        if data is None:
            data = {}
        
        logger.info(f'Notification: {event_type} to {recipient_type}={recipient_id}')
        
        # Verificar se temos config para este evento
        config = cls.NOTIFICATION_TEMPLATES.get(event_type)
        if not config:
            logger.warning(f'No notification config for event: {event_type}')
            return {
                'success': False,
                'error': f'Tipo de evento não configurado: {event_type}'
            }
        
        results = {}
        
        # Determinar canais
        if channels is None:
            channels = []
            if config.get('whatsapp'):
                channels.append(cls.CHANNEL_WHATSAPP)
            if config.get('email'):
                channels.append(cls.CHANNEL_EMAIL)
            if config.get('push'):
                channels.append(cls.CHANNEL_PUSH)
        
        # Enviar por cada canal
        for channel in channels:
            if channel == cls.CHANNEL_WHATSAPP and config.get('whatsapp'):
                results['whatsapp'] = cls._send_whatsapp(
                    template_name=config['whatsapp'],
                    recipient_id=recipient_id,
                    recipient_type=recipient_type,
                    data=data
                )
            elif channel == cls.CHANNEL_EMAIL and config.get('email'):
                results['email'] = cls._send_email(
                    template_name=config['email'],
                    recipient_id=recipient_id,
                    recipient_type=recipient_type,
                    data=data
                )
            elif channel == cls.CHANNEL_PUSH and config.get('push'):
                results['push'] = cls._send_push(
                    event_type=event_type,
                    recipient_id=recipient_id,
                    recipient_type=recipient_type,
                    data=data
                )
        
        return {
            'success': any(r.get('success') for r in results.values()),
            'results': results
        }
    
    @classmethod
    def _send_whatsapp(
        cls,
        template_name: str,
        recipient_id: str,
        recipient_type: str,
        data: dict,
    ) -> dict:
        """Enviar notificação via WhatsApp."""
        from apps.workflows.tasks import send_workflow_notification
        
        try:
            # Determinar o lead_id
            if recipient_type == 'lead':
                lead_id = recipient_id
            else:
                # Buscar lead associado ao user
                lead_id = data.get('lead_id')
            
            if not lead_id:
                return {
                    'success': False,
                    'error': 'Lead ID não encontrado para WhatsApp'
                }
            
            # Verificar se WhatsApp está habilitado
            if not getattr(settings, 'WHATSAPP_ENABLED', False):
                return {
                    'success': False,
                    'skipped': True,
                    'reason': 'whatsapp_disabled'
                }
            
            # Enviar via Celery task
            task = send_workflow_notification.delay(
                notification_type=template_name,
                lead_id=lead_id,
                **data
            )
            
            return {
                'success': True,
                'task_id': task.id,
                'channel': 'whatsapp'
            }
            
        except Exception as e:
            logger.error(f'Error sending WhatsApp: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def _send_email(
        cls,
        template_name: str,
        recipient_id: str,
        recipient_type: str,
        data: dict,
    ) -> dict:
        """Enviar notificação via Email."""
        # Placeholder - implementar quando módulo de email existir
        logger.info(f'Email notification queued: {template_name}')
        return {
            'success': True,
            'channel': 'email',
            'note': 'Email queue not yet implemented'
        }
    
    @classmethod
    def _send_push(
        cls,
        event_type: str,
        recipient_id: str,
        recipient_type: str,
        data: dict,
    ) -> dict:
        """Enviar notificação push."""
        # Placeholder - implementar quando módulo mobile push existir
        logger.info(f'Push notification queued: {event_type}')
        return {
            'success': True,
            'channel': 'push',
            'note': 'Push queue not yet implemented'
        }
    
    # -------------------------------------------------------------------------
    # Event-specific notification methods
    # -------------------------------------------------------------------------
    
    @classmethod
    def on_task_assigned(cls, task, user=None) -> dict:
        """Notificar encarregado de nova tarefa."""
        if not task.assigned_to:
            return {'success': False, 'skipped': True, 'reason': 'no_assignee'}
        
        return cls.notify(
            event_type='task_assigned',
            recipient_id=str(task.assigned_to.id),
            recipient_type='user',
            data={
                'task_id': str(task.id),
                'task_name': task.name,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'project_id': str(task.project.id),
                'priority': task.priority,
            }
        )
    
    @classmethod
    def on_task_overdue(cls, task) -> dict:
        """Alerta de atraso na tarefa."""
        results = []
        
        # Notificar assignee
        if task.assigned_to:
            results.append(cls.notify(
                event_type='task_overdue',
                recipient_id=str(task.assigned_to.id),
                recipient_type='user',
                data={
                    'task_id': str(task.id),
                    'task_name': task.name,
                    'days_overdue': task.days_overdue,
                }
            ))
        
        # Notificar gestor
        if hasattr(task.project, 'project_manager') and task.project.project_manager:
            results.append(cls.notify(
                event_type='task_overdue',
                recipient_id=str(task.project.project_manager.id),
                recipient_type='user',
                data={
                    'task_id': str(task.id),
                    'task_name': task.name,
                    'assignee': str(task.assigned_to) if task.assigned_to else 'Não atribuído',
                    'days_overdue': task.days_overdue,
                }
            ))
        
        return {
            'success': any(r.get('success') for r in results),
            'results': results
        }
    
    @classmethod
    def on_task_completed(cls, task, completed_by=None) -> dict:
        """Notificar que tarefa foi concluída."""
        # Notificar gestor do projeto
        if hasattr(task.project, 'project_manager') and task.project.project_manager:
            return cls.notify(
                event_type='task_completed',
                recipient_id=str(task.project.project_manager.id),
                recipient_type='user',
                data={
                    'task_id': str(task.id),
                    'task_name': task.name,
                    'completed_by': str(completed_by) if completed_by else 'Sistema',
                    'phase': str(task.phase) if task.phase else None,
                }
            )
        
        return {'success': False, 'skipped': True}
    
    @classmethod
    def on_payment_due(cls, payment, days_before: int = 3) -> dict:
        """Lembrete de pagamento."""
        from apps.contracts.models import Payment
        
        if isinstance(payment, Payment):
            lead_id = str(payment.contract.lead.id)
            contract_id = str(payment.contract.id)
            amount = str(payment.amount_cve)
        else:
            # PaymentPlanItem
            lead_id = str(payment.plan.contract.lead.id)
            contract_id = str(payment.plan.contract.id)
            amount = str(payment.amount_cve)
        
        return cls.notify(
            event_type='payment_due',
            recipient_id=lead_id,
            recipient_type='lead',
            data={
                'contract_id': contract_id,
                'payment_id': str(payment.id),
                'amount': amount,
                'due_date': payment.due_date.isoformat() if hasattr(payment, 'due_date') else None,
                'days_before': days_before,
            }
        )
    
    @classmethod
    def on_payment_received(cls, payment) -> dict:
        """Confirmação de pagamento recebido."""
        return cls.notify(
            event_type='payment_received',
            recipient_id=str(payment.contract.lead.id),
            recipient_type='lead',
            data={
                'contract_id': str(payment.contract.id),
                'payment_id': str(payment.id),
                'amount': str(payment.amount_cve),
                'payment_date': payment.paid_date.isoformat() if payment.paid_date else None,
            }
        )
    
    @classmethod
    def on_contract_signed(cls, contract) -> dict:
        """Confirmação de assinatura de contrato."""
        return cls.notify(
            event_type='contract_signed',
            recipient_id=str(contract.lead.id),
            recipient_type='lead',
            data={
                'contract_id': str(contract.id),
                'contract_number': contract.contract_number,
                'unit_code': contract.unit.code,
                'signed_at': contract.signed_at.isoformat() if contract.signed_at else None,
            }
        )
    
    @classmethod
    def on_signature_requested(cls, signature_request) -> dict:
        """Notificar solicitação de assinatura."""
        contract = signature_request.contract
        
        return cls.notify(
            event_type='signature_requested',
            recipient_id=str(contract.lead.id),
            recipient_type='lead',
            data={
                'contract_id': str(contract.id),
                'contract_number': contract.contract_number,
                'signature_token': str(signature_request.token),
                'expires_at': signature_request.expires_at.isoformat(),
            }
        )
    
    @classmethod
    def on_reservation_created(cls, reservation) -> dict:
        """Confirmar criação de reserva."""
        return cls.notify(
            event_type='reservation_created',
            recipient_id=str(reservation.lead.id),
            recipient_type='lead',
            data={
                'reservation_id': str(reservation.id),
                'unit_code': reservation.unit.code,
                'expires_at': reservation.expires_at.isoformat(),
            }
        )
    
    @classmethod
    def on_project_initialized(cls, project) -> dict:
        """Notificar início de obra."""
        # Buscar cliente através do contrato
        if hasattr(project, 'contract'):
            return cls.notify(
                event_type='project_initialized',
                recipient_id=str(project.contract.lead.id),
                recipient_type='lead',
                data={
                    'project_id': str(project.id),
                    'project_name': project.name,
                    'unit_code': project.unit.code if project.unit else None,
                    'start_date': project.start_planned.isoformat() if project.start_planned else None,
                }
            )
        
        return {'success': False, 'skipped': True}
    
    @classmethod
    def on_milestone_reached(cls, phase, milestone_name: str) -> dict:
        """Notificar atingimento de milestone."""
        # Buscar contrato associado
        from apps.workflows.services.project_init_workflow import ProjectInitWorkflow
        
        project = phase.project
        building = getattr(phase, 'building', None)
        
        # Tentar encontrar contrato
        contract = ProjectInitWorkflow._get_contract_for_project(project, building)
        
        if contract:
            return cls.notify(
                event_type='milestone_reached',
                recipient_id=str(contract.lead.id),
                recipient_type='lead',
                data={
                    'phase_id': str(phase.id),
                    'phase_name': phase.name,
                    'milestone_name': milestone_name,
                    'progress': phase.progress_percent,
                }
            )
        
        return {'success': False, 'skipped': True}
