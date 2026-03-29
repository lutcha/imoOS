import uuid
from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class InvestorProfile(models.Model):
    """
    Optional profile for users with role INVESTIDOR.
    Links a user to their investor metadata within a tenant schema.

    Lives in TENANT_APPS — one profile per user per tenant schema.
    The investor portal logic (InvestorPortalViewSet) reads contracts
    from apps.contracts directly; this model stores supplementary metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='investor_profile',
    )
    phone = models.CharField(max_length=20, blank=True)
    preferred_language = models.CharField(
        max_length=5,
        default='pt-pt',
        choices=[
            ('pt-pt', 'Português'),
            ('en', 'English'),
            ('fr', 'Français'),
        ],
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Perfil de Investidor'
        verbose_name_plural = 'Perfis de Investidores'

    def __str__(self):
        return f'Investor: {self.user.email}'
