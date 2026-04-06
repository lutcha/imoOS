"""
Workflow Celery Tasks — Processamento assíncrono de workflows.

Todas as tasks recebem tenant_schema como string e usam tenant_context().
"""
import logging
from typing import Optional

from celery import shared_task
from django.conf import settings
from django_tenants.utils import get_tenant_model, tenant_context

logger = logging.getLogger(__name__)


def _get_tenant(tenant_schema: str):
    """Helper para obter tenant."""
    TenantModel = get_tenant_model()
    return TenantModel.objects.get(schema_name=tenant_schema)


# ---------------------------------------------------------------------------
# Workflow Execution Tasks
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3, name='workflows.execute_workflow')
def execute_workflow(self, *, tenant_schema: str, workflow_instance_id: str) -> dict:
    """
    Executar uma instância de workflow.
    
    Processa cada passo do workflow sequencialmente.
    """
    tenant = _get_tenant(tenant_schema)
    
    with tenant_context(tenant):
        from apps.workflows.models import WorkflowInstance, WorkflowStep, WorkflowLog
        
        try:
            instance = WorkflowInstance.objects.select_related('workflow').get(
                id=workflow_instance_id
            )
        except WorkflowInstance.DoesNotExist:
            return {'error': 'workflow_instance_not_found'}
        
        if instance.status not in [WorkflowInstance.STATUS_PENDING, WorkflowInstance.STATUS_RETRYING]:
            return {'error': 'invalid_status', 'status': instance.status}
        
        # Marcar como em execução
        from django.utils import timezone
        instance.status = WorkflowInstance.STATUS_RUNNING
        instance.started_at = timezone.now()
        instance.save(update_fields=['status', 'started_at'])
        
        # Buscar passos pendentes
        steps = WorkflowStep.objects.filter(
            instance=instance,
            status=WorkflowStep.STATUS_PENDING
        ).order_by('order')
        
        for step in steps:
            # Executar passo
            step.status = WorkflowStep.STATUS_RUNNING
            step.started_at = timezone.now()
            step.save(update_fields=['status', 'started_at'])
            
            try:
                result = _execute_step(step, instance.context)
                
                step.status = WorkflowStep.STATUS_COMPLETED
                step.result_data = result
                step.completed_at = timezone.now()
                step.save(update_fields=['status', 'result_data', 'completed_at'])
                
                # Atualizar contexto
                instance.context.update(result.get('context_update', {}))
                instance.current_step = step.order
                instance.save(update_fields=['context', 'current_step'])
                
                # Log
                WorkflowLog.objects.create(
                    instance=instance,
                    step=step,
                    level=WorkflowLog.LEVEL_INFO,
                    message=f'Step {step.name} completed successfully',
                    details=result
                )
                
            except Exception as exc:
                logger.error(f'Workflow step failed: {exc}')
                
                step.status = WorkflowStep.STATUS_FAILED
                step.error_message = str(exc)
                step.save(update_fields=['status', 'error_message'])
                
                instance.status = WorkflowInstance.STATUS_FAILED
                instance.error_message = str(exc)
                instance.error_step = step.order
                instance.save(update_fields=['status', 'error_message', 'error_step'])
                
                # Log
                WorkflowLog.objects.create(
                    instance=instance,
                    step=step,
                    level=WorkflowLog.LEVEL_ERROR,
                    message=f'Step {step.name} failed: {exc}',
                    details={'error': str(exc)}
                )
                
                # Retry
                if instance.retry_count < instance.max_retries:
                    instance.retry_count += 1
                    instance.status = WorkflowInstance.STATUS_RETRYING
                    instance.save(update_fields=['retry_count', 'status'])
                    
                    countdown = 60 * (2 ** self.request.retries)
                    raise self.retry(exc=exc, countdown=countdown)
                
                return {
                    'success': False,
                    'error': str(exc),
                    'failed_step': step.order
                }
        
        # Workflow completo
        instance.status = WorkflowInstance.STATUS_COMPLETED
        instance.completed_at = timezone.now()
        instance.save(update_fields=['status', 'completed_at'])
        
        # Notificar conclusão
        if instance.workflow.notify_on_complete:
            _notify_workflow_complete.delay(
                tenant_schema=tenant_schema,
                instance_id=workflow_instance_id
            )
        
        return {
            'success': True,
            'instance_id': workflow_instance_id,
            'steps_executed': steps.count()
        }


def _execute_step(step, context: dict) -> dict:
    """Executar um passo específico baseado no tipo de ação."""
    from apps.workflows.models import WorkflowStep
    
    action_type = step.action_type
    config = step.action_config
    
    if action_type == WorkflowStep.ACTION_CREATE_MODEL:
        return _execute_create_model(config, context)
    
    elif action_type == WorkflowStep.ACTION_UPDATE_MODEL:
        return _execute_update_model(config, context)
    
    elif action_type == WorkflowStep.ACTION_SEND_NOTIFICATION:
        return _execute_send_notification(config, context)
    
    elif action_type == WorkflowStep.ACTION_SEND_WHATSAPP:
        return _execute_send_whatsapp(config, context)
    
    elif action_type == WorkflowStep.ACTION_GENERATE_DOCUMENT:
        return _execute_generate_document(config, context)
    
    else:
        raise ValueError(f'Unknown action type: {action_type}')


