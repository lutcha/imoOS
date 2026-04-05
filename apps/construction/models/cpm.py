"""
CPM (Critical Path Method) - Advanced Mode
Dependências entre tasks e snapshots de cálculo CPM.
"""
from django.db import models

from apps.core.models import TenantAwareModel


class TaskDependency(TenantAwareModel):
    """
    Dependências entre tasks - só usado em modo avançado.
    
    Tipos de dependência:
    - FS (Finish-to-Start): A termina → B começa (mais comum)
    - SS (Start-to-Start): A começa → B começa
    - FF (Finish-to-Finish): A termina → B termina
    - SF (Start-to-Finish): A começa → B termina (raro)
    """
    
    DEP_FS = 'FS'
    DEP_SS = 'SS'
    DEP_FF = 'FF'
    DEP_SF = 'SF'
    
    DEP_TYPES = [
        (DEP_FS, 'Finish-to-Start'),
        (DEP_SS, 'Start-to-Start'),
        (DEP_FF, 'Finish-to-Finish'),
        (DEP_SF, 'Start-to-Finish'),
    ]
    
    from_task = models.ForeignKey(
        'construction.ConstructionTask',
        on_delete=models.CASCADE,
        related_name='successors',
        verbose_name='Da Tarefa'
    )
    to_task = models.ForeignKey(
        'construction.ConstructionTask',
        on_delete=models.CASCADE,
        related_name='predecessors',
        verbose_name='Para a Tarefa'
    )
    dependency_type = models.CharField(
        max_length=2,
        choices=DEP_TYPES,
        default=DEP_FS,
        verbose_name='Tipo de Dependência'
    )
    lag_days = models.IntegerField(
        default=0,
        verbose_name='Lag (dias)',
        help_text='Atraso entre tasks (positivo) ou overlap (negativo)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'construction'
        verbose_name = 'Dependência entre Tarefas'
        verbose_name_plural = 'Dependências entre Tarefas'
        unique_together = ['from_task', 'to_task']
        indexes = [
            models.Index(fields=['from_task']),
            models.Index(fields=['to_task']),
        ]
    
    def __str__(self):
        return f'{self.from_task.wbs_code} {self.dependency_type}+{self.lag_days} {self.to_task.wbs_code}'
    
    def clean(self):
        """Validar que não há ciclos."""
        from django.core.exceptions import ValidationError
        
        if self.from_task == self.to_task:
            raise ValidationError('Uma tarefa não pode depender de si mesma.')
        
        # Verificar ciclo simples
        current = self.to_task
        visited = set()
        while True:
            if current.id in visited:
                raise ValidationError('Ciclo detectado nas dependências.')
            visited.add(current.id)
            
            # Pegar primeiro predecessor
            pred = TaskDependency.objects.filter(to_task=current).first()
            if not pred:
                break
            current = pred.from_task
            if current.id == self.from_task.id:
                raise ValidationError('Ciclo detectado nas dependências.')


class CPMSnapshot(TenantAwareModel):
    """
    Cache do cálculo CPM - recalculado quando tasks mudam.
    
    Armazena Early/Late dates e identifica caminho crítico.
    """
    
    task = models.OneToOneField(
        'construction.ConstructionTask',
        on_delete=models.CASCADE,
        related_name='cpm_data',
        verbose_name='Tarefa'
    )
    
    # Early dates (forward pass)
    early_start = models.DateField(
        null=True,
        blank=True,
        verbose_name='Early Start'
    )
    early_finish = models.DateField(
        null=True,
        blank=True,
        verbose_name='Early Finish'
    )
    
    # Late dates (backward pass)
    late_start = models.DateField(
        null=True,
        blank=True,
        verbose_name='Late Start'
    )
    late_finish = models.DateField(
        null=True,
        blank=True,
        verbose_name='Late Finish'
    )
    
    # Critical path
    total_float = models.IntegerField(
        default=0,
        verbose_name='Folga Total (dias)'
    )
    free_float = models.IntegerField(
        default=0,
        verbose_name='Folga Livre (dias)'
    )
    is_critical = models.BooleanField(
        default=False,
        verbose_name='No Caminho Crítico'
    )
    
    # Metadados
    calculated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Calculado em'
    )
    
    class Meta:
        app_label = 'construction'
        verbose_name = 'Snapshot CPM'
        verbose_name_plural = 'Snapshots CPM'
        ordering = ['-calculated_at']
        indexes = [
            models.Index(fields=['task', 'is_critical']),
            models.Index(fields=['calculated_at']),
        ]
    
    def __str__(self):
        critical = 'CRÍTICO' if self.is_critical else 'normal'
        return f'{self.task.wbs_code} - {critical} (TF={self.total_float})'
    
    @property
    def can_delay(self):
        """Verificar se pode atrasar sem afetar o projeto."""
        return self.total_float > 0
    
    @property
    def delay_impact(self):
        """Impacto do atraso no projeto (dias)."""
        if self.is_critical:
            return 'Projeto atrasará igual número de dias'
        return f'Pode atrasar até {self.total_float} dias sem afetar o projeto'
