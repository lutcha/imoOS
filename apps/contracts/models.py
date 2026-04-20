"""
Contracts module — Tenant schema.

Manages the full lifecycle of a property sale contract: from a converted
UnitReservation through to payment collection (deposit, instalments, final).

Lives in the tenant schema — fully isolated per promotora.
"""
from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
import uuid

from apps.core.models import TenantAwareModel


class ContractTemplate(TenantAwareModel):
    """
    Template de contrato (HTML) com placeholders para substituição dinâmica.
    Permite que cada promotora personalize as suas cláusulas.
    """
    name = models.CharField(max_length=100, verbose_name='Nome do Template')
    html_content = models.TextField(verbose_name='Conteúdo HTML', help_text='Use {{ variable }} para placeholders')
    is_default = models.BooleanField(default=False, verbose_name='Template Padrão')
    
    history = HistoricalRecords()

    class Meta:
        app_label = 'contracts'
        verbose_name = 'Template de Contrato'
        verbose_name_plural = 'Templates de Contrato'

    def __str__(self):
        return self.name


class PaymentPattern(TenantAwareModel):
    """
    Padrão genérico de parcelamento para automatização de tranches.
    Ex: "30/60/10" -> 30% Sinal, 60% em X tranches, 10% Final.
    """
    name = models.CharField(max_length=100, verbose_name='Nome do Padrão')
    deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Sinal (%)')
    final_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Pagamento Final (%)')
    installments_count = models.PositiveIntegerField(default=0, verbose_name='Número de Prestações')
    is_default = models.BooleanField(default=False, verbose_name='Padrão Padrão')

    history = HistoricalRecords()

    class Meta:
        app_label = 'contracts'
        verbose_name = 'Padrão de Pagamento'
        verbose_name_plural = 'Padrões de Pagamento'

    def __str__(self):
        return self.name


class Contract(TenantAwareModel):
    """
    Contrato de compra e venda entre a promotora e um comprador (Lead).

    Lifecycle:
        DRAFT → ACTIVE (contrato assinado) → COMPLETED (pagamento final liquidado)
                                            → CANCELLED

    A contract is typically created by converting a UnitReservation.  The
    reservation FK is nullable to allow contracts to be created directly
    (e.g. off-plan bulk sales) without a prior reservation flow.

    The unit's status should be set to Unit.STATUS_CONTRACT when a contract
    becomes ACTIVE; this is enforced in the service layer, not here.
    """

    STATUS_DRAFT = 'DRAFT'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Rascunho'),
        (STATUS_ACTIVE, 'Activo'),
        (STATUS_COMPLETED, 'Concluído'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    # Origin — optional: a contract can exist without a prior reservation.
    reservation = models.OneToOneField(
        'crm.UnitReservation',
        on_delete=models.PROTECT,
        related_name='contract',
        null=True,
        blank=True,
        verbose_name='Reserva de origem',
    )

    # Core commercial parties.
    unit = models.ForeignKey(
        'inventory.Unit',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name='Unidade',
    )
    lead = models.ForeignKey(
        'crm.Lead',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name='Lead / Comprador',
    )
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts_as_vendor',
        verbose_name='Vendedor responsável',
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True,
        verbose_name='Estado',
    )

    # Human-readable reference printed on the PDF document.
    # Unique at DB level; generation strategy (e.g. ImoOS-2026-0001) lives in
    # the service layer so it can be tenant-prefixed at runtime.
    contract_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número do contrato',
        help_text='Ex: ImoOS-2026-0001',
    )

    # Agreed sale price in Cape Verdean Escudos (authoritative).
    # EUR display conversion is computed at serializer/view level.
    total_price_cve = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor total (CVE)',
    )

    # Timestamps specific to the contract lifecycle.
    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de assinatura',
    )

    signature_request = models.OneToOneField(
        'SignatureRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_contract',
        verbose_name='Pedido de Assinatura',
    )

    # S3 object key for the generated/uploaded PDF — stored without the
    # full URL so the bucket or CDN prefix can change without a migration.
    # Pattern: tenants/{tenant_slug}/contracts/{contract_number}.pdf
    pdf_s3_key = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='S3 key do PDF',
    )

    notes = models.TextField(
        blank=True,
        verbose_name='Notas internas',
    )

    # Advanced Management Links
    template = models.ForeignKey(
        ContractTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts',
        verbose_name='Template utilizado',
    )
    payment_pattern = models.ForeignKey(
        PaymentPattern,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts',
        verbose_name='Padrão de pagamento',
    )

    history = HistoricalRecords()

    class Meta:
        app_label = 'contracts'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at'], name='contract_status_created_idx'),
            models.Index(fields=['unit', 'status'], name='contract_unit_status_idx'),
        ]
        constraints = [
            # Only one ACTIVE contract may exist per reservation.
            # Partial unique index — ignored when reservation IS NULL.
            models.UniqueConstraint(
                fields=['reservation'],
                condition=models.Q(status='ACTIVE'),
                name='unique_active_contract_per_reservation',
            ),
        ]

    def __str__(self):
        return f'{self.contract_number} ({self.get_status_display()})'


