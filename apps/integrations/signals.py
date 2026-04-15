"""
Signals para WhatsApp Business API integration.
Notificações automáticas baseadas em eventos do sistema.
"""
import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from apps.integrations.models import NotificationPreference
from apps.integrations.tasks import send_whatsapp_message

logger = logging.getLogger('apps.integrations')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_notification_preferences(sender, instance, created, **kwargs):
    """
    Criar preferências de notificação padrão quando um novo utilizador é criado.

    Uses a savepoint so a missing table (e.g. integrations not yet migrated in a
    new tenant schema) aborts only this sub-transaction and not the outer one.
    Without the savepoint, PostgreSQL marks the whole transaction as aborted and
    every subsequent query fails — even though we catch the Python exception.
    """
    if not created:
        return
    from django.db import transaction
    try:
        with transaction.atomic():
            NotificationPreference.objects.get_or_create(
                user=instance,
                defaults={
                    'whatsapp_enabled': True,
                    'email_enabled': True,
                    'sms_enabled': False,
                    'urgent_only_whatsapp': False,
                    'notify_task_assignment': True,
                    'notify_task_overdue': True,
                    'notify_daily_reminder': True,
                }
            )
            logger.info(f'Preferências criadas para utilizador {instance.email}')
    except Exception as e:
        logger.warning(f'Could not create notification preferences for {instance.email}: {e}')


# Signals para ConstructionTask - comentados para evitar import circular
# Descomentar quando o model existir

# @receiver(post_save, sender='construction.ConstructionTask')
# def notify_task_assignment_signal(sender, instance, created, **kwargs):
#     """
#     Notificar utilizador quando uma tarefa é atribuída a ele.
#     """
#     if created and instance.assigned_to:
#         from apps.integrations.services import NotificationRouter
#         
#         try:
#             router = NotificationRouter()
#             router.notify_task_assignment(instance)
#             logger.info(f'Notificação enviada para tarefa {instance.id}')
#         except Exception as e:
#             logger.error(f'Erro ao notificar atribuição: {e}')


# @receiver(post_save, sender='construction.ConstructionTask')
# def notify_task_status_change(sender, instance, created, update_fields, **kwargs):
#     """
#     Notificar alterações importantes no status da tarefa.
#     """
#     if created or not update_fields:
#         return
#     
#     if 'status' in update_fields:
#         # Notificar gestor quando tarefa é concluída
#         if instance.status == 'COMPLETED' and instance.assigned_to:
#             logger.info(f'Tarefa {instance.id} concluída por {instance.assigned_to}')
