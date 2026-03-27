---
name: e-signature-integration
description: Criação de envelope DocuSign a partir do PDF do contrato, webhook para atualizar Contract.status após assinatura e armazenamento do PDF assinado em S3.
argument-hint: "[contract_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Integrar assinatura eletrónica via DocuSign para contratos de compra e venda. O fluxo é totalmente assíncrono: o PDF é enviado ao DocuSign, o comprador assina na plataforma e o webhook notifica o ImoOS quando concluído.

## Code Pattern

```python
# contracts/services.py
import base64
import docusign_esign as docusign
from django.conf import settings

def create_docusign_envelope(contract) -> str:
    """Cria envelope e retorna envelope_id."""
    pdf_bytes = generate_contract_pdf(contract)
    pdf_b64 = base64.b64encode(pdf_bytes).decode()

    document = docusign.Document(
        document_base64=pdf_b64,
        name=f"Contrato_{contract.reference}.pdf",
        file_extension="pdf",
        document_id="1",
    )
    signer = docusign.Signer(
        email=contract.buyer.email,
        name=contract.buyer.full_name,
        recipient_id="1",
        routing_order="1",
        sign_here_tabs=docusign.Tabs(
            sign_here_tabs=[
                docusign.SignHere(
                    anchor_string="/assinatura_comprador/",
                    anchor_units="pixels",
                )
            ]
        ),
    )
    envelope_definition = docusign.EnvelopeDefinition(
        email_subject=f"Assine o seu contrato — {contract.unit.project.name}",
        documents=[document],
        recipients=docusign.Recipients(signers=[signer]),
        status="sent",
    )

    api_client = _get_docusign_client()
    envelopes_api = docusign.EnvelopesApi(api_client)
    result = envelopes_api.create_envelope(
        account_id=settings.DOCUSIGN_ACCOUNT_ID,
        envelope_definition=envelope_definition,
    )

    contract.docusign_envelope_id = result.envelope_id
    contract.status = "PENDING_SIGNATURE"
    contract.save(update_fields=["docusign_envelope_id", "status"])

    return result.envelope_id
```

```python
# contracts/views.py — webhook DocuSign
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import xml.etree.ElementTree as ET

@csrf_exempt
def docusign_webhook(request):
    """POST /api/v1/contracts/webhooks/docusign/"""
    tree = ET.fromstring(request.body)
    ns = {"ds": "http://www.docusign.net/API/3.0"}

    envelope_id = tree.findtext("ds:EnvelopeID", namespaces=ns)
    status = tree.findtext("ds:Status", namespaces=ns)

    from .models import Contract
    try:
        contract = Contract.objects.get(docusign_envelope_id=envelope_id)
    except Contract.DoesNotExist:
        return HttpResponse(status=404)

    if status == "Completed":
        from .tasks import download_signed_contract
        download_signed_contract.delay(contract.id, envelope_id)

    return HttpResponse(status=200)
```

```python
# contracts/tasks.py
@shared_task
def download_signed_contract(contract_id: int, envelope_id: str):
    from .models import Contract
    contract = Contract.objects.get(id=contract_id)

    api_client = _get_docusign_client()
    envelopes_api = docusign.EnvelopesApi(api_client)
    pdf_bytes = envelopes_api.get_document(
        account_id=settings.DOCUSIGN_ACCOUNT_ID,
        envelope_id=envelope_id,
        document_id="combined",
    )

    s3_key = f"tenants/{get_schema()}/contracts/{contract_id}/signed_{envelope_id}.pdf"
    boto3.client("s3").put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key, Body=pdf_bytes)

    contract.signed_pdf_s3_key = s3_key
    contract.status = "SIGNED"
    contract.signed_at = timezone.now()
    contract.save(update_fields=["signed_pdf_s3_key", "status", "signed_at"])
```

## Key Rules

- Nunca armazenar o PDF assinado localmente — sempre em S3 com encriptação AES256.
- O webhook DocuSign deve retornar HTTP 200 imediatamente; o download do PDF assinado vai para Celery.
- Verificar a autenticidade do webhook via IP whitelist da DocuSign ou HMAC se disponível.
- Após `status=SIGNED`, disparar automaticamente `calculate_commission()` e `generate_payment_plan()`.

## Anti-Pattern

```python
# ERRADO: aguardar a assinatura com polling ao DocuSign
while True:
    envelope = api.get_envelope(envelope_id)
    if envelope.status == "completed":
        break
    time.sleep(60)  # bloqueio desnecessário — usar webhook
```
