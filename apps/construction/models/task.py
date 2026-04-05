"""
ConstructionTask - Core model
SIMPLE MODE (default): Tasks básicas com status, progresso, datas
ADVANCED MODE: Quando ativado, usa CPM/EVM
"""
from decimal import Decimal
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel


class ConstructionTask(TenantAwareModel):
    """
    Tarefa de construção - SIMPLE MODE é default.
    
    Integra com:
    - WhatsApp (A3): Notificações de atribuição e atraso
    - Budget (A4): estimated_cost e actual_cost
    - Projects: Via ForeignKey para Project e Building
    """
    
    # Status simples (SIMPLE MODE - sempre visível)
    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_BLOCKED = 'BLOCKED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_IN_PROGRESS, 'Em Andamento'),
        (STATUS_COMPLETED, 'Concluído'),
        (STATUS_BLOCKED, 'Bloqueada'),
    ]
    
    # Prioridades
    PRIORITY_LOW = 'LOW'
    PRIORITY_MEDIUM = 'MEDIUM'
    PRIORITY_HIGH = 'HIGH'
    PRIORITY_URGENT = 'URGENT'
    
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Baixa'),
        (PRIORITY_MEDIUM, 'Média'),
        (PRIORITY_HIGH, 'Alta'),
        (PRIORITY_URGENT, 'Urgente'),
    ]
    
    # Modo avançado toggle
    ADVANCED_MODE_OFF = 'OFF'
    ADVANCED_MODE_ON = 'ON'
    
    ADVANCED_MODE_CHOICES = [
        (ADVANCED_MODE_OFF, 'Desligado'),
        (ADVANCED_MODE_ON, 'Ligado'),
    ]
    
    # Relações
    phase = models.ForeignKey(
        'construction.ConstructionPhase',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Fase',
        null=True,  # Permite tasks sem fase inicialmente
        blank=True
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Projecto'
    )
    building = models.ForeignKey(
        'projects.Building',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Edifício'
    )
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Atribuído a'
    )
    
    # Identificação WBS
    wbs_code = models.CharField(
        max_length=20,
        verbose_name='Código WBS',
        help_text='Ex: 1.1, 1.2, 2.1...'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nome da Tarefa'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    
    # Status e prioridade
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado',
        db_index=True
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name='Prioridade'
    )
    
    # Datas
    due_date = models.DateField(
        verbose_name='Data Limite',
        db_index=True
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Iniciada em'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Concluída em'
    )
    
    # Progresso (SIMPLE: 0-100 slider)
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Progresso (%)',
        help_text='0-100%'
    )
    
    # Orçamento (link para budget do projeto)
    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Custo Estimado (CVE)'
    )
    actual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Custo Real (CVE)'
    )
    
    # Modo avançado (CPM/EVM)
    advanced_mode = models.CharField(
        max_length=10,
        choices=ADVANCED_MODE_CHOICES,
        default=ADVANCED_MODE_OFF,
        verbose_name='Modo Avançado'
    )
    
    # CPM fields (apenas quando advanced_mode=ON)
    duration_days = models.PositiveIntegerField(
        default=1,
        verbose_name='Duração (dias)',
        help_text='Duração planeada para CPM'
    )
    
    # BIM Link (opcional, para future)
    bim_element_ids = models.JSONField(
        default=list,
        blank=True,
        verbose_name='IDs BIM (IFC)',
        help_text='Lista de GUIDs IFC'
    )
    
    # Meta
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    
    # Notificações
    reminder_sent = models.BooleanField(
        default=False,
        help_text='Lembrete enviado'
    )
    overdue_notified = models.BooleanField(
        default=False,
        help_text='Notificação de atraso enviada'
    )
    
    history = HistoricalRecords()
    
    class Meta:
        app_label = 'construction'
        verbose_name = 'Tarefa de Construção'
        verbose_name_plural = 'Tarefas de Construção'
        ordering = ['phase', 'wbs_code', 'due_date']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['phase', 'wbs_code']),
            models.Index(fields=['advanced_mode']),
        ]
        unique_together = ['project', 'wbs_code']
    
    def __str__(self):
        return f'{self.wbs_code} - {self.name}'
    
    @property
    def is_overdue(self):
        """Verificar se a tarefa está atrasada."""
        if self.status == self.STATUS_COMPLETED:
            return False
        return self.due_date < timezone.now().date()
    
    @property
    def days_overdue(self):
        """Número de dias de atraso."""
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days
    
    @property
    def days_until_due(self):
        """Número de dias até o vencimento."""
        if self.due_date < timezone.now().date():
            return 0
        return (self.due_date - timezone.now().date()).days
    
    @property
    def is_critical(self):
        """Verificar se está no caminho crítico (apenas modo avançado)."""
        if self.advanced_mode == self.ADVANCED_MODE_OFF:
            return False
        cpm_data = getattr(self, 'cpm_data', None)
        return cpm_data.is_critical if cpm_data else False
    
    @property
    def total_float(self):
        """Folga total (apenas modo avançado)."""
        if self.advanced_mode == self.ADVANCED_MODE_OFF:
            return None
        cpm_data = getattr(self, 'cpm_data', None)
        return cpm_data.total_float if cpm_data else None
    
    def save(self, *args, **kwargs):
        # Auto-update completed_at e progress quando status muda
        if self.status == self.STATUS_COMPLETED:
            if not self.completed_at:
                self.completed_at = timezone.now()
            if self.progress_percent < 100:
                self.progress_percent = 100
        
        # Auto-update started_at
        if self.status == self.STATUS_IN_PROGRESS and not self.started_at:
            self.started_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def start(self, user=None):
        """Marcar tarefa como iniciada."""
        self.status = self.STATUS_IN_PROGRESS
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def complete(self, user=None):
        """Marcar tarefa como concluída."""
        self.status = self.STATUS_COMPLETED
        self.progress_percent = 100
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'progress_percent', 'completed_at'])
        
        # Recalcular progresso da fase
        if self.phase:
            self.phase.recalculate_progress()
    
    def update_progress(self, percent, user=None):
        """Atualizar progresso (0-100)."""
        self.progress_percent = min(max(percent, 0), 100)
        
        # Auto-update status baseado no progresso
        if self.progress_percent >= 100:
            self.status = self.STATUS_COMPLETED
            if not self.completed_at:
                self.completed_at = timezone.now()
        elif self.progress_percent > 0:
            if self.status == self.STATUS_PENDING:
                self.status = self.STATUS_IN_PROGRESS
                if not self.started_at:
                    self.started_at = timezone.now()
        
        self.save(update_fields=['progress_percent', 'status', 'started_at', 'completed_at'])
        
        # Recalcular progresso da fase
        if self.phase:
            self.phase.recalculate_progress()
    
    def needs_cpm_recalculation(self):
        """Verificar se mudanças requerem recálculo CPM."""
        if self.advanced_mode == self.ADVANCED_MODE_OFF:
            return False
        return True
