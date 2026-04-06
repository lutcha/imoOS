"""
Testes de Isolamento: Workflows

Valida que workflows e suas instâncias estão isoladas por tenant.
"""
import uuid
from decimal import Decimal

import pytest
from django_tenants.utils import tenant_context
from rest_framework import status

from apps.workflows.models import (
    WorkflowDefinition, WorkflowInstance, WorkflowStep, WorkflowLog
)


pytestmark = [pytest.mark.isolation, pytest.mark.django_db(transaction=True)]


class TestWorkflowDefinitionIsolation:
    """Testar isolamento de definições de workflow."""
    
    def test_workflow_definition_not_visible_across_tenants(
        self, tenant_a, tenant_b
    ):
        """1. Definição de workflow de tenant A não visível em B."""
        with tenant_context(tenant_a):
            workflow = WorkflowDefinition.objects.create(
                name='Workflow Vendas A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[
                    {'order': 1, 'action': 'CREATE_RESERVATION'},
                    {'order': 2, 'action': 'CREATE_CONTRACT'},
                ],
                is_active=True,
            )
            workflow_id = workflow.id
        
        # Verificar não existe em tenant B
        with tenant_context(tenant_b):
            workflows = WorkflowDefinition.objects.filter(id=workflow_id)
            assert workflows.count() == 0
            
            # Listar todas as workflows em B
            all_workflows = WorkflowDefinition.objects.all()
            workflow_ids = [w.id for w in all_workflows]
            assert workflow_id not in workflow_ids
    
    def test_workflow_definition_duplicate_name_allowed(
        self, tenant_a, tenant_b
    ):
        """2. Mesmo nome de workflow permitido em tenants diferentes."""
        workflow_name = 'Workflow Padrão de Vendas'
        
        with tenant_context(tenant_a):
            workflow_a = WorkflowDefinition.objects.create(
                name=workflow_name,
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
        
        with tenant_context(tenant_b):
            workflow_b = WorkflowDefinition.objects.create(
                name=workflow_name,  # Mesmo nome!
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            # IDs devem ser diferentes
            assert workflow_a.id != workflow_b.id
    
    def test_workflow_definition_update_isolated(
        self, tenant_a, tenant_b
    ):
        """3. Atualização em um tenant não afeta outro."""
        with tenant_context(tenant_a):
            workflow = WorkflowDefinition.objects.create(
                name='Workflow Teste',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[{'step': 1}],
                is_active=True,
            )
            workflow_id = workflow.id
        
        # Criar workflow com mesmo ID em tenant B (não deve ser possível, mas testar)
        with tenant_context(tenant_b):
            # Tentar criar workflow com configuração diferente
            workflow_b = WorkflowDefinition.objects.create(
                name='Workflow Teste',
                workflow_type=WorkflowDefinition.TYPE_CUSTOM,
                trigger_event=WorkflowDefinition.TRIGGER_MANUAL,
                steps_definition=[{'step': 99}],
                is_active=False,
            )
            
            # Deve ser um objeto diferente
            assert workflow_b.id != workflow_id
            assert workflow_b.workflow_type == WorkflowDefinition.TYPE_CUSTOM


class TestWorkflowInstanceIsolation:
    """Testar isolamento de instâncias de workflow."""
    
    def test_workflow_instance_not_visible_across_tenants(
        self, tenant_a, tenant_b
    ):
        """1. Instância de workflow de tenant A não visível em B."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
                context={'lead_id': str(uuid.uuid4())},
                current_step=1,
                total_steps=3,
            )
            instance_id = instance.id
        
        # Verificar não existe em tenant B
        with tenant_context(tenant_b):
            instances = WorkflowInstance.objects.filter(id=instance_id)
            assert instances.count() == 0
    
    def test_workflow_instance_status_isolated(
        self, tenant_a, tenant_b
    ):
        """2. Status de instância é isolado entre tenants."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
                context={},
            )
            instance_id = instance.id
        
        # Criar workflow com mesmo nome em B mas status diferente
        with tenant_context(tenant_b):
            workflow_def_b = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance_b = WorkflowInstance.objects.create(
                workflow=workflow_def_b,
                status=WorkflowInstance.STATUS_COMPLETED,  # Status diferente
                context={},
            )
            
            # IDs diferentes
            assert instance_b.id != instance_id
            assert instance_b.status == WorkflowInstance.STATUS_COMPLETED
        
        # Verificar que A ainda está RUNNING
        with tenant_context(tenant_a):
            instance.refresh_from_db()
            assert instance.status == WorkflowInstance.STATUS_RUNNING


class TestWorkflowStepIsolation:
    """Testar isolamento de passos de workflow."""
    
    def test_workflow_step_not_visible_across_tenants(
        self, tenant_a, tenant_b
    ):
        """1. Passo de workflow de tenant A não visível em B."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
            )
            
            step = WorkflowStep.objects.create(
                instance=instance,
                order=1,
                name='Criar Reserva',
                action_type=WorkflowStep.ACTION_CREATE_MODEL,
                action_config={'model': 'UnitReservation'},
                status=WorkflowStep.STATUS_COMPLETED,
            )
            step_id = step.id
        
        # Verificar não existe em tenant B
        with tenant_context(tenant_b):
            steps = WorkflowStep.objects.filter(id=step_id)
            assert steps.count() == 0
    
    def test_workflow_step_order_isolated(
        self, tenant_a, tenant_b
    ):
        """2. Ordem dos passos é isolada entre tenants."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
            )
            
            # Criar passos em ordem específica
            for i in range(1, 4):
                WorkflowStep.objects.create(
                    instance=instance,
                    order=i,
                    name=f'Passo {i}',
                    action_type=WorkflowStep.ACTION_CREATE_MODEL,
                    action_config={},
                    status=WorkflowStep.STATUS_PENDING,
                )
            
            steps_count = WorkflowStep.objects.filter(instance=instance).count()
            assert steps_count == 3
        
        # Tenant B deve ter zero passos desse workflow
        with tenant_context(tenant_b):
            all_steps = WorkflowStep.objects.all()
            step_names = [s.name for s in all_steps]
            assert 'Passo 1' not in step_names


