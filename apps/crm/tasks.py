"""
Celery tasks for the CRM app.

Rules (CLAUDE.md):
- Always receive tenant_schema as a string argument, never ORM objects
- Use tenant_context() to switch schema before any DB operations
"""
import logging
import uuid

import requests
from celery import shared_task
from django.conf import settings
from django_tenants.utils import get_tenant_model, tenant_context

logger = logging.getLogger(__name__)


def _get_tenant(tenant_schema: str):
    TenantModel = get_tenant_model()
    return TenantModel.objects.get(schema_name=tenant_schema)


# ---------------------------------------------------------------------------
# WhatsApp: unify sending with HSM templates
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    name='crm.send_whatsapp_template',
)
def send_whatsapp_template(
    self, *, tenant_schema: str, lead_id: str, template_name: str, variables: dict
) -> dict:
    """
    Unified task to send WhatsApp templates, respecting opt-outs and logging interactions.
    """
    if not getattr(settings, 'WHATSAPP_ENABLED', False):
        logger.debug('send_whatsapp_template: disabled')
        return {'skipped': True}

    from django.utils import timezone
    tenant = _get_tenant(tenant_schema)

    with tenant_context(tenant):
        from apps.crm.models import Lead, WhatsAppTemplate, WhatsAppMessage
        from apps.tenants.models import TenantSettings
        from apps.crm.whatsapp_client import WhatsAppCloudClient
        
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return {'error': 'lead_not_found'}

        # 1. Check opt-out
        if lead.whatsapp_opt_out:
            logger.info('send_whatsapp_template: skipped due to opt_out (lead=%s)', lead_id)
            WhatsAppMessage.objects.create(
                lead=lead, 
                phone=lead.phone or '',
                status=WhatsAppMessage.STATUS_FAILED, 
                error='opt_out'
            )
            return {'skipped': 'opt_out'}

        if not lead.phone:
            return {'error': 'no_phone'}
            
        # 2. Check Idempotency (prevent duplicate sends within 24h)
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        exists = WhatsAppMessage.objects.filter(
            lead=lead,
            template__name=template_name,
            status__in=[WhatsAppMessage.STATUS_SENT, WhatsAppMessage.STATUS_DELIVERED, WhatsAppMessage.STATUS_READ],
            sent_at__gte=cutoff
        ).exists()
        
        if exists:
            logger.info('send_whatsapp_template: skipped due to idempotency (lead=%s)', lead_id)
            return {'skipped': 'idempotent_duplicate'}

        # 3. Load Settings & Template
        settings_obj, _ = TenantSettings.objects.get_or_create(tenant=tenant)
        phone_id = settings_obj.whatsapp_phone_id
        if not phone_id:
            logger.warning('send_whatsapp_template: missing whatsapp_phone_id for tenant %s', tenant_schema)
            return {'error': 'missing_phone_id'}

        try:
            template = WhatsAppTemplate.objects.get(name=template_name, is_active=True)
        except WhatsAppTemplate.DoesNotExist:
            logger.warning('send_whatsapp_template: template %s not found or inactive', template_name)
            return {'error': 'template_not_found'}

        # 4. Build Components
        # Template Meta API expects ordered parameters
        parameters = []
        for key in sorted(variables.keys()):
            parameters.append({'type': 'text', 'text': str(variables[key])})
            
        components = [{'type': 'body', 'parameters': parameters}] if parameters else []
            
        # 5. Send Notification
        client = WhatsAppCloudClient(phone_id, getattr(settings_obj, 'whatsapp_access_token', None))
        try:
            resp = client.send_template(
                to=lead.phone,
                template_name=template.template_id_meta,
                language=template.language,
                components=components,
            )
            
            message_id = ''
            if 'messages' in resp and resp['messages']:
                message_id = resp['messages'][0].get('id', '')
                
            WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone=lead.phone,
                payload={'template': template.template_id_meta, 'variables': variables},
                status=WhatsAppMessage.STATUS_SENT,
                message_id_meta=message_id,
            )
            return {'sent': True, 'message_id': message_id}
            
        except requests.RequestException as exc:
            WhatsAppMessage.objects.create(
                lead=lead,
                template=template,
                phone=lead.phone,
                status=WhatsAppMessage.STATUS_FAILED,
                error=str(exc)
            )
            countdown = 30 * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)

