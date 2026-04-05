"""
Unit tests for Construction services (CPM, EVM, ProgressUpdater).
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from apps.construction.services import CPMCalculator, EVMCalculator, ProgressUpdater
from apps.construction.models import (
    ConstructionPhase,
    ConstructionTask,
    TaskDependency,
    CPMSnapshot,
)


@pytest.mark.django_db
class TestCPMCalculator:
    """Testes para CPMCalculator."""
    
    def test_topological_sort(self, tenant_a, project_factory, user_factory):
        """Testar ordenação topológica."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            # Criar tasks em modo avançado
            task_a = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task A',
                due_date=date.today(),
                advanced_mode=ConstructionTask.ADVANCED_MODE_ON,
                duration_days=3,
                assigned_to=user,
                created_by=user
            )
            task_b = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.2',
                name='Task B',
                due_date=date.today() + timedelta(days=5),
                advanced_mode=ConstructionTask.ADVANCED_MODE_ON,
                duration_days=2,
                assigned_to=user,
                created_by=user
            )
            task_c = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.3',
                name='Task C',
                due_date=date.today() + timedelta(days=10),
                advanced_mode=ConstructionTask.ADVANCED_MODE_ON,
                duration_days=4,
                assigned_to=user,
                created_by=user
            )
            
            # A -> B -> C
            TaskDependency.objects.create(from_task=task_a, to_task=task_b)
            TaskDependency.objects.create(from_task=task_b, to_task=task_c)
            
            calculator = CPMCalculator(str(project.id))
            calculator.load_data()
            sorted_tasks = calculator.topological_sort()
            
            assert len(sorted_tasks) == 3
            assert sorted_tasks[0] == str(task_a.id)
            assert sorted_tasks[2] == str(task_c.id)
    
    def test_critical_path_identification(self, tenant_a, project_factory, user_factory):
        """Testar identificação do caminho crítico."""
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
            
            # Criar tasks em modo avançado
            task_a = ConstructionTask.objects.create(
                project=project,
                phase=phase,
                wbs_code='1.1',
                name='Task A',
                due_date=date.today() + timedelta(days=3),
                advanced_mode=ConstructionTask.ADVANCED_MODE_ON,
                duration_days=3,
                assigned_to=user,
                created_by=user
            )
            task_b = ConstructionTask.objects.create(
                project=project,
                phase=phase,
                wbs_code='1.2',
                name='Task B',
                due_date=date.today() + timedelta(days=5),
                advanced_mode=ConstructionTask.ADVANCED_MODE_ON,
                duration_days=2,
                assigned_to=user,
                created_by=user
            )
            task_c = ConstructionTask.objects.create(
                project=project,
                phase=phase,
                wbs_code='1.3',
                name='Task C',
                due_date=date.today() + timedelta(days=9),
                advanced_mode=ConstructionTask.ADVANCED_MODE_ON,
                duration_days=4,
                assigned_to=user,
                created_by=user
            )
            
            # A -> B -> C (caminho crítico)
            TaskDependency.objects.create(from_task=task_a, to_task=task_b)
            TaskDependency.objects.create(from_task=task_b, to_task=task_c)
            
            # Recalcular CPM
            calculator = CPMCalculator(str(project.id))
            stats = calculator.recalculate_project()
            
            assert stats['tasks_processed'] == 3
            assert stats['critical_path_length'] == 3  # Todas no caminho crítico
            assert stats['project_duration_days'] == 9  # 3 + 2 + 4
            
            # Verificar snapshots
            task_a.refresh_from_db()
            task_b.refresh_from_db()
            task_c.refresh_from_db()
            
            assert task_a.cpm_data.is_critical is True
            assert task_b.cpm_data.is_critical is True
            assert task_c.cpm_data.is_critical is True
    
    def test_gantt_data_generation(self, tenant_a, project_factory, user_factory):
        """Testar geração de dados para Gantt."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            task = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task Test',
                due_date=date.today() + timedelta(days=5),
                advanced_mode=ConstructionTask.ADVANCED_MODE_ON,
                duration_days=5,
                progress_percent=50,
                assigned_to=user,
                created_by=user
            )
            
            calculator = CPMCalculator(str(project.id))
            gantt_data = calculator.get_gantt_data()
            
            assert len(gantt_data) == 1
            assert gantt_data[0]['wbs_code'] == '1.1'
            assert gantt_data[0]['duration'] == 5
            assert gantt_data[0]['progress'] == 50


@pytest.mark.django_db
class TestEVMCalculator:
    """Testes para EVMCalculator."""
    
    def test_evm_calculation(self, tenant_a, project_factory, user_factory):
        """Testar cálculo EVM básico."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            # Criar tasks com custos e progressos
            task1 = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task 1',
                due_date=date.today() - timedelta(days=5),  # Deveria estar pronta
                estimated_cost=Decimal('10000.00'),
                actual_cost=Decimal('9500.00'),
                progress_percent=100,  # Completa
                assigned_to=user,
                created_by=user
            )
            task1.complete()
            
            task2 = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.2',
                name='Task 2',
                due_date=date.today() + timedelta(days=5),  # Ainda não deveria estar pronta
                estimated_cost=Decimal('10000.00'),
                actual_cost=Decimal('4000.00'),
                progress_percent=50,  # 50% completa
                assigned_to=user,
                created_by=user
            )
            
            calculator = EVMCalculator(str(project.id))
            data = calculator.calculate(save_snapshot=True)
            
            # BAC = 20000
            assert data['bac'] == Decimal('20000.00')
            
            # PV = 10000 (task1 deveria estar pronta)
            assert data['pv'] == Decimal('10000.00')
            
            # EV = 10000*1 + 10000*0.5 = 15000
            assert data['ev'] == Decimal('15000.00')
            
            # AC = 9500 + 4000 = 13500
            assert data['ac'] == Decimal('13500.00')
            
            # SPI = EV/PV = 15000/10000 = 1.5 (adiantado)
            assert data['spi'] == Decimal('1.50')
            
            # CPI = EV/AC = 15000/13500 = 1.11 (abaixo orçamento)
            assert data['cpi'] == Decimal('1.11')
    
    def test_forecast_calculation(self, tenant_a, project_factory, user_factory):
        """Testar previsões EVM."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            # Criar task
            ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task 1',
                due_date=date.today(),
                estimated_cost=Decimal('10000.00'),
                actual_cost=Decimal('5000.00'),
                progress_percent=50,
                assigned_to=user,
                created_by=user
            )
            
            calculator = EVMCalculator(str(project.id))
            calculator.calculate(save_snapshot=True)
            
            forecasts = calculator.get_forecast()
            
            assert 'cost_forecast' in forecasts
            assert 'schedule_forecast' in forecasts
            assert 'recommendations' in forecasts


@pytest.mark.django_db
class TestProgressUpdater:
    """Testes para ProgressUpdater."""
    
    def test_update_progress(self, tenant_a, project_factory, user_factory):
        """Testar atualização de progresso."""
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
            
            updater = ProgressUpdater(task)
            log = updater.update(
                new_percent=Decimal('50'),
                updated_by=user,
                notes='Bom progresso'
            )
            
            assert log is not None
            assert log.old_percent == 0
            assert log.new_percent == 50
            assert log.delta == 50
            
            task.refresh_from_db()
            assert task.progress_percent == 50
            assert task.status == ConstructionTask.STATUS_IN_PROGRESS
    
    def test_update_to_100_completes_task(self, tenant_a, project_factory, user_factory):
        """Testar que 100% completa a task."""
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
            
            updater = ProgressUpdater(task)
            log = updater.update(
                new_percent=Decimal('100'),
                updated_by=user
            )
            
            task.refresh_from_db()
            assert task.status == ConstructionTask.STATUS_COMPLETED
            assert task.completed_at is not None
    
    def test_no_log_for_small_changes(self, tenant_a, project_factory, user_factory):
        """Testar que mudanças pequenas não criam log."""
        from django_tenants.utils import tenant_context
        
        with tenant_context(tenant_a):
            project = project_factory(tenant=tenant_a)
            user = user_factory(tenant=tenant_a)
            
            task = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task 1',
                due_date=date.today(),
                progress_percent=50,
                assigned_to=user,
                created_by=user
            )
            
            updater = ProgressUpdater(task)
            log = updater.update(
                new_percent=Decimal('50.001'),  # Mudança muito pequena
                updated_by=user
            )
            
            assert log is None  # Não deve criar log
