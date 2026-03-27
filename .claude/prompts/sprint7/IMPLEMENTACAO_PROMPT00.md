# Sprint 7 - Prompt 00: Observabilidade e Monitorização

## Resumo da Implementação

### ✅ Tarefas Completadas

#### 1. Sentry Error Tracking (Backend)
**Ficheiros modificados:**
- `requirements/base.txt` - Adicionado `sentry-sdk[django]==1.40.0`
- `config/settings/base.py` - Configuração do Sentry com:
  - Django, Celery e Redis integrations
  - PII scrubbing para LGPD compliance
  - 10% trace sample rate, 5% profile sample rate
  - Environment configuration

#### 2. Health Check Endpoints
**Ficheiros modificados:**
- `apps/core/views.py` - Adicionado `DetailedHealthCheckView` (admin-only)
- `config/urls.py` - URLs actualizados:
  - `GET /api/v1/health/` - Público (load balancers)
  - `GET /api/v1/health/detailed/` - Requer is_staff (monitoring)

**Funcionalidades do detailed health check:**
- Database latency check
- Redis latency check
- Pending migrations detection
- Status code 200/503 baseado no estado

#### 3. Prometheus Metrics
**Ficheiros modificados:**
- `requirements/base.txt` - Adicionado `django-prometheus==2.3.1`
- `config/settings/base.py`:
  - `django_prometheus` em SHARED_APPS
  - PrometheusBeforeMiddleware (primeiro)
  - PrometheusAfterMiddleware (último)
- `config/urls_public.py` - Endpoint `/metrics/` para exportação Prometheus

**Métricas disponíveis:**
- Request rate, latency histograms
- Error rates por endpoint
- Django/Redis/DB metrics

#### 4. Structured Logging (JSON)
**Ficheiros modificados:**
- `requirements/base.txt` - Adicionado `python-json-logger==2.0.7`
- `config/settings/base.py` - LOGGING configurado com:
  - JSON formatter com tenant_schema context
  - Sentry handler para erros
  - Console handler para stdout Docker

**Formato do log:**
```json
{
  "asctime": "2026-03-15 19:00:00,000",
  "name": "apps.crm.views",
  "levelname": "INFO",
  "message": "Lead created",
  "tenant_schema": "demo_promotora"
}
```

#### 5. Celery Failed Tasks Alerts
**Ficheiros criados:**
- `apps/core/tasks.py` - Tasks de monitorização:
  - `monitor_failed_tasks()` - Hourly, alerta se >5 falhas em 2h
  - `cleanup_old_task_results()` - Daily, limpa resultados antigos

**Ficheiros modificados:**
- `config/settings/base.py`:
  - `CELERY_RESULT_BACKEND = 'django-db'`
  - `CELERY_BEAT_SCHEDULE` configurado
  - `django_celery_results` em INSTALLED_APPS
- `config/celery.py` - `result_extended=True`, `result_backend='django-db'`

---

## Variáveis de Ambiente (adicionar ao .env)

```bash
# Sentry
SENTRY_DSN=https://your-key@sentry.io/your-project-id
SENTRY_ENVIRONMENT=development

# Opcional: Production
# SENTRY_ENVIRONMENT=production
# SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

## Endpoints Novos

| Endpoint | Auth | Descrição |
|----------|------|-----------|
| `GET /api/v1/health/` | None | Health check público para load balancers |
| `GET /api/v1/health/detailed/` | IsAdminUser | Health check detalhado com latências |
| `GET /metrics/` | None | Prometheus metrics export |

---

## Comandos de Verificação

```bash
# 1. Health check público
curl http://localhost:8000/api/v1/health/
# Expected: {"status":"ok","checks":{"db":"ok","cache":"ok"}}

# 2. Health check detalhado (requer superuser)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/health/detailed/

# 3. Prometheus metrics
curl http://localhost:8000/metrics/
# Expected: text/plain com métricas Prometheus

# 4. Testar Sentry (apenas se SENTRY_DSN configurado)
python manage.py shell
>>> import sentry_sdk
>>> sentry_sdk.capture_message("Test message from ImoOS")
```

---

## Próximos Passos (Sprint 7)

### Frontend Sentry (pendente)
- Instalar `@sentry/nextjs` no frontend
- Criar `sentry.client.config.ts` e `sentry.server.config.ts`
- Configurar `NEXT_PUBLIC_SENTRY_DSN`

### Admin Backoffice (Prompt 02)
- Django Admin customizado para super-admin
- Tabela de tenants com métricas
- Actions para suspender/activar tenants

### Tenant Onboarding (Prompt 03)
- Self-service registration flow
- Email verification
- Automatic tenant provisioning

---

## Notas de Implementação

### LGPD Compliance
- Sentry configurado com `send_default_pii=False`
- `before_send` hook remove Authorization headers e cookies
- Logs JSON não incluem dados sensíveis

### Multi-Tenancy
- Logs incluem `tenant_schema` context
- Health check funciona em public schema
- Prometheus metrics agregam todos os tenants

### Performance
- Trace sample rate: 10% (produção)
- Profile sample rate: 5% (produção)
- JSON logging overhead mínimo

---

**Implementado por:** Tech Lead Agent  
**Data:** 15 Mar 2026  
**Status:** ✅ Completo (backend)
