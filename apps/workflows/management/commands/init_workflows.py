"""
Initialize default workflow templates for a tenant.

Usage:
    python manage.py init_workflows --schema=tenant_schema
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context, get_tenant_model


class Command(BaseCommand):
    help = 'Initialize default workflow templates for a tenant'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Tenant schema name',
            required=True
        )

    def handle(self, *args, **options):
        schema_name = options['schema']
        
        TenantModel = get_tenant_model()
        
        try:
            tenant = TenantModel.objects.get(schema_name=schema_name)
        except TenantModel.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Tenant with schema "{schema_name}" not found')
            )
            return
        
        self.stdout.write(f'Initializing workflows for tenant: {tenant.name}')
        
        with tenant_context(tenant):
            self._create_default_workflows()
        
        self.stdout.write(self.style.SUCCESS('Workflows initialized successfully'))
    
    def _create_default_workflows(self):
        from apps.workflows.models import WorkflowDefinition, WorkflowTemplate
        
        # Create system templates if they don't exist
        templates = [
            {
                'name': 'Workflow de Venda Padrão',
                'workflow_type': WorkflowDefinition.TYPE_SALES,
                'trigger_event': WorkflowDefinition.TRIGGER_LEAD_CONVERTED,
                'description': 'Fluxo completo de venda: Lead → Reserva → Contrato',
                'steps': [
                    {
                        'name': 'Criar Reserva',
                        'action_type': 'CUSTOM',
                        'config': {'service': 'SalesWorkflow.convert_lead_to_reservation'}
                    },
                    {
                        'name': 'Notificar Cliente',
                        'action_type': 'SEND_WHATSAPP',
                        'config': {'template': 'reserva_confirmada'}
                    }
                ]
            },
            {
                'name': 'Inicialização de Projeto',
                'workflow_type': WorkflowDefinition.TYPE_PROJECT_INIT,
                'trigger_event': WorkflowDefinition.TRIGGER_CONTRACT_SIGNED,
                'description': 'Criar projeto de obra após assinatura de contrato',
                'steps': [
                    {
                        'name': 'Criar Projeto de Obra',
                        'action_type': 'CUSTOM',
                        'config': {'service': 'ProjectInitWorkflow.create_construction_project'}
                    },
                    {
                        'name': 'Criar Fases',
                        'action_type': 'CUSTOM',
                        'config': {'service': 'ProjectInitWorkflow.create_default_phases'}
                    },
                    {
                        'name': 'Criar Tasks',
                        'action_type': 'CUSTOM',
                        'config': {'service': 'ProjectInitWorkflow.create_default_tasks'}
                    },
                    {
                        'name': 'Notificar Cliente',
                        'action_type': 'SEND_WHATSAPP',
                        'config': {'template': 'obra_iniciada'}
                    }
                ]
            },
            {
                'name': 'Milestone de Pagamento',
                'workflow_type': WorkflowDefinition.TYPE_PAYMENT_MILESTONE,
                'trigger_event': WorkflowDefinition.TRIGGER_TASK_COMPLETED,
                'description': 'Gerar pagamento quando fase de obra é concluída',
                'steps': [
                    {
                        'name': 'Verificar Milestone',
                        'action_type': 'CUSTOM',
                        'config': {'service': 'PaymentMilestoneWorkflow.check_payment_milestone'}
                    },
                    {
                        'name': 'Gerar Fatura',
                        'action_type': 'CUSTOM',
                        'config': {'service': 'PaymentMilestoneWorkflow.generate_invoice'}
                    },
                    {
                        'name': 'Notificar Cliente',
                        'action_type': 'SEND_WHATSAPP',
                        'config': {'template': 'prestacao_gerada'}
                    }
                ]
            }
        ]
        
        for template_data in templates:
            workflow, created = WorkflowDefinition.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'workflow_type': template_data['workflow_type'],
                    'trigger_event': template_data['trigger_event'],
                    'description': template_data['description'],
                    'steps_definition': template_data['steps'],
                    'is_active': True,
                    'auto_execute': True
                }
            )
            
            if created:
                self.stdout.write(f'  Created: {workflow.name}')
            else:
                self.stdout.write(f'  Already exists: {workflow.name}')
        
        # Also create system templates
        for template_data in templates:
            WorkflowTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'workflow_type': template_data['workflow_type'],
                    'trigger_event': template_data['trigger_event'],
                    'description': template_data['description'],
                    'steps_definition': template_data['steps'],
                    'is_system': True
                }
            )
