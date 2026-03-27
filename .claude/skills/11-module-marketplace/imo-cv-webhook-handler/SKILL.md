---
name: imo-cv-webhook-handler
description: Endpoint POST /api/v1/marketplace/webhooks/imo-cv/ com verificação de assinatura HMAC, tratamento de eventos lead.created/reservation.updated/listing.status_changed e processamento idempotente por event_id.
argument-hint: "[event_type]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Receber e processar eventos do portal imo.cv de forma segura e idempotente. A verificação HMAC protege contra pedidos falsos e o controlo por `event_id` previne processamento duplicado em caso de reenvio.

## Code Pattern

```python
# marketplace/views.py
import hashlib
import hmac
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def imo_cv_webhook(request):
    """POST /api/v1/marketplace/webhooks/imo-cv/"""
    # 1. Verificar assinatura HMAC
    signature = request.META.get("HTTP_X_IMO_CV_SIGNATURE", "")
    if not _verify_signature(request.body, signature):
        return HttpResponse(status=401)

    # 2. Parse do payload
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    event_id = payload.get("event_id")
    event_type = payload.get("event_type")

    if not event_id or not event_type:
        return HttpResponse(status=400)

    # 3. Idempotência: verificar se já foi processado
    from .models import ProcessedWebhookEvent
    if ProcessedWebhookEvent.objects.filter(event_id=event_id).exists():
        return HttpResponse(status=200)  # já processado — responder OK

    # 4. Processar de forma assíncrona
    from .tasks import process_imo_cv_event
    process_imo_cv_event.delay(event_id=event_id, event_type=event_type, payload=payload)

    # 5. Registar como processado
    ProcessedWebhookEvent.objects.create(event_id=event_id, event_type=event_type)
    return HttpResponse(status=200)


def _verify_signature(body: bytes, signature: str) -> bool:
    expected = hmac.new(
        settings.IMO_CV_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

```python
# marketplace/tasks.py
from celery import shared_task

EVENT_HANDLERS = {}

def event_handler(event_type: str):
    def decorator(func):
        EVENT_HANDLERS[event_type] = func
        return func
    return decorator

@shared_task
def process_imo_cv_event(event_id: str, event_type: str, payload: dict):
    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        handler(payload)

@event_handler("lead.created")
def handle_lead_created(payload: dict):
    from crm.services import create_lead_from_marketplace
    create_lead_from_marketplace(payload["data"], source="IMO_CV")

@event_handler("reservation.updated")
def handle_reservation_updated(payload: dict):
    from inventory.services import transition_unit_status
    unit_id = payload["data"]["unit_external_id"]
    # ...

@event_handler("listing.status_changed")
def handle_listing_status_changed(payload: dict):
    from inventory.models import Unit
    Unit.objects.filter(
        external_listing_id=payload["data"]["listing_id"]
    ).update(marketplace_status=payload["data"]["new_status"])
```

## Key Rules

- Verificar sempre a assinatura HMAC antes de processar — usar `hmac.compare_digest` para evitar timing attacks.
- Registar `event_id` em `ProcessedWebhookEvent` antes de disparar a task Celery para garantir idempotência mesmo com falhas parciais.
- Retornar HTTP 200 imediatamente após validação — nunca deixar o imo.cv à espera do processamento.
- Usar o padrão `event_handler` registry para manter os handlers organizados e testáveis individualmente.

## Anti-Pattern

```python
# ERRADO: processar o evento de forma síncrona no webhook
def imo_cv_webhook(request):
    handle_lead_created(payload)  # se falhar, imo.cv faz retry e processa duplicado
    return HttpResponse(200)
```
