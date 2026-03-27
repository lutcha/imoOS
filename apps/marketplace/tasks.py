"""Celery tasks for marketplace/imo.cv synchronisation."""
import logging

from celery import shared_task
from django.utils import timezone
from django_tenants.utils import get_tenant_model, tenant_context

logger = logging.getLogger(__name__)


def _get_tenant(tenant_schema: str):
    TenantModel = get_tenant_model()
    return TenantModel.objects.get(schema_name=tenant_schema)


# ---------------------------------------------------------------------------
# Task 1: sync_unit_listing
# Idempotent — publish, update availability, or remove a single unit listing.
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True,
    name='marketplace.sync_unit_listing',
)
def sync_unit_listing(self, *, tenant_schema: str, unit_id: str) -> dict:
    """
    Sync a single unit's MarketplaceListing with imo.cv.
    Idempotent — safe to call multiple times.

    Logic:
    - If unit.status == SOLD and listing exists → remove from imo.cv, set REMOVED
    - If listing.status == PENDING_SYNC → publish to imo.cv, set PUBLISHED
    - If listing.status in PUBLISHED/PAUSED → update_availability based on unit status
    """
    tenant = _get_tenant(tenant_schema)

    with tenant_context(tenant):
        from apps.inventory.models import Unit
        from apps.marketplace.imocv_client import ImoCvClient
        from apps.marketplace.models import MarketplaceListing
        from apps.tenants.models import TenantSettings

        # 1. Fetch tenant settings
        try:
            tenant_settings = TenantSettings.objects.get(tenant=tenant)
        except TenantSettings.DoesNotExist:
            logger.info(
                'sync_unit_listing: no TenantSettings for tenant=%s — skipping',
                tenant_schema,
            )
            return {'skipped': 'no_settings'}

        # 2. Check integration is enabled
        if not getattr(tenant_settings, 'imocv_enabled', False):
            logger.debug(
                'sync_unit_listing: imo.cv disabled for tenant=%s — skipping',
                tenant_schema,
            )
            return {'skipped': 'disabled'}

        # 3. Validate API key
        api_key = (getattr(tenant_settings, 'imo_cv_api_key', '') or '').strip()
        if not api_key:
            logger.warning(
                'sync_unit_listing: no imo_cv_api_key for tenant=%s — skipping',
                tenant_schema,
            )
            return {'skipped': 'no_api_key'}

        # 4. Fetch unit — do not retry on DoesNotExist (object may have been deleted)
        try:
            unit = Unit.objects.select_related(
                'floor__building__project', 'unit_type', 'pricing',
            ).get(id=unit_id)
        except Unit.DoesNotExist:
            logger.warning(
                'sync_unit_listing: Unit %s not found in tenant=%s — aborting',
                unit_id, tenant_schema,
            )
            return {'skipped': 'unit_not_found'}

        # 5. Get or create the MarketplaceListing for this unit
        listing, created = MarketplaceListing.objects.get_or_create(unit=unit)
        if created:
            logger.info(
                'sync_unit_listing: created new MarketplaceListing for unit=%s tenant=%s',
                unit_id, tenant_schema,
            )

        client = ImoCvClient(api_key=api_key)

        try:
            # 6. Handle SOLD units — remove from imo.cv
            if unit.status == Unit.STATUS_SOLD:
                if listing.imocv_listing_id:
                    client.remove_listing(listing.imocv_listing_id)
                    logger.info(
                        'sync_unit_listing: removed listing %s (unit=%s SOLD) tenant=%s',
                        listing.imocv_listing_id, unit_id, tenant_schema,
                    )
                listing.status = MarketplaceListing.STATUS_REMOVED
                listing.sync_error = ''
                listing.last_synced_at = timezone.now()
                listing.save(update_fields=['status', 'sync_error', 'last_synced_at', 'updated_at'])
                return {'action': 'removed', 'unit_id': unit_id}

            # 7. Handle PENDING_SYNC — publish for the first time
            if listing.status == MarketplaceListing.STATUS_PENDING:
                result = client.publish_unit(unit, listing.effective_price_cve)
                listing.imocv_listing_id = result['listing_id']
                listing.status = MarketplaceListing.STATUS_PUBLISHED
                listing.published_at = timezone.now()
                listing.sync_error = ''
                listing.last_synced_at = timezone.now()
                listing.save(update_fields=[
                    'imocv_listing_id', 'status', 'published_at',
                    'sync_error', 'last_synced_at', 'updated_at',
                ])
                logger.info(
                    'sync_unit_listing: published unit=%s as listing=%s tenant=%s',
                    unit_id, listing.imocv_listing_id, tenant_schema,
                )
                return {'action': 'published', 'imocv_listing_id': listing.imocv_listing_id}

            # 8. Handle PUBLISHED/PAUSED — update availability
            if listing.status in (
                MarketplaceListing.STATUS_PUBLISHED,
                MarketplaceListing.STATUS_PAUSED,
            ):
                available = unit.status == Unit.STATUS_AVAILABLE
                client.update_availability(listing.imocv_listing_id, available)
                listing.sync_error = ''
                listing.last_synced_at = timezone.now()
                listing.save(update_fields=['sync_error', 'last_synced_at', 'updated_at'])
                logger.info(
                    'sync_unit_listing: updated availability=%s for listing=%s unit=%s tenant=%s',
                    available, listing.imocv_listing_id, unit_id, tenant_schema,
                )
                return {
                    'action': 'availability_updated',
                    'available': available,
                    'imocv_listing_id': listing.imocv_listing_id,
                }

        except Exception as exc:
            logger.warning(
                'sync_unit_listing: client error for unit=%s tenant=%s (attempt=%d): %s',
                unit_id, tenant_schema, self.request.retries + 1, exc,
            )
            listing.sync_error = str(exc)
            listing.save(update_fields=['sync_error', 'updated_at'])
            raise  # autoretry_for=(Exception,) with retry_backoff handles the retry

        # Listing is in a terminal/unexpected status — skip silently
        logger.debug(
            'sync_unit_listing: no action for listing status=%s unit=%s tenant=%s',
            listing.status, unit_id, tenant_schema,
        )
        return {'skipped': 'no_action', 'listing_status': listing.status}


