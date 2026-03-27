---
name: audit-log-immutable
description: Modelo AuditLog append-only (sem permissões de update/delete para o utilizador da aplicação), cadeia de hash SHA-256 para verificação de integridade e retenção de 7 anos para logs financeiros.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir a imutabilidade e integridade do registo de auditoria para conformidade legal e financeira. A cadeia de hash SHA-256 permite detetar qualquer adulteração dos registos, mesmo por administradores da base de dados.

## Code Pattern

```python
# audit/models.py
import hashlib
import json
from django.db import models

class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100, db_index=True)
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    tenant_schema = models.CharField(max_length=63, db_index=True)

    # Cadeia de hash para integridade
    entry_hash = models.CharField(max_length=64, blank=True)  # SHA-256 deste registo
    previous_hash = models.CharField(max_length=64, blank=True)  # hash do registo anterior

    class Meta:
        ordering = ["timestamp"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("AuditLog é imutável — não é permitido atualizar registos.")
        self._compute_hash()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("AuditLog é imutável — não é permitido eliminar registos.")

    def _compute_hash(self):
        # Obter hash do registo anterior
        last = AuditLog.objects.order_by("-id").first()
        self.previous_hash = last.entry_hash if last else "0" * 64

        # Calcular hash deste registo
        content = json.dumps({
            "timestamp": self.timestamp.isoformat() if self.timestamp else "",
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "previous_hash": self.previous_hash,
        }, sort_keys=True)
        self.entry_hash = hashlib.sha256(content.encode()).hexdigest()
```

```python
# audit/services.py
from django.db import connection

def log_action(user, action: str, resource_type: str = "", resource_id: str = "",
               details: dict = None, ip: str = None) -> AuditLog:
    """Função central para registar no log de auditoria."""
    return AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        details=details or {},
        ip_address=ip,
        tenant_schema=connection.schema_name,
    )


def verify_audit_log_integrity(from_id: int = None, to_id: int = None) -> dict:
    """Verifica a integridade da cadeia de hash."""
    qs = AuditLog.objects.all()
    if from_id:
        qs = qs.filter(id__gte=from_id)
    if to_id:
        qs = qs.filter(id__lte=to_id)

    broken = []
    prev_hash = "0" * 64
    for log in qs.order_by("id"):
        if log.previous_hash != prev_hash:
            broken.append({"id": log.id, "expected": prev_hash, "found": log.previous_hash})
        prev_hash = log.entry_hash

    return {"verified": len(broken) == 0, "broken_chain": broken, "checked": qs.count()}
```

```sql
-- Revogar permissões UPDATE/DELETE do utilizador da aplicação (executar no setup inicial)
REVOKE UPDATE, DELETE ON audit_auditlog FROM imoos_app_user;
GRANT SELECT, INSERT ON audit_auditlog TO imoos_app_user;
```

## Key Rules

- O utilizador PostgreSQL da aplicação nunca deve ter permissões `UPDATE` ou `DELETE` em `AuditLog`.
- A cadeia de hash (`previous_hash → entry_hash`) permite detetar eliminações ou modificações de registos.
- Reter logs financeiros (ações relacionadas com pagamentos e contratos) durante 7 anos mínimo.
- Executar `verify_audit_log_integrity()` mensalmente e alertar se a cadeia estiver quebrada.

## Anti-Pattern

```python
# ERRADO: permitir atualização de logs de auditoria para corrigir erros
audit_log.details["correction"] = "valor correto"
audit_log.save()  # viola a imutabilidade — usar um novo registo de correção
```
