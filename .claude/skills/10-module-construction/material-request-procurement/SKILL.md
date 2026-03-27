---
name: material-request-procurement
description: Modelo MaterialRequest com items/quantities/supplier, estados DRAFT→APPROVED→ORDERED→DELIVERED e task Celery para geração de ordem de compra.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir o processo de requisição e encomenda de materiais de obra. O fluxo de aprovação garante controlo de custos e a geração automática de ordem de compra reduz trabalho manual.

## Code Pattern

```python
# construction/models.py
from django.db import models

class MaterialRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        PENDING_APPROVAL = "PENDING", "Aguarda Aprovação"
        APPROVED = "APPROVED", "Aprovado"
        REJECTED = "REJECTED", "Rejeitado"
        ORDERED = "ORDERED", "Encomendado"
        DELIVERED = "DELIVERED", "Entregue"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    wbs_task = models.ForeignKey("projects.WBSTask", on_delete=models.SET_NULL, null=True, blank=True)
    supplier_name = models.CharField(max_length=255, blank=True)
    supplier_contact = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    requested_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_requests"
    )
    needed_by_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    po_s3_key = models.CharField(max_length=255, blank=True)


class MaterialRequestItem(models.Model):
    request = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    unit = models.CharField(max_length=20)  # ex: "m³", "un", "kg"
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price_cve = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    @property
    def total_cve(self):
        if self.unit_price_cve:
            return self.quantity * self.unit_price_cve
        return None
```

```python
# construction/services.py
from django.db import transaction

VALID_TRANSITIONS = {
    "DRAFT": ["PENDING"],
    "PENDING": ["APPROVED", "REJECTED"],
    "APPROVED": ["ORDERED"],
    "ORDERED": ["DELIVERED"],
}

@transaction.atomic
def advance_material_request(request_id: int, new_status: str, user) -> MaterialRequest:
    mr = MaterialRequest.objects.select_for_update().get(id=request_id)
    if new_status not in VALID_TRANSITIONS.get(mr.status, []):
        raise ValueError(f"Transição inválida: {mr.status} → {new_status}")

    mr.status = new_status
    if new_status == "APPROVED":
        mr.approved_by = user
        from .tasks import generate_purchase_order
        generate_purchase_order.delay(mr.id)
    mr.save()
    return mr
```

```python
# construction/tasks.py
@shared_task
def generate_purchase_order(request_id: int):
    from .models import MaterialRequest
    from weasyprint import HTML
    from django.template.loader import render_to_string

    mr = MaterialRequest.objects.prefetch_related("items").get(id=request_id)
    html = render_to_string("construction/purchase_order.html", {"request": mr})
    pdf_bytes = HTML(string=html).write_pdf()

    key = f"tenants/{get_schema()}/purchase_orders/{request_id}.pdf"
    upload_to_s3(key, pdf_bytes)
    mr.po_s3_key = key
    mr.save(update_fields=["po_s3_key"])
```

## Key Rules

- Apenas `MANAGER` ou `ADMIN` pode aprovar requisições; o solicitante não pode aprovar a sua própria requisição.
- A ordem de compra (PO) é gerada automaticamente quando `status=APPROVED`.
- `needed_by_date` deve ser usado para priorizar requisições no dashboard do gestor.
- Calcular o total estimado da requisição a partir de `sum(item.total_cve for item in items)`.

## Anti-Pattern

```python
# ERRADO: permitir que o mesmo utilizador requisite e aprove
if request.user == mr.requested_by:
    mr.status = "APPROVED"  # conflito de interesse — sem segregação de funções
```
