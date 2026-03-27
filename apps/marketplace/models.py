"""Marketplace module — imo.cv integration models."""

from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel


class MarketplaceListing(TenantAwareModel):
    """
    Represents a Unit's listing on the imo.cv marketplace.

    One listing per Unit (OneToOne). Tracks the synchronisation lifecycle
    between ImoOS inventory and the external imo.cv platform, including
    the remote listing ID, sync status, error messages, and an optional
    price override that takes precedence over Unit.pricing.final_price_cve.

    Lives in tenant schema — isolated per company.
    """

    STATUS_PENDING = 'PENDING_SYNC'
    STATUS_PUBLISHED = 'PUBLISHED'
    STATUS_PAUSED = 'PAUSED'
    STATUS_REMOVED = 'REMOVED'

    STATUS_CHOICES = [
        (STATUS_PENDING,   'Pendente Sync'),
        (STATUS_PUBLISHED, 'Publicado'),
        (STATUS_PAUSED,    'Pausado'),
        (STATUS_REMOVED,   'Removido'),
    ]

    unit = models.OneToOneField(
        'inventory.Unit',
        on_delete=models.CASCADE,
        related_name='listing',
        verbose_name='Unidade',
    )
    imocv_listing_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID do anúncio no imo.cv',
        verbose_name='ID imo.cv',
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado',
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última sincronização',
    )
    sync_error = models.TextField(
        blank=True,
        help_text='Último erro de sincronização',
        verbose_name='Erro de sincronização',
    )
    price_override_cve = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Preço publicado no imo.cv. Se None, usa Unit.pricing.final_price_cve',
        verbose_name='Preço publicado (CVE)',
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Publicado em',
    )

    history = HistoricalRecords()

    class Meta:
        app_label = 'marketplace'
        verbose_name = 'Listing Marketplace'
        verbose_name_plural = 'Listings Marketplace'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['imocv_listing_id']),
        ]

    def __str__(self):
        return f'Listing {self.unit} — {self.get_status_display()}'

    @property
    def effective_price_cve(self):
        """
        Returns the price to be published on imo.cv.

        Uses price_override_cve when explicitly set. Falls back to
        Unit.pricing.final_price_cve, returning None gracefully if the
        related UnitPricing object does not exist.
        """
        if self.price_override_cve is not None:
            return self.price_override_cve
        pricing = getattr(self.unit, 'pricing', None)
        if pricing is None:
            return None
        return pricing.final_price_cve


class ImoCvWebhookLog(TenantAwareModel):
    """
    Immutable record of every inbound webhook event received from imo.cv.

    Each row captures the raw payload, the event type, and processing
    outcome. No HistoricalRecords is added — the table itself serves as
    the audit log and rows must never be mutated after creation (except
    processed_at and error fields set by the processing task).

    Lives in tenant schema — isolated per company.
    """

    EVENT_LEAD_CAPTURED = 'lead_captured'
    EVENT_UNIT_VIEWED = 'unit_viewed'
    EVENT_LISTING_UPDATED = 'listing_updated'

    EVENT_CHOICES = [
        (EVENT_LEAD_CAPTURED,   'Lead Capturado'),
        (EVENT_UNIT_VIEWED,     'Unidade Visualizada'),
        (EVENT_LISTING_UPDATED, 'Listing Actualizado'),
    ]

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_CHOICES,
        verbose_name='Tipo de evento',
    )
    imocv_listing_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID imo.cv',
    )
    payload = models.JSONField(
        default=dict,
        verbose_name='Payload',
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Processado em',
    )
    error = models.TextField(
        blank=True,
        verbose_name='Erro de processamento',
    )

    class Meta:
        app_label = 'marketplace'
        verbose_name = 'Webhook Log imo.cv'
        verbose_name_plural = 'Webhook Logs imo.cv'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['processed_at']),
        ]

    def __str__(self):
        return f'[{self.get_event_type_display()}] {self.imocv_listing_id} @ {self.created_at}'
