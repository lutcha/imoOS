---
name: log-aggregation-loki
description: Logging JSON estruturado com label tenant_schema, configuração Promtail para scraping de logs Docker, exemplos de queries Loki e dashboard Grafana para taxa de erros por inquilino.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Centralizar logs de todos os serviços ImoOS no Loki com o schema do inquilino como label. Permite filtrar logs por inquilino, monitorizar erros em tempo real e criar alertas baseados em padrões de log.

## Code Pattern

```python
# settings/logging.py
import logging
import json
from django.db import connection

class TenantJSONFormatter(logging.Formatter):
    """Formata logs como JSON com tenant_schema como campo."""

    def format(self, record):
        try:
            tenant_schema = connection.schema_name
        except Exception:
            tenant_schema = "public"

        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "tenant_schema": tenant_schema,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "settings.logging.TenantJSONFormatter"},
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "imoos": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
```

```yaml
# promtail/config.yml — scraping de logs Docker
server:
  http_listen_port: 9080

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
        filters:
          - name: label
            values: ["logging=promtail"]

    relabel_configs:
      - source_labels: ["__meta_docker_container_name"]
        target_label: container

    pipeline_stages:
      - json:
          expressions:
            tenant_schema: tenant_schema
            level: level
            message: message
      - labels:
          tenant_schema:
          level:
      - output:
          source: message
```

```logql
# Queries Loki úteis

# Taxa de erros por inquilino (última hora)
sum(rate({job="docker", level="ERROR"}[1h])) by (tenant_schema)

# Logs de um inquilino específico
{job="docker", tenant_schema="meu_cliente"} | json | level="ERROR"

# Erros de tasks Celery
{job="docker", container=~".*celery.*"} | json | level="ERROR" | line_format "{{.message}}"

# Pedidos lentos (> 500ms)
{job="docker", container=~".*web.*"} | json | response_time > 500
```

## Key Rules

- Incluir sempre `tenant_schema` como label Loki — permite filtrar e criar alertas por inquilino.
- O formato JSON deve usar `ensure_ascii=False` para preservar caracteres portugueses/cabo-verdianos.
- Configurar alertas Grafana para taxa de erros > 10/min por inquilino.
- Nunca incluir dados PII (emails, NIF, telefone) nas mensagens de log — apenas IDs.

## Anti-Pattern

```python
# ERRADO: logging em texto livre sem estrutura JSON
logger.error(f"Erro ao processar lead {lead.email} do cliente {tenant_schema}")
# Email no log — viola LGPD; impossível filtrar por tenant_schema no Loki
```
