# ImoOS — AI Agent Guide

This document provides essential context for AI coding agents working on the ImoOS codebase.

---

## Project Overview

**ImoOS** (Imobiliária Operating System) is a multi-tenant SaaS platform for real estate companies (promotoras imobiliárias) in Cape Verde and Portuguese/French-speaking African markets. It provides an integrated system for managing real estate projects, inventory, sales, contracts, construction, and investor relations.

### Key Characteristics

- **Multi-tenant architecture**: Each real estate company gets an isolated PostgreSQL schema
- **SaaS model**: Subscription plans (Starter, Pro, Enterprise) with different resource limits
- **Multi-platform**: Web (Next.js), Mobile (React Native), and REST API
- **Localization**: Primary language is Portuguese (Cabo Verde), with support for Angola and Senegal

---

## Technology Stack

### Backend (Django)

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Django | 4.2.9 |
| API | Django REST Framework | 3.14.0 |
| Multi-tenancy | django-tenants | 3.5.0 |
| Authentication | djangorestframework-simplejwt | 5.3.1 |
| Database | PostgreSQL + PostGIS | 15 |
| Cache/Queue | Redis | 7 |
| Tasks | Celery + Celery Beat | 5.3.6 |
| Storage | S3-compatible (DigitalOcean Spaces) | - |

### Frontend

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Next.js | 15.1.6 |
| React | React | 19.2.3 |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 4.x |
| State | TanStack Query | 5.x |
| Testing | Vitest + Playwright | - |

### Mobile

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | React Native | 0.84.1 |
| Navigation | React Navigation | 6.x |
| Database | WatermelonDB | 0.28.0 |
| Platform | iOS & Android | - |

---

## Project Structure

```
imos/
├── apps/                      # Django applications
│   ├── core/                  # Shared utilities, pagination, throttling
│   ├── tenants/               # Multi-tenant management (SHARED_APP)
│   ├── users/                 # Custom user model (SHARED_APP)
│   ├── memberships/           # Per-tenant user roles (TENANT_APP)
│   ├── projects/              # Real estate projects (TENANT_APP)
│   ├── inventory/             # Property units (TENANT_APP)
│   ├── crm/                   # Customer relationship (TENANT_APP)
│   ├── sales/                 # Sales/reservations (TENANT_APP)
│   ├── contracts/             # Contract management (TENANT_APP)
│   ├── payments/              # Payment tracking (TENANT_APP)
│   ├── construction/          # Construction management (TENANT_APP)
│   ├── marketplace/           # imo.cv integration (TENANT_APP)
│   └── investors/             # Investor portal (TENANT_APP)
├── config/                    # Django configuration
│   ├── settings/              # Environment-specific settings
│   │   ├── base.py            # Common settings
│   │   ├── development.py     # Local dev
│   │   ├── testing.py         # Test settings
│   │   ├── staging.py         # Staging env
│   │   └── production.py      # Production env
│   ├── urls.py                # Main URL configuration
│   ├── urls_public.py         # Public schema URLs
│   ├── wsgi.py                # WSGI entry point
│   ├── asgi.py                # ASGI entry point
│   └── celery.py              # Celery configuration
├── frontend/                  # Next.js web application
│   ├── src/
│   │   ├── app/               # Next.js App Router pages
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilities
│   │   └── test/              # Test utilities
│   ├── tests/                 # Playwright E2E tests
│   └── package.json
├── mobile/                    # React Native mobile app
│   ├── src/
│   │   ├── screens/           # App screens
│   │   ├── components/        # Shared components
│   │   ├── auth/              # Authentication
│   │   ├── data/              # Data layer
│   │   └── notifications/     # Push notifications
│   ├── ios/                   # iOS native code
│   ├── android/               # Android native code
│   └── package.json
├── tests/                     # Backend test suite
│   ├── conftest.py            # pytest fixtures
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── tenant_isolation/      # MANDATORY isolation tests
├── requirements/              # Python dependencies
│   ├── base.txt               # Production dependencies
│   ├── development.txt        # Dev + test dependencies
│   └── production.txt         # Production-only
├── docker/                    # Docker configurations
│   ├── Dockerfile.dev         # Development image
│   └── Dockerfile.staging     # Staging/production image
├── docs/                      # Documentation (Portuguese)
├── .github/workflows/         # CI/CD pipelines
│   ├── ci.yml                 # Main CI pipeline
│   ├── frontend-ci.yml        # Frontend checks
│   ├── deploy-staging.yml     # Staging deployment
│   └── deploy-production.yml  # Production deployment
├── Makefile                   # Development commands
├── manage.py                  # Django management
├── docker-compose.dev.yml     # Local development stack
├── pytest.ini                # pytest configuration
└── SECURITY.md               # Security documentation
```

---

