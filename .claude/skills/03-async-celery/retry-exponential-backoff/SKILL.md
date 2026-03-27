---
name: retry-exponential-backoff
description: Exponential backoff retry pattern for ImoOS Celery tasks — for imo.cv API calls, WhatsApp, and bank integrations. Auto-load when writing tasks that call external services.
argument-hint: [max-retries] [service-name]
allowed-tools: Read, Write
---

# Exponential Backoff Retry — ImoOS

## Standard Retry Configuration
```python
@shared_task(
    bind=True,
    max_retries=5,
    autoretry_for=(requests.exceptions.RequestException, ConnectionError),
    retry_backoff=True,       # Exponential: 1s, 2s, 4s, 8s, 16s
    retry_backoff_max=3600,   # Cap at 1 hour
    retry_jitter=True,        # Randomize to avoid thundering herd
)
def sync_to_imo_cv(self, tenant_id, unit_id):
    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        unit = Unit.objects.get(id=unit_id)
        try:
            response = imo_cv_client.publish_unit(unit)
            response.raise_for_status()
            MarketplaceSyncLog.objects.create(
                unit=unit, channel='imo_cv', status='SUCCESS'
            )
        except requests.HTTPError as exc:
            if exc.response.status_code == 429:  # Rate limited
                retry_after = int(exc.response.headers.get('Retry-After', 60))
                raise self.retry(exc=exc, countdown=retry_after)
            elif exc.response.status_code >= 500:
                raise self.retry(exc=exc)  # Server error — backoff and retry
            else:
                # 4xx client error — don't retry, log and alert
                MarketplaceSyncLog.objects.create(
                    unit=unit, channel='imo_cv', status='FAILED',
                    error_message=str(exc)
                )
```

## Dead Letter Queue (After Max Retries)
```python
def sync_to_imo_cv_dlq(self, tenant_id, unit_id, error):
    """Called when all retries exhausted."""
    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        MarketplaceError.objects.create(
            unit_id=unit_id,
            error_message=error,
            requires_manual_action=True,
        )
        # Notify tenant admin
        send_admin_alert.delay(tenant_id, f'Sync failed for unit {unit_id} after 5 retries')
```

## Retry Schedule Reference
| Attempt | Delay (base 60s) |
|---------|-----------------|
| 1st retry | ~60s |
| 2nd retry | ~120s |
| 3rd retry | ~240s (4 min) |
| 4th retry | ~480s (8 min) |
| 5th retry | ~960s (16 min) |
| Max cap | 3600s (1 hour) |

## Key Rules
- 4xx errors (400, 401, 403) should NOT be retried — they indicate a code/data issue
- 5xx and network errors SHOULD be retried with backoff
- 429 Rate Limited: respect the Retry-After header
- After max retries, create a `MarketplaceError` record and notify admin
