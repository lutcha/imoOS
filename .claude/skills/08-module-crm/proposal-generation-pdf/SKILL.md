---
name: proposal-generation-pdf
description: PDF de proposta via WeasyPrint a partir de template Django, detalhes da unidade + preços em CVE/EUR, marca do inquilino (logo + cores), armazenamento em S3 e URL pré-assinado para download.
argument-hint: "[lead_id] [unit_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerar propostas comerciais personalizadas em PDF com a marca de cada inquilino. O PDF é gerado de forma assíncrona via Celery, armazenado no S3 e o link de download é enviado ao comercial.

## Code Pattern

```python
# crm/tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=2)
def generate_proposal_pdf(self, lead_id: int, unit_id: int, user_id: int):
    from crm.models import Lead
    from inventory.models import Unit
    from tenants.models import TenantSettings
    from .services import render_proposal_pdf, upload_proposal_to_s3

    lead = Lead.objects.select_related("project").get(id=lead_id)
    unit = Unit.objects.select_related("pricing", "project").get(id=unit_id)
    branding = TenantSettings.objects.get()

    pdf_bytes = render_proposal_pdf(lead=lead, unit=unit, branding=branding)
    s3_key = upload_proposal_to_s3(pdf_bytes, lead_id, unit_id)

    from crm.models import Proposal
    proposal = Proposal.objects.create(
        lead=lead, unit=unit, s3_key=s3_key, generated_by_id=user_id
    )
    return {"proposal_id": proposal.id, "s3_key": s3_key}
```

```python
# crm/services.py
import boto3
from weasyprint import HTML
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

CVE_EUR_RATE = Decimal("110.265")

def render_proposal_pdf(lead, unit, branding) -> bytes:
    context = {
        "lead": lead,
        "unit": unit,
        "price_cve": unit.pricing.price_cve,
        "price_eur": (unit.pricing.price_cve / CVE_EUR_RATE).quantize(Decimal("0.01")),
        "branding": branding,
        "logo_url": branding.logo_url,
        "primary_color": branding.primary_color,
    }
    html_string = render_to_string("crm/proposal_pdf.html", context)
    return HTML(string=html_string, base_url=settings.FRONTEND_URL).write_pdf()


def upload_proposal_to_s3(pdf_bytes: bytes, lead_id: int, unit_id: int) -> str:
    import uuid
    from django.conf import settings
    tenant_slug = _get_current_schema()
    key = f"tenants/{tenant_slug}/proposals/{lead_id}/{unit_id}/{uuid.uuid4()}.pdf"

    boto3.client("s3").put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        Body=pdf_bytes,
        ContentType="application/pdf",
        ServerSideEncryption="AES256",
    )
    return key


def get_proposal_download_url(s3_key: str, expiry: int = 3600) -> str:
    s3 = boto3.client("s3")
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": s3_key},
        ExpiresIn=expiry,
    )
```

```html
<!-- templates/crm/proposal_pdf.html -->
<!DOCTYPE html>
<html>
<head>
  <style>
    :root { --primary: {{ primary_color }}; }
    .header { background: var(--primary); }
    .logo { max-height: 60px; }
  </style>
</head>
<body>
  <div class="header">
    <img class="logo" src="{{ logo_url }}" alt="Logo">
    <h1>Proposta Comercial</h1>
  </div>
  <p>Prezado/a {{ lead.full_name }},</p>
  <p>Unidade: {{ unit.code }} — {{ unit.type }}</p>
  <p>Preço: {{ price_cve|floatformat:0 }} CVE ({{ price_eur }} EUR)</p>
</body>
</html>
```

## Key Rules

- A geração de PDF deve ser sempre assíncrona via Celery — WeasyPrint pode demorar 2-5 segundos.
- O PDF fica armazenado em S3 e nunca é servido diretamente pelo Django.
- O URL de download pré-assinado expira em 1 hora — gerar no momento do pedido, não armazenar.
- Incluir sempre os preços em CVE e EUR na proposta conforme o mercado cabo-verdiano.

## Anti-Pattern

```python
# ERRADO: gerar e servir o PDF diretamente na response HTTP
response = HttpResponse(content_type="application/pdf")
HTML(string=html).write_pdf(target=response)  # bloqueia o servidor durante a geração
```
