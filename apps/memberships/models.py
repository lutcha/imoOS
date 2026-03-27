"""
Tenant Membership — TENANT_APP (lives in each tenant's PostgreSQL schema).

Why this exists:
  User lives in the public schema (SHARED_APP).  Storing `role` on User
  makes it a global flag that grants admin access across ALL tenants —
  a critical isolation flaw.  TenantMembership stores the role per-schema
  so a user can be 'admin' in Empresa A while being 'vendedor' in Empresa B.

Cross-schema FK:
  The FK to users.User works because django-tenants sets search_path to
  '{tenant_schema},public', making the public users_user table visible from
  within any tenant schema.  This pattern is already used by apps.crm and
  apps.projects.
"""
import uuid
from django.conf import settings
from django.db import models


class TenantMembership(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_GESTOR = 'gestor'
    ROLE_VENDEDOR = 'vendedor'
    ROLE_ENGENHEIRO = 'engenheiro'
    ROLE_INVESTIDOR = 'investidor'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_GESTOR, 'Gestor de Projecto'),
        (ROLE_VENDEDOR, 'Vendedor'),
        (ROLE_ENGENHEIRO, 'Engenheiro de Obra'),
        (ROLE_INVESTIDOR, 'Investidor'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',
        db_index=True,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Membro do Tenant'
        verbose_name_plural = 'Membros do Tenant'
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='unique_user_per_tenant_schema',
            ),
        ]

    def __str__(self):
        return f'{self.user_id} — {self.role}'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN and self.is_active
