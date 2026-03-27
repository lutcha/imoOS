---
name: celery-safe-pattern
description: Generate Celery tasks with proper tenant context, retry logic, and idempotency for ImoOS. Auto-load when writing any background task.
argument-hint: [task-name] [module]
allowed-tools: Read, Write, Grep
---

# Celery Safe Pattern — ImoOS

## The Three Laws of ImoOS Celery Tasks
1. **Pass IDs only** — never ORM objects (not serializable across workers)
2. **Re-fetch tenant inside task** — always use `tenant_context()`
3. **Implement retry** — all external calls must handle failures

## Standard Task Pattern

```python
# apps/<module>/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
from django_tenants.utils import tenant_context
from apps.tenants.models import Client

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,   # 1 min base delay
    acks_late=True,            # Only acknowledge after successful processing
    autoretry_for=(Exception,),
    retry_backoff=True,        # Exponential backoff: 60s, 120s, 240s
    retry_backoff_max=3600,    # Cap at 1 hour
    retry_jitter=True,         # Add randomness to avoid thundering herd
)
def process_<action>(self, tenant_id: str, object_id: str, **kwargs):
    """
    <Description of what this task does>.

    Args:
        tenant_id: UUID of the Client tenant (string, not UUID object)
        object_id: UUID of the target object (string)
    """
    logger.info(
        'Starting process_<action>',
        extra={'tenant_id': tenant_id, 'object_id': object_id}
    )

    try:
        tenant = Client.objects.get(id=tenant_id)
    except Client.DoesNotExist:
        logger.error(f'Tenant {tenant_id} not found — skipping task')
        return  # Don't retry — tenant was deleted

    with tenant_context(tenant):
        try:
            obj = <Model>.objects.get(id=object_id)
            # ... business logic ...
            logger.info(f'Completed process_<action> for {object_id}')
        except <Model>.DoesNotExist:
            logger.warning(f'<Model> {object_id} not found in {tenant_id}')
            return  # Object deleted — don't retry
        except Exception as exc:
            logger.error(f'Failed process_<action>: {exc}', exc_info=True)
            raise self.retry(exc=exc)
```

## Enqueueing Tasks (from views/services)
```python
# Correct: pass string IDs, not ORM objects
process_<action>.delay(
    tenant_id=str(request.tenant.id),
    object_id=str(obj.id),
)

# With priority (for time-sensitive tasks)
process_<action>.apply_async(
    args=[str(tenant.id), str(obj.id)],
    queue='high_priority',
    countdown=0,
)
```

## Celery Configuration
```python
# config/settings/base.py
CELERY_BROKER_URL = env('REDIS_URL')
CELERY_RESULT_BACKEND = env('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300       # 5 min hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 270  # 4.5 min soft limit (raises SoftTimeLimitExceeded)
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Prevent worker hoarding tasks
```

## Periodic Tasks (Celery Beat)
```python
# config/celery_beat.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'sync-all-listings-hourly': {
        'task': 'apps.marketplace.tasks.sync_all_active_listings',
        'schedule': crontab(minute=0),  # Every hour
    },
    'check-overdue-installments-daily': {
        'task': 'apps.payments.tasks.check_overdue_installments',
        'schedule': crontab(hour=8, minute=0),  # 08:00 CV time
    },
}
```
