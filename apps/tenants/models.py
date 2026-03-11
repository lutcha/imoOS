import uuid
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from simple_history.models import HistoricalRecords

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
    imo_cv_api_key = models.CharField(max_length=200, blank=True)
    whatsapp_phone_id = models.CharField(max_length=50, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Configurações do Tenant'
        verbose_name_plural = 'Configurações dos Tenants'

