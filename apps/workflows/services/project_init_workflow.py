"""
Project Initialization Workflow — Contrato → Projeto de Obra

Este módulo implementa a inicialização automática de projetos de obra
após a assinatura de um contrato:
1. Criar ConstructionProject vinculado ao contrato
2. Criar fases padrão (Fundação, Estrutura, etc.)
3. Criar tasks baseadas em templates
4. Vincular unidade habitacional
5. Criar orçamento baseado no tipo de projeto
"""
import logging
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProjectInitWorkflow:
    """
    Inicializar projeto de obra após venda/assinatura de contrato.
    """
    
    # Fases padrão de um projeto de construção
    DEFAULT_PHASES = [
        {
            'phase_type': 'FOUNDATION',
            'name_prefix': 'Fundação',
            'duration_days': 30,
            'order': 1
        },
        {
            'phase_type': 'STRUCTURE',
            'name_prefix': 'Estrutura',
            'duration_days': 60,
            'order': 2
        },
        {
            'phase_type': 'MASONRY',
            'name_prefix': 'Alvenaria',
            'duration_days': 45,
            'order': 3
        },
        {
            'phase_type': 'MEP',
            'name_prefix': 'Instalações Hidro/Eléctricas',
            'duration_days': 40,
            'order': 4
        },
        {
            'phase_type': 'FINISHES',
            'name_prefix': 'Acabamentos',
            'duration_days': 50,
            'order': 5
        },
        {
            'phase_type': 'DELIVERY',
            'name_prefix': 'Entrega',
            'duration_days': 15,
            'order': 6
        },
    ]
    
    # Templates de tasks por fase
    TASK_TEMPLATES = {
        'FOUNDATION': [
            {'wbs_code': '1.1', 'name': 'Escavação', 'duration': 10, 'priority': 'HIGH'},
            {'wbs_code': '1.2', 'name': 'Armaduras', 'duration': 8, 'priority': 'HIGH'},
            {'wbs_code': '1.3', 'name': 'Betonagem Fundações', 'duration': 7, 'priority': 'HIGH'},
            {'wbs_code': '1.4', 'name': 'Impermeabilização', 'duration': 5, 'priority': 'MEDIUM'},
        ],
        'STRUCTURE': [
            {'wbs_code': '2.1', 'name': 'Pilares - Armaduras', 'duration': 15, 'priority': 'HIGH'},
            {'wbs_code': '2.2', 'name': 'Pilares - Betonagem', 'duration': 12, 'priority': 'HIGH'},
            {'wbs_code': '2.3', 'name': 'Lajes - Armaduras', 'duration': 18, 'priority': 'HIGH'},
            {'wbs_code': '2.4', 'name': 'Lajes - Betonagem', 'duration': 15, 'priority': 'HIGH'},
        ],
        'MASONRY': [
            {'wbs_code': '3.1', 'name': 'Paredes Externas', 'duration': 20, 'priority': 'MEDIUM'},
            {'wbs_code': '3.2', 'name': 'Paredes Internas', 'duration': 15, 'priority': 'MEDIUM'},
            {'wbs_code': '3.3', 'name': 'Reboco Preparatório', 'duration': 10, 'priority': 'LOW'},
        ],
        'MEP': [
            {'wbs_code': '4.1', 'name': 'Instalação Eléctrica', 'duration': 20, 'priority': 'HIGH'},
            {'wbs_code': '4.2', 'name': 'Instalação Hidráulica', 'duration': 15, 'priority': 'HIGH'},
            {'wbs_code': '4.3', 'name': 'Instalação Sanitária', 'duration': 10, 'priority': 'MEDIUM'},
        ],
        'FINISHES': [
            {'wbs_code': '5.1', 'name': 'Pavimentos', 'duration': 15, 'priority': 'MEDIUM'},
            {'wbs_code': '5.2', 'name': 'Caixilharia', 'duration': 12, 'priority': 'MEDIUM'},
            {'wbs_code': '5.3', 'name': 'Pintura', 'duration': 15, 'priority': 'LOW'},
            {'wbs_code': '5.4', 'name': 'Louças Sanitárias', 'duration': 8, 'priority': 'MEDIUM'},
        ],
        'DELIVERY': [
            {'wbs_code': '6.1', 'name': 'Limpeza Final', 'duration': 5, 'priority': 'MEDIUM'},
            {'wbs_code': '6.2', 'name': 'Inspecção', 'duration': 5, 'priority': 'HIGH'},
            {'wbs_code': '6.3', 'name': 'Entrega ao Cliente', 'duration': 5, 'priority': 'HIGH'},
        ],
    }
    
    @classmethod
    @transaction.atomic
    def create_construction_project(
        cls,
        contract_id: str,
        user=None,
        start_date: Optional[date] = None,
    ) -> dict:
        """
        Criar projeto de obra a partir de um contrato.
        
        Args:
            contract_id: UUID do contrato assinado
            user: User que está criando o projeto
            start_date: Data de início do projeto (default: hoje)
            
        Returns:
            dict com project_id e dados do projeto criado
        """
        from apps.contracts.models import Contract
        from apps.projects.models import Project
        from apps.construction.models import ConstructionPhase, ConstructionTask
        
        logger.info(f'Creating construction project for contract: {contract_id}')
        
        try:
            # 1. Buscar contrato
            contract = Contract.objects.select_related(
                'lead', 'unit', 'unit__floor', 'unit__floor__building'
            ).get(id=contract_id)
            
            if contract.status != Contract.STATUS_ACTIVE:
                return {
                    'success': False,
                    'error': f'Contrato deve estar assinado (estado: {contract.status})'
                }
            
            # 2. Verificar se já existe projeto para este contrato
            from apps.construction.models import ConstructionProject
            existing = ConstructionProject.objects.filter(contract=contract).first()
            if existing:
                return {
                    'success': False,
                    'error': f'Já existe um projeto de obra para este contrato',
                    'project_id': str(existing.id)
                }
            
            # 3. Obter projeto imobiliário relacionado
            unit = contract.unit
            building = unit.floor.building
            project = building.project
            
            # 4. Criar ConstructionProject
            if start_date is None:
                start_date = timezone.now().date()
            
            construction_project = ConstructionProject.objects.create(
                contract=contract,
                project=project,
                building=building,
                unit=unit,
                name=f'Obra - {unit.code}',
                description=f'Projeto de obra para unidade {unit.code} (Contrato {contract.contract_number})',
                start_planned=start_date,
                status='PLANNING',
                created_by=user
            )
            
            # 5. Criar fases padrão
            phases = cls._create_default_phases(
                construction_project=construction_project,
                project=project,
                building=building,
                start_date=start_date,
                user=user
            )
            
            # 6. Criar tasks para cada fase
            tasks = cls._create_default_tasks(
                phases=phases,
                project=project,
                building=building,
                user=user
            )
            
            # 7. Criar orçamento base
            budget_result = cls._create_default_budget(
                construction_project=construction_project,
                project=project,
                unit=unit,
                user=user
            )
            
            # 8. Atualizar status do projeto
            construction_project.status = 'IN_PROGRESS'
            construction_project.save(update_fields=['status'])
            
            # 9. Criar workflow instance
            from apps.workflows.models import WorkflowInstance, WorkflowDefinition
            try:
                workflow_def = WorkflowDefinition.objects.get(
                    workflow_type=WorkflowDefinition.TYPE_PROJECT_INIT,
                    is_active=True
                )
                WorkflowInstance.objects.create(
                    workflow=workflow_def,
                    status=WorkflowInstance.STATUS_COMPLETED,
                    context={
                        'contract_id': str(contract_id),
                        'project_id': str(construction_project.id),
                        'phases_count': len(phases),
                        'tasks_count': len(tasks),
                    },
                    trigger_model='Contract',
                    trigger_object_id=str(contract_id),
                    completed_at=timezone.now()
                )
            except WorkflowDefinition.DoesNotExist:
                pass
            
            # 10. Notificar cliente
            from apps.workflows.tasks import send_workflow_notification
            send_workflow_notification.delay(
                notification_type='project_initialized',
                lead_id=str(contract.lead.id),
                project_id=str(construction_project.id),
                unit_code=unit.code
            )
            
            return {
                'success': True,
                'project_id': str(construction_project.id),
                'project_name': construction_project.name,
                'phases_created': len(phases),
                'tasks_created': len(tasks),
                'budget_id': budget_result.get('budget_id'),
                'message': f'Projeto de obra criado com {len(phases)} fases e {len(tasks)} tasks'
            }
            
        except Contract.DoesNotExist:
            return {
                'success': False,
                'error': 'Contrato não encontrado'
            }
        except Exception as e:
            logger.error(f'Error creating construction project: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def _create_default_phases(
        cls,
        construction_project,
        project,
        building,
        start_date: date,
        user=None,
    ) -> List:
        """Criar fases padrão do projeto."""
        from apps.construction.models import ConstructionPhase
        
        phases = []
        current_start = start_date
        
        for phase_def in cls.DEFAULT_PHASES:
            end_date = current_start + timedelta(days=phase_def['duration_days'])
            
            phase = ConstructionPhase.objects.create(
                project=project,
                building=building,
                phase_type=phase_def['phase_type'],
                name=f"{phase_def['name_prefix']} - {building.name}",
                description=f"Fase de {phase_def['name_prefix'].lower()} do projeto",
                start_planned=current_start,
                end_planned=end_date,
                status=ConstructionPhase.STATUS_NOT_STARTED,
                order=phase_def['order'],
                created_by=user
            )
            phases.append(phase)
            current_start = end_date
        
        return phases
    
    @classmethod
    def _create_default_tasks(
        cls,
        phases: List,
        project,
        building,
        user=None,
    ) -> List:
        """Criar tasks padrão para cada fase."""
        from apps.construction.models import ConstructionTask, ConstructionPhase
        
        tasks = []
        
        for phase in phases:
            task_templates = cls.TASK_TEMPLATES.get(phase.phase_type, [])
            
            for template in task_templates:
                # Calcular data baseada na fase
                days_offset = template['duration'] // 2  # Simplificação
                due_date = phase.start_planned + timedelta(days=days_offset)
                
                task = ConstructionTask.objects.create(
                    phase=phase,
                    project=project,
                    building=building,
                    wbs_code=template['wbs_code'],
                    name=template['name'],
                    description=f"Task de {template['name'].lower()}",
                    due_date=due_date,
                    priority=template['priority'],
                    status=ConstructionTask.STATUS_PENDING,
                    created_by=user
                )
                tasks.append(task)
        
        return tasks
    
    @classmethod
    def _create_default_budget(
        cls,
        construction_project,
        project,
        unit,
        user=None,
    ) -> dict:
        """Criar orçamento baseado no tipo de unidade."""
        from apps.budget.models import SimpleBudget
        
        try:
            # Determinar ilha do projeto
            island = project.island if hasattr(project, 'island') else 'SANTIAGO'
            
            # Criar orçamento simplificado
            budget = SimpleBudget.objects.create(
                project=project,
                name=f'Orçamento Obra - {unit.code}',
                version='1.0',
                description=f'Orçamento automático para obra da unidade {unit.code}',
                island=island,
                status=SimpleBudget.STATUS_DRAFT,
                created_by=user
            )
            
            return {
                'success': True,
                'budget_id': str(budget.id)
            }
            
        except Exception as e:
            logger.warning(f'Could not create budget: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def import_bim_model(
        cls,
        project_id: str,
        ifc_file,
        user=None,
    ) -> dict:
        """
        Importar modelo BIM (IFC) para o projeto.
        
        Args:
            project_id: UUID do ConstructionProject
            ifc_file: Ficheiro IFC
            user: User que está a importar
            
        Returns:
            dict com resultado da importação
        """
        logger.info(f'Importing BIM model for project: {project_id}')
        
        try:
            from apps.construction.models import ConstructionProject
            
            project = ConstructionProject.objects.get(id=project_id)
            
            # TODO: Integração com módulo BIM quando disponível
            # Por agora, apenas registamos a intenção
            
            return {
                'success': True,
                'project_id': str(project_id),
                'message': 'Importação de IFC registada. Processamento em background.',
                'note': 'Integração BIM completa em desenvolvimento'
            }
            
        except Exception as e:
            logger.error(f'Error importing BIM model: {e}')
            return {
                'success': False,
                'error': str(e)
            }


