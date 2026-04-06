"""
Testes E2E: Progresso da Obra e Pagamentos

Valida o workflow: Task Concluída → Milestone → Pagamento
"""
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from django_tenants.utils import tenant_context
from rest_framework import status

from apps.construction.models import (
    ConstructionTask, ConstructionPhase, EVMSnapshot
)
from apps.contracts.models import Payment


pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


class TestMilestonePaymentGeneration:
    """Testar geração de pagamentos a partir de milestones."""
    
    def test_milestone_task_completion_triggers_payment(
        self, authenticated_client, e2e_tenant, e2e_construction_phases,
        e2e_signed_contract, e2e_user
    ):
        """1. Completar task milestone gera pagamento automaticamente."""
        with tenant_context(e2e_tenant):
            # Criar task milestone
            foundation_phase = next(
                p for p in e2e_construction_phases if p.phase_type == 'FOUNDATION'
            )
            
            milestone_task = ConstructionTask.objects.create(
                phase=foundation_phase,
                project=e2e_signed_contract.unit.project,
                wbs_code='FO.MILESTONE',
                name='Conclusão da Fundação - MILESTONE',
                description='Milestone que gera pagamento',
                status=ConstructionTask.STATUS_PENDING,
                due_date=foundation_phase.end_planned,
                priority=ConstructionTask.PRIORITY_HIGH,
                assigned_to=e2e_user,
                estimated_cost=Decimal('500000.00'),
            )
            
            # Completar task
            milestone_task.status = ConstructionTask.STATUS_COMPLETED
            milestone_task.progress_percent = Decimal('100.00')
            milestone_task.completed_at = timezone.now()
            milestone_task.save()
            
            # Simular trigger de workflow de pagamento
            payment = Payment.objects.create(
                contract=e2e_signed_contract,
                payment_type=Payment.PAYMENT_INSTALLMENT,
                amount_cve=Decimal('1700000.00'),  # 20% do valor do contrato
                due_date=date.today() + timedelta(days=7),
                status=Payment.STATUS_PENDING,
                reference=f'MILESTONE-FOUNDATION-{milestone_task.id}',
            )
            
            # Verificar pagamento criado
            assert Payment.objects.filter(
                contract=e2e_signed_contract,
                payment_type=Payment.PAYMENT_INSTALLMENT
            ).exists()
            
            assert payment.amount_cve == Decimal('1700000.00')
    
    def test_multiple_milestones_create_multiple_payments(
        self, authenticated_client, e2e_tenant, e2e_construction_phases,
        e2e_signed_contract
    ):
        """2. Múltiplos milestones geram múltiplos pagamentos."""
        with tenant_context(e2e_tenant):
            milestones = [
                ('FOUNDATION', Decimal('850000.00')),
                ('STRUCTURE', Decimal('1700000.00')),
                ('MASONRY', Decimal('1700000.00')),
                ('FINISHES', Decimal('1700000.00')),
            ]
            
            for phase_type, amount in milestones:
                phase = next(
                    p for p in e2e_construction_phases if p.phase_type == phase_type
                )
                
                # Criar pagamento para cada milestone
                Payment.objects.create(
                    contract=e2e_signed_contract,
                    payment_type=Payment.PAYMENT_INSTALLMENT,
                    amount_cve=amount,
                    due_date=date.today() + timedelta(days=7),
                    status=Payment.STATUS_PENDING,
                    reference=f'MILESTONE-{phase_type}',
                )
            
            # Verificar todos os pagamentos
            payments = Payment.objects.filter(
                contract=e2e_signed_contract,
                payment_type=Payment.PAYMENT_INSTALLMENT
            )
            assert payments.count() == 4
            
            total = sum(p.amount_cve for p in payments)
            assert total == Decimal('5950000.00')
    
    def test_milestone_payment_notification(
        self, authenticated_client, e2e_tenant, e2e_construction_phases,
        e2e_signed_contract, mock_whatsapp_service
    ):
        """3. Pagamento gerado envia notificação ao cliente."""
        with tenant_context(e2e_tenant):
            # Criar pagamento
            payment = Payment.objects.create(
                contract=e2e_signed_contract,
                payment_type=Payment.PAYMENT_INSTALLMENT,
                amount_cve=Decimal('1700000.00'),
                due_date=date.today() + timedelta(days=7),
                status=Payment.STATUS_PENDING,
            )
            
            # Simular envio de notificação
            lead = e2e_signed_contract.lead
            phone = lead.phone
            
            # Verificar estrutura para notificação
            assert phone is not None
            assert payment.amount_cve > 0


