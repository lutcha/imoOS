"""
Celery tasks para WhatsApp Business API integration.
Envio assíncrono de mensagens e processamento de respostas.
"""
import logging
from datetime import date, timedelta

from celery import shared_task
from django.utils import timezone
from django.db import transaction

from apps.integrations.models import WhatsAppMessage, NotificationPreference
from apps.integrations.services import WhatsAppClient, NotificationRouter

logger = logging.getLogger('apps.integrations')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_whatsapp_message(self, message_id: str):
    """
    Enviar mensagem WhatsApp de forma assíncrona.
    
    Args:
        message_id: ID da WhatsAppMessage a enviar
    """
    try:
        message = WhatsAppMessage.objects.get(id=message_id)
        
        # Verificar se já foi enviada
        if message.status == WhatsAppMessage.STATUS_SENT and message.meta_message_id:
            logger.info(f'Mensagem {message_id} já enviada, ignorando')
            return {'status': 'already_sent', 'message_id': message_id}
        
        client = WhatsAppClient()
        
        # Enviar via API
        if message.template:
            result = client.send_template_message(
                to_phone=message.phone_number,
                template_name=message.template.meta_template_id or message.template.name,
                variables=message.raw_webhook_data.get('template_variables', {})
            )
        else:
            result = client.send_free_text(
                to_phone=message.phone_number,
                message=message.message_body
            )
        
        # Atualizar status
        if result.success:
            message.status = WhatsAppMessage.STATUS_SENT
            message.meta_message_id = result.message_id or ''
            message.save(update_fields=['status', 'meta_message_id'])
            logger.info(f'Mensagem {message_id} enviada com sucesso: {result.message_id}')
            return {'status': 'sent', 'message_id': message_id, 'whatsapp_id': result.message_id}
        else:
            message.status = WhatsAppMessage.STATUS_FAILED
            message.error_message = result.error_message or 'Unknown error'
            message.save(update_fields=['status', 'error_message'])
            logger.error(f'Falha ao enviar mensagem {message_id}: {result.error_message}')
            
            # Retry se aplicável
            if self.request.retries < self.max_retries:
                raise self.retry(exc=Exception(result.error_message))
            
            return {'status': 'failed', 'message_id': message_id, 'error': result.error_message}
    
    except WhatsAppMessage.DoesNotExist:
        logger.error(f'Mensagem {message_id} não encontrada')
        return {'status': 'error', 'error': 'Message not found'}
    except Exception as e:
        logger.exception(f'Erro ao enviar mensagem {message_id}: {e}')
        
        # Retry
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def process_inbound_message(self, message_id: str):
    """
    Processar resposta recebida async.
    Atualiza task status baseado na resposta.
    
    Args:
        message_id: ID da WhatsAppMessage inbound
    """
    try:
        message = WhatsAppMessage.objects.get(
            id=message_id,
            direction=WhatsAppMessage.DIRECTION_INBOUND
        )
        
        if message.processed:
            logger.info(f'Mensagem {message_id} já processada')
            return {'status': 'already_processed'}
        
        router = NotificationRouter()
        result = router.process_inbound_response(message)
        
        logger.info(f'Mensagem {message_id} processada: {result}')
        return {'status': 'processed', 'message_id': message_id, 'action': result}
    
    except WhatsAppMessage.DoesNotExist:
        logger.error(f'Mensagem {message_id} não encontrada')
        return {'status': 'error', 'error': 'Message not found'}
    except Exception as e:
        logger.exception(f'Erro ao processar mensagem {message_id}: {e}')
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {'status': 'error', 'error': str(e)}


