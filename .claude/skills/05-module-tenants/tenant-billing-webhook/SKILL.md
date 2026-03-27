---
name: tenant-billing-webhook
description: Processamento de webhook Stripe para atualizar plano e estado ativo do inquilino. Verificação de assinatura HMAC e atualização de TenantSettings.plan.
argument-hint: "[stripe_event_type]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Receber eventos do Stripe (subscription criada, atualizada, cancelada) e sincronizar o plano e o estado `is_active` do inquilino em `TenantSettings`. A verificação da assinatura Stripe é obrigatória.

## Code Pattern

```python
# billing/views.py
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from tenants.models import TenantSettings

PLAN_MAP = {
    settings.STRIPE_PRICE_STARTER: "starter",
    settings.STRIPE_PRICE_PRO: "pro",
    settings.STRIPE_PRICE_ENTERPRISE: "enterprise",
}

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    handlers = {
        "customer.subscription.updated": handle_subscription_updated,
        "customer.subscription.deleted": handle_subscription_deleted,
        "invoice.payment_failed": handle_payment_failed,
    }

    handler = handlers.get(event["type"])
    if handler:
        handler(event["data"]["object"])

    return HttpResponse(status=200)


def handle_subscription_updated(subscription):
    price_id = subscription["items"]["data"][0]["price"]["id"]
    plan = PLAN_MAP.get(price_id, "starter")
    tenant_slug = subscription["metadata"].get("tenant_slug")

    from django_tenants.utils import schema_context
    with schema_context(tenant_slug):
        TenantSettings.objects.update(
            plan=plan,
            is_active=subscription["status"] == "active",
            stripe_subscription_id=subscription["id"],
        )


def handle_subscription_deleted(subscription):
    tenant_slug = subscription["metadata"].get("tenant_slug")
    from django_tenants.utils import schema_context
    with schema_context(tenant_slug):
        TenantSettings.objects.update(is_active=False, plan="starter")


def handle_payment_failed(invoice):
    tenant_slug = invoice["metadata"].get("tenant_slug")
    from django_tenants.utils import schema_context
    with schema_context(tenant_slug):
        TenantSettings.objects.update(payment_overdue=True)
```

## Key Rules

- Verificar sempre a assinatura Stripe com `stripe.Webhook.construct_event` antes de processar o evento.
- Usar `metadata.tenant_slug` na subscrição Stripe para identificar o inquilino — configurar ao criar a subscrição.
- O webhook deve retornar HTTP 200 imediatamente; processamento pesado deve ir para uma task Celery.
- Tornar o handler idempotente: verificar se `stripe_subscription_id` já foi processado.

## Anti-Pattern

```python
# ERRADO: confiar no payload sem verificar a assinatura
event = json.loads(request.body)  # qualquer pessoa pode enviar eventos falsos
handle_subscription_updated(event["data"]["object"])
```
