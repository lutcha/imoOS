"""
Platform-level imo.cv webhook view (public schema).

imo.cv sends a single webhook URL (not per-tenant). This view receives the
event, verifies the HMAC signature, then routes processing to the correct
tenant's Celery task using the imocv_listing_id to resolve the tenant schema.
"""
import hashlib
import hmac as hmac_lib
import logging

from django.conf import settings
from django_tenants.utils import get_tenant_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .views import verify_imocv_signature

logger = logging.getLogger(__name__)


def _resolve_tenant_schema(imocv_listing_id: str) -> str | None:
    """
    Find which tenant owns the given imocv_listing_id.
    Queries each tenant schema looking for a MarketplaceListing match.
    Returns the schema_name, or None if not found.
    """
    from django_tenants.utils import tenant_context

    TenantModel = get_tenant_model()
    # Skip public/shared schemas
    tenants = TenantModel.objects.exclude(schema_name='public')

    for tenant in tenants:
        with tenant_context(tenant):
            from apps.marketplace.models import MarketplaceListing
            if MarketplaceListing.objects.filter(
                imocv_listing_id=imocv_listing_id
            ).exists():
                return tenant.schema_name

    return None


class ImoCvPlatformWebhookView(APIView):
    """
    POST /api/v1/marketplace/webhook/imocv/  (public schema — platform domain)

    Single entry point for all imo.cv webhooks regardless of tenant.
    Resolves the target tenant from the listing_id, then enqueues async
    processing in the correct tenant schema via Celery.

    Authentication: HMAC-SHA256 via X-ImoCv-Signature header.
    Always responds 200 immediately.
    """
    permission_classes = [AllowAny]
    throttle_classes = []

    def post(self, request):
        # 1. Verify HMAC signature
        signature = request.META.get('HTTP_X_IMOCV_SIGNATURE', '')
        raw_body = request.body
        secret = getattr(settings, 'IMOCV_WEBHOOK_SECRET', '')

        if not verify_imocv_signature(raw_body, signature, secret):
            logger.warning(
                'ImoCvPlatformWebhookView: invalid signature from %s',
                request.META.get('REMOTE_ADDR'),
            )
            return Response(
                {'error': 'invalid_signature'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        payload = request.data
        listing_id = payload.get('listing_id', '')
        event_type_raw = payload.get('event', '')

        # 2. Resolve tenant from listing_id
        if not listing_id:
            logger.warning('ImoCvPlatformWebhookView: no listing_id in payload')
            return Response({'received': True, 'note': 'no_listing_id'})

        tenant_schema = _resolve_tenant_schema(listing_id)

        if not tenant_schema:
            logger.warning(
                'ImoCvPlatformWebhookView: no tenant found for listing_id=%s',
                listing_id,
            )
            # Still return 200 — don't expose tenant info to imo.cv
            return Response({'received': True})

        # 3. Store webhook log and enqueue in tenant context
        from django_tenants.utils import tenant_context, get_tenant_model
        TenantModel = get_tenant_model()
        tenant = TenantModel.objects.get(schema_name=tenant_schema)

        with tenant_context(tenant):
            from apps.marketplace.models import ImoCvWebhookLog
            event_map = {
                'lead_captured':   ImoCvWebhookLog.EVENT_LEAD_CAPTURED,
                'unit_viewed':     ImoCvWebhookLog.EVENT_UNIT_VIEWED,
                'listing_updated': ImoCvWebhookLog.EVENT_LISTING_UPDATED,
            }
            mapped_event = event_map.get(event_type_raw, ImoCvWebhookLog.EVENT_UNIT_VIEWED)

            log = ImoCvWebhookLog.objects.create(
                event_type=mapped_event,
                imocv_listing_id=listing_id,
                payload=payload,
            )

        from apps.marketplace.tasks import process_imocv_webhook
        process_imocv_webhook.delay(
            tenant_schema=tenant_schema,
            webhook_log_id=str(log.id),
        )

        logger.info(
            'ImoCvPlatformWebhookView: queued %s for tenant=%s listing=%s',
            event_type_raw, tenant_schema, listing_id,
        )
        return Response({'received': True, 'log_id': str(log.id)})
