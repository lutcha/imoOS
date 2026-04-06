"""
Testes E2E: Isolamento entre Tenants

Valida que dados de um tenant não são acessíveis por outro.
"""
import uuid
from decimal import Decimal

import pytest
from django_tenants.utils import tenant_context
from rest_framework import status


pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


class TestCrossTenantAccess:
    """Testar acesso cruzado entre tenants."""
    
    def test_tenant_a_cannot_access_tenant_b_leads(
        self, api_client_tenant_a, tenant_b
    ):
        """1. Tenant A não pode aceder leads do Tenant B."""
        from apps.crm.models import Lead
        
        with tenant_context(tenant_b):
            # Criar lead em tenant B
            lead_b = Lead.objects.create(
                first_name='Maria',
                last_name='Santos',
                email='maria@tenant-b.cv',
                phone='+2389990000',
                status=Lead.STATUS_NEW,
            )
            lead_b_id = lead_b.id
        
        # Tentar aceder via cliente do tenant A
        response = api_client_tenant_a.get(f'/api/v1/crm/leads/{lead_b_id}/')
        
        # Deve retornar 404 (não encontrado neste tenant)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_tenant_b_cannot_list_tenant_a_units(
        self, api_client_tenant_b, tenant_a
    ):
        """2. Tenant B não pode listar unidades do Tenant A."""
        from apps.inventory.models import Unit, UnitType
        from apps.projects.models import Project, Building, Floor
        
        with tenant_context(tenant_a):
            # Criar projeto e unidade em tenant A
            project = Project.objects.create(
                name='Projeto Tenant A',
                slug='projeto-a',
                city='Praia',
            )
            building = Building.objects.create(
                project=project,
                name='Bloco A',
                code='BLK-A',
            )
            floor = Floor.objects.create(
                building=building,
                number=1,
                name='R/C',
            )
            unit_type, _ = UnitType.objects.get_or_create(
                name='T2', defaults={'code': 'T2', 'bedrooms': 2}
            )
            unit = Unit.objects.create(
                floor=floor,
                unit_type=unit_type,
                code='T2-A1',
                status=Unit.STATUS_AVAILABLE,
                area_bruta=Decimal('80.00'),
            )
        
        # Listar unidades via tenant B
        response = api_client_tenant_b.get('/api/v1/inventory/units/')
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                units = data['results']
            else:
                units = data
            
            # Não deve conter unidade do tenant A
            unit_ids = [u['id'] if isinstance(u, dict) else str(u.id) for u in units]
            assert str(unit.id) not in unit_ids
    
    def test_contract_isolation_between_tenants(
        self, api_client_tenant_a, tenant_a, tenant_b
    ):
        """3. Contratos são isolados entre tenants."""
        from apps.contracts.models import Contract
        from apps.crm.models import Lead
        from apps.inventory.models import Unit, UnitType
        from apps.projects.models import Project, Building, Floor
        
        # Criar contrato em tenant A
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='João',
                last_name='Silva',
                email='joao@tenant-a.cv',
            )
            
            project = Project.objects.create(
                name='Projeto A', slug='projeto-a', city='Praia'
            )
            building = Building.objects.create(
                project=project, name='Bloco A', code='BLK-A'
            )
            floor = Floor.objects.create(
                building=building, number=1, name='R/C'
            )
            unit_type, _ = UnitType.objects.get_or_create(
                name='T2', defaults={'code': 'T2'}
            )
            unit = Unit.objects.create(
                floor=floor, unit_type=unit_type,
                code='T2-01', status=Unit.STATUS_AVAILABLE,
                area_bruta=Decimal('80.00'),
            )
            
            contract = Contract.objects.create(
                unit=unit,
                lead=lead,
                contract_number='CNT-A-001',
                total_price_cve=Decimal('5000000.00'),
                status=Contract.STATUS_DRAFT,
            )
            contract_id = contract.id
        
        # Tentar aceder de tenant B
        with tenant_context(tenant_b):
            contracts = Contract.objects.filter(id=contract_id)
            assert contracts.count() == 0
        
        # Tentar via API
        response = api_client_tenant_a.get(
            f'/api/v1/contracts/contracts/{contract_id}/'
        )
        
        # Deve encontrar em tenant A
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data['contract_number'] == 'CNT-A-001'


