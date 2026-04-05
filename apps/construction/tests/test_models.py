"""
Unit tests for Construction models.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from apps.construction.models import (
    ConstructionPhase,
    ConstructionTask,
    TaskPhoto,
    TaskProgressLog,
    TaskDependency,
    CPMSnapshot,
    EVMSnapshot,
)


@pytest.mark.django_db
class TestConstructionPhase:
    """Testes para ConstructionPhase."""
    
    def test_create_phase(self, tenant_a, project_factory):
        """Testar criação de fase."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            phase = ConstructionPhase.objects.create(
                project=project,
                phase_type='FOUNDATION',
                name='Fundação - Bloco A',
                start_planned=date.today(),
                end_planned=date.today() + timedelta(days=30),
                order=1
            )
            
            assert phase.name == 'Fundação - Bloco A'
            assert phase.phase_type == 'FOUNDATION'
            assert phase.status == ConstructionPhase.STATUS_NOT_STARTED
            assert phase.progress_percent == 0
    
    def test_recalculate_progress(self, tenant_a, project_factory, user_factory):
        """Testar recálculo de progresso da fase."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            phase = ConstructionPhase.objects.create(
                project=project,
                phase_type='FOUNDATION',
                name='Fundação',
                start_planned=date.today(),
                end_planned=date.today() + timedelta(days=30),
                order=1
            )
            
            # Criar tasks
            task1 = ConstructionTask.objects.create(
                project=project,
                phase=phase,
                wbs_code='1.1',
                name='Escavação',
                due_date=date.today() + timedelta(days=10),
                progress_percent=100,
                assigned_to=user,
                created_by=user
            )
            task1.complete()
            
            task2 = ConstructionTask.objects.create(
                project=project,
                phase=phase,
                wbs_code='1.2',
                name='Concretagem',
                due_date=date.today() + timedelta(days=20),
                progress_percent=50,
                assigned_to=user,
                created_by=user
            )
            
            # Recalcular
            phase.recalculate_progress()
            
            assert phase.progress_percent == 75  # (100 + 50) / 2
            assert phase.status == ConstructionPhase.STATUS_IN_PROGRESS


@pytest.mark.django_db
class TestConstructionTask:
    """Testes para ConstructionTask."""
    
    def test_create_task(self, tenant_a, project_factory, user_factory):
        """Testar criação de task."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            task = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Escavação',
                due_date=date.today() + timedelta(days=10),
                assigned_to=user,
                created_by=user
            )
            
            assert task.wbs_code == '1.1'
            assert task.name == 'Escavação'
            assert task.status == ConstructionTask.STATUS_PENDING
            assert task.progress_percent == 0
            assert task.advanced_mode == ConstructionTask.ADVANCED_MODE_OFF
    
    def test_task_progress_auto_updates_status(self, tenant_a, project_factory, user_factory):
        """Testar que progresso atualiza status automaticamente."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            task = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Escavação',
                due_date=date.today() + timedelta(days=10),
                assigned_to=user,
                created_by=user
            )
            
            # Atualizar progresso para 50%
            task.update_progress(50)
            
            assert task.progress_percent == 50
            assert task.status == ConstructionTask.STATUS_IN_PROGRESS
            assert task.started_at is not None
            
            # Completar
            task.update_progress(100)
            
            assert task.status == ConstructionTask.STATUS_COMPLETED
            assert task.completed_at is not None
    
    def test_task_is_overdue(self, tenant_a, project_factory, user_factory):
        """Testar detecção de atraso."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            task = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Escavação',
                due_date=date.today() - timedelta(days=5),
                assigned_to=user,
                created_by=user
            )
            
            assert task.is_overdue is True
            assert task.days_overdue == 5
            
            # Completar task
            task.complete()
            assert task.is_overdue is False  # Tasks completadas não estão atrasadas
    
    def test_unique_wbs_per_project(self, tenant_a, project_factory, user_factory):
        """Testar que WBS é único por projeto."""
        from django_tenants.utils import tenant_context
        from django.db import IntegrityError
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task 1',
                due_date=date.today(),
                created_by=user
            )
            
            # Tentar criar outra com mesmo WBS
            with pytest.raises(IntegrityError):
                ConstructionTask.objects.create(
                    project=project,
                    wbs_code='1.1',
                    name='Task 2',
                    due_date=date.today(),
                    created_by=user
                )


@pytest.mark.django_db
class TestTaskDependency:
    """Testes para TaskDependency."""
    
    def test_create_dependency(self, tenant_a, project_factory, user_factory):
        """Testar criação de dependência."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            task1 = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task 1',
                due_date=date.today(),
                assigned_to=user,
                created_by=user
            )
            task2 = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.2',
                name='Task 2',
                due_date=date.today() + timedelta(days=5),
                assigned_to=user,
                created_by=user
            )
            
            dep = TaskDependency.objects.create(
                from_task=task1,
                to_task=task2,
                dependency_type='FS',
                lag_days=2
            )
            
            assert dep.dependency_type == 'FS'
            assert dep.lag_days == 2
    
    def test_self_dependency_not_allowed(self, tenant_a, project_factory, user_factory):
        """Testar que task não pode depender de si mesma."""
        from django_tenants.utils import tenant_context
        from django.core.exceptions import ValidationError
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            task = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task 1',
                due_date=date.today(),
                assigned_to=user,
                created_by=user
            )
            
            dep = TaskDependency(
                from_task=task,
                to_task=task,
                dependency_type='FS'
            )
            
            with pytest.raises(ValidationError):
                dep.clean()


@pytest.mark.django_db
class TestEVMSnapshot:
    """Testes para EVMSnapshot."""
    
    def test_evm_calculations(self, tenant_a, project_factory):
        """Testar cálculos EVM."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            
            snapshot = EVMSnapshot.objects.create(
                project=project,
                date=date.today(),
                bac=Decimal('100000.00'),
                pv=Decimal('50000.00'),
                ev=Decimal('45000.00'),
                ac=Decimal('48000.00'),
                spi=Decimal('0.90'),
                cpi=Decimal('0.94'),
                eac=Decimal('106382.98'),
                vac=Decimal('-6382.98')
            )
            
            assert snapshot.spi == Decimal('0.90')
            assert snapshot.cpi == Decimal('0.94')
            assert snapshot.schedule_status == 'ATRASADO_LEVE'
            assert snapshot.cost_status == 'ACIMA_ORÇAMENTO_LEVE'
            assert snapshot.overall_health == 'ATENÇÃO'


@pytest.mark.django_db
class TestTaskProgressLog:
    """Testes para TaskProgressLog."""
    
    def test_progress_log_created(self, tenant_a, project_factory, user_factory):
        """Testar criação de log de progresso."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            task = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task 1',
                due_date=date.today(),
                assigned_to=user,
                created_by=user
            )
            
            log = TaskProgressLog.objects.create(
                task=task,
                updated_by=user,
                old_percent=0,
                new_percent=50,
                notes='Início do trabalho'
            )
            
            assert log.delta == 50
            assert log.notes == 'Início do trabalho'
