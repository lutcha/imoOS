---
name: celery-beat-scheduling
description: Configure Celery Beat periodic tasks for ImoOS — iterate all tenants, crontab schedules, Atlantic/Cape_Verde timezone. Auto-load when adding scheduled/recurring tasks.
argument-hint: [schedule] [task-name]
allowed-tools: Read, Write
---

# Celery Beat Scheduling — ImoOS

## Beat Schedule Configuration
```python
# config/celery_beat.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Hourly: sync all active listings to imo.cv
    'sync-listings-hourly': {
        'task': 'apps.marketplace.tasks.sync_all_active_listings',
        'schedule': crontab(minute=0),  # Every hour at :00
    },
    # Daily 08:00 CV time: check overdue installments and send reminders
    'check-overdue-installments': {
        'task': 'apps.payments.tasks.check_overdue_installments',
        'schedule': crontab(hour=8, minute=0),  # Atlantic/Cape_Verde
    },
    # Daily 07:00: expire stale reservations (>48h without confirmation)
    'expire-stale-reservations': {
        'task': 'apps.crm.tasks.expire_stale_reservations',
        'schedule': crontab(hour=7, minute=0),
    },
    # Weekly Monday 09:00: generate investor reports
    'generate-investor-reports': {
        'task': 'apps.investors.tasks.generate_weekly_reports',
        'schedule': crontab(day_of_week='monday', hour=9, minute=0),
    },
}

# settings/base.py
CELERY_TIMEZONE = 'Atlantic/Cape_Verde'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

## Task That Iterates All Tenants
```python
# apps/marketplace/tasks.py
@shared_task
def sync_all_active_listings():
    """Beat task: dispatches per-tenant sync tasks."""
    from apps.tenants.models import Client
    tenants = Client.objects.filter(is_active=True)
    for tenant in tenants:
        # Dispatch individual tenant tasks — don't process inline
        sync_tenant_listings.delay(str(tenant.id))

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def sync_tenant_listings(self, tenant_id):
    """Actual per-tenant sync work."""
    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        # ... sync logic
        pass
```

## Key Rules
- Beat tasks should only DISPATCH per-tenant tasks — never process inline (fan-out pattern)
- Always use `CELERY_TIMEZONE = 'Atlantic/Cape_Verde'` — all schedules are in CV time
- Use `DatabaseScheduler` so admins can adjust schedules without redeploy
- Test beat tasks by calling the task directly in tests (CELERY_TASK_ALWAYS_EAGER=True)
