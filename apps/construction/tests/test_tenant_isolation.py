"""
Tenant Isolation Tests for Construction app.

CRÍTICO: Garantir que dados de um tenant não vazam para outro.
Testes MANDATÓRIOS conforme AGENTS.md.
"""
import pytest
from datetime import date, timedelta

from django_tenants.utils import tenant_context

from apps.construction.models import (
    ConstructionPhase,
    ConstructionTask,
    TaskDependency,
    CPMSnapshot,
    EVMSnapshot,
)


@pytest.mark.django_db(transaction=True)
class TestConstructionTenantIsolation:
    """
    Testes de isolamento multi-tenant para Construction.
    
    Garante que:
    1. Tasks do Tenant A não aparecem no Tenant B
    2. Fases do Tenant A não aparecem no Tenant B
    3. CPM/EVM são isolados por tenant
    4. Dependências não cruzam tenants
    """
    
    def test_phase_isolation_between_tenants(self, tenant_a, tenant_b):
        """Fases criadas no Tenant A não devem aparecer no Tenant B."""
        from apps.projects.models import Project
        
        # Criar projeto e fase no Tenant A
        with tenant_context(tenant_a):
            project_a = Project.objects.create(
                name='Projeto A',
                slug='projeto-a',
                status=Project.STATUS_CONSTRUCTION
            )
            phase_a = ConstructionPhase.objects.create(
                project=project_a,
                phase_type='FOUNDATION',
                name='Fundação A',
                start_planned=date.today(),
                end_planned=date.today() + timedelta(days=30),
                order=1
            )
            phase_a_id = str(phase_a.id)
        
        # Verificar que fase não existe no Tenant B
        with tenant_context(tenant_b):
            count = ConstructionPhase.objects.filter(id=phase_a_id).count()
            assert count == 0, 'Fase do Tenant A não deve existir no Tenant B'
            
            # Verificar lista vazia
            all_phases = ConstructionPhase.objects.all()
            assert all_phases.count() == 0
    
    def test_task_isolation_between_tenants(self, tenant_a, tenant_b):
        """Tasks criadas no Tenant A não devem aparecer no Tenant B."""
        from apps.projects.models import Project
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Criar no Tenant A
        with tenant_context(tenant_a):
            project_a = Project.objects.create(
                name='Projeto A',
                slug='projeto-a',
                status=Project.STATUS_CONSTRUCTION
            )
            user_a = User.objects.create_user(
                email='test@empresa-a.cv',
                password='testpass123'
            )
            task_a = ConstructionTask.objects.create(
                project=project_a,
                wbs_code='1.1',
                name='Task A',
                due_date=date.today() + timedelta(days=10),
                assigned_to=user_a,
                created_by=user_a
            )
            task_a_id = str(task_a.id)
        
        # Verificar isolamento no Tenant B
        with tenant_context(tenant_b):
            count = ConstructionTask.objects.filter(id=task_a_id).count()
            assert count == 0, 'Task do Tenant A não deve existir no Tenant B'
            
            # Tentar acessar diretamente deve falhar
            with pytest.raises(ConstructionTask.DoesNotExist):
                ConstructionTask.objects.get(id=task_a_id)
    
    def test_task_list_isolated_per_tenant(self, tenant_a, tenant_b):
        """Listagem de tasks deve retornar apenas do tenant atual."""
        from apps.projects.models import Project
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Criar projetos e tasks em ambos os tenants
        with tenant_context(tenant_a):
            project_a = Project.objects.create(
                name='Projeto A',
                slug='projeto-a',
                status=Project.STATUS_CONSTRUCTION
            )
            user_a = User.objects.create_user(
                email='test@empresa-a.cv',
                password='testpass123'
            )
            ConstructionTask.objects.create(
                project=project_a,
                wbs_code='1.1',
                name='Task A1',
                due_date=date.today(),
                assigned_to=user_a,
                created_by=user_a
            )
            ConstructionTask.objects.create(
                project=project_a,
                wbs_code='1.2',
                name='Task A2',
                due_date=date.today(),
                assigned_to=user_a,
                created_by=user_a
            )
        
        with tenant_context(tenant_b):
            project_b = Project.objects.create(
                name='Projeto B',
                slug='projeto-b',
                status=Project.STATUS_CONSTRUCTION
            )
            user_b = User.objects.create_user(
                email='test@empresa-b.cv',
                password='testpass123'
            )
            ConstructionTask.objects.create(
                project=project_b,
                wbs_code='1.1',
                name='Task B1',
                due_date=date.today(),
                assigned_to=user_b,
                created_by=user_b
            )
        
        # Verificar contagens isoladas
        with tenant_context(tenant_a):
            assert ConstructionTask.objects.count() == 2
            task_names = set(ConstructionTask.objects.values_list('name', flat=True))
            assert task_names == {'Task A1', 'Task A2'}
        
        with tenant_context(tenant_b):
            assert ConstructionTask.objects.count() == 1
            task_names = set(ConstructionTask.objects.values_list('name', flat=True))
            assert task_names == {'Task B1'}
    
    def test_cpm_snapshot_isolation(self, tenant_a, tenant_b):
        """Snapshots CPM devem ser isolados por tenant."""
        from apps.projects.models import Project
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Criar dados CPM no Tenant A
        with tenant_context(tenant_a):
            project_a = Project.objects.create(
                name='Projeto A',
                slug='projeto-a',
                status=Project.STATUS_CONSTRUCTION
            )
            user_a = User.objects.create_user(
                email='test@empresa-a.cv',
                password='testpass123'
            )
            task_a = ConstructionTask.objects.create(
                project=project_a,
                wbs_code='1.1',
                name='Task A',
                due_date=date.today(),
                advanced_mode=ConstructionTask.ADVANCED_MODE_ON,
                duration_days=5,
                assigned_to=user_a,
                created_by=user_a
            )
            snapshot_a = CPMSnapshot.objects.create(
                task=task_a,
                early_start=date.today(),
                early_finish=date.today() + timedelta(days=5),
                is_critical=True,
                total_float=0
            )
            snapshot_a_id = str(snapshot_a.id)
        
        # Verificar isolamento
        with tenant_context(tenant_b):
            count = CPMSnapshot.objects.filter(id=snapshot_a_id).count()
            assert count == 0, 'Snapshot CPM do Tenant A não deve existir no Tenant B'
    
    def test_evm_snapshot_isolation(self, tenant_a, tenant_b):
        """Snapshots EVM devem ser isolados por tenant."""
        from apps.projects.models import Project
        from decimal import Decimal
        
        # Criar snapshot EVM no Tenant A
        with tenant_context(tenant_a):
            project_a = Project.objects.create(
                name='Projeto A',
                slug='projeto-a',
                status=Project.STATUS_CONSTRUCTION
            )
            snapshot_a = EVMSnapshot.objects.create(
                project=project_a,
                date=date.today(),
                bac=Decimal('100000.00'),
                pv=Decimal('50000.00'),
                ev=Decimal('45000.00'),
                ac=Decimal('48000.00'),
                spi=Decimal('0.90'),
                cpi=Decimal('0.94'),
                eac=Decimal('106382.98')
            )
            snapshot_a_id = str(snapshot_a.id)
        
        # Verificar isolamento
        with tenant_context(tenant_b):
            count = EVMSnapshot.objects.filter(id=snapshot_a_id).count()
            assert count == 0, 'Snapshot EVM do Tenant A não deve existir no Tenant B'
    
    def test_dependency_isolation(self, tenant_a, tenant_b):
        """Dependências não devem cruzar entre tenants."""
        from apps.projects.models import Project
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Criar tasks e dependência no Tenant A
        with tenant_context(tenant_a):
            project_a = Project.objects.create(
                name='Projeto A',
                slug='projeto-a',
                status=Project.STATUS_CONSTRUCTION
            )
            user_a = User.objects.create_user(
                email='test@empresa-a.cv',
                password='testpass123'
            )
            task_a1 = ConstructionTask.objects.create(
                project=project_a,
                wbs_code='1.1',
                name='Task A1',
                due_date=date.today(),
                assigned_to=user_a,
                created_by=user_a
            )
            task_a2 = ConstructionTask.objects.create(
                project=project_a,
                wbs_code='1.2',
                name='Task A2',
                due_date=date.today() + timedelta(days=5),
                assigned_to=user_a,
                created_by=user_a
            )
            dep_a = TaskDependency.objects.create(
                from_task=task_a1,
                to_task=task_a2,
                dependency_type='FS'
            )
            dep_a_id = str(dep_a.id)
        
        # Verificar isolamento
        with tenant_context(tenant_b):
            count = TaskDependency.objects.filter(id=dep_a_id).count()
            assert count == 0, 'Dependência do Tenant A não deve existir no Tenant B'
    
    def test_wbs_code_uniqueness_per_project_not_global(self, tenant_a, tenant_b):
        """
        WBS code deve ser único por projeto, não globalmente.
        
        Ou seja, Tenant A e Tenant B podem ter tasks com mesmo WBS
        desde que em projetos diferentes.
        """
        from apps.projects.models import Project
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Criar task no Tenant A
        with tenant_context(tenant_a):
            project_a = Project.objects.create(
                name='Projeto A',
                slug='projeto-a',
                status=Project.STATUS_CONSTRUCTION
            )
            user_a = User.objects.create_user(
                email='test@empresa-a.cv',
                password='testpass123'
            )
            task_a = ConstructionTask.objects.create(
                project=project_a,
                wbs_code='1.1',
                name='Task A',
                due_date=date.today(),
                assigned_to=user_a,
                created_by=user_a
            )
        
        # Criar task com mesmo WBS no Tenant B (deve funcionar)
        with tenant_context(tenant_b):
            project_b = Project.objects.create(
                name='Projeto B',
                slug='projeto-b',
                status=Project.STATUS_CONSTRUCTION
            )
            user_b = User.objects.create_user(
                email='test@empresa-b.cv',
                password='testpass123'
            )
            task_b = ConstructionTask.objects.create(
                project=project_b,
                wbs_code='1.1',  # Mesmo WBS
                name='Task B',
                due_date=date.today(),
                assigned_to=user_b,
                created_by=user_b
            )
            
            # Deve existir
            assert ConstructionTask.objects.filter(wbs_code='1.1').count() == 1


