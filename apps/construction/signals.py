"""
Construction signals - Integração com WhatsApp (A3) e notificações automáticas.

Signals:
- post_save ConstructionTask: Notificar atribuição
- Verificar tasks atrasadas: Notificar atraso
"""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ConstructionTask

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ConstructionTask)
def notify_task_assignment(sender, instance, created, **kwargs):
    """
    Notificar quando uma task é atribuída a um utilizador.
    
    Envia WhatsApp para o encarregado quando:
    - Task é criada com assigned_to
    - Task é reatribuída para outro utilizador
    """
    if not created:
        return  # Apenas novas tasks
    
    if not instance.assigned_to:
        return  # Sem atribuição
    
    # Verificar se o utilizador tem WhatsApp configurado
    user = instance.assigned_to
    if not user.phone:
        logger.info(f'User {user.email} não tem telefone configurado. Skip notificação.')
        return
    
    # Tentar enviar notificação (não quebrar se A3 estiver offline)
    try:
        from apps.integrations.services.notification_router import NotificationRouter
        
        NotificationRouter.notify_task_assignment(instance)
        
        # Marcar como notificado
        instance.notification_sent = True
        instance.save(update_fields=['notification_sent'])
        
        logger.info(f'Notificação enviada para {user.email} sobre task {instance.wbs_code}')
        
    except ImportError:
        logger.warning('NotificationRouter não disponível (A3 offline?)')
    except Exception as e:
        logger.error(f'Erro ao enviar notificação: {e}')


@receiver(pre_save, sender=ConstructionTask)
def check_task_reassignment(sender, instance, **kwargs):
    """
    Detectar reatribuição de task e notificar novo assignee.
    """
    if not instance.pk:
        return  # Nova task, tratado pelo post_save
    
    try:
        old_task = ConstructionTask.objects.get(pk=instance.pk)
    except ConstructionTask.DoesNotExist:
        return
    
    # Verificar se mudou o assigned_to
    if old_task.assigned_to_id != instance.assigned_to_id:
        if instance.assigned_to and instance.assigned_to.phone:
            try:
                from apps.integrations.services.notification_router import NotificationRouter
                NotificationRouter.notify_task_assignment(
                    instance,
                    is_reassignment=True
                )
                logger.info(f'Notificação de reatribuição enviada para {instance.assigned_to.email}')
            except Exception as e:
                logger.error(f'Erro ao notificar reatribuição: {e}')


@receiver(post_save, sender=ConstructionTask)
def check_overdue_notification(sender, instance, **kwargs):
    """
    Verificar se task está atrasada e notificar.
    
    Notifica apenas uma vez (quando passa do due_date).
    """
    # Só notificar se:
    # - Não está completa
    # - Está atrasada
    # - Ainda não foi notificada
    if instance.status == ConstructionTask.STATUS_COMPLETED:
        return
    
    if not instance.is_overdue:
        return
    
    if instance.overdue_notified:
        return
    
    if not instance.assigned_to or not instance.assigned_to.phone:
        return
    
    try:
        from apps.integrations.services.notification_router import NotificationRouter
        
        NotificationRouter.notify_overdue_task(instance)
        
        # Marcar como notificada
        instance.overdue_notified = True
        instance.save(update_fields=['overdue_notified'])
        
        logger.info(f'Notificação de atraso enviada para {instance.assigned_to.email}')
        
    except ImportError:
        logger.warning('NotificationRouter não disponível')
    except Exception as e:
        logger.error(f'Erro ao notificar atraso: {e}')


def send_daily_reminders():
    """
    Tarefa Celery para enviar lembretes diários.
    
    Chamada todos os dias às 8h.
    """
    today = timezone.now().date()
    
    # Tasks para hoje
    tasks_today = ConstructionTask.objects.filter(
        due_date=today,
        status__in=[
            ConstructionTask.STATUS_PENDING,
            ConstructionTask.STATUS_IN_PROGRESS
        ],
        reminder_sent=False
    ).select_related('assigned_to')
    
    for task in tasks_today:
        if not task.assigned_to or not task.assigned_to.phone:
            continue
        
        try:
            from apps.integrations.services.notification_router import NotificationRouter
            NotificationRouter.notify_daily_reminder(task)
            
            task.reminder_sent = True
            task.save(update_fields=['reminder_sent'])
            
        except Exception as e:
            logger.error(f'Erro ao enviar lembrete: {e}')


def check_overdue_tasks():
    """
    Tarefa Celery para verificar tasks atrasadas.
    
    Chamada todos os dias às 9h.
    """
    yesterday = timezone.now().date() - timezone.timedelta(days=1)
    
    # Tasks que venceram ontem e ainda não notificadas
    overdue_tasks = ConstructionTask.objects.filter(
        due_date__lte=yesterday,
        status__in=[
            ConstructionTask.STATUS_PENDING,
            ConstructionTask.STATUS_IN_PROGRESS
        ],
        overdue_notified=False
    ).select_related('assigned_to')
    
    for task in overdue_tasks:
        if not task.assigned_to or not task.assigned_to.phone:
            continue
        
        try:
            from apps.integrations.services.notification_router import NotificationRouter
            NotificationRouter.notify_overdue_task(task)
            
            task.overdue_notified = True
            task.save(update_fields=['overdue_notified'])
            
        except Exception as e:
            logger.error(f'Erro ao notificar atraso: {e}')