# ---------------------------------------------------------------------------
# WhatsApp: new lead notification
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=5,
    name='crm.notify_whatsapp_new_lead',
)
def notify_whatsapp_new_lead(self, *, tenant_schema: str, lead_id: str) -> dict:
    """
    Send a WhatsApp message to the sales team when a new lead is captured.

    Triggered by LeadCaptureView.perform_create() after every successful save.
    Retries up to 5 times with exponential back-off on connection / HTTP errors.
    """
    tenant = _get_tenant(tenant_schema)
    with tenant_context(tenant):
        from apps.crm.models import Lead
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            logger.warning(
                'notify_whatsapp_new_lead: Lead %s not found in tenant %s',
                lead_id, tenant_schema,
            )
            return {'error': 'lead_not_found'}
            
    # Submeter via novo sistema de templates
    send_whatsapp_template.delay(
        tenant_schema=tenant_schema,
        lead_id=str(lead_id),
        template_name='novo_lead',
        variables={'1': lead.full_name, '2': dict(Lead.SOURCE_CHOICES).get(lead.source, lead.source)},
    )

    logger.info('notify_whatsapp_new_lead: queued via template for lead %s (tenant=%s)', lead_id, tenant_schema)
    return {'queued': True, 'lead_id': lead_id}





# ---------------------------------------------------------------------------
# Reservation: auto-expire (run every 15 minutes per tenant via Celery beat)
# ---------------------------------------------------------------------------

@shared_task(name='crm.expire_reservations')
def expire_reservations(*, tenant_schema: str) -> dict:
    """
    Expire all UnitReservations whose expires_at has passed and free the unit.

    Schedule: every 15 minutes per tenant via Celery beat.
    Idempotent — safe to call multiple times.
    """
    from django.utils import timezone

    tenant = _get_tenant(tenant_schema)
    expired_count = 0

    with tenant_context(tenant):
        from apps.crm.models import UnitReservation
        from apps.inventory.models import Unit

        expired_qs = UnitReservation.objects.filter(
            status=UnitReservation.STATUS_ACTIVE,
            expires_at__lt=timezone.now(),
        ).select_related('unit')

        for reservation in expired_qs:
            reservation.status = UnitReservation.STATUS_EXPIRED
            reservation._change_reason = 'Expirada automaticamente'
            reservation.save(update_fields=['status', 'updated_at'])

            unit = reservation.unit
            if unit.status == Unit.STATUS_RESERVED:
                unit.status = Unit.STATUS_AVAILABLE
                unit._change_reason = f'Reserva #{reservation.id} expirada'
                unit.save(update_fields=['status', 'updated_at'])

            expired_count += 1

    logger.info(
        'expire_reservations: %d reservations expired (tenant=%s)',
        expired_count, tenant_schema,
    )
    return {'expired': expired_count, 'tenant': tenant_schema}


# ---------------------------------------------------------------------------
# Visit reminders (run hourly per tenant via Celery beat)
# ---------------------------------------------------------------------------