class TestWorkflowLogIsolation:
    """Testar isolamento de logs de workflow."""
    
    def test_workflow_log_not_visible_across_tenants(
        self, tenant_a, tenant_b
    ):
        """1. Log de workflow de tenant A não visível em B."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
            )
            
            log = WorkflowLog.objects.create(
                instance=instance,
                level=WorkflowLog.LEVEL_INFO,
                message='Workflow iniciado com sucesso',
                details={'timestamp': '2026-01-01T00:00:00Z'},
            )
            log_id = log.id
        
        # Verificar não existe em tenant B
        with tenant_context(tenant_b):
            logs = WorkflowLog.objects.filter(id=log_id)
            assert logs.count() == 0
    
    def test_workflow_log_search_isolated(
        self, tenant_a, tenant_b
    ):
        """2. Busca em logs é isolada por tenant."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
            )
            
            WorkflowLog.objects.create(
                instance=instance,
                level=WorkflowLog.LEVEL_ERROR,
                message='Erro crítico no tenant A',
                details={},
            )
        
        # Buscar por 'Erro crítico' em tenant B não deve retornar nada
        with tenant_context(tenant_b):
            logs = WorkflowLog.objects.filter(message__contains='Erro crítico')
            assert logs.count() == 0


class TestWorkflowAPICrossTenantAccess:
    """Testar acesso cross-tenant via API de workflows."""
    
    def test_api_cannot_access_workflow_from_other_tenant(
        self, api_client_tenant_a, tenant_b
    ):
        """1. API não pode aceder workflow de outro tenant."""
        with tenant_context(tenant_b):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow B',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            workflow_id = workflow_def.id
        
        # Tentar aceder via API de tenant A
        response = api_client_tenant_a.get(
            f'/api/v1/workflows/definitions/{workflow_id}/'
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_api_cannot_access_instance_from_other_tenant(
        self, api_client_tenant_b, tenant_a
    ):
        """2. API não pode aceder instância de outro tenant."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
            )
            instance_id = instance.id
        
        # Tentar aceder via API de tenant B
        response = api_client_tenant_b.get(
            f'/api/v1/workflows/instances/{instance_id}/'
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_api_cannot_modify_instance_from_other_tenant(
        self, api_client_tenant_a, tenant_b
    ):
        """3. API não pode modificar instância de outro tenant."""
        with tenant_context(tenant_b):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow B',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
            )
            instance_id = instance.id
        
        # Tentar cancelar via API de tenant A
        response = api_client_tenant_a.post(
            f'/api/v1/workflows/instances/{instance_id}/cancel/'
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verificar que ainda está RUNNING em tenant B
        with tenant_context(tenant_b):
            instance.refresh_from_db()
            assert instance.status == WorkflowInstance.STATUS_RUNNING


class TestWorkflowTriggerIsolation:
    """Testar isolamento de triggers de workflow."""
    
    def test_trigger_only_affects_own_tenant(
        self, tenant_a, tenant_b
    ):
        """1. Trigger de workflow só afeta seu próprio tenant."""
        from apps.crm.models import Lead
        
        with tenant_context(tenant_a):
            # Criar workflow trigger
            workflow_def = WorkflowDefinition.objects.create(
                name='Auto Workflow A',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                auto_execute=True,
                steps_definition=[{'action': 'NOTIFY'}],
            )
            
            # Criar lead
            lead = Lead.objects.create(
                first_name='Lead',
                last_name='A',
                email='lead@a.cv',
                status=Lead.STATUS_NEW,
            )
            
            # Contar instâncias
            instances_before = WorkflowInstance.objects.filter(
                workflow=workflow_def
            ).count()
        
        with tenant_context(tenant_b):
            # Criar workflow com mesmo trigger
            workflow_def_b = WorkflowDefinition.objects.create(
                name='Auto Workflow B',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                auto_execute=True,
                steps_definition=[{'action': 'NOTIFY'}],
            )
            
            # Contar instâncias em B
            instances_b_before = WorkflowInstance.objects.filter(
                workflow=workflow_def_b
            ).count()
        
        # Verificar isolamento
        with tenant_context(tenant_a):
            instances_after = WorkflowInstance.objects.filter(
                workflow=workflow_def
            ).count()
            # Instâncias em A não mudaram por causa de B
            assert instances_after == instances_before
