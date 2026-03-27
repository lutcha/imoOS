"""
Core models - ImoOS
Base models and report generation job tracking.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class TenantAwareModel(models.Model):
    """
    Base model for all tenant-scoped models.
    Provides UUID pk + created_at/updated_at timestamps.
    Lives in per-tenant schema — never in 'public'.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ReportJob(models.Model):
    """
    Tracks asynchronous report generation jobs.
    Users create a job, poll for status, and download when ready.
    """
    
    # Report types
    TYPE_SALES_BY_PROJECT = 'sales_by_project'
    TYPE_CRM_PIPELINE = 'crm_pipeline'
    TYPE_PAYMENT_EXTRACT = 'payment_extract'
    TYPE_CONSTRUCTION_REPORT = 'construction_report'
    TYPE_UNIT_LISTING = 'unit_listing'
    
    TYPE_CHOICES = [
        (TYPE_SALES_BY_PROJECT, 'Vendas por Projecto'),
        (TYPE_CRM_PIPELINE, 'Pipeline CRM'),
        (TYPE_PAYMENT_EXTRACT, 'Extracto de Pagamentos'),
        (TYPE_CONSTRUCTION_REPORT, 'Relatório de Obra'),
        (TYPE_UNIT_LISTING, 'Listagem de Unidades'),
    ]
    
    # Output formats
    FORMAT_PDF = 'pdf'
    FORMAT_EXCEL = 'excel'
    FORMAT_CSV = 'csv'
    
    FORMAT_CHOICES = [
        (FORMAT_PDF, 'PDF'),
        (FORMAT_EXCEL, 'Excel (.xlsx)'),
        (FORMAT_CSV, 'CSV'),
    ]
    
    # Status
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_PROCESSING, 'A processar'),
        (STATUS_COMPLETED, 'Concluído'),
        (STATUS_FAILED, 'Falhou'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Report configuration
    report_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    output_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default=FORMAT_PDF)
    
    # Filters (stored as JSON)
    filters = models.JSONField(default=dict, blank=True, help_text='Filters applied to report')
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    progress = models.IntegerField(default=0, help_text='Progress percentage (0-100)')
    
    # Result
    file_url = models.URLField(blank=True, help_text='S3 presigned download URL')
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True, help_text='File size in bytes')
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Metadata
    tenant = models.ForeignKey('tenants.Client', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(help_text='Download URL expires at')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status', '-created_at']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.get_report_type_display()} - {self.status} - {self.created_at:%Y-%m-%d %H:%M}'
    
    def save(self, *args, **kwargs):
        # Set default expiry (7 days from now)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
    
    @property
    def is_ready(self):
        """Check if report is ready for download."""
        return self.status == self.STATUS_COMPLETED and self.file_url
    
    @property
    def is_expired(self):
        """Check if download URL has expired."""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def mark_completed(self, file_url: str, file_name: str, file_size: int = None):
        """Mark job as completed with download URL."""
        self.status = self.STATUS_COMPLETED
        self.progress = 100
        self.file_url = file_url
        self.file_name = file_name
        self.file_size = file_size
        self.completed_at = timezone.now()
        self.save(update_fields=[
            'status', 'progress', 'file_url', 'file_name', 
            'file_size', 'completed_at'
        ])
    
    def mark_failed(self, error_message: str):
        """Mark job as failed with error message."""
        self.status = self.STATUS_FAILED
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])
    
    def mark_processing(self, progress: int = 0):
        """Mark job as processing with optional progress."""
        self.status = self.STATUS_PROCESSING
        self.progress = progress
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'progress', 'started_at'])
