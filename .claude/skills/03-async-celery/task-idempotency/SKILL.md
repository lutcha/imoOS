---
name: task-idempotency
description: Make ImoOS Celery tasks safe to retry without duplicate side effects. Auto-load when writing tasks that send notifications, create records, or call external APIs.
argument-hint: [task-name] [idempotency-strategy]
allowed-tools: Read, Write
---

# Task Idempotency — ImoOS

## Strategy 1: Database Lock (for record creation)
```python
from django.db import transaction

@shared_task(bind=True)
def create_installments_for_contract(self, tenant_id, contract_id):
    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        with transaction.atomic():
            contract = Contract.objects.select_for_update().get(id=contract_id)
            # Check if already processed
            if contract.installments_generated:
                return  # Idempotent: already done
            # Generate installments
            generate_installments(contract)
            contract.installments_generated = True
            contract.save()
```

## Strategy 2: Redis Idempotency Key (for external calls)
```python
from django.core.cache import cache

@shared_task(bind=True)
def send_whatsapp_reminder(self, tenant_id, installment_id):
    idempotency_key = f'whatsapp_sent:{tenant_id}:{installment_id}'
    if cache.get(idempotency_key):
        return  # Already sent — skip

    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        installment = Installment.objects.get(id=installment_id)
        result = whatsapp_api.send_reminder(installment)
        if result.success:
            # Mark as sent — expires in 25 hours (longer than reminder interval)
            cache.set(idempotency_key, True, timeout=90000)
```

## Strategy 3: Unique Constraint (for listings sync)
```python
# Model approach: use unique_together to prevent duplicates
class MarketplaceListing(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    channel = models.CharField(max_length=50)  # 'imo_cv'
    external_id = models.CharField(max_length=100)

    class Meta:
        unique_together = ['unit', 'channel']  # Can't sync same unit twice
```

## Key Rules
- Every task that creates DB records or sends external messages MUST be idempotent
- Prefer database constraints over application-level checks (more reliable)
- Redis keys for idempotency must have TTL longer than max retry window
- Log idempotency hits (not errors) — they indicate retry is working correctly
