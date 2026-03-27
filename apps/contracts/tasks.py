"""
Celery tasks for the Contracts app.

Rules (CLAUDE.md):
- Always receive tenant_schema as a string argument, never ORM objects
- Use tenant_context() to switch schema before any DB operations
- Celery tasks must be tenant-safe: fetch tenant from public schema first,
  then perform all business logic inside with tenant_context(tenant)
"""
import logging
import uuid
from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django_tenants.utils import get_tenant_model, tenant_context

logger = logging.getLogger(__name__)

_CVE_EUR_RATE = Decimal('110.265')  # Fixed peg CVE/EUR; future: read from TenantSettings


def _get_tenant(tenant_schema: str):
    TenantModel = get_tenant_model()
    return TenantModel.objects.get(schema_name=tenant_schema)


# ---------------------------------------------------------------------------
# Contract PDF generation (async, tenant-safe)
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True,
    name='contracts.generate_contract_pdf',
)
def generate_contract_pdf(self, tenant_schema: str, contract_id: str) -> dict:
    """
    Generate a PDF for a Contract and upload to S3.

    Args:
        tenant_schema: schema_name string — NEVER pass ORM objects across task boundaries.
        contract_id:   UUID string of the Contract to render.

    S3 key pattern: tenants/{tenant.slug}/contracts/{contract_id}/{uuid4()}.pdf

    After a successful upload the task writes the key back to
    contract.pdf_s3_key so the API can produce presigned GET URLs on demand.

    Returns:
        dict with 's3_key' and 'contract_id' on success,
        dict with 'error' key on non-retryable failure (missing object).

    Retry schedule (exponential backoff with jitter, capped at 1 hour):
        attempt 1 — ~60 s
        attempt 2 — ~120 s
        attempt 3 — ~240 s
    """
    # ------------------------------------------------------------------
    # 0. Validate WeasyPrint is available (fail fast, no retry needed)
    # ------------------------------------------------------------------
    try:
        from weasyprint import HTML
    except ImportError:
        logger.error('generate_contract_pdf: WeasyPrint not installed — aborting')
        return {'error': 'weasyprint_not_installed'}

    import boto3
    from django.template.loader import render_to_string

    # ------------------------------------------------------------------
    # 1. Fetch tenant from the PUBLIC schema
    # ------------------------------------------------------------------
    try:
        tenant = _get_tenant(tenant_schema)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            'generate_contract_pdf: tenant %s not found: %s',
            tenant_schema, exc,
        )
        # Non-retryable — tenant must exist before the task is dispatched.
        return {'error': 'tenant_not_found', 'tenant_schema': tenant_schema}

    # ------------------------------------------------------------------
    # 2. Switch to the tenant schema and build the rendering context
    # ------------------------------------------------------------------
    with tenant_context(tenant):
        from apps.contracts.models import Contract
        from apps.tenants.models import TenantSettings

        try:
            contract = (
                Contract.objects
                .select_related(
                    'unit__floor__building__project',
                    'unit__pricing',
                    'lead',
                    'vendor',
                    'reservation',
                )
                .prefetch_related('payments')
                .get(id=contract_id)
            )
        except Contract.DoesNotExist:
            logger.error(
                'generate_contract_pdf: Contract %s not found in tenant %s',
                contract_id, tenant_schema,
            )
            # Non-retryable — the object does not exist.
            return {'error': 'contract_not_found', 'contract_id': contract_id}

        # Branding — TenantSettings lives in the PUBLIC schema (OneToOne → Client).
        # We query it outside tenant_context but keep it here for clarity; the
        # get_tenant_model() result already uses the public schema connection.
        try:
            branding = TenantSettings.objects.get(tenant=tenant)
        except TenantSettings.DoesNotExist:
            branding = None  # Template handles missing branding gracefully.

        unit = contract.unit
        # Use the contract's agreed price as the authoritative figure;
        # unit.pricing.price_cve reflects list price which may differ post-negotiation.
        price_cve = contract.total_price_cve
        price_eur = (price_cve / _CVE_EUR_RATE).quantize(Decimal('0.01'))

        payments = list(contract.payments.order_by('due_date'))

        context = {
            'tenant_name': tenant.name,
            'branding': branding,
            'contract': contract,
            'unit': unit,
            'lead': contract.lead,
            'vendor': contract.vendor,
            'reservation': contract.reservation,
            'payments': payments,
            'price_cve': price_cve,
            'price_eur': price_eur,
        }

        html_string = render_to_string('contracts/contract.html', context)

    # ------------------------------------------------------------------
    # 3. Render PDF — outside tenant_context (no DB access needed)
    # ------------------------------------------------------------------
    try:
        pdf_bytes = HTML(string=html_string).write_pdf()
    except Exception as exc:
        logger.error(
            'generate_contract_pdf: WeasyPrint render failed (tenant=%s contract=%s): %s',
            tenant_schema, contract_id, exc,
        )
        raise self.retry(exc=exc)

    # ------------------------------------------------------------------
    # 4. Upload to S3 with per-tenant prefix
    # ------------------------------------------------------------------
    s3_key = f'tenants/{tenant.slug}/contracts/{contract_id}/{uuid.uuid4()}.pdf'
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None) or None,
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
        logger.error(
            'generate_contract_pdf: S3 upload failed (tenant=%s contract=%s key=%s): %s',
            tenant_schema, contract_id, s3_key, exc,
        )
        raise self.retry(exc=exc)

    # ------------------------------------------------------------------
    # 5. Persist the S3 key back onto the contract (re-enter tenant schema)
    # ------------------------------------------------------------------
    # NOTE: auto_now fields are NOT updated by QuerySet.update(); fetch the
    # instance and call save(update_fields=...) so updated_at is refreshed.
    with tenant_context(tenant):
        from apps.contracts.models import Contract as ContractModel  # noqa: PLC0415

        refreshed = ContractModel.objects.get(id=contract_id)
        refreshed.pdf_s3_key = s3_key
        refreshed.save(update_fields=['pdf_s3_key', 'updated_at'])

    logger.info(
        'generate_contract_pdf: done — tenant=%s contract=%s key=%s',
        tenant_schema, contract_id, s3_key,
    )
    return {'s3_key': s3_key, 'contract_id': contract_id}