@pytest.mark.django_db(transaction=True)
class TestConstructionAPIIsolation:
    """
    Testes de isolamento via API.
    
    Garante que endpoints retornam apenas dados do tenant correto.
    """
    
    def test_api_task_list_isolated(self, api_client_tenant_a, api_client_tenant_b, tenant_a, tenant_b):
        """API deve retornar apenas tasks do tenant autenticado."""
        from apps.projects.models import Project
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Criar dados
        with tenant_context(tenant_a):
            project_a = Project.objects.create(
                name='Projeto A',
                slug='projeto-a',
                status=Project.STATUS_CONSTRUCTION
            )
            user_a = User.objects.get(email='gestor@empresa-a.cv')
            ConstructionTask.objects.create(
                project=project_a,
                wbs_code='1.1',
                name='Task A',
                due_date=date.today(),
                assigned_to=user_a,
                created_by=user_a
            )
        
        with tenant_context(tenant_b):
            project_b = Project.objects.create(
                name='Projeto B',
                slug='projeto-b',
                status=Project.STATUS_CONSTRUCTION
            )
            user_b = User.objects.get(email='gestor@empresa-b.cv')
            ConstructionTask.objects.create(
                project=project_b,
                wbs_code='1.1',
                name='Task B',
                due_date=date.today(),
                assigned_to=user_b,
                created_by=user_b
            )
        
        # Client A deve ver apenas Task A
        response_a = api_client_tenant_a.get('/api/v1/construction/tasks/')
        assert response_a.status_code == 200
        data_a = response_a.json()
        assert len(data_a['results'] if 'results' in data_a else data_a) == 1
        
        # Client B deve ver apenas Task B
        response_b = api_client_tenant_b.get('/api/v1/construction/tasks/')
        assert response_b.status_code == 200
        data_b = response_b.json()
        assert len(data_b['results'] if 'results' in data_b else data_b) == 1
    
    def test_api_cannot_access_other_tenant_task_detail(self, api_client_tenant_a, tenant_a, tenant_b):
        """Não deve ser possível acesar detalhes de task de outro tenant."""
        from apps.projects.models import Project
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Criar task no Tenant B
        with tenant_context(tenant_b):
            project_b = Project.objects.create(
                name='Projeto B',
                slug='projeto-b',
                status=Project.STATUS_CONSTRUCTION
            )
            user_b = User.objects.create_user(
                email='test-b@empresa-b.cv',
                password='testpass123'
            )
            task_b = ConstructionTask.objects.create(
                project=project_b,
                wbs_code='1.1',
                name='Task B Secret',
                due_date=date.today(),
                assigned_to=user_b,
                created_by=user_b
            )
            task_b_id = str(task_b.id)
        
        # Tentar acessar via API do Tenant A
        response = api_client_tenant_a.get(f'/api/v1/construction/tasks/{task_b_id}/')
        assert response.status_code == 404, 'Não deve encontrar task de outro tenant'