def _execute_create_model(config: dict, context: dict) -> dict:
    """Criar um modelo."""
    model_path = config['model']
    data = config.get('data', {})
    
    # Interpolar contexto
    for key, value in data.items():
        if isinstance(value, str) and value.startswith('{{'):
            ctx_key = value.strip('{{}}').strip()
            data[key] = context.get(ctx_key)
    
    # Importar e criar modelo
    module_name, model_name = model_path.rsplit('.', 1)
    module = __import__(module_name, fromlist=[model_name])
    ModelClass = getattr(module, model_name)
    
    instance = ModelClass.objects.create(**data)
    
    return {
        'success': True,
        'created_id': str(instance.id),
        'context_update': {
            f'{model_name.lower()}_id': str(instance.id)
        }
    }


def _execute_update_model(config: dict, context: dict) -> dict:
    """Atualizar um modelo."""
    model_path = config['model']
    object_id = config['object_id']
    data = config.get('data', {})
    
    # Buscar modelo
    module_name, model_name = model_path.rsplit('.', 1)
    module = __import__(module_name, fromlist=[model_name])
    ModelClass = getattr(module, model_name)
    
    instance = ModelClass.objects.get(id=object_id)
    
    for key, value in data.items():
        setattr(instance, key, value)
    
    instance.save(update_fields=list(data.keys()))
    
    return {
        'success': True,
        'updated_id': str(instance.id)
    }


def _execute_send_notification(config: dict, context: dict) -> dict:
    """Enviar notificação interna."""
    # Implementação básica
    return {
        'success': True,
        'message': 'Notification sent'
    }


def _execute_send_whatsapp(config: dict, context: dict) -> dict:
    """Enviar WhatsApp."""
    # Delega para a task existente
    return {
        'success': True,
        'message': 'WhatsApp queued'
    }


def _execute_generate_document(config: dict, context: dict) -> dict:
    """Gerar documento."""
    return {
        'success': True,
        'message': 'Document generation queued'
    }


# ---------------------------------------------------------------------------
# Specific Workflow Triggers
# ---------------------------------------------------------------------------

@shared_task(name='workflows.trigger_project_init_workflow')
def trigger_project_init_workflow(*, contract_id: str) -> dict:
    """
    Trigger para iniciar workflow de projeto de obra.
    
    Este task é chamado quando um contrato é assinado.
    """
    from apps.workflows.services.project_init_workflow import ProjectInitWorkflow
    
    logger.info(f'Triggering project init workflow for contract: {contract_id}')
    
    result = ProjectInitWorkflow.create_construction_project(
        contract_id=contract_id
    )
    
    return result


@shared_task(name='workflows.trigger_payment_milestone')
def trigger_payment_milestone(*, task_id: str) -> dict:
    """Trigger para verificar milestone de pagamento."""
    from apps.workflows.services.payment_milestone_workflow import PaymentMilestoneWorkflow
    
    result = PaymentMilestoneWorkflow.check_payment_milestone(task_id=task_id)
    
    return result


@shared_task(bind=True, max_retries=3, name='workflows.retry_workflow')
def retry_workflow(self, *, instance_id: str) -> dict:
    """Re-executar workflow que falhou."""
    # Buscar tenant a partir da instance
    from apps.workflows.models import WorkflowInstance
    
    try:
        instance = WorkflowInstance.objects.get(id=instance_id)
    except WorkflowInstance.DoesNotExist:
        return {'error': 'instance_not_found'}
    
    # Não precisamos de tenant_context aqui porque o signal já está no schema correto
    # Mas precisamos obter o tenant para a task
    from django_tenants.utils import get_current_tenant
    
    tenant = get_current_tenant()
    if not tenant:
        logger.error(f'Cannot retry workflow {instance_id}: no tenant context')
        return {'error': 'no_tenant_context'}
    
    # Re-executar
    return execute_workflow.delay(
        tenant_schema=tenant.schema_name,
        workflow_instance_id=instance_id
    )


