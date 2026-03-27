# Sprint 8 — CI/CD DigitalOcean App Platform

## Contexto

O `.do/app.yaml` já existe (Sprint inicial). O objectivo é ter um pipeline
GitHub Actions completo: lint → test → build → deploy automático em push para `main`.

O DigitalOcean App Platform faz o deploy via spec file (`app.yaml`). O pipeline
deve:
1. Correr testes (pytest + tenant isolation)
2. Build da imagem Docker
3. Push para DigitalOcean Container Registry
4. Trigger de deploy via `doctl`

## Pré-requisitos — Ler antes de começar

```
.do/app.yaml                    → spec do App Platform (já existe)
.github/workflows/              → verificar se existe CI
docker-compose.dev.yml          → referência para a stack
requirements/production.txt     → deps de produção
config/settings/production.py   → settings de produção (verificar se existe)
```

```bash
cat .do/app.yaml
ls .github/workflows/ 2>/dev/null || echo "No CI yet"
cat config/settings/production.py 2>/dev/null | head -30
```

## Skills a carregar

```
@.claude/skills/15-infrastructure/docker-cicd/SKILL.md
@.claude/skills/15-infrastructure/digitalocean-deploy/SKILL.md
@.claude/skills/14-testing/pytest-fixtures/SKILL.md
@.claude/skills/16-security-compliance/secrets-management/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `migration-orchestrator` | GitHub Actions workflow + settings de produção |
| `isolation-test-writer` | Garantir testes correm em CI sem DB real |

---

## Tarefa 1 — GitHub Actions: CI workflow

Criar `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "20"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install -r requirements/development.txt
      - run: black --check apps/ config/
      - run: flake8 apps/ config/ --max-line-length=120
      - run: isort --check-only apps/ config/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:15-3.4
        env:
          POSTGRES_DB: imos_test
          POSTGRES_USER: imos
          POSTGRES_PASSWORD: testpassword
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install -r requirements/development.txt
      - name: Run tests
        env:
          DJANGO_SETTINGS_MODULE: config.settings.testing
          DATABASE_URL: postgres://imos:testpassword@localhost:5432/imos_test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: ci-test-secret-key-not-for-production
        run: |
          pytest tests/ \
            --cov=apps \
            --cov-report=term-missing \
            --cov-fail-under=75 \
            -x \
            --tb=short

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: cd frontend && npm ci
      - run: cd frontend && npm run build
        env:
          NEXT_PUBLIC_API_URL: https://api.imos.cv
          SKIP_ENV_VALIDATION: true

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install bandit safety
      - run: bandit -r apps/ -ll -x apps/*/tests/,apps/*/migrations/
      - run: safety check -r requirements/production.txt || true  # non-blocking
```

---

## Tarefa 2 — GitHub Actions: Deploy workflow

Criar `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: []  # Run independently (CI is on PR, deploy is on merge)
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Build and push Django image
        env:
          REGISTRY: registry.digitalocean.com/imos-registry
        run: |
          doctl registry login
          docker build -f docker/Dockerfile.staging -t $REGISTRY/imos-web:${{ github.sha }} .
          docker push $REGISTRY/imos-web:${{ github.sha }}

      - name: Deploy to App Platform
        run: |
          doctl apps update ${{ secrets.DO_APP_ID }} --spec .do/app.yaml

      - name: Run migrations on production
        run: |
          doctl apps logs ${{ secrets.DO_APP_ID }} --type=deploy --follow --wait
          # Migrations are run as part of the app deploy (release command in app.yaml)

      - name: Notify on Slack
        if: always()
        uses: rtCamp/action-slack-notify@v2
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
          SLACK_MESSAGE: "Deploy ${{ job.status }} — ${{ github.sha }}"
```

---

## Tarefa 3 — Settings de produção

Verificar/criar `config/settings/production.py`:

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*.imos.cv', 'imos.cv'])

# Database — via DATABASE_URL env var
DATABASES = {
    'default': env.db('DATABASE_URL'),
}
DATABASES['default']['CONN_MAX_AGE'] = 60

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static + Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = f"https://{env('DO_SPACES_BUCKET')}.{env('DO_SPACES_REGION')}.digitaloceanspaces.com/"

# Sentry
import sentry_sdk
sentry_sdk.init(
    dsn=env('SENTRY_DSN', default=''),
    traces_sample_rate=0.1,
    environment='production',
)

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@imos.cv')
```

---

## Tarefa 4 — Dockerfile de staging/produção

Verificar/criar `docker/Dockerfile.staging`:

```dockerfile
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev libpq-dev gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

WORKDIR /app

# Install Python deps
COPY requirements/production.txt ./
RUN pip install --no-cache-dir -r production.txt

# Copy application
COPY . .

# Collect static
RUN python manage.py collectstatic --noinput

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60"]
```

---

## Tarefa 5 — requirements/production.txt

Verificar que `requirements/production.txt` existe e tem:
```
-r base.txt
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.6.0
django-storages[boto3]==1.14.2
boto3==1.34.0
sentry-sdk[django]==1.44.1
django-prometheus==2.3.1
django-csp==3.8
django-permissions-policy==4.28.0
```

## GitHub Secrets necessários

Documentar no `.env.example` os secrets que devem estar no GitHub:
```
DIGITALOCEAN_ACCESS_TOKEN   → token de acesso à DO API
DO_APP_ID                   → ID da app no App Platform
SLACK_WEBHOOK               → webhook para notificações de deploy
SENTRY_DSN                  → DSN do projecto Sentry
```

## Verificação final

- [ ] `gh workflow run ci.yml` → passa lint + test + build
- [ ] `git push origin main` → trigger deploy automático
- [ ] Django Admin em `https://api.imos.cv/admin/` acessível após deploy
- [ ] `/api/v1/health/` retorna 200 em staging
- [ ] Migrations executadas automaticamente em staging
- [ ] Sentry recebe erros de staging
