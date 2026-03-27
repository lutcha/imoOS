# Sprint 4 — Staging: DigitalOcean App Platform + CD Pipeline

## Pré-requisitos — Ler antes de começar

```
.github/workflows/          → verificar o que já existe
docker-compose.dev.yml      → configuração local para referência
config/settings/staging.py  → verificar se existe
requirements/staging.txt    → verificar se existe
```

```bash
ls .github/workflows/
ls config/settings/
ls requirements/
```

## Skills a carregar

```
@.claude/skills/15-infrastructure/digitalocean-app-platform/SKILL.md
@.claude/skills/15-infrastructure/github-actions-ci/SKILL.md
@.claude/skills/15-infrastructure/docker-production/SKILL.md
```

## Agent a activar

- Agent: `general-purpose` (infra não tem agent especializado)
  - Tarefa: Ler `.do/app.yaml` existente e os workflows de CI, verificar o que falta para staging funcional, propor ajustes mínimos.

---

## Tarefa 1 — Verificar e corrigir `.do/app.yaml`

**Ler o ficheiro existente antes de qualquer edição:**
```bash
cat .do/app.yaml
```

O ficheiro já existe (commit `1a0345e`). Verificar:
- [ ] `DJANGO_SETTINGS_MODULE` aponta para `config.settings.staging`
- [ ] `DATABASE_URL` referencia o managed DB do DO
- [ ] Workers Celery configurados como `worker` components (não como `web`)
- [ ] `migrate_schemas` run job definido
- [ ] `ALLOWED_HOSTS` inclui o domínio DO App Platform

Ajustes típicos sem destruir o que está:
```yaml
# Exemplo de run job para migrations (verificar se já existe)
jobs:
  - name: migrate
    kind: PRE_DEPLOY
    run_command: python manage.py migrate_schemas --shared && python manage.py migrate_schemas
    envs:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.staging
```

---

## Tarefa 2 — `config/settings/staging.py`

**Ler o ficheiro se existir.** Se não existir, criar baseado em `base.py`:

```python
from .base import *  # noqa
import os

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database — DO Managed PostgreSQL via DATABASE_URL
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ['DATABASE_URL'],
        conn_max_age=600,
        ssl_require=True,
    )
}

# Forçar HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Cache — DO Managed Redis
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
    }
}

# S3 — DigitalOcean Spaces
AWS_ACCESS_KEY_ID = os.environ['DO_SPACES_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['DO_SPACES_SECRET']
AWS_STORAGE_BUCKET_NAME = os.environ['DO_SPACES_BUCKET']
AWS_S3_ENDPOINT_URL = os.environ['DO_SPACES_ENDPOINT']
AWS_S3_CUSTOM_DOMAIN = os.environ.get('DO_SPACES_CDN_ENDPOINT', '')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
```

---

## Tarefa 3 — GitHub Actions: CI + Deploy para Staging

**Verificar workflows existentes** — não duplicar, apenas complementar.

Se não existir `.github/workflows/staging-deploy.yml`, criar:
```yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: imos_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: --health-cmd "redis-cli ping"

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements/testing.txt

      - name: Run lint
        run: make lint

      - name: Run security scan
        run: make security

      - name: Run tenant isolation tests
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost/imos_test
          DJANGO_SETTINGS_MODULE: config.settings.testing
        run: pytest tests/tenant_isolation/ -v --tb=short

      - name: Run full test suite
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost/imos_test
          DJANGO_SETTINGS_MODULE: config.settings.testing
        run: pytest --cov=apps --cov-fail-under=80

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to DigitalOcean App Platform
        uses: digitalocean/app_action@v1.1.5
        with:
          app_name: imos-staging
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
```

---

## Tarefa 4 — Variáveis de ambiente necessárias (checklist)

Configurar no DO App Platform (Settings → App-Level Env Vars):

```
SECRET_KEY                = <gerar com python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DJANGO_SETTINGS_MODULE    = config.settings.staging
DATABASE_URL              = <DO Managed PostgreSQL URL>
REDIS_URL                 = <DO Managed Redis URL>
ALLOWED_HOSTS             = *.ondigitalocean.app,staging.imos.cv
DO_SPACES_KEY             = <DO Spaces Access Key>
DO_SPACES_SECRET          = <DO Spaces Secret>
DO_SPACES_BUCKET          = imos-staging
DO_SPACES_ENDPOINT        = https://fra1.digitaloceanspaces.com
WHATSAPP_ENABLED          = false   # desactivado em staging
AWS_ACCESS_KEY_ID         = <alias de DO_SPACES_KEY>
AWS_SECRET_ACCESS_KEY     = <alias de DO_SPACES_SECRET>
```

Adicionar ao GitHub Secrets:
```
DIGITALOCEAN_ACCESS_TOKEN = <DO personal access token>
```

---

## Verificação final

- [ ] Push para `develop` → GitHub Actions corre testes automaticamente
- [ ] Testes tenant isolation passam em CI
- [ ] Deploy automático para DO staging após testes passarem
- [ ] `https://staging.imos.cv/api/v1/health/` → `{"status": "ok"}`
- [ ] `https://staging.imos.cv/api/docs/` → Swagger acessível
- [ ] `python manage.py check --deploy` sem erros críticos
