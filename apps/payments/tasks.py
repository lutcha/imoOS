"""
Celery tasks for the payments module — ImoOS.

Three Laws:
1. Pass IDs / schema names only — never ORM objects.
2. Re-enter the tenant context inside the task.
3. Implement retry with exponential backoff for all external calls.
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache
from django_tenants.utils import schema_context

logger = get_task_logger(__name__)

WHATSAPP_ENABLED = getattr(settings, 'WHATSAPP_ENABLED', False)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True,
)
def send_payment_reminders(self, tenant_schema: str) -> dict:
    """
    Send payment reminders for upcoming instalments.

    Scans all PaymentPlanItems within the tenant schema that:
      - have a due_date in the next 7 days
      - are not yet linked to a paid contracts.Payment record

    For each item, sends a WhatsApp message to the lead associated with
    the contract (if WHATSAPP_ENABLED).

    Idempotency: skips items where the cache key
    ``{tenant_schema}:payment_reminder:{item_id}:{due_date}`` is already set,
    preventing duplicate messages within the same day.

    Args:
        tenant_schema: schema_name of the Client tenant (e.g. 'empresa_a').
    """
    from datetime import date, timedelta

    logger.info('send_payment_reminders started', extra={'tenant_schema': tenant_schema})

    sent = 0
    skipped = 0
    errors = 0

    with schema_context(tenant_schema):
        from apps.payments.models import PaymentPlanItem

        today = date.today()
        window_end = today + timedelta(days=7)

        items = (
            PaymentPlanItem.objects
            .filter(
                due_date__gte=today,
                due_date__lte=window_end,
                payment__isnull=True,  # Not yet paid
            )
            .select_related(
                'plan__contract__lead',
            )
        )

        for item in items:
            cache_key = f'{tenant_schema}:payment_reminder:{item.id}:{item.due_date}'

            if cache.get(cache_key):
                skipped += 1
                continue

            lead = item.plan.contract.lead
            try:
                if WHATSAPP_ENABLED:
                    _send_whatsapp_reminder(lead=lead, item=item)

                # Mark as sent for today — TTL = 24 hours
                cache.set(cache_key, '1', timeout=86400)
                sent += 1

            except Exception as exc:
                errors += 1
                logger.error(
                    'Failed to send reminder for item %s: %s',
                    item.id,
                    exc,
                    exc_info=True,
                )

    logger.info(
        'send_payment_reminders completed',
        extra={'tenant_schema': tenant_schema, 'sent': sent, 'skipped': skipped, 'errors': errors},
    )
    return {'sent': sent, 'skipped': skipped, 'errors': errors}


def _send_whatsapp_reminder(lead, item) -> None:
    """
    Send a WhatsApp reminder message to the lead.

    Stub: Replace with real WhatsApp Business API integration.
    Typical providers for Cabo Verde: Twilio, 360dialog.

    Raises on failure so the caller can increment the error counter
    (task-level retry handles retries globally).
    """
    phone = lead.phone
    if not phone:
        logger.warning('Lead %s has no phone — skipping WhatsApp', lead.id)
        return

    message = (
        f'Olá {lead.first_name},\n'
        f'Lembrete: tem um pagamento de {item.amount_cve} CVE previsto para '
        f'{item.due_date.strftime("%d/%m/%Y")}.\n'
        f'Referência MBE: {item.mbe_reference or "N/D"}.\n'
        f'Obrigado — ImoOS'
    )

    logger.info(
        'WhatsApp reminder queued for lead %s (%s): %s',
        lead.id,
        phone,
        message[:80],
    )
    # TODO: integrate with WhatsApp Business API
    # client.messages.create(to=f'whatsapp:{phone}', body=message, from_='whatsapp:+...')
