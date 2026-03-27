---
name: payment-reconciliation
description: Função de serviço reconcile_payment(installment_id, amount_cve, payment_date) que associa transação bancária à prestação, trata pagamentos parciais e marca como PAID/PARTIAL.
argument-hint: "[installment_id] [amount_cve] [payment_date]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Reconciliar pagamentos bancários com prestações de contratos. O serviço trata pagamentos exatos, parciais (abaixo do valor) e excessivos (acima do valor), registando toda a movimentação para auditoria.

## Code Pattern

```python
# contracts/services.py
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

class ReconciliationError(Exception):
    pass

@transaction.atomic
def reconcile_payment(
    installment_id: int,
    amount_cve: Decimal,
    payment_date,
    payment_reference: str = "",
    reconciled_by=None,
) -> dict:
    from .models import Installment, Payment

    installment = Installment.objects.select_for_update().get(id=installment_id)

    if installment.status == Installment.Status.PAID:
        raise ReconciliationError(f"Prestação #{installment_id} já está totalmente paga.")

    if amount_cve <= 0:
        raise ReconciliationError("Valor do pagamento deve ser maior que zero.")

    # Registar o pagamento
    payment = Payment.objects.create(
        installment=installment,
        amount_cve=amount_cve,
        payment_date=payment_date,
        reference=payment_reference,
        reconciled_by=reconciled_by,
    )

    # Atualizar o valor pago acumulado
    installment.paid_amount_cve += amount_cve
    remaining = installment.amount_cve - installment.paid_amount_cve

    if remaining <= 0:
        installment.status = Installment.Status.PAID
        installment.paid_at = timezone.now()
        if remaining < 0:
            # Pagamento em excesso — registar crédito para aplicar à próxima prestação
            _apply_credit_to_next(installment, abs(remaining))
    else:
        installment.status = Installment.Status.PARTIAL

    installment.save(update_fields=["paid_amount_cve", "status", "paid_at"])

    return {
        "installment_id": installment_id,
        "payment_id": payment.id,
        "status": installment.status,
        "paid_amount_cve": str(installment.paid_amount_cve),
        "remaining_cve": str(max(remaining, Decimal("0"))),
    }


def _apply_credit_to_next(installment, credit_amount: Decimal):
    """Aplica crédito excedente à prestação seguinte."""
    next_installment = Installment.objects.filter(
        contract=installment.contract,
        sequence=installment.sequence + 1,
        status=Installment.Status.PENDING,
    ).first()
    if next_installment:
        reconcile_payment(
            installment_id=next_installment.id,
            amount_cve=credit_amount,
            payment_date=timezone.now().date(),
            payment_reference="CREDIT_FORWARD",
        )
```

```python
# contracts/models.py
class Payment(models.Model):
    installment = models.ForeignKey(Installment, on_delete=models.CASCADE, related_name="payments")
    amount_cve = models.DecimalField(max_digits=14, decimal_places=2)
    payment_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    reconciled_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Key Rules

- Usar `select_for_update()` para evitar reconciliações simultâneas da mesma prestação.
- Pagamentos parciais atualizam `paid_amount_cve` incrementalmente — nunca substituem.
- O excedente de pagamento deve ser automaticamente aplicado à próxima prestação pendente.
- Toda a reconciliação deve ser registada em `Payment` para auditoria completa da movimentação.

## Anti-Pattern

```python
# ERRADO: marcar diretamente como PAID sem verificar o valor pago
installment.status = "PAID"
installment.save()  # sem registar o pagamento, sem tratar parciais
```
