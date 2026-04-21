"""
ConstructionProject — Projeto de obra vinculado a contrato.

Este modelo representa um projeto de construção específico para uma
unidade vendida, permitindo o acompanhamento individualizado da obra.
"""
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel


class ConstructionProject(TenantAwareModel):
    """
    Projeto de obra vinculado a um contrato de venda.
    
    Permite o acompanhamento individualizado da construção
    para cada unidade vendida.
    """
    
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
    
    # Relações principais
    contract = models.OneToOneField(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='construction_project',
        verbose_name='Contrato'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='construction_projects',
        verbose_name='Projecto Imobiliário'
    )
    building = models.ForeignKey(
        'projects.Building',
        on_delete=models.CASCADE,
        related_name='construction_projects',
        verbose_name='Edifício',
        null=True,
        blank=True
    )
    unit = models.ForeignKey(
        'inventory.Unit',
        on_delete=models.CASCADE,
        related_name='construction_project',
        verbose_name='Unidade'
    )
    
    # Identificação
    name = models.CharField(max_length=200, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNING,
        verbose_name='Estado'
    )
    
    # Cronograma
    start_planned = models.DateField(verbose_name='Início Planeado')
    end_planned = models.DateField(null=True, blank=True, verbose_name='Fim Planeado')
    start_actual = models.DateField(null=True, blank=True, verbose_name='Início Real')
    end_actual = models.DateField(null=True, blank=True, verbose_name='Fim Real')
    
    # BIM (opcional)
    bim_model_s3_key = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='S3 Key do Modelo BIM'
    )
    
    # Meta
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_construction_projects',
        verbose_name='Criado por'
    )
    
    history = HistoricalRecords()
    
    class Meta:
        app_label = 'construction'
        verbose_name = 'Projeto de Obra'
        verbose_name_plural = 'Projetos de Obra'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'
    
    @property
    def progress_percent(self):
        """
        Calcular progresso baseado no prédio ou fases se vinculadas.
        Aqui assumimos as fases do Projecto imobiliário.
        """
        # Se o ConstructionProject tiver suas próprias fases no futuro, priorizar.
        # Por agora, usa o progresso do prédio ou projeto global.
        phases = self.project.phases.all()
        if self.building:
            phases = phases.filter(building=self.building)
            
        if not phases:
            return 0
            
        total_progress = sum(p.progress_percent for p in phases)
        return float(total_progress / phases.count())

    @property
    def is_delayed(self):
        """Verificar se está atrasado em relação ao plano."""
        from django.utils import timezone
        if self.status == self.STATUS_COMPLETED:
            return False
        if not self.end_planned:
            return False
        return self.end_planned < timezone.now().date()

    @property
    def sales_value(self):
        """Valor de venda do contrato associado."""
        return self.contract.total_price_cve

    @property
    def estimated_construction_cost(self):
        """
        Custo de construção estimado. 
        Calculado a partir das tasks do Projecto/Building.
        """
        from apps.construction.models.task import ConstructionTask
        from django.db.models import Sum
        
        # Filtramos tasks que pertencem ao mesmo projeto e prédio
        qs = ConstructionTask.objects.filter(project=self.project)
        if self.building:
            qs = qs.filter(building=self.building)
            
        result = qs.aggregate(total=Sum('estimated_cost'))
        return result['total'] or 0

    @property
    def actual_construction_cost(self):
        """Custo de construção real até o momento."""
        from apps.construction.models.task import ConstructionTask
        from django.db.models import Sum
        
        qs = ConstructionTask.objects.filter(project=self.project)
        if self.building:
            qs = qs.filter(building=self.building)
            
        result = qs.aggregate(total=Sum('actual_cost'))
        return result['total'] or 0
