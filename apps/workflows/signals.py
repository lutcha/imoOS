"""
Workflow Signals — Triggers automáticos para workflows.

Este módulo conecta os workflows aos eventos do sistema via Django signals.
"""
import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CRM Signals
# ---------------------------------------------------------------------------

@receiver(post_save, sender='crm.Lead')
def on_lead_status_changed(sender, instance, created, **kwargs):
    """
    Quando lead muda de status, executar workflow apropriado.
    
    - CONVERTED: Iniciar fluxo de reserva/contrato
    """
    if created:
        return  # Novo lead, não fazer nada
    
    from apps.crm.models import Lead
    
    if instance.status == Lead.STATUS_CONVERTED:
        logger.info(f'Lead {instance.id} converted - queuing sales workflow')
        
        # O workflow de reserva deve ser iniciado explicitamente via API
        # Este signal apenas loga para auditoria


@receiver(post_save, sender='crm.UnitReservation')
def on_reservation_created(sender, instance, created, **kwargs):
    """Quando uma reserva é criada, notificar lead."""
    if not created:
        return
    
    from apps.workflows.services.notification_workflow import NotificationWorkflow
    
    logger.info(f'Reservation created: {instance.id}')
    
    # Notificar lead
    try:
        NotificationWorkflow.on_reservation_created(instance)
    except Exception as e:
        logger.error(f'Error in reservation notification: {e}')


# ---------------------------------------------------------------------------
# Contracts Signals
# ---------------------------------------------------------------------------

@receiver(post_save, sender='contracts.Contract')
def on_contract_status_changed(sender, instance, created, **kwargs):
    """
    Quando contrato muda de status:
    
    - ACTIVE (assinado): Iniciar projeto de obra
    - COMPLETED: Finalizar workflow
    """
    from apps.contracts.models import Contract
    
    if instance.status == Contract.STATUS_ACTIVE:
        # Contrato foi assinado - iniciar projeto de obra
        logger.info(f'Contract {instance.id} signed - queuing project init workflow')
        
        from apps.workflows.tasks import trigger_project_init_workflow
        trigger_project_init_workflow.delay(contract_id=str(instance.id))
        
        # Notificar cliente
        from apps.workflows.services.notification_workflow import NotificationWorkflow
        try:
            NotificationWorkflow.on_contract_signed(instance)
        except Exception as e:
            logger.error(f'Error in contract signed notification: {e}')
    
    elif instance.status == Contract.STATUS_COMPLETED:
        logger.info(f'Contract {instance.id} completed')


@receiver(post_save, sender='contracts.SignatureRequest')
def on_signature_request_updated(sender, instance, created, **kwargs):
    """Quando pedido de assinatura é criado ou assinado."""
    from apps.contracts.models import SignatureRequest
    
    if created:
        # Notificar cliente para assinar
        logger.info(f'Signature request created: {instance.id}')
        
        from apps.workflows.services.notification_workflow import NotificationWorkflow
        try:
            NotificationWorkflow.on_signature_requested(instance)
        except Exception as e:
            logger.error(f'Error in signature request notification: {e}')
    
    elif instance.status == SignatureRequest.STATUS_SIGNED:
        # Assinatura completa - atualizar contrato
        logger.info(f'Signature completed: {instance.id}')
        
        from apps.workflows.services.sales_workflow import SalesWorkflow
        try:
            SalesWorkflow.mark_contract_signed(
                contract_id=str(instance.contract.id),
                signature_data={
                    'ip_address': instance.ip_address,
                    'signed_by_name': instance.signed_by_name,
                }
            )
        except Exception as e:
            logger.error(f'Error marking contract signed: {e}')


@receiver(post_save, sender='contracts.Payment')
def on_payment_status_changed(sender, instance, created, **kwargs):
    """Quando pagamento muda de status."""
    from apps.contracts.models import Payment
    
    if instance.status == Payment.STATUS_PAID and not created:
        logger.info(f'Payment received: {instance.id}')
        
        from apps.workflows.services.notification_workflow import NotificationWorkflow
        try:
            NotificationWorkflow.on_payment_received(instance)
        except Exception as e:
            logger.error(f'Error in payment received notification: {e}')


