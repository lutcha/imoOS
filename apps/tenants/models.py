import uuid
from django.conf import settings
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from simple_history.models import HistoricalRecords
from django.utils import timezone


class Client(TenantMixin):
    """
    Represents a Promotora/Construtora — a company that uses ImoOS.
    Each Client gets an isolated PostgreSQL schema.
    """
    PLAN_STARTER = 'starter'
    PLAN_PRO = 'pro'
    PLAN_ENTERPRISE = 'enterprise'
    PLAN_CHOICES = [
        (PLAN_STARTER, 'Starter'),
        (PLAN_PRO, 'Pro'),
        (PLAN_ENTERPRISE, 'Enterprise'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Nome da Empresa')
    slug = models.SlugField(unique=True, help_text='Used for S3 prefix and subdomain')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_STARTER)
    is_active = models.BooleanField(default=True)
    country = models.CharField(max_length=2, default='CV', help_text='ISO 3166-1 alpha-2')
    currency = models.CharField(max_length=3, default='CVE')
    timezone = models.CharField(max_length=50, default='Atlantic/Cape_Verde')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    # Required by django-tenants
    auto_create_schema = True

    class Meta:
        verbose_name = 'Cliente (Tenant)'
        verbose_name_plural = 'Clientes (Tenants)'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.schema_name})'

    @property
    def s3_prefix(self):
        """S3 storage prefix for this tenant's files."""
        return f'tenants/{self.slug}/'


class Domain(DomainMixin):
    """
    Maps a subdomain to a tenant.
    Example: empresa-a.imos.cv → Client(schema_name='empresa_a')
    """
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Domínio'
        verbose_name_plural = 'Domínios'
        ordering = ['domain']


class TenantSettings(models.Model):
    """
    Per-tenant configuration: branding, limits, integrations.
    Lives in public schema, references Client.
    """
    tenant = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='settings')
    # Branding
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default='#1E40AF')  # Tailwind blue-800
    # Limits (enforced based on plan)
    max_projects = models.PositiveIntegerField(default=5)
    max_units = models.PositiveIntegerField(default=500)
    max_users = models.PositiveIntegerField(default=20)
    # Integrations
    imo_cv_api_key = models.CharField(max_length=512, blank=True)
    imocv_enabled = models.BooleanField(default=False, help_text='Activar integração com imo.cv')
    imocv_auto_publish = models.BooleanField(
        default=False,
        help_text='Publicar automaticamente unidades AVAILABLE no imo.cv',
    )
    whatsapp_phone_id = models.CharField(max_length=50, blank=True)
    whatsapp_access_token = models.CharField(max_length=512, blank=True, help_text='Token permanente do Meta App')

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Configurações do Tenant'
        verbose_name_plural = 'Configurações dos Tenants'


class PlanEvent(models.Model):
    """
    Immutable audit log of plan lifecycle events for a tenant.
    Lives in the public schema (SHARED_APPS). No HistoricalRecords — it IS the log.
    """
    EVENT_PLAN_UPGRADED = 'PLAN_UPGRADED'
    EVENT_PLAN_DOWNGRADED = 'PLAN_DOWNGRADED'
    EVENT_LIMIT_HIT = 'LIMIT_HIT'
    EVENT_TRIAL_STARTED = 'TRIAL_STARTED'
    EVENT_TRIAL_ENDED = 'TRIAL_ENDED'
    EVENT_IMPERSONATED = 'IMPERSONATED'

    EVENT_CHOICES = [
        (EVENT_PLAN_UPGRADED, 'Plano Actualizado'),
        (EVENT_PLAN_DOWNGRADED, 'Plano Rebaixado'),
        (EVENT_LIMIT_HIT, 'Limite Atingido'),
        (EVENT_TRIAL_STARTED, 'Trial Iniciado'),
        (EVENT_TRIAL_ENDED, 'Trial Terminado'),
        (EVENT_IMPERSONATED, 'Impersonation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='plan_events',
    )
    event_type = models.CharField(max_length=25, choices=EVENT_CHOICES, db_index=True)
    from_plan = models.CharField(max_length=20, blank=True)
    to_plan = models.CharField(max_length=20, blank=True)
    # e.g. {"resource": "projects", "current": 5, "limit": 5}
    metadata = models.JSONField(default=dict)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plan_events_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evento de Plano'
        verbose_name_plural = 'Eventos de Plano'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at'], name='plan_event_tenant_date_idx'),
        ]

    def __str__(self):
        return f'{self.tenant.name} — {self.event_type} — {self.created_at:%Y-%m-%d}'


