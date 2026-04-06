"""
Payment Milestone Workflow — Progresso de Obra → Pagamentos

Este módulo implementa a geração automática de pagamentos baseados
em milestones de obra:
1. Task concluída é verificada como milestone de pagamento
2. Fatura/Prestacao é gerada
3. Cliente é notificado
4. Pagamento é aguardado e reconciliado
"""
import logging
from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Optional

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class PaymentMilestoneWorkflow:
    """
    Gerar pagamentos baseado em milestones de obra.
    """
    
    # Mapeamento de fases para milestones de pagamento
    PHASE_MILESTONES = {
        'FOUNDATION': {
            'name': 'Fundação Concluída',
            'percentage': 15,
            'description': 'Conclusão da fase de fundações'
        },
        'STRUCTURE': {
            'name': 'Estrutura Concluída',
            'percentage': 25,
            'description': 'Conclusão da estrutura do edifício'
        },
        'MASONRY': {
            'name': 'Alvenaria Concluída',
            'percentage': 15,
            'description': 'Conclusão da alvenaria'
        },
        'MEP': {
            'name': 'Instalações Concluídas',
            'percentage': 10,
            'description': 'Conclusão das instalações hidro/eletricas'
        },
        'FINISHES': {
            'name': 'Acabamentos Concluídos',
            'percentage': 25,
            'description': 'Conclusão dos acabamentos'
        },
        'DELIVERY': {
            'name': 'Entrega',
            'percentage': 10,
            'description': 'Entrega final da unidade'
        },
    }
    
    @classmethod
    def check_payment_milestone(
        cls,
        task_id: str,
        user=None,
    ) -> dict:
        """
        Verificar se task concluída atinge milestone de pagamento.
        
        Args:
            task_id: UUID da task concluída
            user: User que completou a task
            
        Returns:
            dict com resultado da verificação
        """
        from apps.construction.models import ConstructionTask, ConstructionPhase
        
        logger.info(f'Checking payment milestone for task: {task_id}')
        
        try:
            # 1. Buscar task
            task = ConstructionTask.objects.select_related(
                'phase', 'project', 'building'
            ).get(id=task_id)
            
            if task.status != ConstructionTask.STATUS_COMPLETED:
                return {
                    'success': False,
                    'is_milestone': False,
                    'message': 'Task não está concluída'
                }
            
            # 2. Verificar se a fase é um milestone de pagamento
            phase_type = task.phase.phase_type
            if phase_type not in cls.PHASE_MILESTONES:
                return {
                    'success': True,
                    'is_milestone': False,
                    'message': 'Fase não é um milestone de pagamento'
                }
            
            # 3. Verificar se todas as tasks da fase estão concluídas
            phase = task.phase
            phase_tasks = phase.tasks.all()
            completed_tasks = phase_tasks.filter(status=ConstructionTask.STATUS_COMPLETED)
            
            # Só gera milestone se a fase está completa
            if completed_tasks.count() != phase_tasks.count():
                return {
                    'success': True,
                    'is_milestone': False,
                    'progress': f'{completed_tasks.count()}/{phase_tasks.count()}',
                    'message': 'Fase ainda não está completa'
                }
            
            # 4. Buscar contrato associado
            contract = cls._get_contract_for_project(task.project, task.building)
            if not contract:
                return {
                    'success': False,
                    'is_milestone': False,
                    'message': 'Nenhum contrato encontrado para este projeto'
                }
            
            # 5. Verificar se já existe fatura para este milestone
            milestone_name = cls.PHASE_MILESTONES[phase_type]['name']
            existing = cls._check_existing_milestone_payment(contract, phase_type)
            if existing:
                return {
                    'success': True,
                    'is_milestone': True,
                    'already_generated': True,
                    'payment_id': existing.get('payment_id'),
                    'message': f'Milestone {milestone_name} já gerado'
                }
            
            # 6. Gerar pagamento de milestone
            result = cls._generate_milestone_payment(
                contract=contract,
                phase=phase,
                phase_type=phase_type,
                user=user
            )
            
            return result
            
        except ConstructionTask.DoesNotExist:
            return {
                'success': False,
                'error': 'Task não encontrada'
            }
        except Exception as e:
            logger.error(f'Error checking payment milestone: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def _get_contract_for_project(cls, project, building) -> Optional:
        """Buscar contrato associado ao projeto/edifício."""
        from apps.contracts.models import Contract
        from apps.inventory.models import Unit
        
        # Buscar unidades do edifício
        units = Unit.objects.filter(floor__building=building)
        
        # Buscar contratos ativos para estas unidades
        contract = Contract.objects.filter(
            unit__in=units,
            status=Contract.STATUS_ACTIVE
        ).select_related('lead', 'payment_plan').first()
        
        return contract
    
    @classmethod
    def _check_existing_milestone_payment(cls, contract, phase_type: str) -> Optional[dict]:
        """Verificar se já existe pagamento para este milestone."""
        from apps.payments.models import PaymentPlanItem
        
        milestone_name = cls.PHASE_MILESTONES[phase_type]['name']
        
        try:
            # Verificar nos itens do plano de pagamento
            existing = PaymentPlanItem.objects.filter(
                plan__contract=contract,
                item_type=PaymentPlanItem.TYPE_INSTALLMENT
            ).filter(
                models.Q(description__icontains=milestone_name) |
                models.Q(milestone_phase=phase_type)
            ).first()
            
            if existing:
                return {
                    'payment_id': str(existing.id),
                    'is_paid': existing.is_paid
                }
        except Exception as e:
            logger.warning(f'Error checking existing milestone: {e}')
        
        return None
    
    @classmethod
    @transaction.atomic
    def _generate_milestone_payment(
        cls,
        contract,
        phase,
        phase_type: str,
        user=None,
    ) -> dict:
        """Gerar pagamento de milestone."""
        from apps.payments.models import PaymentPlan, PaymentPlanItem
        from apps.contracts.models import Payment
        
        milestone = cls.PHASE_MILESTONES[phase_type]
        
        # Calcular valor do milestone
        total_price = contract.total_price_cve
        milestone_percentage = Decimal(str(milestone['percentage']))
        milestone_amount = (total_price * milestone_percentage / 100).quantize(Decimal('0.01'))
        
        # Buscar ou criar plano de pagamento
        payment_plan, _ = PaymentPlan.objects.get_or_create(
            contract=contract,
            defaults={
                'total_cve': total_price,
                'plan_type': PaymentPlan.TYPE_CUSTOM
            }
        )
        
        # Determinar próxima ordem
        next_order = payment_plan.items.count()
        
        # Criar item de pagamento
        due_date = timezone.now().date() + timedelta(days=15)  # 15 dias para pagar
        
        item = PaymentPlanItem.objects.create(
            plan=payment_plan,
            item_type=PaymentPlanItem.TYPE_INSTALLMENT,
            percentage=milestone_percentage,
            amount_cve=milestone_amount,
            due_date=due_date,
            order=next_order,
            description=f"{milestone['name']} - {phase.name}"
        )
        
        # Criar registro de pagamento no contrato
        payment = Payment.objects.create(
            contract=contract,
            payment_type=Payment.PAYMENT_INSTALLMENT,
            amount_cve=milestone_amount,
            due_date=due_date,
            status=Payment.STATUS_PENDING,
            reference=f'MILESTONE-{phase_type}-{next_order}'
        )
        
        # Vincular
        item.payment = payment
        item.save(update_fields=['payment'])
        
        # Criar workflow instance
        from apps.workflows.models import WorkflowInstance, WorkflowDefinition
        try:
            workflow_def = WorkflowDefinition.objects.get(
                workflow_type=WorkflowDefinition.TYPE_PAYMENT_MILESTONE,
                is_active=True
            )
            WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_COMPLETED,
                context={
                    'contract_id': str(contract.id),
                    'phase_id': str(phase.id),
                    'phase_type': phase_type,
                    'payment_id': str(payment.id),
                    'amount': str(milestone_amount)
                },
                trigger_model='ConstructionPhase',
                trigger_object_id=str(phase.id),
                completed_at=timezone.now()
            )
        except WorkflowDefinition.DoesNotExist:
            pass
        
        # Notificar cliente
        from apps.workflows.tasks import send_workflow_notification
        send_workflow_notification.delay(
            notification_type='payment_milestone',
            lead_id=str(contract.lead.id),
            contract_id=str(contract.id),
            payment_id=str(payment.id),
            milestone_name=milestone['name'],
            amount=str(milestone_amount),
            due_date=due_date.isoformat()
        )
        
        return {
            'success': True,
            'is_milestone': True,
            'payment_id': str(payment.id),
            'plan_item_id': str(item.id),
            'milestone_name': milestone['name'],
            'amount_cve': str(milestone_amount),
            'percentage': milestone['percentage'],
            'due_date': due_date.isoformat(),
            'message': f'Pagamento de milestone gerado: {milestone["name"]} - {milestone_amount} CVE'
        }
    
    @classmethod
    def reconcile_payment(
        cls,
        payment_id: str,
        payment_data: dict,
        user=None,
    ) -> dict:
        """
        Reconciliar pagamento recebido.
        
        Args:
            payment_id: UUID do pagamento
            payment_data: Dados do pagamento (referencia, data, valor)
            user: User que está reconciliando
            
        Returns:
            dict com resultado da reconciliação
        """
        from apps.contracts.models import Payment
        
        logger.info(f'Reconciling payment: {payment_id}')
        
        try:
            payment = Payment.objects.select_related('contract').get(id=payment_id)
            
            if payment.status == Payment.STATUS_PAID:
                return {
                    'success': False,
                    'error': 'Pagamento já está marcado como pago'
                }
            
            # Marcar como pago
            payment.status = Payment.STATUS_PAID
            payment.paid_date = payment_data.get('paid_date', timezone.now().date())
            payment.save(update_fields=['status', 'paid_date'])
            
            # Atualizar item do plano
            try:
                from apps.payments.models import PaymentPlanItem
                item = PaymentPlanItem.objects.get(payment=payment)
                # Notificar confirmação
                from apps.workflows.tasks import send_workflow_notification
                send_workflow_notification.delay(
                    notification_type='payment_received',
                    lead_id=str(payment.contract.lead.id),
                    payment_id=str(payment.id),
                    amount=str(payment.amount_cve)
                )
            except PaymentPlanItem.DoesNotExist:
                pass
            
            return {
                'success': True,
                'payment_id': str(payment.id),
                'contract_id': str(payment.contract.id),
                'amount': str(payment.amount_cve),
                'paid_date': payment.paid_date.isoformat(),
                'message': 'Pagamento reconciliado com sucesso'
            }
            
        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Pagamento não encontrado'
            }
        except Exception as e:
            logger.error(f'Error reconciling payment: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def get_payment_schedule(
        cls,
        contract_id: str,
    ) -> dict:
        """
        Obter cronograma de pagamentos para um contrato.
        
        Args:
            contract_id: UUID do contrato
            
        Returns:
            dict com cronograma completo
        """
        from apps.contracts.models import Contract
        from apps.payments.models import PaymentPlan, PaymentPlanItem
        
        try:
            contract = Contract.objects.select_related('payment_plan').get(id=contract_id)
            
            # Buscar ou criar plano
            payment_plan, created = PaymentPlan.objects.get_or_create(
                contract=contract,
                defaults={
                    'total_cve': contract.total_price_cve,
                    'plan_type': PaymentPlan.TYPE_STANDARD
                }
            )
            
            if created:
                payment_plan.generate_standard()
            
            # Buscar items
            items = payment_plan.items.all().order_by('order')
            
            schedule = []
            for item in items:
                schedule.append({
                    'id': str(item.id),
                    'type': item.item_type,
                    'type_display': item.get_item_type_display(),
                    'description': getattr(item, 'description', ''),
                    'amount_cve': str(item.amount_cve),
                    'percentage': str(item.percentage),
                    'due_date': item.due_date.isoformat() if item.due_date else None,
                    'is_paid': item.is_paid,
                    'order': item.order,
                })
            
            return {
                'success': True,
                'contract_id': str(contract_id),
                'total_cve': str(contract.total_price_cve),
                'plan_type': payment_plan.get_plan_type_display(),
                'schedule': schedule,
                'paid_amount': str(sum(
                    item.amount_cve for item in items if item.is_paid
                )),
                'pending_amount': str(sum(
                    item.amount_cve for item in items if not item.is_paid
                ))
            }
            
        except Contract.DoesNotExist:
            return {
                'success': False,
                'error': 'Contrato não encontrado'
            }
        except Exception as e:
            logger.error(f'Error getting payment schedule: {e}')
            return {
                'success': False,
                'error': str(e)
            }


# Necessário para queries
from django.db import models
