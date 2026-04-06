"""
Workflow Views — API endpoints para gestão de workflows.
"""
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.workflows.models import (
    WorkflowDefinition, WorkflowInstance, WorkflowStep,
    WorkflowLog, WorkflowTemplate
)
from apps.workflows.services import (
    SalesWorkflow, ProjectInitWorkflow,
    PaymentMilestoneWorkflow, NotificationWorkflow
)

logger = logging.getLogger(__name__)


class WorkflowViewSet(viewsets.ModelViewSet):
    """API para gerir definições de workflow."""
    
    queryset = WorkflowDefinition.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkflowDefinition.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """Executar workflow manualmente."""
        workflow = self.get_object()
        
        # Criar instância
        instance = WorkflowInstance.objects.create(
            workflow=workflow,
            status=WorkflowInstance.STATUS_PENDING,
            context=request.data.get('context', {}),
            trigger_model='Manual',
            trigger_object_id='',
            total_steps=len(workflow.steps_definition)
        )
        
        # Criar passos
        for i, step_def in enumerate(workflow.steps_definition):
            WorkflowStep.objects.create(
                instance=instance,
                order=i,
                name=step_def.get('name', f'Step {i}'),
                action_type=step_def.get('action_type', 'CUSTOM'),
                action_config=step_def.get('config', {})
            )
        
        # Executar
        from apps.workflows.tasks import execute_workflow
        execute_workflow.delay(
            tenant_schema=request.tenant.schema_name,
            workflow_instance_id=str(instance.id)
        )
        
        return Response({
            'success': True,
            'instance_id': str(instance.id),
            'status': instance.status,
            'message': 'Workflow iniciado'
        })
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Listar templates de workflow disponíveis."""
        templates = WorkflowTemplate.objects.filter(is_system=True)
        return Response([{
            'id': str(t.id),
            'name': t.name,
            'workflow_type': t.workflow_type,
            'trigger_event': t.trigger_event,
            'description': t.description
        } for t in templates])


class WorkflowInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    """API para consultar instâncias de workflow."""
    
    queryset = WorkflowInstance.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkflowInstance.objects.select_related('workflow').order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Re-executar workflow que falhou."""
        instance = self.get_object()
        
        if instance.status not in [WorkflowInstance.STATUS_FAILED, WorkflowInstance.STATUS_CANCELLED]:
            return Response({
                'success': False,
                'error': f'Cannot retry workflow with status: {instance.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.status = WorkflowInstance.STATUS_RETRYING
        instance.retry_count += 1
        instance.save(update_fields=['status', 'retry_count'])
        
        from apps.workflows.tasks import execute_workflow
        execute_workflow.delay(
            tenant_schema=request.tenant.schema_name,
            workflow_instance_id=str(instance.id)
        )
        
        return Response({
            'success': True,
            'instance_id': str(instance.id),
            'message': 'Workflow re-executando'
        })
    
    @action(detail=True, methods=['get'])
    def steps(self, request, pk=None):
        """Obter passos de uma instância."""
        instance = self.get_object()
        steps = instance.steps.all().order_by('order')
        
        return Response([{
            'id': str(s.id),
            'order': s.order,
            'name': s.name,
            'action_type': s.action_type,
            'status': s.status,
            'result_data': s.result_data,
            'started_at': s.started_at.isoformat() if s.started_at else None,
            'completed_at': s.completed_at.isoformat() if s.completed_at else None,
        } for s in steps])
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Obter logs de uma instância."""
        instance = self.get_object()
        logs = instance.logs.all().order_by('-created_at')[:100]
        
        return Response([{
            'id': str(l.id),
            'level': l.level,
            'message': l.message,
            'details': l.details,
            'created_at': l.created_at.isoformat()
        } for l in logs])


class SalesWorkflowViewSet(viewsets.ViewSet):
    """API para workflow de vendas (Lead → Contrato)."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_reservation(self, request):
        """Criar reserva a partir de lead."""
        lead_id = request.data.get('lead_id')
        unit_id = request.data.get('unit_id')
        deposit_cve = request.data.get('deposit_cve', '0.00')
        notes = request.data.get('notes', '')
        
        if not lead_id or not unit_id:
            return Response({
                'success': False,
                'error': 'lead_id e unit_id são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from decimal import Decimal
        
        result = SalesWorkflow.convert_lead_to_reservation(
            lead_id=lead_id,
            unit_id=unit_id,
            user=request.user,
            deposit_cve=Decimal(deposit_cve),
            notes=notes
        )
        
        if result.get('success'):
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def create_contract(self, request):
        """Converter reserva em contrato."""
        reservation_id = request.data.get('reservation_id')
        
        if not reservation_id:
            return Response({
                'success': False,
                'error': 'reservation_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SalesWorkflow.reservation_to_contract(
            reservation_id=reservation_id,
            user=request.user
        )
        
        if result.get('success'):
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def request_signature(self, request):
        """Criar pedido de assinatura para contrato."""
        contract_id = request.data.get('contract_id')
        
        if not contract_id:
            return Response({
                'success': False,
                'error': 'contract_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SalesWorkflow.create_signature_request(
            contract_id=contract_id,
            user=request.user
        )
        
        if result.get('success'):
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def mark_signed(self, request):
        """Marcar contrato como assinado."""
        contract_id = request.data.get('contract_id')
        signature_data = request.data.get('signature_data', {})
        
        if not contract_id:
            return Response({
                'success': False,
                'error': 'contract_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SalesWorkflow.mark_contract_signed(
            contract_id=contract_id,
            signature_data=signature_data
        )
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def prepare_deed(self, request):
        """Preparar escritura após contrato assinado."""
        contract_id = request.data.get('contract_id')
        deed_date = request.data.get('deed_date')
        notes = request.data.get('notes', '')
        
        if not contract_id:
            return Response({
                'success': False,
                'error': 'contract_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = SalesWorkflow.contract_to_deed(
            contract_id=contract_id,
            deed_date=deed_date,
            notes=notes
        )
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class ProjectInitWorkflowViewSet(viewsets.ViewSet):
    """API para workflow de inicialização de projeto."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def initialize(self, request):
        """Inicializar projeto de obra a partir de contrato."""
        contract_id = request.data.get('contract_id')
        start_date = request.data.get('start_date')
        
        if not contract_id:
            return Response({
                'success': False,
                'error': 'contract_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = ProjectInitWorkflow.create_construction_project(
            contract_id=contract_id,
            user=request.user,
            start_date=start_date
        )
        
        if result.get('success'):
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def import_bim(self, request):
        """Importar modelo BIM para projeto."""
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response({
                'success': False,
                'error': 'project_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Implementar upload de IFC
        result = ProjectInitWorkflow.import_bim_model(
            project_id=project_id,
            ifc_file=request.FILES.get('ifc_file'),
            user=request.user
        )
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class PaymentMilestoneWorkflowViewSet(viewsets.ViewSet):
    """API para workflow de milestones de pagamento."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def check_milestone(self, request):
        """Verificar milestone de pagamento para uma task."""
        task_id = request.data.get('task_id')
        
        if not task_id:
            return Response({
                'success': False,
                'error': 'task_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = PaymentMilestoneWorkflow.check_payment_milestone(
            task_id=task_id,
            user=request.user
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def reconcile(self, request):
        """Reconciliar pagamento recebido."""
        payment_id = request.data.get('payment_id')
        payment_data = request.data.get('payment_data', {})
        
        if not payment_id:
            return Response({
                'success': False,
                'error': 'payment_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = PaymentMilestoneWorkflow.reconcile_payment(
            payment_id=payment_id,
            payment_data=payment_data,
            user=request.user
        )
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def schedule(self, request):
        """Obter cronograma de pagamentos de um contrato."""
        contract_id = request.query_params.get('contract_id')
        
        if not contract_id:
            return Response({
                'success': False,
                'error': 'contract_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = PaymentMilestoneWorkflow.get_payment_schedule(
            contract_id=contract_id
        )
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class NotificationWorkflowViewSet(viewsets.ViewSet):
    """API para workflow de notificações."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """Enviar notificação manual."""
        event_type = request.data.get('event_type')
        recipient_id = request.data.get('recipient_id')
        recipient_type = request.data.get('recipient_type', 'lead')
        data = request.data.get('data', {})
        channels = request.data.get('channels')
        
        if not event_type or not recipient_id:
            return Response({
                'success': False,
                'error': 'event_type e recipient_id são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = NotificationWorkflow.notify(
            event_type=event_type,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            data=data,
            channels=channels
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Listar templates de notificação disponíveis."""
        templates = NotificationWorkflow.NOTIFICATION_TEMPLATES
        
        return Response([{
            'event_type': key,
            'channels': {
                'whatsapp': bool(config.get('whatsapp')),
                'email': bool(config.get('email')),
                'push': bool(config.get('push'))
            }
        } for key, config in templates.items()])


class WorkflowDashboardViewSet(viewsets.ViewSet):
    """API para dashboard de workflows."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        from apps.workflows.models import WorkflowInstance
        """Estatísticas de workflows."""
        stats = {
            'active_workflows': WorkflowInstance.objects.filter(
                status__in=[WorkflowInstance.STATUS_RUNNING, WorkflowInstance.STATUS_PENDING]
            ).count(),
            'completed_today': WorkflowInstance.objects.filter(
                status=WorkflowInstance.STATUS_COMPLETED,
                completed_at__date=timezone.now().date()
            ).count(),
            'failed_last_24h': WorkflowInstance.objects.filter(
                status=WorkflowInstance.STATUS_FAILED,
                updated_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Listar workflows ativos."""
        instances = WorkflowInstance.objects.filter(
            status__in=[
                WorkflowInstance.STATUS_RUNNING,
                WorkflowInstance.STATUS_PENDING,
                WorkflowInstance.STATUS_RETRYING
            ]
        ).select_related('workflow').order_by('-created_at')[:20]
        
        return Response([{
            'id': str(i.id),
            'workflow_name': i.workflow.name,
            'workflow_type': i.workflow.workflow_type,
            'status': i.status,
            'progress': i.progress_percent,
            'current_step': i.current_step,
            'total_steps': i.total_steps,
            'created_at': i.created_at.isoformat(),
            'started_at': i.started_at.isoformat() if i.started_at else None,
        } for i in instances])
    
    @action(detail=False, methods=['get'])
    def recent_failures(self, request):
        """Listar falhas recentes."""
        instances = WorkflowInstance.objects.filter(
            status=WorkflowInstance.STATUS_FAILED
        ).select_related('workflow').order_by('-updated_at')[:10]
        
        return Response([{
            'id': str(i.id),
            'workflow_name': i.workflow.name,
            'error_message': i.error_message,
            'error_step': i.error_step,
            'retry_count': i.retry_count,
            'created_at': i.created_at.isoformat(),
            'failed_at': i.updated_at.isoformat(),
        } for i in instances])
