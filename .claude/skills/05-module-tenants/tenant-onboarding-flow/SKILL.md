---
name: tenant-onboarding-flow
description: Criação de schema de novo inquilino, dados iniciais e envio de email de boas-vindas via Celery.
argument-hint: "[tenant_slug] [admin_email]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Orquestrar o processo completo de criação de um novo inquilino: schema dedicado na base de dados, seed de dados iniciais (TenantSettings, plano padrão), e envio assíncrono de email de boas-vindas.

## Code Pattern

```python
# management/commands/create_tenant.py
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from tenants.models import Client, Domain, TenantSettings
from tenants.tasks import send_welcome_email

class Command(BaseCommand):
    help = "Cria novo inquilino com schema e dados iniciais"

    def add_arguments(self, parser):
        parser.add_argument("slug", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("--plan", default="starter")

    def handle(self, *args, **options):
        slug = options["slug"]
        email = options["email"]
        plan = options["plan"]

        # 1. Criar Client (cria schema automaticamente via django-tenants)
        client = Client.objects.create(
            schema_name=slug,
            name=slug.title(),
            on_trial=False,
        )
        Domain.objects.create(domain=f"{slug}.imoos.cv", tenant=client, is_primary=True)

        # 2. Criar TenantSettings no schema do inquilino
        with schema_context(slug):
            TenantSettings.objects.create(
                plan=plan,
                max_units=100,
                max_users=10,
                max_projects=5,
            )

        # 3. Enviar email de boas-vindas de forma assíncrona
        send_welcome_email.delay(tenant_slug=slug, admin_email=email)

        self.stdout.write(self.style.SUCCESS(f"Inquilino '{slug}' criado com sucesso."))
```

```python
# tenants/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, tenant_slug: str, admin_email: str):
    try:
        send_mail(
            subject="Bem-vindo ao ImoOS",
            message=f"O seu espaço {tenant_slug}.imoos.cv está pronto.",
            from_email="noreply@imoos.cv",
            recipient_list=[admin_email],
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

## Key Rules

- Criar sempre `TenantSettings` imediatamente após o `Client`, dentro do `schema_context` correto.
- O email de boas-vindas deve ser enviado de forma assíncrona via Celery (nunca de forma síncrona no request cycle).
- Usar `schema_context(slug)` ao aceder a modelos que residem no schema do inquilino.
- O comando deve ser idempotente: verificar se o schema já existe antes de criar.

## Anti-Pattern

```python
# ERRADO: enviar email de forma síncrona durante o processo de criação
client = Client.objects.create(schema_name=slug, ...)
send_mail(subject="Bem-vindo", ...)  # bloqueia o processo e falha silenciosamente se o SMTP estiver em baixo
```
