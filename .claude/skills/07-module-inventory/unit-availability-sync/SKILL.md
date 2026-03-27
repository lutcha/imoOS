---
name: unit-availability-sync
description: Sinal Django em Unit.status dispara task Celery para sincronizar com imo.cv. A task usa padrão de retry com backoff exponencial.
argument-hint: "[unit_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir que qualquer alteração de estado de uma unidade no ImoOS é refletida no portal imo.cv em menos de 5 minutos (requisito NFR-06). O padrão de retry com backoff exponencial garante resiliência a falhas temporárias da API externa.

## Code Pattern

```python
# inventory/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Unit

@receiver(post_save, sender=Unit)
def sync_unit_status_to_marketplace(sender, instance, **kwargs):
    # Sincronizar apenas se o status mudou e a unidade tem listing externo
    if not instance.external_listing_id:
        return

    update_fields = kwargs.get("update_fields")
    if update_fields and "status" not in update_fields:
        return  # Apenas disparar quando status for explicitamente atualizado

    from .tasks import sync_unit_availability
    sync_unit_availability.delay(unit_id=instance.id)
```

```python
# inventory/tasks.py
import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,          # backoff exponencial: 60s, 120s, 240s, 480s, 960s
    retry_backoff_max=900,       # máximo 15 minutos entre tentativas
    retry_jitter=True,           # adicionar ruído para evitar thundering herd
)
def sync_unit_availability(self, unit_id: int):
    from .models import Unit
    unit = Unit.objects.select_related("pricing").get(id=unit_id)

    payload = {
        "external_id": unit.external_listing_id,
        "status": unit.status,
        "price_cve": float(unit.pricing.price_cve) if hasattr(unit, "pricing") else None,
    }

    response = requests.patch(
        f"{settings.IMO_CV_API_URL}/listings/{unit.external_listing_id}/",
        json=payload,
        headers={"Authorization": f"Bearer {settings.IMO_CV_API_TOKEN}"},
        timeout=10,
    )
    response.raise_for_status()

    logger.info(f"Unidade {unit.code} sincronizada com imo.cv: {unit.status}")
    return {"unit_id": unit_id, "status": unit.status}
```

```python
# Polling de fallback — task periódica a cada 15 minutos
@shared_task
def sync_all_pending_units():
    """Fallback: garantir consistência mesmo se o sinal falhar."""
    from .models import Unit
    stale_units = Unit.objects.filter(
        external_listing_id__isnull=False,
        sync_pending=True,
    )
    for unit in stale_units:
        sync_unit_availability.delay(unit_id=unit.id)
```

## Key Rules

- Usar `post_save` com verificação de `update_fields` para evitar sincronizações desnecessárias.
- Configurar `retry_backoff=True` e `retry_jitter=True` para evitar sobrecarregar a API externa em falhas.
- O polling de fallback a cada 15 minutos garante que nenhum estado fica permanentemente dessincronizado.
- Registar `sync_pending=True` na unidade quando o sinal dispara e `False` quando a task conclui com sucesso.

## Anti-Pattern

```python
# ERRADO: chamar a API externa de forma síncrona no sinal post_save
@receiver(post_save, sender=Unit)
def sync_status(sender, instance, **kwargs):
    requests.patch(IMO_CV_API_URL, ...)  # bloqueia o processo Django, sem retry
```
