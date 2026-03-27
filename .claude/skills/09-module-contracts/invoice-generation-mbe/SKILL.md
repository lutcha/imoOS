---
name: invoice-generation-mbe
description: Modelo Invoice com campos mbe_entity/mbe_reference, geração de referência MBE a partir de entity_code + invoice_id, PDF de fatura e envio por email assíncrono.
argument-hint: "[payment_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerar faturas com referência MBE (Multicaixa/Banco de Cabo Verde) para pagamentos de prestações. A referência MBE permite ao comprador efetuar o pagamento em qualquer caixa automático em Cabo Verde.

## Code Pattern

```python
# contracts/models.py
from django.db import models

class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        ISSUED = "ISSUED", "Emitida"
        PAID = "PAID", "Paga"
        CANCELLED = "CANCELLED", "Cancelada"

    installment = models.OneToOneField("Installment", on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    amount_cve = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Campos MBE (Multicaixa)
    mbe_entity = models.CharField(max_length=5, blank=True, help_text="Código de entidade MBE, ex: 12345")
    mbe_reference = models.CharField(max_length=9, blank=True, help_text="Referência MBE de 9 dígitos")
    mbe_expires_at = models.DateField(null=True, blank=True)

    pdf_s3_key = models.CharField(max_length=255, blank=True)
```

```python
# contracts/services.py
def generate_mbe_reference(entity_code: str, invoice_id: int) -> str:
    """
    Gera referência MBE de 9 dígitos: EEEEIIIIC
    E = entity_code (4 dígitos), I = invoice_id (4 dígitos), C = check digit
    """
    entity = str(entity_code).zfill(4)[:4]
    seq = str(invoice_id % 10000).zfill(4)
    base = entity + seq
    check = _calc_mbe_check_digit(base)
    return base + str(check)


def _calc_mbe_check_digit(base: str) -> int:
    """Algoritmo de módulo 97 simplificado para referência MBE."""
    total = sum(int(d) * (i + 1) for i, d in enumerate(base))
    return total % 10


def create_invoice_for_installment(installment) -> "Invoice":
    from .models import Invoice
    from django.conf import settings

    invoice_number = f"INV-{installment.contract_id:04d}-{installment.sequence:03d}"
    mbe_reference = generate_mbe_reference(
        entity_code=settings.MBE_ENTITY_CODE,
        invoice_id=installment.id,
    )

    invoice = Invoice.objects.create(
        installment=installment,
        invoice_number=invoice_number,
        due_date=installment.due_date,
        amount_cve=installment.amount_cve,
        mbe_entity=settings.MBE_ENTITY_CODE,
        mbe_reference=mbe_reference,
        mbe_expires_at=installment.due_date,
        status=Invoice.Status.ISSUED,
    )

    from .tasks import generate_and_send_invoice_pdf
    generate_and_send_invoice_pdf.delay(invoice.id)
    return invoice
```

```python
# contracts/tasks.py
@shared_task
def generate_and_send_invoice_pdf(invoice_id: int):
    from .models import Invoice
    invoice = Invoice.objects.select_related("installment__contract__buyer").get(id=invoice_id)

    html = render_to_string("contracts/invoice_pdf.html", {"invoice": invoice})
    pdf_bytes = HTML(string=html).write_pdf()

    key = f"tenants/{get_schema()}/invoices/{invoice_id}.pdf"
    boto3.client("s3").put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Body=pdf_bytes)

    invoice.pdf_s3_key = key
    invoice.save(update_fields=["pdf_s3_key"])

    # Enviar por email
    send_invoice_email.delay(invoice_id=invoice_id)
```

## Key Rules

- A referência MBE deve ser única por fatura — usar `invoice_id` como base para garantir unicidade.
- `mbe_entity` deve ser configurado em `settings.MBE_ENTITY_CODE` — nunca hardcoded no código.
- Gerar a fatura imediatamente após criar a `Installment` para que o comprador receba a referência de pagamento.
- O PDF deve incluir a referência MBE de forma visualmente destacada (QR code é opcional).

## Anti-Pattern

```python
# ERRADO: gerar referência MBE com base em dados mutáveis
mbe_reference = generate_mbe_reference(invoice.amount_cve)  # montante pode mudar
```
