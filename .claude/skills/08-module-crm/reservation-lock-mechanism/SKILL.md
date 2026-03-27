---
name: reservation-lock-mechanism
description: SELECT FOR UPDATE na Unit, validação de status=AVAILABLE e sem reserva ativa, definição de expires_at=now()+48h, prevenção de double booking por race condition.
argument-hint: "[unit_id] [lead_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir que apenas uma reserva ativa existe por unidade num dado momento. O bloqueio a nível de base de dados (`SELECT FOR UPDATE`) elimina race conditions em reservas simultâneas.

## Code Pattern

```python
# crm/services.py
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

class UnitNotAvailableError(Exception):
    pass

class ActiveReservationExistsError(Exception):
    pass

@transaction.atomic
def create_reservation(unit_id: int, lead_id: int, user) -> "Reservation":
    from inventory.models import Unit, UnitStatus
    from inventory.services import transition_unit_status
    from .models import Reservation

    # 1. Bloquear a linha da unidade para prevenir race conditions
    unit = Unit.objects.select_for_update().get(id=unit_id)

    # 2. Validar que a unidade está disponível
    if unit.status != UnitStatus.AVAILABLE:
        raise UnitNotAvailableError(
            f"Unidade {unit.code} não está disponível (estado atual: {unit.status})."
        )

    # 3. Verificar se não existe reserva ativa (dupla segurança)
    active = Reservation.objects.filter(
        unit=unit,
        status="ACTIVE",
        expires_at__gt=timezone.now(),
    ).exists()
    if active:
        raise ActiveReservationExistsError(
            f"Unidade {unit.code} já tem uma reserva ativa."
        )

    # 4. Criar reserva com prazo de 48 horas
    reservation = Reservation.objects.create(
        unit=unit,
        lead_id=lead_id,
        created_by=user,
        expires_at=timezone.now() + timedelta(hours=48),
        status="ACTIVE",
    )

    # 5. Transitar o estado da unidade
    transition_unit_status(unit.id, UnitStatus.RESERVED, user, reason=f"Reserva #{reservation.id}")

    return reservation
```

```python
# crm/models.py
from django.db import models

class Reservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativa"
        EXPIRED = "EXPIRED", "Expirada"
        CANCELLED = "CANCELLED", "Cancelada"
        CONVERTED = "CONVERTED", "Convertida em Contrato"

    unit = models.ForeignKey("inventory.Unit", on_delete=models.PROTECT)
    lead = models.ForeignKey("Lead", on_delete=models.CASCADE)
    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    deposit_amount_cve = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
```

```python
# crm/tasks.py — expirar reservas automaticamente
@shared_task
def expire_reservations():
    from .models import Reservation
    from inventory.services import transition_unit_status
    from inventory.models import UnitStatus

    expired = Reservation.objects.filter(
        status=Reservation.Status.ACTIVE,
        expires_at__lt=timezone.now(),
    )
    for r in expired:
        r.status = Reservation.Status.EXPIRED
        r.save(update_fields=["status"])
        transition_unit_status(r.unit_id, UnitStatus.AVAILABLE, user=None, reason="Reserva expirada")
```

## Key Rules

- `select_for_update()` é obrigatório — sem ele, duas reservas simultâneas podem ser criadas.
- A verificação de reserva ativa é redundante mas necessária como segunda barreira de segurança.
- `expires_at=now()+48h` é o padrão; deve ser configurável por inquilino.
- A task `expire_reservations` deve correr a cada 15 minutos via Celery beat.

## Anti-Pattern

```python
# ERRADO: verificar disponibilidade sem SELECT FOR UPDATE
if unit.status == "AVAILABLE":  # outra thread pode ler o mesmo valor simultaneamente
    unit.status = "RESERVED"    # double booking garantido em alto volume
    unit.save()
```
