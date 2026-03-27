---
name: cap-table-management
description: Modelo Investor com ownership_percentage/share_class, validação que percentagens somam 100%, cálculo de diluição ao adicionar novo investidor.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir a tabela de capitalização de projetos imobiliários com rastreabilidade de participações. A validação garante que o total é sempre 100% e o cálculo de diluição permite simular novos investimentos antes de os confirmar.

## Code Pattern

```python
# investors/models.py
from django.db import models
from decimal import Decimal

class ShareClass(models.TextChoices):
    COMMON = "COMMON", "Ordinária"
    PREFERRED = "PREFERRED", "Preferencial"
    SENIOR = "SENIOR", "Sénior"

class Investor(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="investors")
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    share_class = models.CharField(max_length=20, choices=ShareClass.choices, default=ShareClass.COMMON)
    ownership_percentage = models.DecimalField(max_digits=7, decimal_places=4)  # ex: 25.0000
    investment_amount_cve = models.DecimalField(max_digits=16, decimal_places=2)
    invested_at = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("project", "user")
```

```python
# investors/services.py
from decimal import Decimal
from django.db import transaction

def validate_cap_table(project_id: int) -> bool:
    total = Investor.objects.filter(
        project_id=project_id, is_active=True
    ).aggregate(total=Sum("ownership_percentage"))["total"] or Decimal("0")
    return abs(total - Decimal("100")) < Decimal("0.01")


def calculate_dilution(project_id: int, new_percentage: Decimal) -> dict:
    """
    Simula a adição de novo investidor com new_percentage.
    Retorna a diluição por investidor existente.
    """
    existing = list(Investor.objects.filter(project_id=project_id, is_active=True))
    total_existing = sum(i.ownership_percentage for i in existing)

    if total_existing + new_percentage > Decimal("100"):
        raise ValueError(
            f"Percentagem excede 100%: {total_existing} + {new_percentage} = {total_existing + new_percentage}"
        )

    dilution_factor = (Decimal("100") - new_percentage) / Decimal("100")
    return {
        "new_investor_percentage": new_percentage,
        "existing_investors": [
            {
                "investor_id": inv.id,
                "user": inv.user.get_full_name(),
                "before": float(inv.ownership_percentage),
                "after": float(inv.ownership_percentage * dilution_factor),
                "dilution": float(inv.ownership_percentage * (1 - dilution_factor)),
            }
            for inv in existing
        ],
    }


@transaction.atomic
def add_investor(project_id: int, user, percentage: Decimal, amount_cve: Decimal,
                 share_class: str, invested_at) -> Investor:
    if not validate_cap_table_has_space(project_id, percentage):
        raise ValueError("Não há espaço para esta participação na tabela de capitalização.")

    investor = Investor.objects.create(
        project_id=project_id, user=user,
        ownership_percentage=percentage,
        investment_amount_cve=amount_cve,
        share_class=share_class,
        invested_at=invested_at,
    )
    return investor
```

## Key Rules

- Validar sempre que a soma de `ownership_percentage` não ultrapassa 100% antes de guardar.
- Usar `Decimal` para percentagens — nunca `float` (precisão crítica em dados financeiros).
- A simulação de diluição (`calculate_dilution`) nunca deve persistir dados — é apenas informativa.
- `PREFERRED` shareholders têm retorno prioritário — considerar na lógica de distribuição de lucros.

## Anti-Pattern

```python
# ERRADO: armazenar percentagem como float
ownership_percentage = models.FloatField()  # 33.33 + 33.33 + 33.34 pode != 100.0 devido a float
```