# ---------------------------------------------------------------------------
# Contract Signature Finalization (async, tenant-safe)
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True,
    name='contracts.finalize_signed_contract',
)
def finalize_signed_contract(self, tenant_schema: str, signature_request_id: str):
    """
    Finalize a newly signed contract (triggered by public API webhook).
    """
    logger.info(
        'Starting finalize_signed_contract',
        extra={'tenant_schema': tenant_schema, 'signature_request_id': signature_request_id}
    )

    try:
        tenant = _get_tenant(tenant_schema)
    except Exception as exc:
        logger.error(f'Tenant {tenant_schema} not found — skipping task')
        return

    with tenant_context(tenant):
        from apps.contracts.models import SignatureRequest
        from apps.crm.services import convert_reservation
        from django.db import transaction

        try:
            sr = SignatureRequest.objects.select_related('contract').get(id=signature_request_id)
        except SignatureRequest.DoesNotExist:
            logger.warning(f'SignatureRequest {signature_request_id} not found')
            return

        contract = sr.contract

        # Activate contract if still DRAFT
        if contract.status == contract.STATUS_DRAFT:
            with transaction.atomic():
                if contract.reservation_id:
                    convert_reservation(str(contract.reservation_id), None)
                contract.status = contract.STATUS_ACTIVE
                contract.signed_at = sr.signed_at
                contract._change_reason = 'Activado por assinatura eletrónica'
                contract.save(update_fields=['status', 'signed_at', 'updated_at'])

                try:
                    from apps.crm.services import advance_lead_stage
                    advance_lead_stage(str(contract.lead_id), 'won', None)
                except Exception:
                    pass

    # Re-generate PDF via synchronous call to the task function logic
    pdf_result = generate_contract_pdf(tenant_schema, str(contract.id))
    
    if 'error' in pdf_result:
        logger.error('Failed to regenerate PDF for signed contract %s', contract.id)
        return

    s3_key = pdf_result['s3_key']

    # Generate presigned URL
    import boto3
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None) or None,
            region_name='us-east-1',
        )
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600 * 24 * 7  # 7 days
        )
    except Exception as exc:
        logger.error('Failed to generate presigned URL for %s: %s', s3_key, exc)
        return

    # Notify via WhatsApp
    send_signed_contract_whatsapp.delay(
        tenant_schema=tenant_schema,
        signature_request_id=signature_request_id,
        pdf_url=presigned_url,
    )


# ---------------------------------------------------------------------------
# WhatsApp Notification Mocks
# ---------------------------------------------------------------------------

@shared_task(
    bind=True, max_retries=3, default_retry_delay=60, acks_late=True, retry_backoff=True
)
def send_signature_request_whatsapp(self, tenant_schema: str, signature_request_id: str, sign_url: str):
    logger.info(
        "Sending signature request WhatsApp for task %s with URL %s in tenant %s",
        signature_request_id, sign_url, tenant_schema
    )
    # Implement real WhatsApp API call here.

@shared_task(
    bind=True, max_retries=3, default_retry_delay=60, acks_late=True, retry_backoff=True
)
def send_signed_contract_whatsapp(self, tenant_schema: str, signature_request_id: str, pdf_url: str):
    logger.info(
        "Sending signed contract WhatsApp for task %s with URL %s in tenant %s",
        signature_request_id, pdf_url, tenant_schema
    )
    # Implement real WhatsApp API call here.
