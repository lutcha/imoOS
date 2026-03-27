---
name: tenant-task-wrapper
description: Decorator for automatic tenant context in ImoOS Celery tasks. Auto-load when creating tasks that need tenant isolation without boilerplate.
argument-hint: [task-name] [args]
allowed-tools: Read, Write
---

# Tenant Task Wrapper — ImoOS

## The @tenant_task Decorator
```python
# apps/core/celery_utils.py
from functools import wraps
from celery import shared_task
from django_tenants.utils import tenant_context
from apps.tenants.models import Client
import logging

logger = logging.getLogger('imos.tasks')

def tenant_task(*task_args, **task_kwargs):
    """
    Decorator that wraps a Celery task with automatic tenant context.
    The decorated task receives 'tenant_id' as first positional argument.

    Usage:
        @tenant_task(bind=True, max_retries=3)
        def my_task(self, tenant_id, other_arg):
            # tenant context is already active here
            Unit.objects.all()  # Auto-scoped!
    """
    def decorator(func):
        @shared_task(*task_args, **task_kwargs)
        @wraps(func)
        def wrapper(self_or_none, tenant_id, *args, **kwargs):
            try:
                tenant = Client.objects.get(id=tenant_id)
            except Client.DoesNotExist:
                logger.error(f'Tenant {tenant_id} not found — dropping task {func.__name__}')
                return

            with tenant_context(tenant):
                logger.info(f'Task {func.__name__} running for {tenant.schema_name}')
                if task_kwargs.get('bind'):
                    return func(self_or_none, tenant_id, *args, **kwargs)
                return func(tenant_id, *args, **kwargs)
        return wrapper
    return decorator
```

## Usage
```python
# apps/marketplace/tasks.py
from apps.core.celery_utils import tenant_task

@tenant_task(bind=True, max_retries=3, retry_backoff=True)
def sync_listing_to_imo_cv(self, tenant_id, unit_id):
    """Tenant context is automatically set — no boilerplate needed."""
    unit = Unit.objects.get(id=unit_id)  # Auto-scoped
    response = imo_cv_api.publish(unit)
    if not response.ok:
        raise self.retry(exc=Exception(response.text))
```

## Key Rules
- `tenant_id` must always be the first argument after `self` (if bind=True)
- The decorator handles `Client.DoesNotExist` gracefully — logs and drops task
- All retry logic still works as normal Celery retry
- Never use `@tenant_task` on tasks that intentionally cross tenant boundaries (use `celery-safe-pattern` instead)
