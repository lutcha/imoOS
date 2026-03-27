---
name: sync-conflict-resolution
description: Quando Unit editada no ImoOS e no imo.cv simultaneamente, last-writer-wins por timestamp updated_at. Modelo MarketplaceSyncConflict para fila de revisão manual.
argument-hint: "[unit_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Resolver conflitos de sincronização quando uma unidade é editada em ambos os sistemas simultaneamente. A estratégia last-writer-wins por timestamp é aplicada automaticamente; casos ambíguos vão para fila de revisão manual.

## Code Pattern

```python
# marketplace/models.py
from django.db import models

class MarketplaceSyncConflict(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Aguarda Revisão"
        RESOLVED_LOCAL = "RESOLVED_LOCAL", "Resolvido: Local Prevaleceu"
        RESOLVED_REMOTE = "RESOLVED_REMOTE", "Resolvido: Remoto Prevaleceu"
        IGNORED = "IGNORED", "Ignorado"

    unit = models.ForeignKey("inventory.Unit", on_delete=models.CASCADE)
    local_data = models.JSONField()
    remote_data = models.JSONField()
    local_updated_at = models.DateTimeField()
    remote_updated_at = models.DateTimeField()
    conflict_field = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
```

```python
# marketplace/services.py
from django.utils import timezone
from datetime import timedelta

CONFLICT_THRESHOLD_SECONDS = 300  # 5 minutos — edições próximas são consideradas conflito

def resolve_sync_conflict(unit, remote_payload: dict) -> str:
    """
    Retorna 'local' ou 'remote' conforme a resolução.
    Cria MarketplaceSyncConflict se necessário.
    """
    from .models import MarketplaceSyncConflict

    local_ts = unit.updated_at
    remote_ts = _parse_remote_timestamp(remote_payload.get("updated_at"))

    time_diff = abs((local_ts - remote_ts).total_seconds())

    if time_diff > CONFLICT_THRESHOLD_SECONDS:
        # Diferença clara: last-writer-wins
        winner = "remote" if remote_ts > local_ts else "local"
        if winner == "remote":
            _apply_remote_changes(unit, remote_payload)
        return winner
    else:
        # Edições quase simultâneas: registar para revisão manual
        conflicting_fields = _find_conflicting_fields(unit, remote_payload)
        for field in conflicting_fields:
            MarketplaceSyncConflict.objects.create(
                unit=unit,
                local_data={"field": field, "value": getattr(unit, field, None)},
                remote_data={"field": field, "value": remote_payload.get(field)},
                local_updated_at=local_ts,
                remote_updated_at=remote_ts,
                conflict_field=field,
            )
        return "conflict"


def _find_conflicting_fields(unit, remote_payload: dict) -> list[str]:
    TRACKED_FIELDS = ["status", "price", "description"]
    conflicts = []
    for field in TRACKED_FIELDS:
        local_val = str(getattr(unit, field, ""))
        remote_val = str(remote_payload.get(field, ""))
        if local_val != remote_val:
            conflicts.append(field)
    return conflicts


def _apply_remote_changes(unit, remote_payload: dict):
    STATUS_REVERSE_MAP = {"available": "AVAILABLE", "reserved": "RESERVED", "sold": "SOLD"}
    if "status" in remote_payload:
        unit.status = STATUS_REVERSE_MAP.get(remote_payload["status"], unit.status)
    unit.marketplace_updated_at = timezone.now()
    unit.save(update_fields=["status", "marketplace_updated_at"])
```

## Key Rules

- Usar `CONFLICT_THRESHOLD_SECONDS = 300` (5 minutos) como limiar para classificar edições como conflito real.
- Quando `remote_ts > local_ts` por margem clara, o imo.cv prevalece — atualizar a unidade localmente.
- Registar sempre o conflito em `MarketplaceSyncConflict` quando a diferença é ambígua — nunca descartar silenciosamente.
- O dashboard de conflitos deve ser visível apenas para `ADMIN` e `MANAGER`.

## Anti-Pattern

```python
# ERRADO: sempre deixar o local prevalecer sem considerar o timestamp remoto
unit.status = local_status  # ignora que o imo.cv pode ter informação mais recente
```