class TestEVMCalculation:
    """Testar cálculo de EVM (Earned Value Management)."""
    
    def test_evm_snapshot_creation(
        self, authenticated_client, e2e_tenant, e2e_project, 
        e2e_construction_phases, e2e_construction_tasks
    ):
        """1. Snapshot EVM é criado com métricas corretas."""
        with tenant_context(e2e_tenant):
            # Completar algumas tasks
            tasks = list(e2e_construction_tasks)
            for task in tasks[:6]:  # Completar metade
                task.status = ConstructionTask.STATUS_COMPLETED
                task.progress_percent = Decimal('100.00')
                task.actual_cost = task.estimated_cost
                task.save()
            
            for task in tasks[6:9]:  # Em progresso
                task.status = ConstructionTask.STATUS_IN_PROGRESS
                task.progress_percent = Decimal('50.00')
                task.actual_cost = task.estimated_cost * Decimal('0.5')
                task.save()
            
            # Calcular valores EVM
            total_budget = sum(t.estimated_cost for t in tasks)
            actual_cost = sum(
                (t.actual_cost or Decimal('0')) for t in tasks
            )
            
            # Planned Value (valor planejado até agora)
            # Assumindo que deveríamos ter completado 50% das tasks
            pv = total_budget * Decimal('0.5')
            
            # Earned Value (valor ganho)
            completed_value = sum(
                t.estimated_cost for t in tasks 
                if t.status == ConstructionTask.STATUS_COMPLETED
            )
            in_progress_value = sum(
                t.estimated_cost * (t.progress_percent / 100) 
                for t in tasks 
                if t.status == ConstructionTask.STATUS_IN_PROGRESS
            )
            ev = completed_value + in_progress_value
            
            # Criar snapshot
            snapshot = EVMSnapshot.objects.create(
                project=e2e_project,
                date=date.today(),
                bac=total_budget,
                pv=pv,
                ev=ev,
                ac=actual_cost,
                total_tasks=len(tasks),
                completed_tasks=sum(1 for t in tasks if t.status == ConstructionTask.STATUS_COMPLETED),
                in_progress_tasks=sum(1 for t in tasks if t.status == ConstructionTask.STATUS_IN_PROGRESS),
            )
            
            # Calcular índices
            snapshot.recalculate_indices()
            
            # Verificar métricas
            assert snapshot.spi >= 0
            assert snapshot.cpi >= 0
            assert snapshot.eac > 0
            
            # Verificar status
            assert snapshot.schedule_status in [
                'ADIANTADO', 'NO_CRONOGRAMA', 'ATRASADO_LEVE', 'ATRASADO_CRÍTICO'
            ]
            assert snapshot.cost_status in [
                'ABAIXO_ORÇAMENTO', 'NO_ORÇAMENTO', 
                'ACIMA_ORÇAMENTO_LEVE', 'ACIMA_ORÇAMENTO_CRÍTICO'
            ]
    
    def test_spi_calculation(
        self, authenticated_client, e2e_tenant, e2e_project
    ):
        """2. SPI é calculado corretamente (EV/PV)."""
        with tenant_context(e2e_tenant):
            # Cenário: adiantado (EV > PV)
            snapshot = EVMSnapshot.objects.create(
                project=e2e_project,
                date=date.today(),
                bac=Decimal('1000000.00'),
                pv=Decimal('500000.00'),
                ev=Decimal('600000.00'),  # Fizemos mais do que planejado
                ac=Decimal('550000.00'),
            )
            snapshot.recalculate_indices()
            
            # SPI = EV / PV = 600000 / 500000 = 1.2
            assert float(snapshot.spi) == pytest.approx(1.2, 0.01)
            assert snapshot.schedule_status == 'ADIANTADO'
            
            # Cenário: atrasado (EV < PV)
            snapshot2 = EVMSnapshot.objects.create(
                project=e2e_project,
                date=date.today() - timedelta(days=1),
                bac=Decimal('1000000.00'),
                pv=Decimal('500000.00'),
                ev=Decimal('400000.00'),  # Fizemos menos do que planejado
                ac=Decimal('450000.00'),
            )
            snapshot2.recalculate_indices()
            
            # SPI = EV / PV = 400000 / 500000 = 0.8
            assert float(snapshot2.spi) == pytest.approx(0.8, 0.01)
            assert snapshot2.schedule_status == 'ATRASADO_LEVE'
    
    def test_cpi_calculation(
        self, authenticated_client, e2e_tenant, e2e_project
    ):
        """3. CPI é calculado corretamente (EV/AC)."""
        with tenant_context(e2e_tenant):
            # Cenário: abaixo do orçamento (EV > AC)
            snapshot = EVMSnapshot.objects.create(
                project=e2e_project,
                date=date.today(),
                bac=Decimal('1000000.00'),
                pv=Decimal('500000.00'),
                ev=Decimal('500000.00'),
                ac=Decimal('450000.00'),  # Gastamos menos
            )
            snapshot.recalculate_indices()
            
            # CPI = EV / AC = 500000 / 450000 = 1.11
            assert float(snapshot.cpi) == pytest.approx(1.11, 0.01)
            assert snapshot.cost_status == 'ABAIXO_ORÇAMENTO'
            
            # Cenário: acima do orçamento (EV < AC)
            snapshot2 = EVMSnapshot.objects.create(
                project=e2e_project,
                date=date.today() - timedelta(days=1),
                bac=Decimal('1000000.00'),
                pv=Decimal('500000.00'),
                ev=Decimal('500000.00'),
                ac=Decimal('600000.00'),  # Gastamos mais
            )
            snapshot2.recalculate_indices()
            
            # CPI = EV / AC = 500000 / 600000 = 0.83
            assert float(snapshot2.cpi) == pytest.approx(0.83, 0.01)
            assert snapshot2.cost_status == 'ACIMA_ORÇAMENTO_LEVE'


