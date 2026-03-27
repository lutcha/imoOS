# Sprint 7 — Observabilidade e Monitorização

## Contexto

Em produção, sem observabilidade não existe operação. Este prompt configura:
1. **Sentry** — error tracking (Python + Next.js)
2. **Health check endpoint** — para load balancers e uptime monitors
3. **Prometheus metrics** — `django-prometheus` + métricas custom (tenants activos, tasks Celery)
4. **Structured logging** — JSON logs para Datadog/Papertrail
5. **Celery monitoring** — Flower já existe; adicionar alertas de falha de task

## Pré-requisitos — Ler antes de começar

```
config/settings/base.py         → SENTRY_DSN já existe como env var
config/settings/production.py   → settings de produção (criar se não existir)
requirements/base.txt           → dependências actuais
apps/core/                      → app de utilities (adicionar health check aqui)
docker/Dockerfile.dev           → para verificar imagem base
```

```bash
cat config/settings/base.py | grep "SENTRY\|LOGGING\|MIDDLEWARE"
cat requirements/base.txt | grep "sentry\|prometheus\|celery"
ls apps/core/
```

## Skills a carregar

```
@.claude/skills/15-infrastructure/monitoring-setup/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/00-global/security-patterns/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `drf-viewset-builder` | HealthCheckView + MetricsView |
| `celery-task-specialist` | Task: alertas de falha (dead letter queue) |

---

## Tarefa 1 — Sentry (backend Django)

**Ler `config/settings/base.py` antes de editar.**

Adicionar a `requirements/base.txt`:
```
sentry-sdk[django]==1.40.0
```

Em `config/settings/base.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        traces_sample_rate=0.1,        # 10% das requests em produção
        profiles_sample_rate=0.05,     # 5% para profiling
        environment=env('SENTRY_ENVIRONMENT', default='development'),
        send_default_pii=False,        # LGPD: sem PII nos reports
        before_send=_scrub_tenant_pii, # função a criar abaixo
    )

def _scrub_tenant_pii(event, hint):
    """Remove campos PII de Sentry events (LGPD compliance)."""
    if 'request' in event:
        # Remover Authorization header e cookies
        headers = event['request'].get('headers', {})
        for key in list(headers.keys()):
            if key.lower() in ('authorization', 'cookie'):
                headers[key] = '[Filtered]'
    return event
```

---

## Tarefa 2 — Sentry (frontend Next.js)

Instalar: `npm install @sentry/nextjs`

Criar `frontend/sentry.client.config.ts`:
```typescript
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT ?? 'development',
  // Não enviar dados de utilizador (LGPD)
  beforeSend(event) {
    if (event.user) {
      delete event.user.email;
      delete event.user.username;
    }
    return event;
  },
});
```

Criar `frontend/sentry.server.config.ts` (igual, sem o `beforeSend` de user — server não tem dados de utilizador).

---

## Tarefa 3 — Health check endpoint

Criar `apps/core/health.py`:
```python
"""
Health check endpoint para load balancers e uptime monitors.
GET /health/ → resposta rápida (sem auth)
GET /health/detailed/ → detalhes (requer auth super admin)
"""
import time
from django.db import connection as db_connection
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser


