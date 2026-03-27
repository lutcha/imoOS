---
name: docker-compose-tenants
description: docker-compose.dev.yml com serviços web/celery/celery-beat/flower/db(postgis)/redis, health checks e volumes montados.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Fornecer o ambiente de desenvolvimento local completo com todos os serviços necessários para o ImoOS multi-tenant. O PostGIS é obrigatório para campos geoespaciais e o Flower permite monitorizar tasks Celery.

## Code Pattern

```yaml
# docker-compose.dev.yml
version: "3.9"

services:
  db:
    image: postgis/postgis:15-3.4
    environment:
      POSTGRES_DB: imoos_dev
      POSTGRES_USER: imoos
      POSTGRES_PASSWORD: imoos_dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U imoos -d imoos_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  web:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
      - ./backend/media:/app/media
    ports:
      - "8000:8000"
    env_file: ./backend/.env.dev
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A imoos worker -l INFO -Q default,high_priority --concurrency=4
    volumes:
      - ./backend:/app
    env_file: ./backend/.env.dev
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A imoos beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - ./backend:/app
    env_file: ./backend/.env.dev
    depends_on:
      - db
      - redis
      - celery

  flower:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A imoos flower --port=5555 --basic_auth=admin:flowerpassword
    ports:
      - "5555:5555"
    env_file: ./backend/.env.dev
    depends_on:
      - redis
      - celery

volumes:
  postgres_data:
  redis_data:
```

```bash
# Comandos úteis de desenvolvimento
docker compose -f docker-compose.dev.yml up -d        # iniciar todos os serviços
docker compose -f docker-compose.dev.yml logs -f web  # logs do servidor Django
docker compose -f docker-compose.dev.yml exec web python manage.py create_tenant demo admin@demo.cv
```

## Key Rules

- Usar `postgis/postgis:15-3.4` (não `postgres:15`) — necessário para `django.contrib.gis`.
- Definir `depends_on` com `condition: service_healthy` para evitar erros de arranque em cascata.
- O Flower deve ter autenticação básica em desenvolvimento — nunca expor sem autenticação.
- Montar `./backend:/app` como volume para hot-reload em desenvolvimento.

## Anti-Pattern

```yaml
# ERRADO: usar imagem postgres standard sem PostGIS
db:
  image: postgres:15  # sem extensão postgis — falha ao carregar modelos com PointField
```
