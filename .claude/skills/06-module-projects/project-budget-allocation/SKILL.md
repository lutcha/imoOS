---
name: project-budget-allocation
description: Modelo BudgetLine com category/budgeted_cve/committed_cve/spent_cve, cálculo de variância e alerta quando gasto ultrapassa 90% do orçamento.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Controlar o orçamento de projetos por linha orçamental. Calcular variâncias e disparar alertas automáticos quando o gasto se aproxima do limite, prevenindo desvios não geridos.

## Code Pattern

```python
# projects/models.py
from django.db import models
from decimal import Decimal

class BudgetCategory(models.TextChoices):
    CONSTRUCTION = "CONSTRUCTION", "Construção"
    MATERIALS = "MATERIALS", "Materiais"
    LABOR = "LABOR", "Mão de Obra"
    LICENSING = "LICENSING", "Licenciamento"
    MARKETING = "MARKETING", "Marketing"
    OTHER = "OTHER", "Outros"

class BudgetLine(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="budget_lines")
    category = models.CharField(max_length=50, choices=BudgetCategory.choices)
    description = models.CharField(max_length=255)
    budgeted_cve = models.DecimalField(max_digits=14, decimal_places=2)
    committed_cve = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    spent_cve = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    @property
    def variance_cve(self) -> Decimal:
        return self.budgeted_cve - self.spent_cve

    @property
    def spent_percentage(self) -> Decimal:
        if self.budgeted_cve == 0:
            return Decimal("0")
        return (self.spent_cve / self.budgeted_cve * 100).quantize(Decimal("0.01"))

    @property
    def is_over_threshold(self) -> bool:
        return self.spent_percentage >= Decimal("90")
```

```python
# projects/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BudgetLine
from .tasks import send_budget_alert

@receiver(post_save, sender=BudgetLine)
def check_budget_threshold(sender, instance, **kwargs):
    if instance.is_over_threshold:
        send_budget_alert.delay(
            project_id=instance.project_id,
            budget_line_id=instance.id,
            spent_pct=float(instance.spent_percentage),
        )
```

```python
# projects/tasks.py
from celery import shared_task

@shared_task
def send_budget_alert(project_id: int, budget_line_id: int, spent_pct: float):
    from .models import BudgetLine
    line = BudgetLine.objects.select_related("project").get(id=budget_line_id)
    # Notificar gestor de projeto via email/WhatsApp
    subject = f"[Alerta Orçamental] {line.project.name} — {line.category}"
    message = f"Linha '{line.description}' atingiu {spent_pct:.1f}% do orçamento."
    # send_notification(line.project.manager, subject, message)
```

## Key Rules

- Usar `DecimalField` para todos os valores monetários — nunca `FloatField`.
- O alerta de 90% é configurável por inquilino em `TenantSettings.budget_alert_threshold`.
- `committed_cve` representa contratos assinados mas ainda não pagos; `spent_cve` representa pagamentos efetivos.
- Calcular o total do projeto com `BudgetLine.objects.filter(project=p).aggregate(total=Sum('budgeted_cve'))`.

## Anti-Pattern

```python
# ERRADO: usar FloatField para valores monetários — causa erros de arredondamento
budgeted = models.FloatField()  # 110265.99 pode virar 110265.9900000001
```
