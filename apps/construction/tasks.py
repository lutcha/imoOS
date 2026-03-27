"""
Celery tasks for the construction app.

Rules (CLAUDE.md):
- Always receive tenant_schema as a string argument, never ORM objects
- Use tenant_context() to switch schema before any DB operations
- Tasks must be idempotent: safe to re-run on the same data
- S3 client is instantiated inside the task to avoid stale credentials
"""
import io
import logging

import boto3
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django_tenants.utils import get_tenant_model, tenant_context

logger = get_task_logger(__name__)


def _get_tenant(tenant_schema: str):
    TenantModel = get_tenant_model()
    return TenantModel.objects.get(schema_name=tenant_schema)


def _make_s3_client():
    """
    Build a boto3 S3 client from Django settings.

    Created inside the task (never at module level) so that credentials
    loaded from environment variables are always fresh.
    """
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None),
        region_name='us-east-1',
    )


@shared_task(
    bind=True,
    max_retries=3,
    name='construction.process_construction_photo',
)
def process_construction_photo(
    self,
    *,
    tenant_schema: str,
    photo_id: str,
) -> dict:
    """
    Download the original photo from S3, generate an 800x600 JPEG thumbnail,
    upload it back to S3, and persist the thumbnail S3 key on the
    ConstructionPhoto record.

    Arguments:
        tenant_schema: schema_name of the target tenant (string, not ORM object)
        photo_id:      UUID string of the ConstructionPhoto record

    Returns one of:
        {'processed': True, 'photo_id': str, 'thumb_key': str}
        {'skipped': 'not_found'}
        {'skipped': 'already_processed'}
        {'error': 'pillow_not_installed'}

    Retry policy: exponential back-off — 1 min, 2 min, 4 min — on any
    boto3 or Pillow error.
    """
    # ------------------------------------------------------------------
    # Guard: Pillow must be installed
    # ------------------------------------------------------------------
    try:
        from PIL import Image
    except ImportError:
        logger.error(
            'process_construction_photo: Pillow is not installed. '
            'Add Pillow to requirements/base.txt.'
        )
        return {'error': 'pillow_not_installed'}

    # ------------------------------------------------------------------
    # 1. Resolve tenant from the PUBLIC schema (no tenant_context needed)
    # ------------------------------------------------------------------
    try:
        tenant = _get_tenant(tenant_schema)
    except Exception as exc:
        logger.error(
            'process_construction_photo: tenant %s not found: %s',
            tenant_schema,
            exc,
        )
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)

    # ------------------------------------------------------------------
    # 2. All business logic runs inside the tenant schema
    # ------------------------------------------------------------------
    with tenant_context(tenant):
        from apps.construction.models import ConstructionPhoto

        # 2a. Fetch the photo record
        try:
            photo = ConstructionPhoto.objects.get(id=photo_id)
        except ConstructionPhoto.DoesNotExist:
            logger.warning(
                'process_construction_photo: photo %s not found in tenant %s',
                photo_id,
                tenant_schema,
            )
            return {'skipped': 'not_found'}

        # 2b. Idempotency check — thumbnail already generated
        if photo.thumbnail_s3_key:
            logger.info(
                'process_construction_photo: photo %s already processed (thumb_key=%s), skipping',
                photo_id,
                photo.thumbnail_s3_key,
            )
            return {'skipped': 'already_processed'}

        try:
            s3 = _make_s3_client()

            # 2c. Download original from S3
            logger.info(
                'process_construction_photo: downloading s3://%s/%s for photo %s',
                settings.AWS_STORAGE_BUCKET_NAME,
                photo.s3_key,
                photo_id,
            )
            response = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=photo.s3_key,
            )
            original_bytes = response['Body'].read()

            # 2d. Generate thumbnail with Pillow (800x600, JPEG, quality=85)
            img = Image.open(io.BytesIO(original_bytes))
            img.thumbnail((800, 600), Image.LANCZOS)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            thumb_buffer = io.BytesIO()
            img.save(thumb_buffer, format='JPEG', quality=85, optimize=True)
            thumb_bytes = thumb_buffer.getvalue()

            # 2e. Upload thumbnail to S3
            thumb_key = f'{photo.s3_key}_thumb.jpg'
            logger.info(
                'process_construction_photo: uploading thumbnail to s3://%s/%s',
                settings.AWS_STORAGE_BUCKET_NAME,
                thumb_key,
            )
            s3.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=thumb_key,
                Body=thumb_bytes,
                ContentType='image/jpeg',
                ServerSideEncryption='AES256',
            )

            # 2f. Persist the thumbnail key — only the single field is updated
            #     to keep the write narrow and avoid race conditions.
            photo.thumbnail_s3_key = thumb_key
            photo.save(update_fields=['thumbnail_s3_key'])

        except Exception as exc:
            countdown = 60 * (2 ** self.request.retries)
            logger.error(
                'process_construction_photo: error processing photo %s in tenant %s '
                '(attempt %d/%d, retrying in %ds): %s',
                photo_id,
                tenant_schema,
                self.request.retries + 1,
                self.max_retries + 1,
                countdown,
                exc,
                exc_info=True,
            )
            raise self.retry(exc=exc, countdown=countdown)

    logger.info(
        'process_construction_photo: tenant=%s photo_id=%s thumb_key=%s',
        tenant_schema,
        photo_id,
        thumb_key,
    )
    return {
        'processed': True,
        'photo_id': photo_id,
        'thumb_key': thumb_key,
    }
