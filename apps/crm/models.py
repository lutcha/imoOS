from decimal import Decimal

from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel
from apps.inventory.models import Unit


# ---------------------------------------------------------------------------
# Lead — pipeline stage transitions (enforced by services.advance_lead_stage)
# ---------------------------------------------------------------------------

LEAD_STAGE_TRANSITIONS = {
    'new':              ['contacted', 'lost'],
    'contacted':        ['visit_scheduled', 'lost'],
    'visit_scheduled':  ['proposal_sent', 'lost'],
    'proposal_sent':    ['negotiation', 'won', 'lost'],
    'negotiation':      ['won', 'lost'],
    'won':              [],
    'lost':             [],
}


class Lead(TenantAwareModel):
    STATUS_NEW = 'NEW'
    STATUS_CONTACTED = 'CONTACTED'
    STATUS_QUALIFIED = 'QUALIFIED'
    STATUS_LOST = 'LOST'
    STATUS_CONVERTED = 'CONVERTED'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Novo'),
        (STATUS_CONTACTED, 'Contactado'),
        (STATUS_QUALIFIED, 'Qualificado'),
        (STATUS_LOST, 'Perdido'),
        (STATUS_CONVERTED, 'Convertido (Venda)'),
    ]

    SOURCE_WEB = 'WEB'
    SOURCE_INSTAGRAM = 'INSTAGRAM'
    SOURCE_FACEBOOK = 'FACEBOOK'
    SOURCE_REFERRAL = 'REFERRAL'
    SOURCE_IMOCV = 'IMOCV'
    SOURCE_OTHER = 'OTHER'

    SOURCE_CHOICES = [
        (SOURCE_WEB, 'Website'),
        (SOURCE_INSTAGRAM, 'Instagram'),
        (SOURCE_FACEBOOK, 'Facebook'),
        (SOURCE_REFERRAL, 'Referência'),
        (SOURCE_IMOCV, 'imo.cv'),
        (SOURCE_OTHER, 'Outro'),
    ]

    # Kanban pipeline stage (finer-grained than status)
    STAGE_NEW = 'new'
    STAGE_CONTACTED = 'contacted'
    STAGE_VISIT_SCHEDULED = 'visit_scheduled'
    STAGE_PROPOSAL_SENT = 'proposal_sent'
    STAGE_NEGOTIATION = 'negotiation'
    STAGE_WON = 'won'
    STAGE_LOST = 'lost'

    STAGE_CHOICES = [
        (STAGE_NEW, 'Novo'),
        (STAGE_CONTACTED, 'Contactado'),
        (STAGE_VISIT_SCHEDULED, 'Visita Agendada'),
        (STAGE_PROPOSAL_SENT, 'Proposta Enviada'),
        (STAGE_NEGOTIATION, 'Negociação'),
        (STAGE_WON, 'Ganho'),
        (STAGE_LOST, 'Perdido'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_WEB)

    # WhatsApp Compliance
    whatsapp_opt_out = models.BooleanField(
        default=False,
        help_text='Lead pediu para não receber mensagens WhatsApp (LGPD/Lei 133/V/2019)',
    )
    whatsapp_opt_out_at = models.DateTimeField(null=True, blank=True)

    # Kanban pipeline
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default=STAGE_NEW)
    lost_reason = models.TextField(blank=True)

    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preferred_typology = models.CharField(max_length=10, blank=True)  # T1, T2 etc.

    notes = models.TextField(blank=True)

    # Sales timeline
    visit_date = models.DateTimeField(null=True, blank=True)
    proposal_sent_at = models.DateTimeField(null=True, blank=True)

    # Commission rate for this lead's eventual sale
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('3.00'),
        help_text='% comissão do vendedor',
    )

    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_leads',
    )

    # Interest
    interested_unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='leads',
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stage', 'created_at'], name='crm_lead_stage_created_idx'),
            models.Index(fields=['email'],                name='crm_lead_email_idx'),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.status})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Interaction(TenantAwareModel):
    TYPE_CALL = 'CALL'
    TYPE_MEETING = 'MEETING'
    TYPE_EMAIL = 'EMAIL'
    TYPE_WHATSAPP = 'WHATSAPP'
    TYPE_CHOICES = [
        (TYPE_CALL, 'Chamada'),
        (TYPE_MEETING, 'Reunião'),
        (TYPE_EMAIL, 'E-mail'),
        (TYPE_WHATSAPP, 'WhatsApp'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateTimeField()
    summary = models.TextField()
    is_completed = models.BooleanField(default=True)

    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Interação'
        verbose_name_plural = 'Interações'
        ordering = ['-date']


class UnitReservation(TenantAwareModel):
    """
    Reserva de uma unidade para um lead.

    Previne double-booking via SELECT FOR UPDATE em services.create_reservation().
    A constraint unique_active_reservation_per_unit é a segunda linha de defesa.
    Uma unidade só pode ter uma reserva ACTIVE de cada vez.
    """
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_EXPIRED = 'EXPIRED'
    STATUS_CONVERTED = 'CONVERTED'   # → contrato assinado
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Activa'),
        (STATUS_EXPIRED, 'Expirada'),
        (STATUS_CONVERTED, 'Convertida em Contrato'),
        (STATUS_CANCELLED, 'Cancelada'),
    ]

    unit = models.ForeignKey(
        'inventory.Unit', on_delete=models.PROTECT, related_name='reservations',
    )
    lead = models.ForeignKey(
        'crm.Lead', on_delete=models.CASCADE, related_name='reservations',
    )
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    expires_at = models.DateTimeField(help_text='Reserva expira automaticamente (default +48h)')
    deposit_amount_cve = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
    )
    notes = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-created_at']
        constraints = [
            # DB-level guarantee: only one ACTIVE reservation per unit at a time.
            # services.create_reservation() uses SELECT FOR UPDATE to prevent the
            # race condition before this constraint would fire.
            models.UniqueConstraint(
                fields=['unit'],
                condition=models.Q(status='ACTIVE'),
                name='unique_active_reservation_per_unit',
            ),
        ]

    def __str__(self):
        return f'Reserva {self.id} — {self.unit.code} ({self.status})'

    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == self.STATUS_ACTIVE and self.expires_at > timezone.now()


