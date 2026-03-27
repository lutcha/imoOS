---
name: unit-status-workflow
description: Transições de estado válidas AVAILABLE→RESERVED→CONTRACT→SOLD, função de serviço transition_unit_status() que valida a transição e regista auditoria.
argument-hint: "[unit_id] [new_status]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir que as unidades apenas transitam entre estados válidos. A função de serviço centraliza a lógica de validação e regista cada transição no log de auditoria, prevenindo estados inconsistentes.

## Code Pattern

```python
# inventory/models.py
from django.db import models

class UnitStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Disponível"
    RESERVED = "RESERVED", "Reservado"
    CONTRACT = "CONTRACT", "Contrato"
    SOLD = "SOLD", "Vendido"
    SUSPENDED = "SUSPENDED", "Suspenso"

VALID_TRANSITIONS = {
    UnitStatus.AVAILABLE: [UnitStatus.RESERVED, UnitStatus.SUSPENDED],
    UnitStatus.RESERVED: [UnitStatus.CONTRACT, UnitStatus.AVAILABLE],  # pode libertar
    UnitStatus.CONTRACT: [UnitStatus.SOLD],
    UnitStatus.SOLD: [],  # estado final
    UnitStatus.SUSPENDED: [UnitStatus.AVAILABLE],
}
```

```python
# inventory/services.py
from django.db import transaction
from django.utils import timezone
from .models import Unit, UnitStatus, VALID_TRANSITIONS

class InvalidStatusTransitionError(Exception):
    pass

@transaction.atomic
def transition_unit_status(
    unit_id: int,
    new_status: str,
    user,
    reason: str = "",
) -> Unit:
    unit = Unit.objects.select_for_update().get(id=unit_id)
    current = unit.status

    if new_status not in VALID_TRANSITIONS.get(current, []):
        raise InvalidStatusTransitionError(
            f"Transição inválida: {current} → {new_status}. "
            f"Transições permitidas: {VALID_TRANSITIONS.get(current, [])}"
        )

    old_status = unit.status
    unit.status = new_status
    unit.save(update_fields=["status", "updated_at"])

    # Registar no log de auditoria
    UnitStatusHistory.objects.create(
        unit=unit,
        from_status=old_status,
        to_status=new_status,
        changed_by=user,
        reason=reason,
        changed_at=timezone.now(),
    )

    return unit
```

```python
# inventory/models.py — histórico de estado
class UnitStatusHistory(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
```

## Key Rules

- Usar `select_for_update()` para prevenir race conditions em reservas simultâneas.
- Toda a lógica de transição de estado deve passar por `transition_unit_status()` — nunca `unit.status = "SOLD"` diretamente.
- `SOLD` é estado final — nenhuma transição permitida a partir deste estado.
- Registar sempre `from_status`, `to_status`, `user` e `reason` no histórico.

## Anti-Pattern

```python
# ERRADO: alterar estado diretamente sem validação
unit.status = "SOLD"
unit.save()  # sem validação de transição, sem log de auditoria
```
