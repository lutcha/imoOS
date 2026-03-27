---
name: tenant-deletion-safe
description: Desativação segura de inquilino (is_active=False, sem DROP SCHEMA), arquivo de dados em S3 e comando de eliminação de dados em conformidade com a LGPD (Lei 133/V/2019).
argument-hint: "[tenant_slug]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Nunca eliminar o schema de um inquilino diretamente. O processo correto é desativar, arquivar os dados em S3 e, apenas após o período de retenção legal, executar a anonimização de dados pessoais conforme exigido pela lei cabo-verdiana de proteção de dados.

## Code Pattern

```python
# management/commands/deactivate_tenant.py
import json
import boto3
from django.core.management.base import BaseCommand
from django.core import serializers
from django_tenants.utils import schema_context
from tenants.models import Client, TenantSettings

class Command(BaseCommand):
    help = "Desativa inquilino e arquiva dados em S3"

    def add_arguments(self, parser):
        parser.add_argument("slug", type=str)
        parser.add_argument("--archive", action="store_true", default=True)

    def handle(self, *args, **options):
        slug = options["slug"]

        with schema_context(slug):
            # 1. Desativar (nunca DROP SCHEMA)
            TenantSettings.objects.update(is_active=False)

            if options["archive"]:
                self._archive_to_s3(slug)

        self.stdout.write(self.style.SUCCESS(f"Inquilino '{slug}' desativado."))

    def _archive_to_s3(self, slug: str):
        from units.models import Unit
        from crm.models import Lead

        data = {
            "units": json.loads(serializers.serialize("json", Unit.objects.all())),
            "leads": json.loads(serializers.serialize("json", Lead.objects.all())),
        }

        s3 = boto3.client("s3")
        s3.put_object(
            Bucket="imoos-archives",
            Key=f"tenants/{slug}/archive.json",
            Body=json.dumps(data),
            ServerSideEncryption="AES256",
        )
        self.stdout.write(f"Dados arquivados em s3://imoos-archives/tenants/{slug}/archive.json")
```

```python
# management/commands/gdpr_erase_tenant.py — apenas após período de retenção
class Command(BaseCommand):
    help = "Anonimiza PII do inquilino conforme Lei 133/V/2019"

    def handle(self, *args, **options):
        slug = options["slug"]
        with schema_context(slug):
            from crm.models import Buyer
            Buyer.objects.update(
                full_name="[ANONIMIZADO]",
                email=None,
                phone=None,
                nif=None,
            )
        self.stdout.write(self.style.SUCCESS("PII anonimizado."))
```

## Key Rules

- Nunca executar `DROP SCHEMA` diretamente — definir `is_active=False` e bloquear logins.
- Arquivar em S3 com encriptação `AES256` antes de qualquer eliminação.
- Manter registos financeiros mesmo após anonimização (exigência legal de 7 anos).
- O comando `gdpr_erase_tenant` só deve ser executado após o período de retenção definido (mínimo 30 dias após desativação).

## Anti-Pattern

```python
# ERRADO: eliminar o schema imediatamente
from django.db import connection
connection.cursor().execute(f"DROP SCHEMA {slug} CASCADE")  # perda irreversível de dados
```
