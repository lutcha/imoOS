---
name: async-email-whatsapp
description: Send email and WhatsApp notifications via Celery tasks in ImoOS with tenant branding. Auto-load when implementing any notification feature.
argument-hint: [channel] [trigger-event]
allowed-tools: Read, Write
---

# Async Email & WhatsApp — ImoOS

## Email via Celery
```python
# apps/core/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_tenants.utils import tenant_context

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_tenant_email(self, tenant_id, to_email, subject, template_name, context):
    """Send email with tenant branding."""
    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        settings_obj = tenant.settings
        full_context = {
            **context,
            'tenant_name': tenant.name,
            'tenant_logo': settings_obj.logo_url,
            'primary_color': settings_obj.primary_color,
        }
        html = render_to_string(f'emails/{template_name}.html', full_context)
        send_mail(
            subject=subject,
            message='',
            from_email=f'{tenant.name} <noreply@imos.cv>',
            recipient_list=[to_email],
            html_message=html,
            fail_silently=False,
        )
```

## WhatsApp via Meta Business API
```python
@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_whatsapp_message(self, tenant_id, phone_number, template_name, template_params):
    """Send WhatsApp template message via Meta Cloud API."""
    import requests
    from django.conf import settings

    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        phone_id = tenant.settings.whatsapp_phone_id
        access_token = tenant.settings.whatsapp_access_token

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "pt_PT"},
            "components": [{"type": "body", "parameters": template_params}],
        }
    }
    resp = requests.post(
        f"https://graph.facebook.com/v18.0/{phone_id}/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
```

## Key Rules
- All notifications go through Celery — never send synchronously in views
- WhatsApp templates must be pre-approved by Meta before use
- Always log notification delivery status in `NotificationLog` model
- Use idempotency key (see task-idempotency skill) for reminders to prevent duplicates
- Rate limit: Meta WhatsApp API has per-number limits — monitor via Celery task count