# ---------------------------------------------------------------------------
# Task 2: sync_all_listings
# Hourly fan-out — enqueues individual sync tasks for all active listings.
# ---------------------------------------------------------------------------

@shared_task(
    name='marketplace.sync_all_listings',
    bind=True,
    max_retries=1,
)
def sync_all_listings(self, *, tenant_schema: str) -> dict:
    """
    Hourly: iterate all PUBLISHED/PAUSED listings and re-sync availability.
    Enqueues individual sync_unit_listing tasks for parallelism.
    Does NOT perform the sync itself — just enqueues.
    """
    tenant = _get_tenant(tenant_schema)

    with tenant_context(tenant):
        from apps.marketplace.models import MarketplaceListing
        from apps.tenants.models import TenantSettings

        try:
            tenant_settings = TenantSettings.objects.get(tenant=tenant)
        except TenantSettings.DoesNotExist:
            logger.info(
                'sync_all_listings: no TenantSettings for tenant=%s — skipping',
                tenant_schema,
            )
            return {'skipped': 'no_settings'}

        if not getattr(tenant_settings, 'imocv_enabled', False):
            logger.debug(
                'sync_all_listings: imo.cv disabled for tenant=%s — skipping',
                tenant_schema,
            )
            return {'skipped': 'disabled'}

        # Materialise before leaving tenant_context — avoids holding schema connection
        # open during potentially slow broker round-trips
        unit_ids = list(
            MarketplaceListing.objects.filter(
                status__in=[
                    MarketplaceListing.STATUS_PUBLISHED,
                    MarketplaceListing.STATUS_PAUSED,
                ]
            ).values_list('unit_id', flat=True)
        )

    count = 0
    for unit_id in unit_ids:
        sync_unit_listing.delay(tenant_schema=tenant_schema, unit_id=str(unit_id))
        count += 1

    logger.info(
        'sync_all_listings: queued %d sync tasks for tenant=%s',
        count, tenant_schema,
    )
    return {'queued': count, 'tenant': tenant_schema}


