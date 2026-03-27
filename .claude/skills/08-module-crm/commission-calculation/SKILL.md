---
name: commission-calculation
description: Modelo CommissionRule com percentage/agent/project, calculate_commission() no momento de assinatura do contrato e agendamento de pagamento via Celery beat.
argument-hint: "[contract_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Calcular e registar comissões de agentes comerciais no momento da assinatura do contrato, com regras configuráveis por projeto e agente. O pagamento é agendado automaticamente via Celery beat.

## Code Pattern

```python
# crm/models.py
from django.db import models

class CommissionRule(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, null=True, blank=True)
    agent = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)  # ex: 3.00 para 3%
    applies_to_all_agents = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-project", "-agent"]  # regras mais específicas têm prioridade


class Commission(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        APPROVED = "APPROVED", "Aprovada"
        PAID = "PAID", "Paga"
        CANCELLED = "CANCELLED", "Cancelada"

    contract = models.ForeignKey("contracts.Contract", on_delete=models.CASCADE)
    agent = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    rule = models.ForeignKey(CommissionRule, on_delete=models.SET_NULL, null=True)
    amount_cve = models.DecimalField(max_digits=14, decimal_places=2)
    percentage_applied = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
```

```python
# crm/services.py
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

def calculate_commission(contract) -> "Commission":
    """Chamado quando contrato muda para status=SIGNED."""
    agent = contract.lead.assigned_to
    if not agent:
        return None

    rule = _find_applicable_rule(agent, contract.unit.project)
    if not rule:
        return None

    amount = (contract.unit.pricing.price_cve * rule.percentage / Decimal("100")).quantize(
        Decimal("0.01")
    )

    commission = Commission.objects.create(
        contract=contract,
        agent=agent,
        rule=rule,
        amount_cve=amount,
        percentage_applied=rule.percentage,
        due_date=timezone.now().date() + timedelta(days=30),
    )
    return commission


def _find_applicable_rule(agent, project) -> "CommissionRule":
    # Regra específica por agente + projeto
    rule = CommissionRule.objects.filter(agent=agent, project=project, is_active=True).first()
    if rule:
        return rule
    # Fallback: regra geral do projeto
    return CommissionRule.objects.filter(
        project=project, applies_to_all_agents=True, is_active=True
    ).first()
```

## Key Rules

- Calcular comissão apenas quando `contract.status` transita para `SIGNED` — via sinal `post_save`.
- A regra mais específica (agente + projeto) tem prioridade sobre a regra geral do projeto.
- `due_date` é calculado como D+30 após assinatura — configurável por inquilino.
- Apenas utilizadores com papel `FINANCE` ou `ADMIN` podem alterar o estado da comissão para `PAID`.

## Anti-Pattern

```python
# ERRADO: calcular comissão com base no preço acordado em negociação (pode divergir do preço final)
amount = lead.budget_max * rule.percentage / 100  # usar sempre contract.unit.pricing.price_cve
```