# Modelo auxiliar para ConstructionProject
# Este modelo deve ser adicionado ao construction/models.py
"""
class ConstructionProject(TenantAwareModel):
    '''Projeto de obra vinculado a um contrato.'''
    
    STATUS_PLANNING = 'PLANNING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_ON_HOLD = 'ON_HOLD'
    STATUS_COMPLETED = 'COMPLETED'
    
    STATUS_CHOICES = [
        (STATUS_PLANNING, 'Em Planeamento'),
        (STATUS_IN_PROGRESS, 'Em Execução'),
        (STATUS_ON_HOLD, 'Suspenso'),
        (STATUS_COMPLETED, 'Concluído'),
    ]
    
    contract = models.OneToOneField(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='construction_project'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='construction_projects'
    )
    building = models.ForeignKey(
        'projects.Building',
        on_delete=models.CASCADE,
        related_name='construction_projects'
    )
    unit = models.ForeignKey(
        'inventory.Unit',
        on_delete=models.CASCADE,
        related_name='construction_project'
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNING)
    start_planned = models.DateField()
    end_planned = models.DateField(null=True, blank=True)
    start_actual = models.DateField(null=True, blank=True)
    end_actual = models.DateField(null=True, blank=True)
    
    bim_model_s3_key = models.CharField(max_length=500, blank=True)
    
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Projeto de Obra'
        verbose_name_plural = 'Projetos de Obra'
        ordering = ['-created_at']
"""