## Multi-Tenant Architecture

### Schema Separation

```python
# SHARED_APPS - stored in public schema
SHARED_APPS = [
    'django_tenants',
    'apps.tenants',      # Tenant model
    'apps.users',        # Global user authentication
    'apps.core',         # Shared utilities
    # ... Django core, third-party
]

# TENANT_APPS - stored in each tenant's schema
TENANT_APPS = [
    'apps.memberships',   # Per-tenant roles
    'apps.projects',      # Business data
    'apps.inventory',
    'apps.crm',
    # ... other business modules
]
```

### Tenant Identification

Tenants are identified by subdomain:
- `empresa-a.imos.cv` → schema `empresa_a`
- `empresa-b.imos.cv` → schema `empresa_b`

Middleware (`apps.tenants.middleware.ImoOSTenantMiddleware`) handles routing based on the `Host` header.

### Important Rules

1. **Never create tenant data in public schema** - Always use `tenant_context(tenant)` or ensure middleware has set the correct schema
2. **JWT tokens include tenant schema** - The `tenant_schema` claim in JWT ensures users can only access their tenant
3. **Run migrations for both schemas** - Use `migrate_schemas` (not just `migrate`)

---

## Build and Development Commands

### Backend (Django)

```bash
# Setup
pip install -r requirements/development.txt

# Database migrations
python manage.py migrate_schemas --shared    # Public schema only
python manage.py migrate_schemas             # All schemas

# Create tenant
python manage.py create_tenant --schema=empresa_a --name="Empresa A" --domain=empresa-a.imos.cv

# Run server
python manage.py runserver

# Shell
python manage.py shell_plus
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev          # Development server (port 3000)
npm run build        # Production build
npm run lint         # ESLint
npm test             # Vitest unit tests
npm run test:e2e     # Playwright E2E tests
npm run storybook    # Component stories
```

### Mobile (React Native)

```bash
cd mobile
npm install

# iOS
bundle install
cd ios && bundle exec pod install && cd ..
npm run ios

# Android
npm run android
```

### Docker (Recommended for Development)

```bash
# Start all services
make up              # docker-compose up

# Other useful commands
make build           # Build images
make down            # Stop services
make migrate         # Run migrations
make shell           # Django shell
make logs            # Tail logs
make test            # Run tests
make test-isolation  # Run MANDATORY tenant isolation tests
make coverage        # Run tests with coverage
make lint            # Check code style
make format          # Auto-format code
make security        # Run security scans
make create-tenant schema=X name=Y domain=Z   # Create new tenant
```

---

## Testing Strategy

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage (minimum 80%)
pytest --cov=apps --cov-report=html --cov-fail-under=80

# Run specific test types
pytest tests/unit/                           # Unit tests
pytest tests/integration/                    # Integration tests
pytest tests/tenant_isolation/ -v            # MANDATORY isolation tests
pytest -m "isolation"                        # Tests marked as isolation
pytest -m "not isolation"                    # Skip isolation tests
```

### Critical: Tenant Isolation Tests

Tenant isolation tests are **MANDATORY** and **BLOCK merges** if they fail. Located in `tests/tenant_isolation/`:

- `test_jwt_isolation.py` - JWT token scoping
- `test_core_isolation.py` - Core data isolation
- `test_contract_isolation.py` - Contract isolation
- `test_payment_isolation.py` - Payment isolation
- `test_construction_isolation.py` - Construction data isolation
- `test_marketplace_isolation.py` - Marketplace isolation
- `test_investor_isolation.py` - Investor data isolation
- `test_reservation_isolation.py` - Reservation isolation

### Frontend Tests

```bash
cd frontend
npm test             # Vitest unit tests
npm run test:ui      # Vitest with UI
npm run test:e2e     # Playwright E2E tests
npm run test:e2e:ui  # Playwright with UI
```

---

## Code Style Guidelines

### Python

- **Formatter**: Black (line length: 88)
- **Import sorting**: isort
- **Linter**: flake8 (max line length: 120)
- **Type checking**: mypy with django-stubs

```bash
make format   # Auto-format with black + isort
make lint     # Check with flake8, isort, black
```

### TypeScript/JavaScript (Frontend)

- **Linter**: ESLint (Next.js config)
- **Formatter**: Prettier (via ESLint)
- Follow Next.js App Router conventions

### Code Conventions

1. **Models**: Use UUID primary keys, include `HistoricalRecords` for audit
2. **Serializers**: Validate tenant-scoped relationships
3. **Views**: Use DRF viewsets, check permissions, throttle by tenant
4. **Tests**: Use fixtures from `conftest.py`, always reset schema after tenant tests

---

## Security Considerations

### Authentication & Authorization

- JWT tokens with `tenant_schema` claim prevent cross-tenant access
- Object-level permissions via django-guardian
- Role-based access control via `apps.memberships`

### Security Headers

Configured in `config/settings/base.py`:
- Content Security Policy (CSP)
- HSTS (production)
- X-Frame-Options: DENY
- Secure cookies (HTTPS only in production)

### Secrets Management

- All secrets in environment variables (never in code)
- `.env` file is gitignored
- Use `.env.example` as template
- DigitalOcean App Platform uses encrypted env vars

### Security Scanning

```bash
make security    # Run bandit + safety

