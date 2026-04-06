# ImoOS Documentation

## Table of Contents

1. [Architecture Overview](./ARCHITECTURE.md)
2. [Deployment Guide](./DEPLOYMENT_GUIDE.md)
3. [API Guide](./API_GUIDE.md)
4. [Development Setup](./DEVELOPMENT.md)
5. [Testing Guide](./TESTING.md)

## Quick Links

- **Staging URL**: https://imos-staging-jiow3.ondigitalocean.app
- **API Docs**: https://imos-staging-jiow3.ondigitalocean.app/api/docs/
- **Admin Panel**: https://imos-staging-jiow3.ondigitalocean.app/django-admin/

## Project Overview

ImoOS is a comprehensive Construction Intelligence Platform built for the Cape Verde market.

### Features

- **CRM**: Lead management and conversion
- **Project Management**: Units, reservations, contracts
- **Construction Management**: Tasks, phases, Gantt charts, EVM
- **Budget**: Local price database, Excel import/export
- **WhatsApp Integration**: Automated notifications
- **BIM Viewer**: IFC file visualization
- **Mobile PWA**: Offline-first construction tracking
- **Dashboard**: Real-time analytics

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS |
| Backend | Django 4.2, Django REST Framework |
| Database | PostgreSQL 15 (Multi-tenant with django-tenants) |
| Cache | Redis (Valkey) |
| Queue | Celery + Celery Beat |
| Storage | DigitalOcean Spaces (S3-compatible) |
| Hosting | DigitalOcean App Platform |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15
- Redis 7

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements/local.txt

# Setup database
python manage.py migrate_schemas --shared
python manage.py migrate_schemas

# Create superuser
python manage.py setup_superuser

# Run server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Run dev server
npm run dev
```

### Environment Variables

See [.env.example](../.env.example) for required variables.

## Project Structure

```
├── apps/                    # Django applications
│   ├── core/               # Core utilities, setup
│   ├── users/              # User management
│   ├── tenants/            # Multi-tenancy
│   ├── crm/                # CRM (Leads)
│   ├── projects/           # Real estate projects
│   ├── contracts/          # Sales contracts
│   ├── construction/       # Construction management
│   ├── budget/             # Budget & pricing
│   ├── integrations/       # WhatsApp, external APIs
│   ├── workflows/          # Automated workflows
│   └── ...
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utilities
│   └── ...
├── tests/                  # Test suites
│   ├── e2e/               # End-to-end tests
│   ├── integration/       # Integration tests
│   └── tenant_isolation/  # Multi-tenancy tests
├── docs/                   # Documentation
└── docker/                 # Docker configurations
```

## Testing

```bash
# Run all tests
pytest

# Run E2E tests only
pytest tests/e2e/ -v

# Run with coverage
pytest --cov=apps --cov-report=html
```

## Deployment

See [Deployment Guide](./DEPLOYMENT_GUIDE.md) for detailed instructions.

## API Reference

See [API Guide](./API_GUIDE.md) for endpoint documentation.

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Run tests
4. Submit a pull request

## License

Proprietary - All rights reserved.

## Support

For support, contact: support@proptech.cv