class SignatureRequest(TenantAwareModel):
    """
    Registo de um pedido de assinatura eletrónica enviado a um lead.
    """
    STATUS_PENDING   = 'PENDING'
    STATUS_SIGNED    = 'SIGNED'
    STATUS_EXPIRED   = 'EXPIRED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_SIGNED, 'Assinado'),
        (STATUS_EXPIRED, 'Expirado'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name='signature_requests',
        verbose_name='Contrato',
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField(verbose_name='Expira a')
    signed_at = models.DateTimeField(null=True, blank=True, verbose_name='Assinado a')
    signature_png_s3_key = models.CharField(max_length=500, blank=True, verbose_name='S3 key da Assinatura')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Endereço IP')
    signed_by_name = models.CharField(max_length=200, blank=True, verbose_name='Assinado por (Nome)')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='Estado')
    
    history = HistoricalRecords()

    class Meta:
        app_label = 'contracts'
        verbose_name = 'Pedido de Assinatura'
        verbose_name_plural = 'Pedidos de Assinatura'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            from django.utils import timezone
            self.expires_at = timezone.now() + timezone.timedelta(hours=72)
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f'Pedido {self.token} - {self.contract.contract_number} ({self.get_status_display()})'


class Payment(TenantAwareModel):
    """
    Registo de um pagamento associado a um contrato.

    Supports three payment types that cover the typical Cabo Verde real-estate
    payment schedule: sinal (deposit), prestações mensais (instalments), and
    pagamento final (balloon / deed payment).

    The MBE bank reference field stores the Multibanco entity/reference pair
    used for domestic transfers — left blank for wire transfers or cash.

    Status transitions (enforced in the service layer):
        PENDING → PAID     (payment confirmed)
        PENDING → OVERDUE  (due_date passed, cron task marks it)
        OVERDUE → PAID     (late payment accepted)
    """

    PAYMENT_DEPOSIT = 'DEPOSIT'
    PAYMENT_INSTALLMENT = 'INSTALLMENT'
    PAYMENT_FINAL = 'FINAL'

    TYPE_CHOICES = [
        (PAYMENT_DEPOSIT, 'Sinal'),
        (PAYMENT_INSTALLMENT, 'Prestação'),
        (PAYMENT_FINAL, 'Pagamento Final'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_PAID = 'PAID'
    STATUS_OVERDUE = 'OVERDUE'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_PAID, 'Pago'),
        (STATUS_OVERDUE, 'Em Atraso'),
    ]

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Contrato',
    )
    payment_type = models.CharField(
        max_length=15,
        choices=TYPE_CHOICES,
        verbose_name='Tipo',
    )
    amount_cve = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor (CVE)',
    )
    due_date = models.DateField(
        verbose_name='Data de vencimento',
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de pagamento',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
        verbose_name='Estado',
    )
    # Multibanco entity/reference or bank transfer reference.
    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Referência de pagamento',
        help_text='Referência MBE ou transferência bancária',
    )

    history = HistoricalRecords()

    class Meta:
        app_label = 'contracts'
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['status', 'due_date'], name='payment_status_due_idx'),
            models.Index(fields=['contract', 'status'], name='payment_contract_status_idx'),
        ]

    def __str__(self):
        return (
            f'{self.get_payment_type_display()} — '
            f'{self.amount_cve} CVE — '
            f'{self.get_status_display()}'
        )
