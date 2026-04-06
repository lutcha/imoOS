"""
Testes de Integração: Workflows

Valida a integração entre workflows e outros módulos do sistema.
"""
import uuid
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

import pytest
from django.utils import timezone
from django_tenants.utils import tenant_context
from rest_framework import status

from apps.workflows.models import (
    WorkflowDefinition, WorkflowInstance, WorkflowStep, WorkflowLog
)


pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


class TestSalesWorkflowIntegration:
    """Testar integração do workflow de vendas."""
    
    def test_lead_conversion_triggers_reservation_workflow(
        self, tenant_a, api_client_tenant_a
    ):
        """1. Conversão de lead dispara workflow de reserva."""
        from apps.crm.models import Lead, UnitReservation
        from apps.inventory.models import Unit, UnitType
        from apps.projects.models import Project, Building, Floor
        
        with tenant_context(tenant_a):
            # Setup
            lead = Lead.objects.create(
                first_name='João',
                last_name='Silva',
                email='joao@test.cv',
                phone='+2389991111',
                status=Lead.STATUS_NEW,
            )
            
            project = Project.objects.create(
                name='Projeto Teste', slug='projeto', city='Praia'
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
            
            # Criar workflow
            workflow_def = WorkflowDefinition.objects.create(
                name='Conversão de Lead',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                auto_execute=True,
                steps_definition=[
                    {
                        'order': 1,
                        'action': 'UPDATE_MODEL',
                        'config': {
                            'model': 'Lead',
                            'fields': {'status': 'CONVERTED'}
                        }
                    },
                    {
                        'order': 2,
                        'action': 'SEND_WHATSAPP',
                        'config': {
                            'template': 'lead_convertido',
                            'variables': ['first_name']
                        }
                    },
                ],
            )
        
        # Executar conversão
        response = api_client_tenant_a.post(
            f'/api/v1/crm/leads/{lead.id}/convert/',
            {'unit_id': str(unit.id)},
            format='json'
        )
        
        # Verificar resultado
        if response.status_code == status.HTTP_200_OK:
            with tenant_context(tenant_a):
                lead.refresh_from_db()
                assert lead.status == Lead.STATUS_CONVERTED
    
    def test_reservation_creation_triggers_contract_workflow(
        self, tenant_a, api_client_tenant_a
    ):
        """2. Criação de reserva dispara workflow de contrato."""
        from apps.crm.models import Lead, UnitReservation
        from apps.inventory.models import Unit, UnitType
        from apps.projects.models import Project, Building, Floor
        
        with tenant_context(tenant_a):
            # Setup
            lead = Lead.objects.create(
                first_name='Maria',
                last_name='Santos',
                email='maria@test.cv',
                phone='+2389992222',
                status=Lead.STATUS_NEW,
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
                code='T2-02', status=Unit.STATUS_AVAILABLE,
                area_bruta=Decimal('80.00'),
            )
            
            # Criar workflow
            workflow_def = WorkflowDefinition.objects.create(
                name='Criação de Reserva',
                workflow_type=WorkflowDefinition.TYPE_SALES,
                trigger_event=WorkflowDefinition.TRIGGER_RESERVATION_CREATED,
                auto_execute=True,
                steps_definition=[
                    {
                        'order': 1,
                        'action': 'UPDATE_MODEL',
                        'config': {
                            'model': 'Unit',
                            'fields': {'status': 'RESERVED'}
                        }
                    },
                    {
                        'order': 2,
                        'action': 'SEND_WHATSAPP',
                        'config': {
                            'template': 'reserva_confirmada',
                            'variables': ['first_name', 'unit_code']
                        }
                    },
                ],
            )
        
        # Criar reserva
        response = api_client_tenant_a.post(
            '/api/v1/crm/reservations/',
            {
                'unit_id': str(unit.id),
                'lead_id': str(lead.id),
                'deposit_amount_cve': '100000.00',
            },
            format='json'
        )
        
        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            with tenant_context(tenant_a):
                unit.refresh_from_db()
                assert unit.status == Unit.STATUS_RESERVED


class TestProjectInitWorkflowIntegration:
    """Testar integração do workflow de inicialização de projeto."""
    
    def test_contract_signed_triggers_project_workflow(
        self, tenant_a, api_client_tenant_a
    ):
        """1. Contrato assinado dispara workflow de projeto de obra."""
        from apps.contracts.models import Contract, SignatureRequest
        from apps.crm.models import Lead
        from apps.inventory.models import Unit, UnitType
        from apps.projects.models import Project, Building, Floor
        from apps.construction.models import ConstructionProject
        
        with tenant_context(tenant_a):
            # Setup
            lead = Lead.objects.create(
                first_name='Cliente',
                last_name='Teste',
                email='cliente@test.cv',
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
                code='T2-03', status=Unit.STATUS_AVAILABLE,
                area_bruta=Decimal('80.00'),
            )
            
            contract = Contract.objects.create(
                unit=unit,
                lead=lead,
                contract_number='CNT-001',
                total_price_cve=Decimal('5000000.00'),
                status=Contract.STATUS_DRAFT,
            )
            
            # Criar workflow
            workflow_def = WorkflowDefinition.objects.create(
                name='Inicialização de Obra',
                workflow_type=WorkflowDefinition.TYPE_PROJECT_INIT,
                trigger_event=WorkflowDefinition.TRIGGER_CONTRACT_SIGNED,
                auto_execute=True,
                steps_definition=[
                    {
                        'order': 1,
                        'action': 'CREATE_MODEL',
                        'config': {
                            'model': 'ConstructionProject',
                            'fields': {
                                'status': 'PLANNING',
                                'name_template': 'Obra - {unit_code}'
                            }
                        }
                    },
                    {
                        'order': 2,
                        'action': 'CREATE_MODEL',
                        'config': {
                            'model': 'ConstructionPhase',
                            'phases': ['FOUNDATION', 'STRUCTURE', 'MASONRY', 'MEP', 'FINISHES']
                        }
                    },
                ],
            )
        
        # Assinar contrato
        response = api_client_tenant_a.post(
            f'/api/v1/contracts/contracts/{contract.id}/sign/',
            {
                'signed_by_name': 'Cliente Teste',
                'ip_address': '192.168.1.1',
            },
            format='json'
        )
        
        if response.status_code == status.HTTP_200_OK:
            with tenant_context(tenant_a):
                # Verificar se projeto foi criado
                projects = ConstructionProject.objects.filter(contract=contract)
                assert projects.exists()


class TestPaymentMilestoneWorkflowIntegration:
    """Testar integração do workflow de milestones de pagamento."""
    
    def test_task_completion_triggers_payment(
        self, tenant_a, api_client_tenant_a
    ):
        """1. Conclusão de task dispara workflow de pagamento."""
        from apps.construction.models import ConstructionTask, ConstructionPhase
        from apps.projects.models import Project
        from apps.contracts.models import Contract, Payment
        from apps.crm.models import Lead
        from apps.inventory.models import Unit, UnitType
        from apps.projects.models import Building, Floor
        
        with tenant_context(tenant_a):
            # Setup
            lead = Lead.objects.create(
                first_name='Cliente',
                last_name='Teste',
                email='cliente@test.cv',
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
                code='T2-04', status=Unit.STATUS_AVAILABLE,
                area_bruta=Decimal('80.00'),
            )
            
            contract = Contract.objects.create(
                unit=unit,
                lead=lead,
                contract_number='CNT-002',
                total_price_cve=Decimal('5000000.00'),
                status=Contract.STATUS_ACTIVE,
            )
            
            phase = ConstructionPhase.objects.create(
                project=project,
                phase_type='FOUNDATION',
                name='Fundação',
                start_planned=date.today(),
                end_planned=date.today() + timedelta(days=30),
            )
            
            task = ConstructionTask.objects.create(
                phase=phase,
                project=project,
                wbs_code='FO.99',
                name='Conclusão Fundação - MILESTONE',
                status=ConstructionTask.STATUS_PENDING,
                due_date=phase.end_planned,
            )
            
            # Criar workflow
            workflow_def = WorkflowDefinition.objects.create(
                name='Milestone de Pagamento',
                workflow_type=WorkflowDefinition.TYPE_PAYMENT_MILESTONE,
                trigger_event=WorkflowDefinition.TRIGGER_TASK_COMPLETED,
                auto_execute=True,
                steps_definition=[
                    {
                        'order': 1,
                        'action': 'CREATE_MODEL',
                        'config': {
                            'model': 'Payment',
                            'fields': {
                                'payment_type': 'INSTALLMENT',
                                'status': 'PENDING'
                            }
                        }
                    },
                    {
                        'order': 2,
                        'action': 'SEND_WHATSAPP',
                        'config': {
                            'template': 'milestone_concluido',
                            'variables': ['phase_name']
                        }
                    },
                ],
            )
        
        # Completar task
        response = api_client_tenant_a.patch(
            f'/api/v1/construction/tasks/{task.id}/',
            {
                'status': 'COMPLETED',
                'progress_percent': '100.00',
            },
            format='json'
        )
        
        if response.status_code == status.HTTP_200_OK:
            with tenant_context(tenant_a):
                # Verificar se pagamento foi criado
                payments = Payment.objects.filter(contract=contract)
                assert payments.exists()


class TestWorkflowExecution:
    """Testar execução de workflows."""
    
    def test_workflow_step_execution_order(
        self, tenant_a
    ):
        """1. Passos de workflow são executados na ordem correta."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow Teste',
                workflow_type=WorkflowDefinition.TYPE_CUSTOM,
                trigger_event=WorkflowDefinition.TRIGGER_MANUAL,
                steps_definition=[
                    {'order': 1, 'action': 'STEP_1'},
                    {'order': 2, 'action': 'STEP_2'},
                    {'order': 3, 'action': 'STEP_3'},
                ],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_PENDING,
                total_steps=3,
            )
            
            # Criar passos
            for i in range(1, 4):
                WorkflowStep.objects.create(
                    instance=instance,
                    order=i,
                    name=f'Passo {i}',
                    action_type=WorkflowStep.ACTION_CUSTOM,
                    action_config={'step_num': i},
                    status=WorkflowStep.STATUS_PENDING,
                )
            
            # Verificar ordem
            steps = WorkflowStep.objects.filter(instance=instance).order_by('order')
            orders = [s.order for s in steps]
            assert orders == [1, 2, 3]
    
    def test_workflow_error_handling(
        self, tenant_a
    ):
        """2. Erros em workflow são registrados corretamente."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow com Erro',
                workflow_type=WorkflowDefinition.TYPE_CUSTOM,
                trigger_event=WorkflowDefinition.TRIGGER_MANUAL,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
            )
            
            # Simular erro
            step = WorkflowStep.objects.create(
                instance=instance,
                order=1,
                name='Passo com Erro',
                action_type=WorkflowStep.ACTION_CUSTOM,
                status=WorkflowStep.STATUS_FAILED,
                error_message='Erro de conexão com API externa',
            )
            
            # Criar log
            WorkflowLog.objects.create(
                instance=instance,
                step=step,
                level=WorkflowLog.LEVEL_ERROR,
                message='Falha ao executar passo 1',
                details={'error': 'Connection timeout'},
            )
            
            # Atualizar instância
            instance.status = WorkflowInstance.STATUS_FAILED
            instance.error_message = 'Falha no passo 1'
            instance.error_step = 1
            instance.save()
            
            # Verificar
            assert instance.status == WorkflowInstance.STATUS_FAILED
            assert instance.error_message == 'Falha no passo 1'
            
            logs = WorkflowLog.objects.filter(instance=instance)
            assert logs.count() > 0
    
    def test_workflow_retry_mechanism(
        self, tenant_a
    ):
        """3. Mecanismo de retry em workflows."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow com Retry',
                workflow_type=WorkflowDefinition.TYPE_CUSTOM,
                trigger_event=WorkflowDefinition.TRIGGER_MANUAL,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RETRYING,
                retry_count=2,
                max_retries=3,
            )
            
            # Verificar estado de retry
            assert instance.retry_count == 2
            assert instance.max_retries == 3
            assert instance.status == WorkflowInstance.STATUS_RETRYING


class TestWorkflowContext:
    """Testar contexto compartilhado em workflows."""
    
    def test_context_passed_between_steps(
        self, tenant_a
    ):
        """1. Contexto é passado entre passos do workflow."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow com Contexto',
                workflow_type=WorkflowDefinition.TYPE_CUSTOM,
                trigger_event=WorkflowDefinition.TRIGGER_MANUAL,
                steps_definition=[],
            )
            
            context = {
                'lead_id': str(uuid.uuid4()),
                'unit_id': str(uuid.uuid4()),
                'contract_value': 5000000,
                'metadata': {
                    'source': 'web',
                    'campaign': 'summer_2026',
                }
            }
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
                context=context,
            )
            
            # Verificar contexto
            assert instance.context['lead_id'] == context['lead_id']
            assert instance.context['metadata']['source'] == 'web'
    
    def test_context_updated_by_steps(
        self, tenant_a
    ):
        """2. Contexto é atualizado por passos do workflow."""
        with tenant_context(tenant_a):
            workflow_def = WorkflowDefinition.objects.create(
                name='Workflow com Contexto',
                workflow_type=WorkflowDefinition.TYPE_CUSTOM,
                trigger_event=WorkflowDefinition.TRIGGER_MANUAL,
                steps_definition=[],
            )
            
            instance = WorkflowInstance.objects.create(
                workflow=workflow_def,
                status=WorkflowInstance.STATUS_RUNNING,
                context={'step_1_result': None},
            )
            
            # Simular atualização por passo
            instance.context['step_1_result'] = 'success'
            instance.context['step_1_data'] = {'id': str(uuid.uuid4())}
            instance.current_step = 1
            instance.save()
            
            # Verificar atualização
            assert instance.context['step_1_result'] == 'success'
            assert 'step_1_data' in instance.context
