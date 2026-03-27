---
name: audit-log-export
description: Exportação de AuditLog como CSV ou JSON com filtros por intervalo de datas, utilizador e tipo de ação. LGPD: redação de PII (email→hash) para exportações não-admin.
argument-hint: "[format] [date_from] [date_to]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Permitir a exportação do registo de auditoria para conformidade regulatória e investigações. A redação de PII garante que utilizadores não-admin não acedem a dados pessoais identificáveis de outros utilizadores.

## Code Pattern

```python
# audit/views.py
import csv
import hashlib
import io
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse

class AuditLogExportView(APIView):
    """GET /api/v1/audit/export/?format=csv&from=2025-01-01&to=2025-12-31&user_id=5&action=UPDATE"""

    def get(self, request):
        fmt = request.query_params.get("format", "csv")
        is_admin = request.user.has_perm("audit.view_full_pii")

        qs = self._build_queryset(request)
        rows = [self._serialize_row(log, is_admin) for log in qs]

        if fmt == "json":
            return Response({"count": len(rows), "logs": rows})
        return self._return_csv(rows)

    def _build_queryset(self, request):
        from .models import AuditLog
        qs = AuditLog.objects.select_related("user").order_by("-timestamp")

        if request.query_params.get("from"):
            qs = qs.filter(timestamp__date__gte=request.query_params["from"])
        if request.query_params.get("to"):
            qs = qs.filter(timestamp__date__lte=request.query_params["to"])
        if request.query_params.get("user_id"):
            qs = qs.filter(user_id=request.query_params["user_id"])
        if request.query_params.get("action"):
            qs = qs.filter(action=request.query_params["action"])

        return qs[:10000]  # limite de 10k registos por exportação

    def _serialize_row(self, log, is_admin: bool) -> dict:
        user_email = log.user.email if log.user else ""
        return {
            "timestamp": log.timestamp.isoformat(),
            "user_id": log.user_id,
            "user_email": user_email if is_admin else self._hash_email(user_email),
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address if is_admin else self._hash_ip(log.ip_address),
            "details": log.details if is_admin else self._redact_pii(log.details),
        }

    @staticmethod
    def _hash_email(email: str) -> str:
        if not email:
            return ""
        return hashlib.sha256(email.lower().encode()).hexdigest()[:16]

    @staticmethod
    def _hash_ip(ip: str) -> str:
        if not ip:
            return ""
        return hashlib.sha256(ip.encode()).hexdigest()[:16]

    @staticmethod
    def _redact_pii(details: dict) -> dict:
        PII_FIELDS = {"email", "phone", "nif", "name", "address"}
        if not isinstance(details, dict):
            return details
        return {
            k: "[REDACTED]" if k.lower() in PII_FIELDS else v
            for k, v in details.items()
        }

    def _return_csv(self, rows: list) -> HttpResponse:
        output = io.StringIO()
        if rows:
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="audit_log.csv"'
        return response
```

## Key Rules

- Utilizadores sem permissão `audit.view_full_pii` devem sempre receber emails e IPs substituídos por hashes.
- Limitar exportações a 10.000 registos por pedido — para exportações maiores, usar task Celery assíncrona.
- Registar no próprio `AuditLog` quem exportou os registos e com que filtros.
- O formato CSV deve usar `UTF-8 com BOM` para compatibilidade com Excel em Windows.

## Anti-Pattern

```python
# ERRADO: expor dados PII completos a todos os utilizadores autenticados
return AuditLog.objects.all().values()  # expõe emails, IPs e dados pessoais sem controlo
```
