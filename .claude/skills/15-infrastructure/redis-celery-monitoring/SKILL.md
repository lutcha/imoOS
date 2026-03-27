---
name: redis-celery-monitoring
description: Flower para monitorização de tasks Celery na porta 5555, comando Redis INFO para comprimentos de fila, alerta quando fila > 1000 tasks, JSON de dashboard Grafana.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Monitorizar a saúde do sistema de mensagens Celery/Redis com visibilidade em tempo real sobre tasks pendentes, falhas e latência. O alerta proativo previne acumulação silenciosa de tasks não processadas.

## Code Pattern

```python
# monitoring/tasks.py
from celery import shared_task
import redis
from django.conf import settings

@shared_task
def check_celery_queue_health():
    """Executa a cada 5 minutos via Celery beat."""
    r = redis.from_url(settings.CELERY_BROKER_URL)

    queues = {
        "default": r.llen("celery"),
        "high_priority": r.llen("high_priority"),
    }

    alerts = []
    for queue_name, length in queues.items():
        if length > 1000:
            alerts.append(f"Fila '{queue_name}': {length} tasks pendentes (limite: 1000)")

    # Verificar tasks com falha (usando API do Flower ou inspect)
    from celery.app.control import Inspect
    i = Inspect()
    reserved = i.reserved() or {}
    active = i.active() or {}

    total_workers = len(reserved)
    if total_workers == 0:
        alerts.append("CRÍTICO: Nenhum worker Celery ativo!")

    if alerts:
        _send_slack_alert(alerts)

    return {
        "queues": queues,
        "workers": total_workers,
        "alerts": alerts,
    }


def _send_slack_alert(alerts: list):
    import requests
    from django.conf import settings

    if not hasattr(settings, "SLACK_ALERT_WEBHOOK"):
        return

    message = "\n".join([f"• {a}" for a in alerts])
    requests.post(settings.SLACK_ALERT_WEBHOOK, json={
        "text": f":warning: *Alerta Celery/Redis — ImoOS*\n{message}",
        "username": "ImoOS Monitor",
    }, timeout=5)
```

```bash
# Comandos úteis de monitorização Redis
redis-cli INFO server          # informação do servidor
redis-cli INFO memory          # uso de memória
redis-cli LLEN celery          # tamanho da fila padrão
redis-cli LLEN high_priority   # tamanho da fila de alta prioridade
redis-cli CLIENT LIST          # clientes ligados
redis-cli DBSIZE               # total de chaves
```

```json
// grafana/dashboards/celery-redis.json — dashboard básico
{
  "title": "ImoOS Celery & Redis",
  "panels": [
    {
      "title": "Fila Celery — Tasks Pendentes",
      "type": "stat",
      "targets": [{ "expr": "redis_list_length{key=\"celery\"}" }],
      "thresholds": {
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 100, "color": "yellow"},
          {"value": 1000, "color": "red"}
        ]
      }
    },
    {
      "title": "Tasks Ativas por Worker",
      "type": "timeseries",
      "targets": [{ "expr": "celery_workers_active_tasks" }]
    },
    {
      "title": "Taxa de Falha de Tasks (1h)",
      "type": "gauge",
      "targets": [{ "expr": "rate(celery_task_failed_total[1h])" }]
    }
  ]
}
```

```yaml
# docker-compose additions para Flower com autenticação
flower:
  command: celery -A imoos flower
    --port=5555
    --basic_auth=${FLOWER_USER}:${FLOWER_PASSWORD}
    --persistent=True
    --state_save_interval=5000
    --max_tasks=10000
  environment:
    FLOWER_UNAUTHENTICATED_API: "false"
```

## Key Rules

- Limitar o acesso ao Flower com autenticação básica ou VPN — nunca expor publicamente.
- O alerta de 1000 tasks deve ser enviado ao Slack E registado no log de auditoria.
- Monitorizar `high_priority` separadamente da fila padrão — esta é crítica para o SLA NFR-06.
- Configurar retenção de estado do Flower (`--persistent=True`) para não perder histórico ao reiniciar.

## Anti-Pattern

```bash
# ERRADO: expor o Flower sem autenticação em produção
celery flower --port=5555  # acesso aberto a logs e controlo de tasks de qualquer pessoa
```