@shared_task
def send_scheduled_reminders():
    """
    Enviar lembretes diários às 8h.
    Query tasks para hoje e envia WhatsApp para cada assignee.
    """
    today = timezone.now().date()
    
    logger.info(f'Iniciando envio de lembretes diários para {today}')
    
    try:
        from apps.construction.models import ConstructionTask
        
        # Buscar tarefas pendentes para hoje
        tasks_today = ConstructionTask.objects.filter(
            due_date=today,
            status__in=['PENDING', 'IN_PROGRESS'],
            assigned_to__isnull=False
        ).select_related('assigned_to')
        
        sent_count = 0
        failed_count = 0
        
        router = NotificationRouter()
        
        for task in tasks_today:
            try:
                # Verificar preferências
                preference = NotificationPreference.objects.filter(
                    user=task.assigned_to
                ).first()
                
                if preference and not preference.notify_daily_reminder:
                    continue
                
                result = router.notify_task_reminder(task, days_before=0)
                
                if result.get('success'):
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f'Erro ao enviar lembrete para tarefa {task.id}: {e}')
                failed_count += 1
        
        logger.info(f'Lembretes enviados: {sent_count} sucesso, {failed_count} falhas')
        
        return {
            'status': 'completed',
            'tasks_found': tasks_today.count(),
            'sent': sent_count,
            'failed': failed_count
        }
    
    except Exception as e:
        logger.exception(f'Erro no envio de lembretes: {e}')
        return {'status': 'error', 'error': str(e)}


@shared_task
def check_overdue_tasks():
    """
    Verificar tarefas atrasadas e enviar alertas.
    Executado diariamente.
    """
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    logger.info(f'Verificando tarefas atrasadas até {yesterday}')
    
    try:
        from apps.construction.models import ConstructionTask
        
        # Buscar tarefas atrasadas não notificadas recentemente
        overdue_tasks = ConstructionTask.objects.filter(
            due_date__lt=today,
            status__in=['PENDING', 'IN_PROGRESS'],
            assigned_to__isnull=False
        ).select_related('assigned_to')
        
        sent_count = 0
        router = NotificationRouter()
        
        for task in overdue_tasks:
            try:
                # Verificar se já notificou hoje
                recent_notification = WhatsAppMessage.objects.filter(
                    task=task,
                    direction=WhatsAppMessage.DIRECTION_OUTBOUND,
                    sent_at__date=today,
                    message_body__contains='ATRASADA'
                ).exists()
                
                if recent_notification:
                    continue
                
                result = router.notify_overdue_task(task)
                
                if result.get('success'):
                    sent_count += 1
                    
            except Exception as e:
                logger.error(f'Erro ao notificar atraso da tarefa {task.id}: {e}')
        
        logger.info(f'Alertas de atraso enviados: {sent_count}')
        
        return {
            'status': 'completed',
            'overdue_found': overdue_tasks.count(),
            'notifications_sent': sent_count
        }
    
    except Exception as e:
        logger.exception(f'Erro ao verificar tarefas atrasadas: {e}')
        return {'status': 'error', 'error': str(e)}


@shared_task
def sync_message_status():
    """
    Sincronizar status de mensagens pendentes.
    Verifica mensagens enviadas há mais de 5 minutos sem status de entrega.
    """
    from django.db.models import Q
    
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    
    pending_messages = WhatsAppMessage.objects.filter(
        direction=WhatsAppMessage.DIRECTION_OUTBOUND,
        status=WhatsAppMessage.STATUS_SENT,
        sent_at__lte=five_minutes_ago,
        delivered_at__isnull=True
    )
    
    logger.info(f'Sincronizando status de {pending_messages.count()} mensagens')
    
    # Nota: A Meta não fornece endpoint de consulta, então
    # dependemos dos webhooks. Este task é placeholder para
    # futuras integrações que suportem polling.
    
    return {
        'status': 'completed',
        'pending_checked': pending_messages.count()
    }


@shared_task
def cleanup_old_messages(days: int = 90):
    """
    Limpar mensagens antigas do banco de dados.
    Mantém apenas últimos N dias para conformidade LGPD.
    
    Args:
        days: Número de dias para reter mensagens
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    old_messages = WhatsAppMessage.objects.filter(sent_at__lt=cutoff_date)
    count = old_messages.count()
    
    # Anonimizar em vez de deletar (LGPD)
    old_messages.update(
        message_body='[REMOVIDO - LGPD]',
        phone_number='[REMOVIDO]',
        raw_webhook_data={}
    )
    
    logger.info(f'{count} mensagens anonimizadas (mais antigas que {days} dias)')
    
    return {
        'status': 'completed',
        'messages_anonymized': count
    }
