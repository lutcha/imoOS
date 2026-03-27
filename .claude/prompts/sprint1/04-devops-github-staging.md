# Sprint 1 — DevOps: GitHub Push + Staging DigitalOcean

## Pré-requisitos antes de fazer push

**Verificar ANTES de qualquer `git push`:**

```bash
# 1. Não há secrets no código
grep -r "SECRET_KEY\|PASSWORD\|API_KEY" apps/ config/ --include="*.py" | grep -v ".env"

# 2. .env* está no .gitignore
cat .gitignore | grep ".env"

# 3. CI passa localmente
make lint
make test
pytest tests/tenant_isolation/ -v  # OBRIGATÓRIO — zero falhas

# 4. Migrations estão geradas
python manage.py migrate_schemas --check
```

## Skills a carregar

```
@.claude/skills/15-infrastructure/docker-compose-dev/SKILL.md
@.claude/skills/15-infrastructure/ci-cd-pipeline/SKILL.md
@.claude/skills/16-security-compliance/secrets-management/SKILL.md
```

## Passo 1 — Repositório GitHub

### Criar repositório

```bash
# Via GitHub CLI
gh repo create imoos-cv/imoos --private --description "ImoOS — Sistema Operativo para Promotoras Imobiliárias"

# Ou via UI: github.com/new
# Nome: imoos  |  Org: imoos-cv  |  Privado  |  Sem README/gitignore (já temos)
```

### .gitignore — verificar que existe e inclui:

```
# Obrigatório
.env
.env.*
!.env.example
*.pyc
__pycache__/
.pytest_cache/
staticfiles/
mediafiles/
node_modules/
frontend/.next/
mobile/.expo/
*.sqlite3
```

### Push inicial

```bash
cd /c/Dev/imos

# Inicializar git se necessário
git init
git add .
git commit -m "feat: Sprint 0 completo — estrutura, modelos, CI, skills, agents"

# Ligar ao remoto
git remote add origin https://github.com/imoos-cv/imoos.git
git branch -M main
git push -u origin main

# Criar branch develop
git checkout -b develop
git push -u origin develop
```

### Branch protection (GitHub Settings → Branches)

Para `main` e `develop`:
- [x] Require status checks to pass: `lint`, `test`, `isolation-tests`
- [x] Require branches to be up to date before merging
- [x] Require pull request reviews: 1 approval
- [x] Restrict pushes — só via PR

## Passo 2 — Staging DigitalOcean

### Opção recomendada: App Platform (mais simples para MVP)

**Criar App em app.digitalocean.com:**

1. **Source:** GitHub → repo `imoos-cv/imoos` → branch `develop`
2. **Components:**
   - Web service: `gunicorn config.wsgi:application --workers 2`
   - Worker: `celery -A config worker -l info`
   - Beat: `celery -A config beat -l info`
3. **Database:** PostgreSQL 15 managed (com PostGIS — usar Droplet se App Platform não suportar PostGIS)
4. **Redis:** Redis managed

### Variáveis de ambiente no App Platform

```
DJANGO_SETTINGS_MODULE=config.settings.staging
SECRET_KEY=<gerar com: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DATABASE_URL=<do managed DB>
REDIS_URL=<do managed Redis>
ALLOWED_HOSTS=staging.imos.cv,*.ondigitalocean.app
CORS_ALLOWED_ORIGINS=https://staging.imos.cv
AWS_ACCESS_KEY_ID=<DigitalOcean Spaces>
AWS_SECRET_ACCESS_KEY=<DigitalOcean Spaces>
AWS_STORAGE_BUCKET_NAME=imos-staging
AWS_S3_ENDPOINT_URL=https://fra1.digitaloceanspaces.com
SENTRY_DSN=<criar projecto em sentry.io>
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

### Criar `config/settings/staging.py`

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Staging usa a mesma config que production mas com DEBUG=False
# e com Sentry activo para capturar erros
INSTALLED_APPS += ['django_extensions']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### Comando de deploy (Dockerfile ou Procfile)

**`Procfile`** (raiz do projecto):
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
worker: celery -A config worker --loglevel=info --concurrency 2
beat: celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
release: python manage.py migrate_schemas --shared && python manage.py migrate_schemas
```

## Passo 3 — Sentry

```bash
# Instalar (já deve estar em requirements/base.txt)
pip install sentry-sdk

# Em config/settings/base.py — adicionar:
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

if env('SENTRY_DSN', default=''):
    sentry_sdk.init(
        dsn=env('SENTRY_DSN'),
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,  # LGPD compliance
    )
```

## Passo 4 — CD automático para staging

No ficheiro `.github/workflows/ci.yml` já existente, adicionar job de deploy:

```yaml
  deploy-staging:
    needs: [lint, test, isolation-tests]
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to DigitalOcean App Platform
        uses: digitalocean/app_action@v1
        with:
          app_name: imoos-staging
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
```

Secret `DIGITALOCEAN_ACCESS_TOKEN` → GitHub Settings → Secrets → Actions.

## Verificação final

- [ ] `git push origin develop` dispara CI no GitHub Actions
- [ ] CI jobs: lint ✓ + test ✓ + isolation-tests ✓ + deploy-staging ✓
- [ ] `https://imoos-staging.ondigitalocean.app/api/docs/` acessível
- [ ] `https://imoos-staging.ondigitalocean.app/api/v1/users/auth/token/` retorna JWT
- [ ] Sentry recebe eventos de erro
- [ ] Branch protection activa — push directo para main/develop bloqueado