class TestJWTTokenIsolation:
    """Testar isolamento via tokens JWT."""
    
    def test_jwt_with_wrong_tenant_schema_denied(
        self, api_client, tenant_a, tenant_b, user_tenant_a
    ):
        """1. JWT com schema errado é rejeitado."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Criar token com schema do tenant B para user do tenant A
        refresh = RefreshToken.for_user(user_tenant_a)
        refresh['tenant_schema'] = tenant_b.schema_name  # Schema errado!
        
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}',
            HTTP_HOST='empresa-a.imos.cv',
        )
        
        # Tentar aceder recurso
        response = api_client.get('/api/v1/crm/leads/')
        
        # Deve ser negado (401 ou 403)
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
    
    def test_jwt_without_tenant_schema_denied(
        self, api_client, user_tenant_a
    ):
        """2. JWT sem claim de tenant é rejeitado."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Criar token sem tenant_schema
        refresh = RefreshToken.for_user(user_tenant_a)
        # Remover tenant_schema se existir
        if 'tenant_schema' in refresh:
            del refresh['tenant_schema']
        
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}',
            HTTP_HOST='empresa-a.imos.cv',
        )
        
        response = api_client.get('/api/v1/crm/leads/')
        
        # Deve ser negado
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
    
    def test_valid_jwt_allows_access(
        self, api_client_tenant_a, tenant_a
    ):
        """3. JWT válido permite acesso."""
        from apps.crm.models import Lead
        
        # Criar lead em tenant A
        with tenant_context(tenant_a):
            Lead.objects.create(
                first_name='Test',
                last_name='User',
                email='test@tenant-a.cv',
                status=Lead.STATUS_NEW,
            )
        
        response = api_client_tenant_a.get('/api/v1/crm/leads/')
        
        # Deve permitir acesso
        assert response.status_code == status.HTTP_200_OK
        
        if isinstance(response.json(), dict) and 'results' in response.json():
            assert len(response.json()['results']) > 0
        else:
            assert len(response.json()) > 0


class TestWorkflowIsolation:
    """Testar isolamento de workflows entre tenants."""
    
    def test_workflow_instances_isolated(
        self, tenant_a, tenant_b
    ):
        """1. Instâncias de workflow são isoladas."""
        from apps.workflows.models import WorkflowDefinition, WorkflowInstance
        
        with tenant_context(tenant_a):
            # Criar workflow em tenant A
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
                context={'test': 'data'},
            )
            instance_id = instance.id
        
        # Verificar que não existe em tenant B
        with tenant_context(tenant_b):
            instances = WorkflowInstance.objects.filter(id=instance_id)
            assert instances.count() == 0
    
    def test_workflow_definition_isolated(
        self, tenant_a, tenant_b
    ):
        """2. Definições de workflow são isoladas."""
        from apps.workflows.models import WorkflowDefinition
        
        with tenant_context(tenant_a):
            workflow = WorkflowDefinition.objects.create(
                name='Workflow Exclusivo A',
                workflow_type=WorkflowDefinition.TYPE_CUSTOM,
                trigger_event=WorkflowDefinition.TRIGGER_MANUAL,
                steps_definition=[{'step': 1}],
            )
            workflow_id = workflow.id
        
        # Verificar que não existe em tenant B
        with tenant_context(tenant_b):
            workflows = WorkflowDefinition.objects.filter(id=workflow_id)
            assert workflows.count() == 0
            
            # Pode criar com mesmo nome
            workflow_b = WorkflowDefinition.objects.create(
                name='Workflow Exclusivo A',  # Mesmo nome!
                workflow_type=WorkflowDefinition.TYPE_CUSTOM,
                trigger_event=WorkflowDefinition.TRIGGER_MANUAL,
            )
            assert workflow_b.id != workflow_id


class TestNotificationIsolation:
    """Testar isolamento de notificações."""
    
    def test_whatsapp_messages_isolated(
        self, tenant_a, tenant_b
    ):
        """1. Mensagens WhatsApp são isoladas."""
        from apps.crm.models import Lead, WhatsAppMessage
        
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='João',
                last_name='Silva',
                email='joao@a.cv',
                phone='+2389991111',
            )
            
            message = WhatsAppMessage.objects.create(
                lead=lead,
                phone=lead.phone,
                payload={'text': 'Mensagem A'},
                status=WhatsAppMessage.STATUS_SENT,
            )
            message_id = message.id
        
        # Verificar que não existe em tenant B
        with tenant_context(tenant_b):
            messages = WhatsAppMessage.objects.filter(id=message_id)
            assert messages.count() == 0


