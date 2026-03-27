"""
Plan limit enforcement for ImoOS SaaS.

Call check_*_limit() in ViewSet.perform_create() before saving a new resource.
All check functions assume they are called from within the correct tenant schema
context (set automatically by django-tenants middleware).
"""
from dataclasses import dataclass

from apps.tenants.models import TenantSettings


@dataclass
class LimitCheck:
    allowed: bool
    current: int
    limit: int
    resource: str

    @property
    def message(self) -> str:
        if self.allowed:
            return ''
        return (
            f'Limite de {self.resource} atingido: {self.current}/{self.limit}. '
            f'Actualize o seu plano para continuar.'
        )

    def as_dict(self) -> dict:
        pct = round(self.current * 100 / self.limit) if self.limit else 0
        return {
            'current': self.current,
            'limit': self.limit,
            'pct_used': pct,
        }


def _get_settings(schema_name: str) -> TenantSettings:
    """Fetch TenantSettings for the schema currently active in the connection."""
    return TenantSettings.objects.select_related('tenant').get(
        tenant__schema_name=schema_name,
    )


def check_project_limit(tenant_settings: TenantSettings) -> LimitCheck:
    """Check whether the tenant can create another Project."""
    from apps.projects.models import Project
    count = Project.objects.count()
    return LimitCheck(
        allowed=count < tenant_settings.max_projects,
        current=count,
        limit=tenant_settings.max_projects,
        resource='projectos',
    )


def check_unit_limit(tenant_settings: TenantSettings) -> LimitCheck:
    """Check whether the tenant can create another Unit."""
    from apps.inventory.models import Unit
    count = Unit.objects.filter(is_deleted=False).count()
    return LimitCheck(
        allowed=count < tenant_settings.max_units,
        current=count,
        limit=tenant_settings.max_units,
        resource='unidades',
    )


def check_user_limit(tenant_settings: TenantSettings) -> LimitCheck:
    """Check whether the tenant can add another user (TenantMembership)."""
    from apps.memberships.models import TenantMembership
    count = TenantMembership.objects.filter(is_active=True).count()
    return LimitCheck(
        allowed=count < tenant_settings.max_users,
        current=count,
        limit=tenant_settings.max_users,
        resource='utilizadores',
    )
