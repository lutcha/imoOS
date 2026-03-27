"""
Marketplace views — imo.cv integration.

Authenticated endpoints: MarketplaceListingViewSet
Public endpoint:         ImoCvWebhookView (HMAC-verified)
"""
import hashlib
import hmac as hmac_lib
import logging

from django.conf import settings
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsTenantMember

from .models import ImoCvWebhookLog, MarketplaceListing

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Serializer
# ---------------------------------------------------------------------------

class MarketplaceListingSerializer(serializers.ModelSerializer):
    unit_code = serializers.CharField(source='unit.code', read_only=True)
    project_name = serializers.CharField(
        source='unit.floor.building.project.name', read_only=True,
    )
    sync_error_display = serializers.SerializerMethodField()

    def get_sync_error_display(self, obj):
        return obj.sync_error or None

    class Meta:
        model = MarketplaceListing
        fields = [
            'id',
            'unit',
            'unit_code',
            'project_name',
            'imocv_listing_id',
            'status',
            'last_synced_at',
            'sync_error_display',
            'price_override_cve',
            'published_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'last_synced_at',
            'published_at',
            'created_at',
            'updated_at',
        ]


# ---------------------------------------------------------------------------
# HMAC verification helper
# ---------------------------------------------------------------------------

def verify_imocv_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Constant-time HMAC-SHA256 comparison against the X-ImoCv-Signature header.
    Returns False if signature is empty or secret is not configured.
    """
    if not signature or not secret:
        return False
    expected = hmac_lib.new(
        secret.encode(), payload, hashlib.sha256,
    ).hexdigest()
    return hmac_lib.compare_digest(f'sha256={expected}', signature)


# ---------------------------------------------------------------------------
# Authenticated ViewSet — tenant-scoped listings
# ---------------------------------------------------------------------------

class MarketplaceListingViewSet(viewsets.ModelViewSet):
    """
    CRUD + sync actions for MarketplaceListing.
    Requires authentication. All queries are automatically scoped to the
    active tenant schema by django-tenants middleware.
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = MarketplaceListingSerializer
    search_fields = ['unit__code', 'imocv_listing_id']
    ordering_fields = ['status', 'last_synced_at', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            MarketplaceListing.objects
            .select_related(
                'unit__floor__building__project',
                'unit__unit_type',
                'unit__pricing',
            )
            .order_by('-created_at')
        )

    @action(detail=True, methods=['post'], url_path='sync')
    def sync(self, request, pk=None):
        """Enqueue a manual sync for a single listing."""
        from django.db import connection
        from .tasks import sync_unit_listing

        listing = self.get_object()
        sync_unit_listing.delay(
            tenant_schema=connection.schema_name,
            unit_id=str(listing.unit_id),
        )
        return Response({'status': 'sync_queued', 'listing_id': str(listing.id)})

    @action(detail=False, methods=['post'], url_path='sync_all')
    def sync_all(self, request):
        """Enqueue a full sync for all PUBLISHED/PAUSED listings."""
        from django.db import connection
        from .tasks import sync_all_listings

        sync_all_listings.delay(tenant_schema=connection.schema_name)
        return Response({'status': 'sync_all_queued'})


# ---------------------------------------------------------------------------
# Public webhook endpoint — receives events from imo.cv
# ---------------------------------------------------------------------------

class ImoCvWebhookView(APIView):
    """
    POST /api/v1/marketplace/webhook/imocv/

    Receives inbound events from imo.cv (lead_captured, unit_viewed, etc.).
    Authentication: HMAC-SHA256 via X-ImoCv-Signature header.
    Always responds 200 immediately; processing is async via Celery.
    """
    permission_classes = [AllowAny]
    throttle_classes = []  # imo.cv is a trusted caller — don't rate-limit

    def post(self, request):
        # 1. Verify HMAC signature
        signature = request.META.get('HTTP_X_IMOCV_SIGNATURE', '')
        raw_body = request.body
        secret = getattr(settings, 'IMOCV_WEBHOOK_SECRET', '')

        if not verify_imocv_signature(raw_body, signature, secret):
            logger.warning(
                'ImoCvWebhookView: invalid signature from %s',
                request.META.get('REMOTE_ADDR'),
            )
            return Response(
                {'error': 'invalid_signature'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 2. Map raw event string to model choices
        payload = request.data  # already parsed by DRF
        event_type_raw = payload.get('event', '')
        event_map = {
            'lead_captured':   ImoCvWebhookLog.EVENT_LEAD_CAPTURED,
            'unit_viewed':     ImoCvWebhookLog.EVENT_UNIT_VIEWED,
            'listing_updated': ImoCvWebhookLog.EVENT_LISTING_UPDATED,
        }
        mapped_event = event_map.get(event_type_raw, ImoCvWebhookLog.EVENT_UNIT_VIEWED)

        # 3. Persist the raw webhook log
        from django.db import connection
        log = ImoCvWebhookLog.objects.create(
            event_type=mapped_event,
            imocv_listing_id=payload.get('listing_id', ''),
            payload=payload,
        )

        # 4. Enqueue async processing
        from .tasks import process_imocv_webhook
        process_imocv_webhook.delay(
            tenant_schema=connection.schema_name,
            webhook_log_id=str(log.id),
        )

        # 5. Always 200 — webhooks must receive an immediate acknowledgement
        return Response({'received': True, 'log_id': str(log.id)})
