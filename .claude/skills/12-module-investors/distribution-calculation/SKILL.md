---
name: distribution-calculation
description: calculate_distribution(project_id, total_amount) aplica lógica de waterfall (retorno preferencial primeiro, depois pro-rata) e cria registos DistributionPayment.
argument-hint: "[project_id] [total_amount_cve]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Calcular e registar a distribuição de lucros de projetos imobiliários usando a lógica de waterfall: investidores preferenciais recebem o seu retorno garantido primeiro, e o remanescente é distribuído pro-rata pelos restantes.

## Code Pattern

```python
# investors/models.py
from django.db import models

class DistributionPayment(models.Model):
    class Status(models.TextChoices):
        CALCULATED = "CALCULATED", "Calculado"
        APPROVED = "APPROVED", "Aprovado"
        PAID = "PAID", "Pago"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    investor = models.ForeignKey("Investor", on_delete=models.CASCADE)
    distribution_round = models.PositiveIntegerField()
    gross_amount_cve = models.DecimalField(max_digits=16, decimal_places=2)
    percentage_applied = models.DecimalField(max_digits=7, decimal_places=4)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CALCULATED)
    calculated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
```

```python
# investors/services.py
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction

PREFERRED_RETURN_RATE = Decimal("0.08")  # 8% ao ano — configurável por projeto

@transaction.atomic
def calculate_distribution(project_id: int, total_amount_cve: Decimal) -> list:
    """
    Waterfall de distribuição:
    1. Retorno preferencial (8% sobre investimento) para PREFERRED shareholders
    2. Devolução de capital para todos
    3. Restante pro-rata por ownership_percentage
    """
    from .models import Investor, DistributionPayment, ShareClass

    investors = list(Investor.objects.filter(
        project_id=project_id, is_active=True
    ).select_related("user"))

    remaining = total_amount_cve
    payments = []
    round_num = DistributionPayment.objects.filter(project_id=project_id).count() + 1

    # Passo 1: Retorno preferencial
    preferred = [i for i in investors if i.share_class == ShareClass.PREFERRED]
    for inv in preferred:
        preferred_return = (inv.investment_amount_cve * PREFERRED_RETURN_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        amount = min(preferred_return, remaining)
        if amount > 0:
            payments.append({"investor": inv, "amount": amount, "type": "PREFERRED_RETURN"})
            remaining -= amount

    # Passo 2: Distribuição pro-rata do remanescente
    if remaining > 0:
        total_percentage = sum(i.ownership_percentage for i in investors)
        for inv in investors:
            pro_rata = (remaining * inv.ownership_percentage / total_percentage).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if pro_rata > 0:
                existing = next((p for p in payments if p["investor"].id == inv.id), None)
                if existing:
                    existing["amount"] += pro_rata
                else:
                    payments.append({"investor": inv, "amount": pro_rata, "type": "PRO_RATA"})

    # Criar registos DistributionPayment
    created = []
    for p in payments:
        dp = DistributionPayment.objects.create(
            project_id=project_id,
            investor=p["investor"],
            distribution_round=round_num,
            gross_amount_cve=p["amount"],
            percentage_applied=p["investor"].ownership_percentage,
        )
        created.append(dp)

    return created
```

## Key Rules

- O waterfall é: retorno preferencial → devolução de capital → lucros pro-rata. Nunca misturar as fases.
- Usar `ROUND_HALF_UP` em todos os arredondamentos — verificar que a soma total bate com `total_amount_cve`.
- A distribuição deve ser aprovada por `ADMIN` antes de mudar para `status=APPROVED`.
- `PREFERRED_RETURN_RATE` deve ser configurável por projeto — não hardcoded.

## Anti-Pattern

```python
# ERRADO: distribuir apenas pro-rata ignorando preferred shareholders
for inv in investors:
    amount = total * inv.ownership_percentage / 100  # viola as condições contratualmente acordadas
```
