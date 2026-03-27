---
name: secret-management-vault
description: django-decouple para leitura de .env em desenvolvimento, em produção todos os segredos vêm de variáveis de ambiente (DO App Platform secrets), nunca commitar .env, .env.example documenta todas as variáveis.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir que nenhum segredo (chaves API, passwords, tokens) é versionado no repositório git. A separação entre desenvolvimento (`.env`) e produção (variáveis de ambiente da plataforma) previne fugas acidentais.

## Code Pattern

```python
# settings/base.py
from decouple import config, Csv

# Segredos — NUNCA ter valores padrão para segredos em produção
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

# Base de dados
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": config("DB_NAME", default="imoos"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Redis & Celery
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/1"),
    }
}

# AWS S3
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="fra1")
AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN")

# APIs Externas
IMO_CV_API_URL = config("IMO_CV_API_URL", default="https://api.imo.cv/v1")
IMO_CV_API_TOKEN = config("IMO_CV_API_TOKEN")
IMO_CV_WEBHOOK_SECRET = config("IMO_CV_WEBHOOK_SECRET")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
DOCUSIGN_ACCOUNT_ID = config("DOCUSIGN_ACCOUNT_ID")

# Sentry
SENTRY_DSN = config("SENTRY_DSN", default="")
SENTRY_RELEASE = config("SENTRY_RELEASE", default="local")
```

```bash
# .env.example — COMMITAR ESTE FICHEIRO (sem valores reais)
# Copiar para .env e preencher com valores reais para desenvolvimento local
# NUNCA commitar o ficheiro .env

# Django
DJANGO_SECRET_KEY=gerar-com-python-c-import-secrets-print-secrets.token_hex-50
DEBUG=True
ENVIRONMENT=development

# Base de Dados PostgreSQL + PostGIS
DB_NAME=imoos_dev
DB_USER=imoos
DB_PASSWORD=password_desenvolvimento_local
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3 (DO Spaces em produção)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=imoos-dev-media
AWS_S3_REGION_NAME=fra1
AWS_S3_CUSTOM_DOMAIN=imoos-dev-media.fra1.cdn.digitaloceanspaces.com

# APIs Externas
IMO_CV_API_URL=https://api.imo.cv/v1
IMO_CV_API_TOKEN=token-de-teste
IMO_CV_WEBHOOK_SECRET=webhook-secret-de-teste

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Sentry (deixar vazio em desenvolvimento)
SENTRY_DSN=
```

```gitignore
# .gitignore — adicionar obrigatoriamente
.env
.env.local
.env.*.local
*.pem
*.key
```

## Key Rules

- `config("KEY")` sem valor padrão lança `UndefinedValueError` se a variável não existir — desejável em produção.
- Usar `cast=bool` para variáveis booleanas — `"False"` como string é `True` em Python sem cast.
- O `.env.example` deve estar sempre atualizado quando se adiciona uma nova variável de configuração.
- Em produção (DO App Platform), configurar segredos como "App-Level Secrets" — são encriptados em repouso.

## Anti-Pattern

```python
# ERRADO: valor padrão para segredos em produção
SECRET_KEY = config("DJANGO_SECRET_KEY", default="chave-insegura-padrao")
# Se a variável não estiver definida em prod, usa o valor padrão inseguro silenciosamente
```