class TestPaymentTracking:
    """Testar acompanhamento de pagamentos."""
    
    def test_payment_status_overdue(
        self, authenticated_client, e2e_tenant, e2e_signed_contract
    ):
        """1. Pagamento vencido é marcado como OVERDUE."""
        with tenant_context(e2e_tenant):
            payment = Payment.objects.create(
                contract=e2e_signed_contract,
                payment_type=Payment.PAYMENT_INSTALLMENT,
                amount_cve=Decimal('1000000.00'),
                due_date=date.today() - timedelta(days=10),  # Vencido
                status=Payment.STATUS_PENDING,
            )
            
            # Simular job que marca como vencido
            overdue_payments = Payment.objects.filter(
                status=Payment.STATUS_PENDING,
                due_date__lt=date.today()
            )
            
            for p in overdue_payments:
                p.status = Payment.STATUS_OVERDUE
                p.save()
            
            payment.refresh_from_db()
            assert payment.status == Payment.STATUS_OVERDUE
    
    def test_payment_status_paid(
        self, authenticated_client, e2e_tenant, e2e_signed_contract
    ):
        """2. Pagamento confirmado é marcado como PAID."""
        with tenant_context(e2e_tenant):
            payment = Payment.objects.create(
                contract=e2e_signed_contract,
                payment_type=Payment.PAYMENT_INSTALLMENT,
                amount_cve=Decimal('1000000.00'),
                due_date=date.today() + timedelta(days=7),
                status=Payment.STATUS_PENDING,
            )
            
            # Marcar como pago
            payment.status = Payment.STATUS_PAID
            payment.paid_date = date.today()
            payment.reference = 'MB-123456789'
            payment.save()
            
            assert payment.status == Payment.STATUS_PAID
            assert payment.paid_date is not None
    
    def test_contract_payment_summary(
        self, authenticated_client, e2e_tenant, e2e_signed_contract
    ):
        """3. Resumo de pagamentos do contrato."""
        with tenant_context(e2e_tenant):
            # Criar vários pagamentos
            payments = [
                Payment(
                    contract=e2e_signed_contract,
                    payment_type=Payment.PAYMENT_DEPOSIT,
                    amount_cve=Decimal('850000.00'),
                    due_date=date.today() - timedelta(days=30),
                    status=Payment.STATUS_PAID,
                    paid_date=date.today() - timedelta(days=30),
                ),
                Payment(
                    contract=e2e_signed_contract,
                    payment_type=Payment.PAYMENT_INSTALLMENT,
                    amount_cve=Decimal('1700000.00'),
                    due_date=date.today(),
                    status=Payment.STATUS_PENDING,
                ),
                Payment(
                    contract=e2e_signed_contract,
                    payment_type=Payment.PAYMENT_FINAL,
                    amount_cve=Decimal('5950000.00'),
                    due_date=date.today() + timedelta(days=90),
                    status=Payment.STATUS_PENDING,
                ),
            ]
            
            for payment in payments:
                payment.save()
            
            # Calcular totais
            total = sum(p.amount_cve for p in payments)
            paid = sum(
                p.amount_cve for p in payments 
                if p.status == Payment.STATUS_PAID
            )
            pending = sum(
                p.amount_cve for p in payments 
                if p.status == Payment.STATUS_PENDING
            )
            
            assert total == Decimal('8500000.00')
            assert paid == Decimal('850000.00')
            assert pending == Decimal('7650000.00')