# Manual scans
bandit -r apps/ -ll -q
safety check -r requirements/base.txt
```

### Rate Limiting

- Anonymous: 100/hour
- Authenticated: 1000/hour
- Per-tenant: 5000/hour

---

## Deployment Process

### Environments

1. **Local**: Docker Compose (`docker-compose.dev.yml`)
2. **Staging**: DigitalOcean App Platform (auto-deploy on `develop` push)
3. **Production**: DigitalOcean App Platform (manual deploy)

### CI/CD Pipeline

```
Push to develop → CI (lint, test, isolation) → Deploy Staging → Smoke Test
Push to main    → CI → Deploy Production (manual trigger)
```

### Configuration Files

- `imos-staging.yaml` - DigitalOcean App Platform spec for staging
- `.github/workflows/deploy-staging.yml` - Staging deployment
- `.github/workflows/deploy-production.yml` - Production deployment
- `Procfile` - Heroku-style process definition (fallback)

---

## Database Migrations

### Important: Multi-Tenant Migrations

Always use `migrate_schemas` instead of `migrate`:

```bash
# Public schema only (shared apps)
python manage.py migrate_schemas --shared

# Specific tenant
python manage.py migrate_schemas --schema=empresa_a

# All tenants (including public)
python manage.py migrate_schemas
```

### Creating Migrations

```bash
# Create migration for an app
python manage.py makemigrations <app_name>

# Apply to all schemas
python manage.py migrate_schemas
```

---

## Common Tasks

### Creating a New App

1. Create directory in `apps/<app_name>/`
2. Add to `TENANT_APPS` or `SHARED_APPS` in `config/settings/base.py`
3. Create `models.py`, `views.py`, `urls.py`, `serializers.py`
4. Create migrations: `python manage.py makemigrations <app_name>`
5. Run migrations: `python manage.py migrate_schemas`
6. Add tests in `tests/unit/` or `tests/integration/`

### Adding an API Endpoint

1. Create/update `views.py` in the appropriate app
2. Add URL pattern in app's `urls.py`
3. Include in `config/urls.py`
4. Add tests
5. Update API documentation (auto-generated via drf-spectacular)

### Adding a Tenant-Aware Model

```python
# In a TENANT_APP
from django.db import models
from simple_history.models import HistoricalRecords

class MyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
```

---

## Language and Localization

- **Code**: English (variables, functions, comments)
- **User-facing text**: Portuguese (Cabo Verde)
- **Model verbose names**: Portuguese
- **Documentation**: Mixed (Portuguese for business docs, English for technical)

Supported locales:
- `pt-pt` - Português (Cabo Verde) - default
- `pt-ao` - Português (Angola)
- `fr-sn` - Français (Sénégal)

Timezone: `Atlantic/Cape_Verde`

---

## External Integrations

### imo.cv Marketplace

Integration for publishing properties:
- API endpoint: `https://api.imo.cv/v1`
- Configured per-tenant in `TenantSettings`

### WhatsApp Business API

For notifications:
- Meta Cloud API
- Phone number ID and access token in env vars

### S3-Compatible Storage

DigitalOcean Spaces for file storage:
- Endpoint: `https://fra1.digitaloceanspaces.com`
- Files organized by tenant: `tenants/{slug}/`

---

## Troubleshooting

### Common Issues

**Migration errors with django-tenants**:
```bash
# Reset and recreate schema
python manage.py shell
>>> from django_tenants.utils import schema_context
>>> with schema_context('public'):
...     # Fix operations
```

**Tenant not found**:
- Check `HTTP_HOST` header matches domain in `domains` table
- Verify tenant `is_active=True`

**Celery tasks not running**:
- Check Redis connection
- Verify `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`
- Check worker logs: `make logs` or `docker logs <celery-container>`

**Frontend API errors**:
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check CORS settings in Django
- Ensure tenant domain is correct

---

## Resources

- **API Docs**: `/api/docs/` (Swagger UI) or `/api/redoc/` (ReDoc)
- **Schema**: `/api/schema/` (OpenAPI)
- **Health Check**: `/api/v1/health/`
- **Security Docs**: `SECURITY.md`
- **Django Admin**: `/django-admin/` (configurable via `DJANGO_SUPERADMIN_URL`)

---

*Last updated: 2026-04-04*
