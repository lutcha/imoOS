---
name: availability-realtime-sync
description: Sinal Django em Unit.status → task Celery → PATCH ao imo.cv para atualizar estado em menos de 5 minutos (requisito NFR-06). Polling de fallback a cada 15 minutos.
argument-hint: "[unit_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir que o estado de disponibilidade de unidades está sincronizado com o imo.cv em menos de 5 minutos após qualquer alteração (NFR-06). O polling de fallback assegura consistência mesmo em caso de falha do sinal.

## Code Pattern

```python
# inventory/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Unit

@receiver(post_save, sender=Unit)
def on_unit_status_change(sender, instance, **kwargs):
    update_fields = kwargs.get("update_fields")
    # Apenas sincronizar quando o status é explicitamente atualizado
    if update_fields is not None and "status" not in update_fields:
        return
    if not instance.external_listing_id:
        return

    from marketplace.tasks import sync_unit_availability_nfr06
    # NFR-06: máximo 5 minutos — task com alta prioridade
    sync_unit_availability_nfr06.apply_async(
        args=[instance.id],
        queue="high_priority",
        expires=240,  # expirar se não executada em 4 minutos
    )
```

```python
# marketplace/tasks.py
import requests
from celery import shared_task
from django.conf import settings

STATUS_MAP = {
    "AVAILABLE": "available",
    "RESERVED": "reserved",
    "CONTRACT": "reserved",
    "SOLD": "sold",
    "SUSPENDED": "unavailable",
}

@shared_task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=120,  # máximo 2 minutos entre tentativas (dentro do limite de 5 min)
    autoretry_for=(requests.RequestException,),
)
def sync_unit_availability_nfr06(self, unit_id: int):
    from inventory.models import Unit
    unit = Unit.objects.get(id=unit_id)

    if not unit.external_listing_id:
        return

    response = requests.patch(
        f"{settings.IMO_CV_API_URL}/listings/{unit.external_listing_id}/",
        json={"status": STATUS_MAP.get(unit.status, "unavailable")},
        headers={"Authorization": f"Bearer {settings.IMO_CV_API_TOKEN}"},
        timeout=10,
    )
    response.raise_for_status()

    unit.last_synced_at = __import__("django.utils.timezone", fromlist=["timezone"]).timezone.now()
    unit.save(update_fields=["last_synced_at"])


@shared_task
def polling_fallback_sync():
    """Fallback: correr a cada 15 minutos via Celery beat."""
    from django.utils import timezone
    from datetime import timedelta
    from inventory.models import Unit

    stale_cutoff = timezone.now() - timedelta(minutes=15)
    stale_units = Unit.objects.filter(
        external_listing_id__isnull=False,
        last_synced_at__lt=stale_cutoff,
    )
    for unit in stale_units:
        sync_unit_availability_nfr06.delay(unit.id)
```

```python
# settings/celery.py
CELERY_TASK_ROUTES = {
    "marketplace.tasks.sync_unit_availability_nfr06": {"queue": "high_priority"},
}
CELERY_BEAT_SCHEDULE = {
    "availability-polling-fallback": {
        "task": "marketplace.tasks.polling_fallback_sync",
        "schedule": 900,  # 15 minutos
    },
}
```

## Key Rules

- Usar a fila `high_priority` para garantir execução dentro do SLA de 5 minutos (NFR-06).
- `expires=240` na task garante que tasks antigas não são processadas fora do SLA.
- `last_synced_at` na unidade permite ao polling de fallback identificar unidades dessincronizadas.
- Monitorar o tempo de execução com Flower e alertar se a fila `high_priority` tiver mais de 100 tasks.

## Anti-Pattern

```python
# ERRADO: usar a fila padrão para sincronização de disponibilidade
sync_unit_availability.delay(unit_id)  # partilha fila com tasks de baixa prioridade — SLA violado
```
