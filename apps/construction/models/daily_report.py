from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel

class DailyReport(TenantAwareModel):
    """
    Diário de obra — one report per (project, building, date) tuple.

    Filed by an engineer on-site and progresses through a DRAFT ->
    SUBMITTED -> APPROVED workflow before it influences aggregate
    progress figures.

    Lives in tenant schema — isolated per company.
    """

    STATUS_DRAFT = 'DRAFT'
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_APPROVED = 'APPROVED'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Rascunho'),
        (STATUS_SUBMITTED, 'Submetido'),
        (STATUS_APPROVED, 'Aprovado'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.PROTECT,
        related_name='daily_reports',
        verbose_name='Projecto',
    )
    building = models.ForeignKey(
        'projects.Building',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_reports',
        verbose_name='Edifício',
        help_text='Opcional — relatório pode ser ao nível do projecto inteiro.',
    )
    date = models.DateField(
        verbose_name='Data',
        db_index=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='daily_reports',
        verbose_name='Autor',
        help_text='Engenheiro ou técnico responsável pelo relatório.',
    )
    summary = models.TextField(
        verbose_name='Resumo',
        help_text='Descrição das actividades realizadas no dia.',
    )
    progress_pct = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Avanço (%)',
        help_text='Percentagem de conclusão estimada no momento do relatório.',
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='Estado',
        db_index=True,
    )
    weather = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Condições meteorológicas',
        help_text='Ex.: Ensolarado, Chuva fraca, Vento forte.',
    )
    workers_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Número de trabalhadores',
        help_text='Total de trabalhadores presentes no local no dia.',
    )

    history = HistoricalRecords()

    class Meta:
        app_label = 'construction'
        verbose_name = 'Diário de Obra'
        verbose_name_plural = 'Diários de Obra'
        unique_together = [('project', 'building', 'date')]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['project', '-date'], name='constr_rpt_proj_date_idx'),
            models.Index(fields=['status', '-date'], name='constr_rpt_status_date_idx'),
        ]

    def __str__(self) -> str:
        building_part = f' — {self.building.name}' if self.building_id else ''
        return f'{self.project.name}{building_part} ({self.date})'


class ConstructionPhoto(TenantAwareModel):
    """
    Fotografia georreferenciada associada a um DailyReport.
    """

    report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Relatório',
    )
    s3_key = models.CharField(
        max_length=500,
        verbose_name='Chave S3',
        help_text='S3 object key: tenants/{slug}/construction/...',
    )
    thumbnail_s3_key = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Chave S3 (miniatura)',
        help_text='S3 object key for the auto-generated thumbnail.',
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Legenda',
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitude',
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitude',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
        verbose_name='Carregado por',
    )

    class Meta:
        app_label = 'construction'
        verbose_name = 'Fotografia de Obra'
        verbose_name_plural = 'Fotografias de Obra'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report', '-created_at'], name='construction_photo_report_idx'),
        ]

    def __str__(self) -> str:
        return f'Foto {self.id} — {self.report}'

class ConstructionProgress(TenantAwareModel):
    """
    Aggregated progress snapshot for a Building.
    """

    building = models.OneToOneField(
        'projects.Building',
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Edifício',
    )
    progress_pct = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Avanço geral (%)',
        help_text='Overall completion % derived from approved daily reports.',
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualização',
    )
    last_report = models.ForeignKey(
        DailyReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Último relatório aprovado',
        help_text='Most recent approved DailyReport that updated this snapshot.',
    )

    class Meta:
        app_label = 'construction'
        verbose_name = 'Progresso de Construção'
        verbose_name_plural = 'Progressos de Construção'

    def __str__(self) -> str:
        return f'{self.building} — {self.progress_pct}%'
