import base64
import json
import logging

from django.db import connection
from django.http import Http404, JsonResponse
from django_tenants.middleware import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name, get_tenant_model
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def _schema_from_jwt(request) -> str | None:
    """
    Extract tenant_schema from a Bearer JWT without full signature validation.
    Used as a fallback when Host-based tenant resolution fails (e.g. local dev
    where the browser calls localhost:8001 instead of demo.localhost).
    """
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth_header.startswith("Bearer "):
        return None
    try:
        token = auth_header.split(" ", 1)[1]
        # JWT is three base64url segments; payload is the second
        payload_b64 = token.split(".")[1]
        # Pad to a multiple of 4
        rem = len(payload_b64) % 4
        if rem:
            payload_b64 += "=" * (4 - rem)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        schema = payload.get("tenant_schema")
        return schema if schema and schema != get_public_schema_name() else None
    except Exception:
        return None


_HEALTH_PATHS = frozenset([
    '/api/v1/health/',
    '/api/v1/health/detailed/',
])

# Auth paths that should always work on public schema
_AUTH_PATHS = frozenset([
    '/api/v1/users/auth/superadmin/token/',
    '/api/v1/users/auth/superadmin/token/refresh/',
])

# Setup paths for initial superuser creation (DigitalOcean deployment)
_SETUP_PATHS = frozenset([
    '/api/v1/setup/status/',
    '/api/v1/setup/superuser/',
])


class ImoOSTenantMiddleware(TenantMainMiddleware):
    """
    Tenant middleware with extra validation.

    Falls back to the JWT claim ``tenant_schema`` when Host-based resolution
    fails.  This lets direct API calls (e.g. from localhost in dev, or from
    the Next.js server via NEXT_PUBLIC_API_URL) work without needing an exact
    Host-to-domain match.

    Health check paths are bypassed entirely — they run on the public schema
    so load-balancer probes never fail due to missing tenant context.
    """

    def get_tenant(self, model, hostname):
        try:
            tenant = super().get_tenant(model, hostname)
            if not tenant.is_active:
                raise PermissionDenied("Tenant inativo")
            return tenant
        except model.DoesNotExist:
            raise Http404("Tenant não encontrado")

    def process_request(self, request):
        if request.path in _HEALTH_PATHS or request.path in _AUTH_PATHS or request.path in _SETUP_PATHS:
            # Set public schema — no tenant resolution needed for health probes
            # or superadmin auth (superadmin always operates on public schema)
            TenantModel = get_tenant_model()
            try:
                public_tenant = TenantModel.objects.get(schema_name=get_public_schema_name())
                request.tenant = public_tenant
                connection.set_tenant(public_tenant)
            except TenantModel.DoesNotExist:
                pass
            return None

        try:
            return super().process_request(request)
        except Http404:
            # Host-based lookup failed → try JWT fallback
            schema = _schema_from_jwt(request)
            if schema:
                TenantModel = get_tenant_model()
                try:
                    tenant = TenantModel.objects.get(schema_name=schema)
                    if not tenant.is_active:
                        return JsonResponse({"error": "Tenant inativo"}, status=403)
                    request.tenant = tenant
                    connection.set_tenant(tenant)
                    # Clear content-type cache (same as TenantMainMiddleware does)
                    from django.contrib.contenttypes.models import ContentType
                    ContentType.objects.clear_cache()
                    # Set urlconf for public schema if applicable
                    from django.conf import settings as _settings
                    if (
                        hasattr(_settings, "PUBLIC_SCHEMA_URLCONF")
                        and schema == get_public_schema_name()
                    ):
                        request.urlconf = _settings.PUBLIC_SCHEMA_URLCONF
                    logger.debug(
                        "ImoOSTenantMiddleware: JWT fallback resolved tenant=%s "
                        "for host=%s",
                        schema,
                        request.META.get("HTTP_HOST", ""),
                    )
                    return None  # continue processing
                except TenantModel.DoesNotExist:
                    pass
            return JsonResponse({"error": "Tenant não encontrado"}, status=404)
        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)

    def process_response(self, request, response):
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)
        if tenant is not None and user is not None and user.is_authenticated:
            response["X-Tenant-Name"] = tenant.name
            response["X-Tenant-Schema"] = tenant.schema_name
        return response