class HealthCheckView(APIView):
    """
    Liveness probe — responde 200 se o processo está vivo.
    Usado por load balancers (DigitalOcean App Platform).
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # sem auth para não criar overhead

    def get(self, request):
        return Response({'status': 'ok', 'service': 'imos-api'})


class DetailedHealthCheckView(APIView):
    """
    Readiness probe — verifica DB, Redis, migrations.
    Requerer autenticação para não expor info de infra publicamente.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        checks = {}

        # Database
        try:
            t0 = time.time()
            db_connection.ensure_connection()
            checks['database'] = {'status': 'ok', 'latency_ms': round((time.time()-t0)*1000, 1)}
        except Exception as e:
            checks['database'] = {'status': 'error', 'error': str(e)}

        # Redis
        try:
            t0 = time.time()
            cache.set('_health_check', '1', timeout=5)
            val = cache.get('_health_check')
            checks['redis'] = {
                'status': 'ok' if val == '1' else 'error',
                'latency_ms': round((time.time()-t0)*1000, 1),
            }
        except Exception as e:
            checks['redis'] = {'status': 'error', 'error': str(e)}

        # Pending migrations
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(db_connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            checks['migrations'] = {
                'status': 'ok' if not plan else 'pending',
                'pending': len(plan),
            }
        except Exception as e:
            checks['migrations'] = {'status': 'error', 'error': str(e)}

        overall = 'ok' if all(c['status'] == 'ok' for c in checks.values()) else 'degraded'
        status_code = 200 if overall == 'ok' else 503
        return Response({'status': overall, 'checks': checks}, status=status_code)
```

Registar em `config/urls_public.py`:
```python
path('health/', HealthCheckView.as_view(), name='health'),
path('health/detailed/', DetailedHealthCheckView.as_view(), name='health-detailed'),
```

---

## Tarefa 4 — Prometheus metrics

Adicionar a `requirements/base.txt`:
```
django-prometheus==2.3.1
```

Em `config/settings/base.py`:
```python
# Adicionar a INSTALLED_APPS (em SHARED_APPS):
'django_prometheus',

# Adicionar ao início de MIDDLEWARE:
'django_prometheus.middleware.PrometheusBeforeMiddleware',
# E ao fim de MIDDLEWARE:
'django_prometheus.middleware.PrometheusAfterMiddleware',
```

Em `config/urls_public.py`:
```python
from django_prometheus import exports
path('metrics/', exports.ExportToDjangoView, name='prometheus-metrics'),
```

**Métricas custom** em `apps/core/metrics.py`:
```python
from prometheus_client import Counter, Histogram, Gauge

# Reservations
reservation_created = Counter(
    'imos_reservation_created_total',
    'Total de reservas criadas',
    ['tenant_schema'],
)
reservation_cancelled = Counter(
    'imos_reservation_cancelled_total',
    'Total de reservas canceladas',
    ['tenant_schema'],
)

# Contracts
contract_signed = Counter(
    'imos_contract_signed_total',
    'Contratos assinados',
    ['tenant_schema'],
)

# WhatsApp
whatsapp_sent = Counter(
    'imos_whatsapp_sent_total',
    'Mensagens WhatsApp enviadas',
    ['tenant_schema', 'template_name', 'status'],
)

# Active tenants
active_tenants = Gauge(
    'imos_active_tenants',
    'Número de tenants activos',
)
```

---

## Tarefa 5 — Structured logging (JSON)

Em `config/settings/base.py` (substituir LOGGING simples):
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(tenant_schema)s',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
            'filters': ['require_debug_false'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'apps': {'handlers': ['console', 'sentry'], 'level': 'INFO', 'propagate': False},
        'celery': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}
```

Instalar: `python-json-logger==2.0.7` em `requirements/base.txt`.

---

## Tarefa 6 — Alertas de falha Celery

Prompt para `celery-task-specialist`:
> "Cria `monitor_failed_tasks(tenant_schema)` em `apps/core/tasks.py`. Corre de hora em hora. Usa `django_celery_results` para contar tasks FAILED nas últimas 2h. Se falhas > 5: envia alerta por email ao super-admin (`settings.ADMINS`). Inclui nome da task, número de falhas, schema do tenant. Usa `send_mail`, não WhatsApp (admin pode não ter número configurado)."

---

## Verificação final

- [ ] `GET /health/` → 200 `{"status": "ok"}` (sem auth)
- [ ] `GET /metrics/` → formato Prometheus (text/plain)
- [ ] Sentry recebe erro de teste: `raise Exception("Sentry test")` em shell
- [ ] `sentry_sdk.init()` só corre quando `SENTRY_DSN` está definido
- [ ] Logs em JSON no stdout do Docker
- [ ] `NEXT_PUBLIC_SENTRY_DSN` configurado no frontend `.env.local`
- [ ] Health check responde em < 100ms