@shared_task(name='crm.send_visit_reminders')
def send_visit_reminders(*, tenant_schema: str) -> dict:
    """
    Send WhatsApp reminders for leads with a visit_date in the next 24 hours.
    Uses a cache key for idempotency — task can run multiple times safely.
    """
    from datetime import timedelta
    from django.utils import timezone

    if not getattr(settings, 'WHATSAPP_ENABLED', False):
        return {'skipped': True}

    tenant = _get_tenant(tenant_schema)
    sent_count = 0

    with tenant_context(tenant):
        from apps.crm.models import Lead
        from django.core.cache import cache

        window_start = timezone.now() + timedelta(hours=23)
        window_end = timezone.now() + timedelta(hours=25)

        upcoming = Lead.objects.filter(
            stage=Lead.STAGE_VISIT_SCHEDULED,
            visit_date__range=(window_start, window_end),
        )

        for lead in upcoming:
            cache_key = f'{tenant_schema}:visit_reminder:{lead.id}'
            if cache.get(cache_key):
                continue   # already sent for this visit window

            try:
                # Disparar via template
                send_whatsapp_template.delay(
                    tenant_schema=tenant_schema,
                    lead_id=str(lead.id),
                    template_name='lembrete_visita',
                    variables={
                        '1': lead.first_name, 
                        '2': lead.visit_date.strftime("%H:%M")
                    }
                )
                cache.set(cache_key, True, timeout=86400)
                sent_count += 1
            except Exception as exc:
                logger.warning(
                    'send_visit_reminders: failed queueing for lead %s: %s', lead.id, exc,
                )

    return {'sent': sent_count, 'tenant': tenant_schema}


# ---------------------------------------------------------------------------
# Proposal PDF generation (async, tenant-safe)
# ---------------------------------------------------------------------------

_CVE_EUR_RATE = 110.265   # Fixed rate; future: fetch from TenantSettings or FX API


@shared_task(
    bind=True,
    max_retries=3,
    name='crm.generate_proposal_pdf',
)
def generate_proposal_pdf(self, *, tenant_schema: str, lead_id: str, unit_id: str) -> dict:
    """
    Generate a commercial proposal PDF with WeasyPrint and upload to S3.

    Key: tenants/{slug}/proposals/{lead_id}/{unit_id}/{uuid4}.pdf

    Returns the S3 object key. The frontend must request a presigned GET URL
    on demand — never store or expose pre-signed URLs long-term.
    """
    from decimal import Decimal

    try:
        from weasyprint import HTML
    except ImportError:
        logger.error('generate_proposal_pdf: WeasyPrint not installed')
        return {'error': 'weasyprint_not_installed'}

    import boto3
    from django.template.loader import render_to_string

    tenant = _get_tenant(tenant_schema)

    with tenant_context(tenant):
        from apps.crm.models import Lead
        from apps.inventory.models import Unit
        from apps.tenants.models import TenantSettings

        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            logger.error('generate_proposal_pdf: Lead %s not found in %s', lead_id, tenant_schema)
            return {'error': 'lead_not_found'}

        try:
            unit = Unit.objects.select_related(
                'unit_type', 'floor__building__project', 'pricing',
            ).get(id=unit_id)
        except Unit.DoesNotExist:
            logger.error('generate_proposal_pdf: Unit %s not found in %s', unit_id, tenant_schema)
            return {'error': 'unit_not_found'}

        branding, _ = TenantSettings.objects.get_or_create(tenant=tenant)
        price_cve = getattr(getattr(unit, 'pricing', None), 'price_cve', Decimal('0'))
        price_eur = (price_cve / Decimal(str(_CVE_EUR_RATE))).quantize(Decimal('0.01'))

        context = {
            'lead': lead,
            'unit': unit,
            'project': unit.floor.building.project,
            'price_cve': price_cve,
            'price_eur': price_eur,
            'branding': branding,
            'tenant_name': tenant.name,
        }
        html_string = render_to_string('crm/proposal.html', context)

    # Generate PDF (outside tenant_context — no DB needed)
    try:
        pdf_bytes = HTML(string=html_string).write_pdf()
    except Exception as exc:
        logger.error('generate_proposal_pdf: WeasyPrint failed: %s', exc)
        raise self.retry(exc=exc, countdown=60)

    # Upload to S3 with per-tenant prefix
    s3_key = f'tenants/{tenant.slug}/proposals/{lead_id}/{unit_id}/{uuid.uuid4()}.pdf'
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
            region_name='us-east-1',
        )
        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=s3_key,
            Body=pdf_bytes,
            ContentType='application/pdf',
            ServerSideEncryption='AES256',
        )
    except Exception as exc:
        logger.error('generate_proposal_pdf: S3 upload failed: %s', exc)
        raise self.retry(exc=exc, countdown=120)

    logger.info(
        'generate_proposal_pdf: done — tenant=%s lead=%s key=%s',
        tenant_schema, lead_id, s3_key,
    )
    return {'s3_key': s3_key, 'lead_id': lead_id, 'unit_id': unit_id}