# ---------------------------------------------------------------------------
# WhatsApp Automation
# ---------------------------------------------------------------------------

class WhatsAppTemplate(TenantAwareModel):
    """
    Template oficial registado na Meta Cloud API.
    A API exige `template_id_meta` (ou só o nome exato do template) aprovado
    para originar uma conversa (HSM - Highly Structured Message).
    """
    name = models.CharField(max_length=100)          # ex: 'novo_lead', 'lembrete_pagamento'
    template_id_meta = models.CharField(max_length=100)  # ID registado na Meta
    language = models.CharField(max_length=10, default='pt_PT')
    variables = models.JSONField(default=dict)        # ex: {"1": "nome_lead", "2": "nome_unidade"}
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [('name',)]  # único por schema (tenant)
        verbose_name = 'Template WhatsApp'
        verbose_name_plural = 'Templates WhatsApp'

    def __str__(self):
        return self.name


class WhatsAppMessage(TenantAwareModel):
    """
    Auditoria e registo de mensagens WhatsApp enviadas (LGPD / Lei 133/V/2019).
    """
    STATUS_SENT      = 'SENT'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_READ      = 'READ'
    STATUS_FAILED    = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_SENT, 'Enviada'),
        (STATUS_DELIVERED, 'Entregue'),
        (STATUS_READ, 'Lida'),
        (STATUS_FAILED, 'Falhou'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(WhatsAppTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_SENT)
    message_id_meta = models.CharField(max_length=100, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.phone} - {self.status}'

