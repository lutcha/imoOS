---
name: unit-pricing-currency
description: UnitPricing com price_cve/price_eur, EUR derivado de CVE pela paridade fixa 110.265, rastreio histórico de preços via simple_history.
argument-hint: "[unit_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir os preços de unidades em Escudos Cabo-Verdianos (CVE) e Euros (EUR), com conversão automática pela taxa de câmbio fixa. O histórico de preços é mantido automaticamente via `django-simple-history` para auditoria.

## Code Pattern

```python
# inventory/models.py
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from simple_history.models import HistoricalRecords

CVE_EUR_RATE = Decimal("110.265")  # paridade fixa CVE/EUR

class UnitPricing(models.Model):
    unit = models.OneToOneField("Unit", on_delete=models.CASCADE, related_name="pricing")
    price_cve = models.DecimalField(
        max_digits=14, decimal_places=2,
        help_text="Preço de venda em Escudos Cabo-Verdianos"
    )
    price_eur = models.DecimalField(
        max_digits=12, decimal_places=2,
        editable=False,
        help_text="Calculado automaticamente: price_cve / 110.265"
    )
    price_per_sqm_cve = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Derivar EUR a partir de CVE com taxa fixa
        self.price_eur = (self.price_cve / CVE_EUR_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if self.unit.area_bruta and self.unit.area_bruta > 0:
            self.price_per_sqm_cve = (self.price_cve / self.unit.area_bruta).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unit.code}: {self.price_cve:,.0f} CVE / {self.price_eur:,.2f} EUR"
```

```python
# inventory/serializers.py
from rest_framework import serializers
from .models import UnitPricing

class UnitPricingSerializer(serializers.ModelSerializer):
    price_eur = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = UnitPricing
        fields = ["price_cve", "price_eur", "price_per_sqm_cve", "updated_at"]
        read_only_fields = ["price_eur", "updated_at"]
```

```python
# Aceder ao histórico de preços
pricing = UnitPricing.objects.get(unit=unit)
history = pricing.history.all().order_by("-history_date")
for record in history[:5]:
    print(f"{record.history_date}: {record.price_cve} CVE")
```

## Key Rules

- `price_eur` é sempre derivado — nunca permitir edição direta pelo utilizador.
- A taxa `CVE_EUR_RATE = 110.265` é uma paridade fixa legal — não usar API de câmbio.
- Usar `ROUND_HALF_UP` para arredondamento monetário conforme normas contabilísticas.
- O `simple_history` regista automaticamente quem alterou e quando — passar `updated_by` via `_change_reason`.

## Anti-Pattern

```python
# ERRADO: calcular EUR com divisão em float e sem arredondamento
price_eur = price_cve / 110.265  # float — acumulação de erros de precisão
```