# ---------------------------------------------------------------------------
# Task 3: process_imocv_webhook
# Process a stored ImoCvWebhookLog entry.
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name='marketplace.process_imocv_webhook',
)
def process_imocv_webhook(self, *, tenant_schema: str, webhook_log_id: str) -> dict:
    """
    Process a stored ImoCvWebhookLog.

    Events:
    - 'lead_captured': create Lead with source='IMOCV' and notify via WhatsApp
    - 'unit_viewed': log only
    - 'listing_updated': log only (imo.cv→ImoOS direction is for leads only)
    """
    tenant = _get_tenant(tenant_schema)

    with tenant_context(tenant):
        from apps.crm.models import Lead
        from apps.crm.tasks import notify_whatsapp_new_lead
        from apps.marketplace.models import ImoCvWebhookLog, MarketplaceListing

        # 1. Fetch the webhook log — do not retry on DoesNotExist
        try:
            log = ImoCvWebhookLog.objects.get(id=webhook_log_id)
        except ImoCvWebhookLog.DoesNotExist:
            logger.warning(
                'process_imocv_webhook: ImoCvWebhookLog %s not found in tenant=%s — aborting',
                webhook_log_id, tenant_schema,
            )
            return {'skipped': 'log_not_found'}

        # 2. Idempotency — already processed
        if log.processed_at is not None:
            logger.debug(
                'process_imocv_webhook: log %s already processed at %s — skipping',
                webhook_log_id, log.processed_at,
            )
            return {'skipped': 'already_processed'}

        payload = log.payload or {}

        try:
            if log.event_type == ImoCvWebhookLog.EVENT_LEAD_CAPTURED:
                lead_data = payload.get('lead', {})
                lead = Lead(
                    first_name=lead_data.get('first_name', ''),
                    last_name=lead_data.get('last_name', ''),
                    email=lead_data.get('email', ''),
                    phone=lead_data.get('phone', ''),
                    source=Lead.SOURCE_IMOCV,
                    status=Lead.STATUS_NEW,
                    stage=Lead.STAGE_NEW,
                )

                # Optionally link to the unit the lead viewed
                listing_id = payload.get('listing_id')
                if listing_id:
                    try:
                        linked_listing = MarketplaceListing.objects.get(
                            imocv_listing_id=listing_id,
                        )
                        lead.interested_unit = linked_listing.unit
                    except MarketplaceListing.DoesNotExist:
                        logger.debug(
                            'process_imocv_webhook: no listing for imocv_listing_id=%s',
                            listing_id,
                        )

                lead.save()
                logger.info(
                    'process_imocv_webhook: created Lead %s from imo.cv (tenant=%s)',
                    lead.id, tenant_schema,
                )

                notify_whatsapp_new_lead.delay(
                    tenant_schema=tenant_schema,
                    lead_id=str(lead.id),
                )

            elif log.event_type == ImoCvWebhookLog.EVENT_UNIT_VIEWED:
                logger.debug(
                    'process_imocv_webhook: unit_viewed for listing=%s tenant=%s',
                    log.imocv_listing_id, tenant_schema,
                )

            elif log.event_type == ImoCvWebhookLog.EVENT_LISTING_UPDATED:
                logger.info(
                    'process_imocv_webhook: listing_updated for listing=%s tenant=%s — no action',
                    log.imocv_listing_id, tenant_schema,
                )

            else:
                logger.warning(
                    'process_imocv_webhook: unknown event_type=%r log=%s tenant=%s',
                    log.event_type, webhook_log_id, tenant_schema,
                )

            # Mark as processed
            log.processed_at = timezone.now()
            log.save(update_fields=['processed_at'])

        except Exception as exc:
            logger.warning(
                'process_imocv_webhook: error for log=%s tenant=%s (attempt=%d): %s',
                webhook_log_id, tenant_schema, self.request.retries + 1, exc,
            )
            log.error = str(exc)
            log.save(update_fields=['error'])
            raise self.retry(exc=exc)

    return {
        'processed': True,
        'webhook_log_id': webhook_log_id,
        'event_type': log.event_type,
    }
