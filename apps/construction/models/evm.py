"""
EVM (Earned Value Management) - Advanced Mode
Snapshots diários ou sob demanda para análise de valor ganho.
"""
from decimal import Decimal
from django.db import models

from apps.core.models import TenantAwareModel


class EVMSnapshot(TenantAwareModel):
    """
    Earned Value Management - snapshot diário ou sob demanda.
    
    Calcula métricas de performance de cronograma e custo:
    - PV (Planned Value): Valor planejado até a data
    - EV (Earned Value): Valor ganho (trabalho realizado)
    - AC (Actual Cost): Custo real incorrido
    - SPI (Schedule Performance Index): EV/PV (>1 = adiantado)
    - CPI (Cost Performance Index): EV/AC (>1 = abaixo orçamento)
    - EAC (Estimate at Completion): Previsão de custo final
    """
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='evm_snapshots',
        verbose_name='Projecto'
    )
    date = models.DateField(
        verbose_name='Data'
    )
    
    # Valores base
    bac = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='BAC (Budget at Completion)',
        help_text='Orçamento total do projeto'
    )
    
    # Valores calculados
    pv = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='PV (Planned Value)',
        help_text='Valor planejado até a data'
    )
    ev = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='EV (Earned Value)',
        help_text='Valor ganho (trabalho realizado)'
    )
    ac = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='AC (Actual Cost)',
        help_text='Custo real incorrido'
    )
    
    # Índices de performance
    spi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name='SPI (Schedule Performance Index)',
        help_text='>1 = adiantado, <1 = atrasado'
    )
    cpi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name='CPI (Cost Performance Index)',
        help_text='>1 = abaixo orçamento, <1 = acima orçamento'
    )
    
    # Variâncias
    sv = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='SV (Schedule Variance)',
        help_text='EV - PV'
    )
    cv = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='CV (Cost Variance)',
        help_text='EV - AC'
    )
    
    # Previsões
    eac = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='EAC (Estimate at Completion)',
        help_text='Previsão de custo final'
    )
    etc = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='ETC (Estimate to Complete)',
        help_text='Estimativa para terminar'
    )
    vac = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='VAC (Variance at Completion)',
        help_text='BAC - EAC'
    )
    
    # Performance indices para previsão
    tcpi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='TCPI (To-Complete Performance Index)',
        help_text='Índice necessário para cumprir orçamento'
    )
    
    # Contadores
    total_tasks = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Tarefas'
    )
    completed_tasks = models.PositiveIntegerField(
        default=0,
        verbose_name='Tarefas Concluídas'
    )
    in_progress_tasks = models.PositiveIntegerField(
        default=0,
        verbose_name='Tarefas em Andamento'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    class Meta:
        app_label = 'construction'
        verbose_name = 'Snapshot EVM'
        verbose_name_plural = 'Snapshots EVM'
        ordering = ['-date']
        unique_together = ['project', 'date']
        indexes = [
            models.Index(fields=['project', '-date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f'{self.project.name} - {self.date} (SPI={self.spi}, CPI={self.cpi})'
    
    @property
    def schedule_status(self):
        """Status do cronograma."""
        if self.spi > Decimal('1.05'):
            return 'ADIANTADO'
        elif self.spi >= Decimal('0.95'):
            return 'NO_CRONOGRAMA'
        elif self.spi >= Decimal('0.8'):
            return 'ATRASADO_LEVE'
        else:
            return 'ATRASADO_CRÍTICO'
    
    @property
    def cost_status(self):
        """Status do custo."""
        if self.cpi > Decimal('1.05'):
            return 'ABAIXO_ORÇAMENTO'
        elif self.cpi >= Decimal('0.95'):
            return 'NO_ORÇAMENTO'
        elif self.cpi >= Decimal('0.8'):
            return 'ACIMA_ORÇAMENTO_LEVE'
        else:
            return 'ACIMA_ORÇAMENTO_CRÍTICO'
    
    @property
    def overall_health(self):
        """Saúde geral do projeto."""
        if self.spi >= 1 and self.cpi >= 1:
            return 'EXCELENTE'
        elif self.spi >= 0.95 and self.cpi >= 0.95:
            return 'BOM'
        elif self.spi >= 0.9 and self.cpi >= 0.9:
            return 'ATENÇÃO'
        else:
            return 'CRÍTICO'
    
    def recalculate_indices(self):
        """Recalcular índices baseado em PV, EV, AC."""
        # SPI = EV / PV
        if self.pv > 0:
            self.spi = (self.ev / self.pv).quantize(Decimal('0.01'))
        
        # CPI = EV / AC
        if self.ac > 0:
            self.cpi = (self.ev / self.ac).quantize(Decimal('0.01'))
        
        # Variâncias
        self.sv = self.ev - self.pv
        self.cv = self.ev - self.ac
        
        # EAC = BAC / CPI (fórmula típica)
        if self.cpi > 0:
            self.eac = (self.bac / self.cpi).quantize(Decimal('0.01'))
        else:
            self.eac = self.bac
        
        # ETC = EAC - AC
        self.etc = self.eac - self.ac
        
        # VAC = BAC - EAC
        self.vac = self.bac - self.eac
        
        # TCPI = (BAC - EV) / (BAC - AC)
        denominator = self.bac - self.ac
        if denominator > 0:
            self.tcpi = ((self.bac - self.ev) / denominator).quantize(Decimal('0.01'))
