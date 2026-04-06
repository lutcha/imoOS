"""
ConstructionPhase - WBS Level 1
Fases principais da obra (Fundação, Estrutura, Alvenaria...)
"""
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel


class ConstructionPhase(TenantAwareModel):
    """
    Fases principais da obra - WBS Level 1.
    
    Agrupa tasks relacionadas em fases lógicas da construção.
    O progresso é calculado automaticamente baseado nas tasks.
    """
    
    PHASES = [
        ('FOUNDATION', 'Fundação'),
        ('STRUCTURE', 'Estrutura'),
        ('MASONRY', 'Alvenaria'),
        ('MEP', 'Instalações Hidro/Elétrica'),
        ('FINISHES', 'Acabamentos'),
        ('DELIVERY', 'Entrega'),
    ]
    
    STATUS_NOT_STARTED = 'NOT_STARTED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_BLOCKED = 'BLOCKED'
    
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Não Iniciado'),
        (STATUS_IN_PROGRESS, 'Em Execução'),
        (STATUS_COMPLETED, 'Concluído'),
        (STATUS_BLOCKED, 'Bloqueado'),
    ]
    
    # Relações
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='phases',
        verbose_name='Projecto'
    )
    building = models.ForeignKey(
        'projects.Building',
        on_delete=models.CASCADE,
        related_name='phases',
        verbose_name='Edifício',
        null=True,
        blank=True
    )
    
    # Identificação
    phase_type = models.CharField(
        max_length=20,
        choices=PHASES,
        verbose_name='Tipo de Fase'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nome'
    )  # Ex: "Fundação - Bloco A"
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    
    # Cronograma
    start_planned = models.DateField(
        verbose_name='Início Planeado'
    )
    end_planned = models.DateField(
        verbose_name='Fim Planeado'
    )
    start_actual = models.DateField(
        null=True,
        blank=True,
        verbose_name='Início Real'
    )
    end_actual = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fim Real'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
        verbose_name='Estado',
        db_index=True
    )
    
    # Progresso agregado (calculado das tasks)
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Progresso (%)'
    )
    
    # Ordem
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Ordem'
    )
    
    # Meta
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_phases'
    )
    
    history = HistoricalRecords()
    
    class Meta:
        app_label = 'construction'
        verbose_name = 'Fase da Obra'
        verbose_name_plural = 'Fases da Obra'
        ordering = ['project', 'order']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'order']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.get_phase_type_display()})'
    
    def recalculate_progress(self):
        """Recalcular progresso baseado nas tasks."""
        tasks = self.tasks.all()
        if not tasks:
            self.progress_percent = 0
            return
        
        total_progress = sum(t.progress_percent for t in tasks)
        self.progress_percent = total_progress / tasks.count()
        
        # Auto-update status baseado no progresso
        if self.progress_percent >= 100:
            self.status = self.STATUS_COMPLETED
            from django.utils import timezone
            if not self.end_actual:
                self.end_actual = timezone.now().date()
        elif self.progress_percent > 0:
            self.status = self.STATUS_IN_PROGRESS
            if not self.start_actual:
                from django.utils import timezone
                self.start_actual = timezone.now().date()
        
        self.save(update_fields=['progress_percent', 'status', 'start_actual', 'end_actual'])