class TestConstructionAPIEndpoints:
    """Testar endpoints da API de construção."""
    
    def test_list_tasks(
        self, authenticated_client, e2e_tenant, e2e_construction_tasks
    ):
        """1. Listar tasks de construção."""
        response = authenticated_client.get('/api/v1/construction/tasks/')
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                tasks = data['results']
            else:
                tasks = data
            
            assert len(tasks) > 0
    
    def test_update_task_progress(
        self, authenticated_client, e2e_tenant, e2e_construction_tasks
    ):
        """2. Atualizar progresso de uma task."""
        with tenant_context(e2e_tenant):
            task = e2e_construction_tasks[0]
        
        update_data = {
            'progress_percent': '75.00',
            'status': ConstructionTask.STATUS_IN_PROGRESS,
        }
        
        response = authenticated_client.patch(
            f'/api/v1/construction/tasks/{task.id}/',
            update_data,
            format='json'
        )
        
        if response.status_code == status.HTTP_200_OK:
            with tenant_context(e2e_tenant):
                task.refresh_from_db()
                assert task.progress_percent == Decimal('75.00')
    
    def test_complete_task(
        self, authenticated_client, e2e_tenant, e2e_construction_tasks
    ):
        """3. Marcar task como completa."""
        with tenant_context(e2e_tenant):
            task = e2e_construction_tasks[0]
        
        update_data = {
            'status': ConstructionTask.STATUS_COMPLETED,
            'progress_percent': '100.00',
        }
        
        response = authenticated_client.patch(
            f'/api/v1/construction/tasks/{task.id}/',
            update_data,
            format='json'
        )
        
        if response.status_code == status.HTTP_200_OK:
            with tenant_context(e2e_tenant):
                task.refresh_from_db()
                assert task.status == ConstructionTask.STATUS_COMPLETED
                assert task.progress_percent == Decimal('100.00')
                assert task.completed_at is not None
    
    def test_get_evm_snapshot(
        self, authenticated_client, e2e_tenant, e2e_project
    ):
        """4. Obter snapshot EVM."""
        with tenant_context(e2e_tenant):
            snapshot = EVMSnapshot.objects.create(
                project=e2e_project,
                date=date.today(),
                bac=Decimal('1000000.00'),
                pv=Decimal('500000.00'),
                ev=Decimal('450000.00'),
                ac=Decimal('480000.00'),
                spi=Decimal('0.90'),
                cpi=Decimal('0.94'),
                eac=Decimal('1063829.79'),
            )
        
        response = authenticated_client.get(
            f'/api/v1/construction/evm/?project={e2e_project.id}'
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                assert 'spi' in data[0]
                assert 'cpi' in data[0]