# ---------------------------------------------------------------------------
# WhatsApp Webhook Processing (Global, Multi-tenant router)
# ---------------------------------------------------------------------------

@shared_task(name='crm.process_whatsapp_webhook')
def process_whatsapp_webhook(payload: dict) -> dict:
    """
    Process incoming Meta WhatsApp payloads asynchronously.
    Finds the correct tenant based on the message ID or phone number.
    Handles 'sent', 'delivered', 'read' status updates and 'STOP' opt-outs.
    """
    from django.utils import timezone
    from apps.crm.models import Lead, WhatsAppMessage
    from django_tenants.utils import schema_context
    from django.conf import settings

    if not payload.get('entry'):
        return {'status': 'ignored_no_entry'}

    processed = 0

    # Meta returns data batched inside entry -> changes -> value
    for entry in payload['entry']:
        for change in entry.get('changes', []):
            value = change.get('value', {})
            
            # 1. Handle Status updates (DELIVERED, READ, FAILED)
            if 'statuses' in value:
                for status_obj in value['statuses']:
                    wamid = status_obj.get('id')
                    status_text = status_obj.get('status', '').upper()
                    
                    if wamid and status_text:
                        # Find which tenant this WAMID belongs to
                        # Since WhatsAppMessage is isolated by tenant, we must query across schemas globally
                        # This is a slower query but necessary for incoming unbound webhooks
                        tenant_schemas = _get_all_tenant_schemas()
                        
                        for schema in tenant_schemas:
                            with schema_context(schema):
                                try:
                                    msg = WhatsAppMessage.objects.get(message_id_meta=wamid)
                                    msg.status = status_text
                                    
                                    if status_text == WhatsAppMessage.STATUS_DELIVERED:
                                        msg.delivered_at = timezone.now()
                                    elif status_text == WhatsAppMessage.STATUS_READ:
                                        msg.read_at = timezone.now()
                                    elif status_text == WhatsAppMessage.STATUS_FAILED:
                                        msg.error = str(status_obj.get('errors', 'unknown_error'))
                                        
                                    msg.save(update_fields=['status', 'delivered_at', 'read_at', 'error'])
                                    processed += 1
                                    break # Found it, stop searching schemas
                                except WhatsAppMessage.DoesNotExist:
                                    continue
                                    
            # 2. Handle incoming messages (Text - for Opt-outs)
            if 'messages' in value:
                for msg_obj in value['messages']:
                    if msg_obj.get('type') == 'text':
                        text_body = msg_obj.get('text', {}).get('body', '').strip().upper()
                        from_phone = msg_obj.get('from', '')
                        
                        if text_body in ['STOP', 'PARAR', 'CANCELAR'] and from_phone:
                            # Flag Opt-Out across all schemas just in case exact cross-tenant match
                            tenant_schemas = _get_all_tenant_schemas()
                            for schema in tenant_schemas:
                                with schema_context(schema):
                                    updated = Lead.objects.filter(phone=from_phone).update(
                                        whatsapp_opt_out=True,
                                        whatsapp_opt_out_at=timezone.now()
                                    )
                                    if updated > 0:
                                        processed += 1

    return {'processed_items': processed}

def _get_all_tenant_schemas():
    """Helper to list all valid tenant schemas for global webhook broadcast."""
    TenantModel = get_tenant_model()
    return list(TenantModel.objects.exclude(schema_name='public').values_list('schema_name', flat=True))
