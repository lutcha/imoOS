---
name: payment-plan-generator
description: generate_payment_plan(contract, plan_type) onde plan_type é '20_80' ou 'phased', cria registos Installment com due_date e amount_cve.
argument-hint: "[contract_id] [plan_type]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerar automaticamente o plano de pagamento de um contrato após assinatura. O plano `20_80` é comum no mercado imobiliário cabo-verdiano (20% na reserva, 80% na escritura). O plano `phased` distribui por fases de construção.

## Code Pattern

```python
# contracts/services.py
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction

ROUND2 = Decimal("0.01")

@transaction.atomic
def generate_payment_plan(contract, plan_type: str) -> list:
    """
    Cria Installment records e retorna a lista criada.
    plan_type: '20_80' | 'phased' | 'monthly_N' (ex: 'monthly_24')
    """
    price = contract.unit.pricing.price_cve
    signed_date = contract.signed_at.date()

    if plan_type == "20_80":
        installments = _plan_20_80(price, signed_date)
    elif plan_type == "phased":
        installments = _plan_phased(price, contract.unit.project)
    elif plan_type.startswith("monthly_"):
        months = int(plan_type.split("_")[1])
        installments = _plan_monthly(price, signed_date, months)
    else:
        raise ValueError(f"Tipo de plano desconhecido: {plan_type}")

    # Validar que a soma é igual ao preço total
    total = sum(i["amount_cve"] for i in installments)
    assert total == price, f"Total {total} != preço {price}"

    from .models import Installment
    created = []
    for i, item in enumerate(installments, start=1):
        inst = Installment.objects.create(
            contract=contract,
            sequence=i,
            description=item["description"],
            amount_cve=item["amount_cve"],
            due_date=item["due_date"],
            status="PENDING",
        )
        created.append(inst)
    return created


def _plan_20_80(price: Decimal, signed_date: date) -> list:
    entry = (price * Decimal("0.20")).quantize(ROUND2, rounding=ROUND_HALF_UP)
    balance = price - entry
    return [
        {"description": "Entrada (20%)", "amount_cve": entry, "due_date": signed_date},
        {"description": "Saldo (80%) — Escritura", "amount_cve": balance, "due_date": signed_date + relativedelta(months=24)},
    ]


def _plan_phased(price: Decimal, project) -> list:
    milestones = project.milestones.filter(status="PENDING").order_by("planned_date")
    if not milestones:
        raise ValueError("Projeto sem marcos definidos para plano faseado.")

    per_milestone = (price / len(milestones)).quantize(ROUND2, rounding=ROUND_HALF_UP)
    remainder = price - per_milestone * len(milestones)

    result = []
    for i, milestone in enumerate(milestones):
        amount = per_milestone + (remainder if i == len(milestones) - 1 else Decimal("0"))
        result.append({
            "description": f"Fase: {milestone.name}",
            "amount_cve": amount,
            "due_date": milestone.planned_date,
        })
    return result


def _plan_monthly(price: Decimal, start: date, months: int) -> list:
    monthly = (price / months).quantize(ROUND2, rounding=ROUND_HALF_UP)
    remainder = price - monthly * months
    return [
        {
            "description": f"Prestação {i+1}/{months}",
            "amount_cve": monthly + (remainder if i == months - 1 else Decimal("0")),
            "due_date": start + relativedelta(months=i + 1),
        }
        for i in range(months)
    ]
```

## Key Rules

- Sempre validar que a soma das prestações é igual ao preço total do contrato.
- Usar `ROUND_HALF_UP` e ajustar o arredondamento na última prestação para evitar diferenças de cêntimos.
- `generate_payment_plan()` deve ser chamado automaticamente quando `contract.status=SIGNED`.
- Não permitir regerar o plano se já existem prestações pagas.

## Anti-Pattern

```python
# ERRADO: dividir igualmente sem tratar arredondamentos
monthly = price / months  # float — causa soma diferente do preço total
for i in range(months):
    Installment.objects.create(amount_cve=monthly, ...)
```
