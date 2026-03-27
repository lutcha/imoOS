---
name: github-actions-ci-cd
description: CI com lint→test→isolation-tests→coverage→security. CD staging em push para develop (Docker, registry, DO App Platform). CD prod em tag v*.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Automatizar a pipeline de integração e entrega contínua do ImoOS. A separação em CI/CD staging/CD prod garante que o código é validado completamente antes de chegar a produção.

## Code Pattern

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [develop]

jobs:
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install ruff black isort
      - run: ruff check backend/
      - run: black --check backend/
      - run: isort --check-only backend/

  test:
    name: Unit & Integration Tests
    runs-on: ubuntu-latest
    needs: lint
    services:
      db:
        image: postgis/postgis:15-3.4
        env: { POSTGRES_DB: test_db, POSTGRES_USER: imoos, POSTGRES_PASSWORD: test }
        options: --health-cmd pg_isready --health-interval 10s --health-retries 5
      redis:
        image: redis:7-alpine
        options: --health-cmd "redis-cli ping" --health-interval 10s

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r backend/requirements/test.txt
      - name: Run Tests with Coverage
        run: |
          cd backend
          pytest --cov=. --cov-report=xml --cov-fail-under=80 \
            -m "not isolation"  # testes de isolamento separados
        env:
          DATABASE_URL: postgis://imoos:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0

      - uses: codecov/codecov-action@v4
        with: { file: backend/coverage.xml }

  isolation-tests:
    name: Tenant Isolation Tests
    runs-on: ubuntu-latest
    needs: test
    services:
      db:
        image: postgis/postgis:15-3.4
        env: { POSTGRES_DB: test_db, POSTGRES_USER: imoos, POSTGRES_PASSWORD: test }
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r backend/requirements/test.txt
      - run: cd backend && pytest -m "isolation" -v
        env:
          DATABASE_URL: postgis://imoos:test@localhost:5432/test_db
```

```yaml
# .github/workflows/cd-staging.yml
name: CD Staging

on:
  push:
    branches: [develop]

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and Push Docker Image
        run: |
          docker build -t registry.digitalocean.com/imoos/backend:staging-${{ github.sha }} ./backend
          docker push registry.digitalocean.com/imoos/backend:staging-${{ github.sha }}
        env:
          DOCKER_REGISTRY_TOKEN: ${{ secrets.DO_REGISTRY_TOKEN }}

      - name: Deploy to DO App Platform (Staging)
        uses: digitalocean/app_action@v2
        with:
          app_name: imoos-staging
          token: ${{ secrets.DO_API_TOKEN }}
          images: '[{"name":"web","image":{"registry_type":"DOCR","repository":"imoos/backend","tag":"staging-${{ github.sha }}"}}]'
```

```yaml
# .github/workflows/cd-prod.yml
name: CD Production

on:
  push:
    tags: ["v*"]  # ex: v1.2.0

jobs:
  deploy-prod:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment: production  # requer aprovação manual
    steps:
      - uses: actions/checkout@v4
      - name: Build and Deploy to Production
        run: |
          docker build -t registry.digitalocean.com/imoos/backend:${{ github.ref_name }} ./backend
          docker push registry.digitalocean.com/imoos/backend:${{ github.ref_name }}
```

## Key Rules

- Os testes de isolamento de tenant devem correr separadamente dos testes unitários — usar `@pytest.mark.isolation`.
- O CD de produção deve usar `environment: production` do GitHub para exigir aprovação manual.
- A cobertura mínima de 80% deve bloquear o merge — configurar como required status check.
- Usar `needs:` para garantir a ordem: lint → test → isolation-tests → deploy.

## Anti-Pattern

```yaml
# ERRADO: fazer deploy direto para produção sem aprovação manual
on:
  push:
    branches: [main]
# Deploy automático para produção em cada push — sem gate de aprovação
```
