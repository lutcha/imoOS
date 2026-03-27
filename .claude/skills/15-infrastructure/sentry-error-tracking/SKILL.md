---
name: sentry-error-tracking
description: Configuração do SDK Sentry para Django com hook before_send que adiciona tenant_schema às tags do evento, rastreio de releases via SENTRY_RELEASE e alertas Slack para novos issues.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Capturar e rastrear erros de produção com contexto multi-tenant. O hook `before_send` enriquece cada evento com o schema do inquilino, permitindo filtrar e priorizar erros por cliente.

## Code Pattern

```python
# settings/base.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import os

def before_send(event, hint):
    """Enriquecer evento com contexto do inquilino."""
    try:
        from django.db import connection
        schema = connection.schema_name
        event.setdefault("tags", {})["tenant_schema"] = schema
        event.setdefault("extra", {})["tenant_schema"] = schema

        # Filtrar erros esperados para reduzir ruído
        if "hint" in hint:
            exc = hint.get("exc_info", [None, None, None])[1]
            if exc and isinstance(exc, (KeyboardInterrupt,)):
                return None  # não reportar paragens manuais

    except Exception:
        pass  # nunca falhar no before_send
    return event


def traces_sampler(sampling_context):
    """Taxa de sampling por tipo de operação."""
    op = sampling_context.get("transaction_context", {}).get("op", "")
    if "health" in sampling_context.get("wsgi_environ", {}).get("PATH_INFO", ""):
        return 0  # não rastrear health checks
    if op == "celery.task":
        return 0.1  # 10% das tasks
    return 0.2  # 20% das transações web


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""),
    environment=os.environ.get("ENVIRONMENT", "development"),
    release=os.environ.get("SENTRY_RELEASE", "unknown"),
    integrations=[
        DjangoIntegration(transaction_style="url"),
        CeleryIntegration(monitor_beat_tasks=True),
        RedisIntegration(),
    ],
    traces_sampler=traces_sampler,
    before_send=before_send,
    send_default_pii=False,  # conformidade LGPD — não enviar PII
    attach_stacktrace=True,
)
```

```python
# middleware/sentry_tenant_context.py
from django.utils.deprecation import MiddlewareMixin
import sentry_sdk

class SentryTenantContextMiddleware(MiddlewareMixin):
    """Define o contexto do inquilino no Sentry para cada pedido."""

    def process_request(self, request):
        try:
            from django.db import connection
            sentry_sdk.set_tag("tenant_schema", connection.schema_name)
            sentry_sdk.set_context("tenant", {
                "schema": connection.schema_name,
                "host": request.get_host(),
            })
            if request.user.is_authenticated:
                sentry_sdk.set_user({
                    "id": request.user.id,
                    "username": request.user.email,  # email como identificador (sem PII extra)
                })
        except Exception:
            pass
```

```yaml
# .github/workflows/cd-staging.yml — configurar SENTRY_RELEASE
- name: Create Sentry Release
  run: |
    sentry-cli releases new "${{ github.sha }}"
    sentry-cli releases set-commits "${{ github.sha }}" --auto
    sentry-cli releases finalize "${{ github.sha }}"
  env:
    SENTRY_ORG: imoos
    SENTRY_PROJECT: imoos-backend
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
```

## Key Rules

- `send_default_pii=False` é obrigatório por conformidade LGPD — nunca enviar emails, nomes ou IPs ao Sentry.
- O `before_send` deve ter `try/except` envolvente — uma exceção no hook silencia todos os outros erros.
- Configurar alertas Sentry no canal `#alerts-prod` do Slack apenas para issues novos (não cada ocorrência).
- Usar `SENTRY_RELEASE` para correlacionar erros com a versão de código que os introduziu.

## Anti-Pattern

```python
# ERRADO: enviar PII ao Sentry sem anonimização
sentry_sdk.init(dsn=DSN, send_default_pii=True)  # envia cookies, headers, IPs — viola LGPD
```