# ---------------------------------------------------------------------------
# Construction Signals
# ---------------------------------------------------------------------------

@receiver(post_save, sender='construction.ConstructionTask')
def on_task_status_changed(sender, instance, created, **kwargs):
    """
    Quando task muda de status:
    
    - ASSIGNED: Notificar assignee
    - COMPLETED: Verificar milestones de pagamento
    """
    from apps.construction.models import ConstructionTask
    from apps.workflows.services.notification_workflow import NotificationWorkflow
    
    if created and instance.assigned_to:
        # Nova task atribuída
        logger.info(f'Task assigned: {instance.id} to {instance.assigned_to}')
        
        try:
            NotificationWorkflow.on_task_assigned(instance)
        except Exception as e:
            logger.error(f'Error in task assignment notification: {e}')
    
    elif instance.status == ConstructionTask.STATUS_COMPLETED and not created:
        # Task concluída
        logger.info(f'Task completed: {instance.id}')
        
        # Verificar milestones de pagamento
        from apps.workflows.services.payment_milestone_workflow import PaymentMilestoneWorkflow
        try:
            PaymentMilestoneWorkflow.check_payment_milestone(
                task_id=str(instance.id)
            )
        except Exception as e:
            logger.error(f'Error checking payment milestone: {e}')
        
        # Notificar completion
        try:
            NotificationWorkflow.on_task_completed(instance)
        except Exception as e:
            logger.error(f'Error in task completion notification: {e}')


@receiver(post_save, sender='construction.ConstructionPhase')
def on_phase_status_changed(sender, instance, created, **kwargs):
    """Quando fase muda de status."""
    from apps.construction.models import ConstructionPhase
    
    if instance.status == ConstructionPhase.STATUS_COMPLETED:
        logger.info(f'Phase completed: {instance.id} - {instance.name}')
        
        # Notificar milestone
        from apps.workflows.services.notification_workflow import NotificationWorkflow
        try:
            NotificationWorkflow.on_milestone_reached(
                phase=instance,
                milestone_name=f'Conclusão de {instance.get_phase_type_display()}'
            )
        except Exception as e:
            logger.error(f'Error in milestone notification: {e}')


# ---------------------------------------------------------------------------
# Payments Signals
# ---------------------------------------------------------------------------

@receiver(post_save, sender='payments.PaymentPlanItem')
def on_payment_plan_item_created(sender, instance, created, **kwargs):
    """Quando item de pagamento é criado (milestone)."""
    if not created:
        return
    
    # Notificar cliente sobre novo pagamento
    logger.info(f'Payment plan item created: {instance.id}')
    
    # Notificação será feita pelo workflow que criou o item


# ---------------------------------------------------------------------------
# Projects Signals
# ---------------------------------------------------------------------------

@receiver(post_save, sender='projects.Project')
def on_project_status_changed(sender, instance, created, **kwargs):
    """Quando projeto imobiliário muda de status."""
    if created:
        return
    
    from apps.projects.models import Project
    
    if instance.status == Project.STATUS_CONSTRUCTION:
        logger.info(f'Project started construction: {instance.id}')


# ---------------------------------------------------------------------------
# Workflow Instance Signals
# ---------------------------------------------------------------------------

@receiver(post_save, sender='workflows.WorkflowInstance')
def on_workflow_instance_status_changed(sender, instance, created, **kwargs):
    """Quando instância de workflow muda de status."""
    from apps.workflows.models import WorkflowInstance
    
    if instance.status == WorkflowInstance.STATUS_FAILED:
        logger.error(f'Workflow failed: {instance.id} - {instance.error_message}')
        
        # Tentar re-executar se ainda tem tentativas
        if instance.retry_count < instance.max_retries:
            logger.info(f'Queueing retry for workflow: {instance.id}')
            
            from apps.workflows.tasks import retry_workflow
            retry_workflow.delay(instance_id=str(instance.id))