class TestUserIsolation:
    """Testar isolamento de utilizadores."""
    
    def test_user_data_isolated(
        self, tenant_a, tenant_b
    ):
        """1. Dados de utilizadores são isolados."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        with tenant_context(tenant_a):
            user_a = User.objects.create_user(
                email='user@tenant-a.cv',
                password='testpass123!',
                first_name='User',
                last_name='A',
            )
            user_a_id = user_a.id
        
        # Verificar que não existe em tenant B
        with tenant_context(tenant_b):
            users = User.objects.filter(id=user_a_id)
            assert users.count() == 0
            
            # Pode criar user com mesmo email (se schema separado)
            # ou pode ter constraint unique global
    
    def test_membership_isolated(
        self, tenant_a, tenant_b
    ):
        """2. Memberships são isoladas por tenant."""
        from django.contrib.auth import get_user_model
        from apps.memberships.models import Membership
        User = get_user_model()
        
        with tenant_context(tenant_a):
            user = User.objects.create_user(
                email='member@test.cv',
                password='testpass123!',
            )
            
            membership = Membership.objects.create(
                user=user,
                tenant=tenant_a,
                role='ADMIN',
                is_active=True,
            )
            membership_id = membership.id
        
        # Verificar que não existe em tenant B
        with tenant_context(tenant_b):
            memberships = Membership.objects.filter(id=membership_id)
            assert memberships.count() == 0


class TestPaymentIsolation:
    """Testar isolamento de pagamentos."""
    
    def test_payments_isolated_between_tenants(
        self, tenant_a, tenant_b
    ):
        """1. Pagamentos são isolados entre tenants."""
        from apps.contracts.models import Contract, Payment
        from apps.crm.models import Lead
        from apps.inventory.models import Unit, UnitType
        from apps.projects.models import Project, Building, Floor
        
        with tenant_context(tenant_a):
            lead = Lead.objects.create(
                first_name='Cliente',
                last_name='A',
                email='cliente@a.cv',
            )
            
            project = Project.objects.create(
                name='Projeto', slug='projeto', city='Praia'
            )
            building = Building.objects.create(
                project=project, name='Bloco', code='BLK'
            )
            floor = Floor.objects.create(
                building=building, number=1, name='R/C'
            )
            unit_type, _ = UnitType.objects.get_or_create(
                name='T2', defaults={'code': 'T2'}
            )
            unit = Unit.objects.create(
                floor=floor, unit_type=unit_type,
                code='T2-01', status=Unit.STATUS_AVAILABLE,
                area_bruta=Decimal('80.00'),
            )
            
            contract = Contract.objects.create(
                unit=unit,
                lead=lead,
                contract_number='CNT-A-001',
                total_price_cve=Decimal('5000000.00'),
            )
            
            payment = Payment.objects.create(
                contract=contract,
                payment_type=Payment.PAYMENT_INSTALLMENT,
                amount_cve=Decimal('1000000.00'),
                due_date='2026-12-31',
                status=Payment.STATUS_PENDING,
            )
            payment_id = payment.id
        
        # Verificar que não existe em tenant B
        with tenant_context(tenant_b):
            payments = Payment.objects.filter(id=payment_id)
            assert payments.count() == 0


class TestConstructionDataIsolation:
    """Testar isolamento de dados de construção."""
    
    def test_construction_tasks_isolated(
        self, tenant_a, tenant_b
    ):
        """1. Tasks de construção são isoladas."""
        from apps.construction.models import ConstructionTask
        from apps.projects.models import Project
        
        with tenant_context(tenant_a):
            project = Project.objects.create(
                name='Projeto A', slug='projeto-a', city='Praia'
            )
            
            task = ConstructionTask.objects.create(
                project=project,
                wbs_code='1.1',
                name='Task A',
                status=ConstructionTask.STATUS_PENDING,
                due_date='2026-12-31',
            )
            task_id = task.id
        
        # Verificar que não existe em tenant B
        with tenant_context(tenant_b):
            tasks = ConstructionTask.objects.filter(id=task_id)
            assert tasks.count() == 0
    
    def test_evm_snapshots_isolated(
        self, tenant_a, tenant_b
    ):
        """2. Snapshots EVM são isolados."""
        from apps.construction.models import EVMSnapshot
        from apps.projects.models import Project
        
        with tenant_context(tenant_a):
            project = Project.objects.create(
                name='Projeto A', slug='projeto-a', city='Praia'
            )
            
            snapshot = EVMSnapshot.objects.create(
                project=project,
                date='2026-06-01',
                bac=Decimal('1000000.00'),
                pv=Decimal('500000.00'),
                ev=Decimal('450000.00'),
                ac=Decimal('480000.00'),
            )
            snapshot_id = snapshot.id
        
        # Verificar que não existe em tenant B
        with tenant_context(tenant_b):
            snapshots = EVMSnapshot.objects.filter(id=snapshot_id)
            assert snapshots.count() == 0