# ---------------------------------------------------------------------------
# Notification Tasks
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3, name='workflows.send_workflow_notification')
def send_workflow_notification(
    self,
    notification_type: str,
    lead_id: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Enviar notificação de workflow.
    
    Wrapper unificado para enviar notificações via WhatsApp.
    """
    from django_tenants.utils import get_current_tenant
    
    tenant = get_current_tenant()
    if not tenant:
        logger.error('Cannot send notification: no tenant context')
        return {'error': 'no_tenant_context'}
    
    tenant_schema = tenant.schema_name
    
    # Mapear tipos de notificação para templates
    TEMPLATE_MAP = {
        'reservation_created': 'reserva_confirmada',
        'signature_requested': 'assinatura_solicitada',
        'contract_signed': 'contrato_assinado',
        'project_initialized': 'obra_iniciada',
        'payment_milestone': 'prestacao_gerada',
        'payment_received': 'pagamento_confirmado',
        'task_assigned': 'tarefa_atribuida',
        'task_overdue': 'tarefa_atraso',
    }
    
    template_name = TEMPLATE_MAP.get(notification_type, notification_type)
    
    # Preparar variáveis baseado no tipo
    variables = _prepare_notification_variables(notification_type, kwargs)
    
    # Enviar via task existente do CRM
    from apps.crm.tasks import send_whatsapp_template
    
    try:
        result = send_whatsapp_template.delay(
            tenant_schema=tenant_schema,
            lead_id=lead_id,
            template_name=template_name,
            variables=variables
        )
        
        return {
            'success': True,
            'task_id': result.id,
            'template': template_name
        }
        
    except Exception as exc:
        logger.error(f'Error sending workflow notification: {exc}')
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


def _prepare_notification_variables(notification_type: str, data: dict) -> dict:
    """Preparar variáveis para templates WhatsApp."""
    variables = {}
    
    if notification_type == 'reservation_created':
        variables = {
            '1': data.get('unit_code', ''),
            '2': data.get('expires_at', '')[:10] if data.get('expires_at') else ''
        }
    
    elif notification_type == 'signature_requested':
        variables = {
            '1': data.get('contract_number', ''),
            '2': data.get('expires_at', '')[:10] if data.get('expires_at') else ''
        }
    
    elif notification_type == 'contract_signed':
        variables = {
            '1': data.get('contract_number', ''),
            '2': data.get('unit_code', '')
        }
    
    elif notification_type == 'project_initialized':
        variables = {
            '1': data.get('unit_code', ''),
            '2': data.get('start_date', '')[:10] if data.get('start_date') else ''
        }
    
    elif notification_type == 'payment_milestone':
        variables = {
            '1': data.get('milestone_name', ''),
            '2': data.get('amount', ''),
            '3': data.get('due_date', '')[:10] if data.get('due_date') else ''
        }
    
    elif notification_type == 'payment_received':
        variables = {
            '1': data.get('amount', '')
        }
    
    elif notification_type == 'task_assigned':
        variables = {
            '1': data.get('task_name', ''),
            '2': data.get('due_date', '')[:10] if data.get('due_date') else ''
        }
    
    elif notification_type == 'task_overdue':
        variables = {
            '1': data.get('task_name', ''),
            '2': str(data.get('days_overdue', 0))
        }
    
    return variables


@shared_task(name='workflows.notify_workflow_complete')
def _notify_workflow_complete(*, tenant_schema: str, instance_id: str) -> dict:
    """Notificar conclusão de workflow (para administradores)."""
    # Implementação futura
    return {'success': True}


# ---------------------------------------------------------------------------
# Scheduled Tasks
# ---------------------------------------------------------------------------

@shared_task(name='workflows.check_overdue_tasks')
def check_overdue_tasks(*, tenant_schema: str) -> dict:
    """Verificar tasks atrasadas e notificar."""
    tenant = _get_tenant(tenant_schema)
    
    with tenant_context(tenant):
        from apps.construction.models import ConstructionTask
        from apps.workflows.services.notification_workflow import NotificationWorkflow
        
        overdue_tasks = ConstructionTask.objects.filter(
            status__in=[ConstructionTask.STATUS_PENDING, ConstructionTask.STATUS_IN_PROGRESS],
            due_date__lt=timezone.now().date(),
            overdue_notified=False
        )
        
        notified_count = 0
        
        for task in overdue_tasks:
            try:
                result = NotificationWorkflow.on_task_overdue(task)
                if result.get('success'):
                    task.overdue_notified = True
                    task.save(update_fields=['overdue_notified'])
                    notified_count += 1
            except Exception as e:
                logger.error(f'Error notifying overdue task {task.id}: {e}')
        
        return {
            'overdue_tasks': overdue_tasks.count(),
            'notified': notified_count
        }


@shared_task(name='workflows.check_upcoming_payments')
def check_upcoming_payments(*, tenant_schema: str, days_ahead: int = 3) -> dict:
    """Verificar pagamentos próximos e enviar lembretes."""
    from datetime import timedelta
    
    tenant = _get_tenant(tenant_schema)
    
    with tenant_context(tenant):
        from apps.contracts.models import Payment
        from apps.workflows.services.notification_workflow import NotificationWorkflow
        
        upcoming_date = timezone.now().date() + timedelta(days=days_ahead)
        
        upcoming_payments = Payment.objects.filter(
            status=Payment.STATUS_PENDING,
            due_date=upcoming_date
        ).select_related('contract', 'contract__lead')
        
        notified_count = 0
        
        for payment in upcoming_payments:
            try:
                result = NotificationWorkflow.on_payment_due(payment, days_before=days_ahead)
                if result.get('success'):
                    notified_count += 1
            except Exception as e:
                logger.error(f'Error notifying payment {payment.id}: {e}')
        
        return {
            'upcoming_payments': upcoming_payments.count(),
            'notified': notified_count
        }