class TenantRegistration(models.Model):
    """
    Self-service tenant registration (Sprint 7 - Prompt 03).
    Lives in public schema. Tracks onboarding flow from sign-up to active tenant.
    """
    
    # Status choices
    STATUS_PENDING = 'PENDING_VERIFICATION'
    STATUS_VERIFIED = 'VERIFIED'
    STATUS_PROVISIONING = 'PROVISIONING'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_REJECTED = 'REJECTED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente de Verificação'),
        (STATUS_VERIFIED, 'Verificado'),
        (STATUS_PROVISIONING, 'A Provisionar'),
        (STATUS_ACTIVE, 'Activo'),
        (STATUS_REJECTED, 'Rejeitado'),
    ]
    
    # Plan choices (same as Client)
    PLAN_STARTER = 'starter'
    PLAN_PRO = 'pro'
    PLAN_ENTERPRISE = 'enterprise'
    PLAN_CHOICES = [
        (PLAN_STARTER, 'Starter (Gratuito)'),
        (PLAN_PRO, 'Pro (€49/mês)'),
        (PLAN_ENTERPRISE, 'Enterprise'),
    ]
    
    # Company info
    company_name = models.CharField(max_length=200, verbose_name='Nome da Empresa')
    subdomain = models.CharField(
        max_length=63, 
        unique=True, 
        verbose_name='Subdomínio',
        help_text='Será usado como schema_name e subdomínio (ex: subdomain.imos.cv)'
    )
    plan = models.CharField(
        max_length=20, 
        choices=PLAN_CHOICES, 
        default=PLAN_STARTER,
        verbose_name='Plano'
    )
    
    # Contact info
    contact_email = models.EmailField(unique=True, verbose_name='Email de Contacto')
    contact_name = models.CharField(max_length=200, verbose_name='Nome Completo')
    contact_phone = models.CharField(max_length=20, verbose_name='Telefone / WhatsApp')
    
    # Location
    country = models.CharField(
        max_length=2, 
        default='CV', 
        verbose_name='País',
        help_text='ISO 3166-1 alpha-2 (CV, AO, SN)'
    )
    
    # Verification
    verification_token = models.UUIDField(
        default=uuid.uuid4, 
        unique=True, 
        editable=False,
        verbose_name='Token de Verificação'
    )
    token_expires_at = models.DateTimeField(verbose_name='Token Expira Em')
    
    # Status tracking
    status = models.CharField(
        max_length=25, 
        choices=STATUS_CHOICES, 
        default=STATUS_PENDING,
        db_index=True,
        verbose_name='Estado'
    )
    error_message = models.TextField(blank=True, verbose_name='Mensagem de Erro')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado Em')
    provisioned_at = models.DateTimeField(null=True, blank=True, verbose_name='Provisionado Em')
    
    class Meta:
        verbose_name = 'Registo de Tenant'
        verbose_name_plural = 'Registos de Tenants'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Set token expiry on first save."""
        if not self.token_expires_at:
            self.token_expires_at = timezone.now() + timezone.timedelta(hours=48)
        super().save(*args, **kwargs)
    
    @property
    def is_token_expired(self):
        """Check if verification token has expired."""
        return timezone.now() > self.token_expires_at
    
    @property
    def schema_name(self):
        """Generate schema_name from subdomain (django-tenants convention)."""
        return self.subdomain.replace('-', '_')
    
    def __str__(self):
        return f'{self.company_name} ({self.subdomain}) - {self.get_status_display()}'

