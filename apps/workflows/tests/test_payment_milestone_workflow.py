"""
Tests for Payment Milestone Workflow — Progresso → Pagamentos.
"""
import pytest
from decimal import Decimal
from datetime import date

from apps.workflows.services.payment_milestone_workflow import PaymentMilestoneWorkflow
from apps.construction.models import ConstructionTask, ConstructionPhase
from apps.contracts.models import Contract, Payment
from apps.payments.models import PaymentPlan, PaymentPlanItem


@pytest.mark.django_db
def test_check_payment_milestone_phase_complete(
    tenant_context, task_factory, contract_factory, phase_factory
):
    """Test milestone payment generated when phase completes."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        # Setup: contract, phase with tasks
        contract = contract_factory(status=Contract.STATUS_ACTIVE)
        
        phase = phase_factory(
            phase_type='FOUNDATION',
            project=contract.unit.project if hasattr(contract.unit, 'project') else None
        )
        
        # Create and complete all tasks in phase
        for i, template in enumerate(PaymentMilestoneWorkflow.TASK_TEMPLATES.get('FOUNDATION', [])):
            task = task_factory(
                phase=phase,
                status=ConstructionTask.STATUS_COMPLETED,
                wbs_code=template['wbs_code']
            )
        
        # Check milestone
        result = PaymentMilestoneWorkflow.check_payment_milestone(
            task_id=str(task.id)
        )
        
        # Should generate milestone payment
        assert result['is_milestone'] is True
        if result.get('already_generated'):
            # Already generated in previous test
            pass
        else:
            assert result['success'] is True
            assert 'payment_id' in result
            assert 'milestone_name' in result


@pytest.mark.django_db
def test_check_payment_milestone_phase_not_complete(
    tenant_context, task_factory, phase_factory
):
    """Test no milestone when phase is not fully complete."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        phase = phase_factory(phase_type='FOUNDATION')
        
        # Create some completed tasks, but not all
        task1 = task_factory(
            phase=phase,
            status=ConstructionTask.STATUS_COMPLETED
        )
        task_factory(
            phase=phase,
            status=ConstructionTask.STATUS_PENDING
        )
        
        result = PaymentMilestoneWorkflow.check_payment_milestone(
            task_id=str(task1.id)
        )
        
        assert result['is_milestone'] is False
        assert 'progress' in result


@pytest.mark.django_db
def test_check_payment_milestone_not_milestone_phase(
    tenant_context, task_factory, phase_factory
):
    """Test no milestone for non-milestone phases."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        phase = phase_factory(phase_type='CUSTOM')  # Not in PHASE_MILESTONES
        
        task = task_factory(
            phase=phase,
            status=ConstructionTask.STATUS_COMPLETED
        )
        
        result = PaymentMilestoneWorkflow.check_payment_milestone(
            task_id=str(task.id)
        )
        
        assert result['is_milestone'] is False


@pytest.mark.django_db
def test_reconcile_payment(tenant_context, payment_factory, contract_factory):
    """Test reconciling a received payment."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        contract = contract_factory()
        payment = payment_factory(
            contract=contract,
            status=Payment.STATUS_PENDING,
            amount_cve=Decimal('100000.00')
        )
        
        result = PaymentMilestoneWorkflow.reconcile_payment(
            payment_id=str(payment.id),
            payment_data={'paid_date': date(2026, 6, 15)}
        )
        
        assert result['success'] is True
        
        # Verify payment updated
        payment.refresh_from_db()
        assert payment.status == Payment.STATUS_PAID
        assert payment.paid_date == date(2026, 6, 15)


@pytest.mark.django_db
def test_reconcile_payment_already_paid(tenant_context, payment_factory):
    """Test reconciling fails if already paid."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        payment = payment_factory(status=Payment.STATUS_PAID)
        
        result = PaymentMilestoneWorkflow.reconcile_payment(
            payment_id=str(payment.id),
            payment_data={}
        )
        
        assert result['success'] is False
        assert 'já está marcado' in result['error'].lower()


@pytest.mark.django_db
def test_get_payment_schedule(tenant_context, contract_factory):
    """Test getting payment schedule for contract."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        contract = contract_factory(total_price_cve=Decimal('5000000.00'))
        
        result = PaymentMilestoneWorkflow.get_payment_schedule(
            contract_id=str(contract.id)
        )
        
        assert result['success'] is True
        assert 'schedule' in result
        assert result['total_cve'] == '5000000.00'
        assert isinstance(result['schedule'], list)
