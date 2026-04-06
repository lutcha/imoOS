# ImoOS Deployment Guide

## Overview

ImoOS is deployed on **DigitalOcean App Platform** with the following architecture:

- **Frontend**: Next.js 15 (Port 3000)
- **Backend API**: Django 4.2 (Port 8000)  
- **Database**: PostgreSQL 15 (Managed)
- **Cache/Queue**: Redis (Valkey)
- **Workers**: Celery + Celery Beat

## Environments

### Staging
- **URL**: https://imos-staging-jiow3.ondigitalocean.app
- **Branch**: `develop`
- **Auto-deploy**: Enabled on push

### Production (Future)
- **URL**: https://proptech.cv
- **Branch**: `main`
- **Auto-deploy**: Manual approval required

## Deployment Process

### Automatic Deployment

1. Push to `develop` branch
2. GitHub webhook triggers DigitalOcean
3. Build process starts (Docker containers)
4. Migration job runs
5. Health checks pass
6. New deployment goes live

### Manual Deployment

```bash
# Using doctl
doctl apps create-deployment <app-id>

# Or via web console
# Apps > imos-staging > Deployments > Deploy
```

## Pre-Deployment Checklist

- [ ] All tests pass (`pytest`)
- [ ] Frontend builds locally (`npm run build`)
- [ ] Migrations are backwards compatible
- [ ] Environment variables are set
- [ ] No sensitive data in commits

## Environment Variables

### Required

| Variable | Description | Staging Value |
|----------|-------------|---------------|
| `DJANGO_SETTINGS_MODULE` | Django settings path | `config.settings.staging` |
| `SECRET_KEY` | Django secret key | [Secret] |
| `DB_NAME` | Database name | `${db.DATABASE}` |
| `DB_USER` | Database user | `${db.USERNAME}` |
| `DB_PASSWORD` | Database password | [Secret] |
| `DB_HOST` | Database host | `${db.HOSTNAME}` |
| `DB_PORT` | Database port | `${db.PORT}` |
| `REDIS_URL` | Redis connection URL | `${redis.DATABASE_URL}` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | [Secret] |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | [Secret] |
| `TWILIO_WHATSAPP_NUMBER` | WhatsApp number | `+14155238886` |

### Optional

| Variable | Description |
|----------|-------------|
| `SENTRY_DSN` | Error tracking |
| `AWS_ACCESS_KEY_ID` | Spaces object storage |
| `AWS_SECRET_ACCESS_KEY` | Spaces secret |
| `AWS_STORAGE_BUCKET_NAME` | Bucket name |

## Troubleshooting

### Build Failures

Check build logs:
```bash
doctl apps logs <app-id> <component> --type build
```

Common issues:
- **Frontend**: Check `npm install` output
- **Backend**: Verify Python dependencies
- **Migrations**: Database permission errors

### Runtime Issues

Check runtime logs:
```bash
doctl apps logs <app-id> <component>
```

Components: `api`, `frontend`, `celery-worker`, `celery-beat`, `migrate`

### Database Issues

Managed PostgreSQL doesn't allow `CREATE SCHEMA`:
- Tenants must be created via Django shell
- Use management commands: `create_tenant`, `create_demo_tenant`

## Initial Setup

### 1. Create Superuser

```bash
curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/superuser/ \
  -H "Content-Type: application/json" \
  -H "X-Setup-Token: imos-setup-2026" \
  -d '{
    "email": "admin@proptech.cv",
    "password": "SecurePass123!"
  }'
```

### 2. Check Setup Status

```bash
curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/status/
```

### 3. Create Demo Tenant

```bash
# Via Django shell
python manage.py create_demo_tenant
python manage.py seed_demo_data --tenant=demo_promotora
```

## Rollback

To rollback to a previous deployment:

1. Go to DigitalOcean Console
2. Apps > imos-staging > Deployments
3. Find the previous working deployment
4. Click "Rollback"

Or via CLI:
```bash
doctl apps create-deployment <app-id> --commit <commit-hash>
```

## Health Checks

- **API**: `/api/v1/health/` - Returns 200 if healthy
- **Detailed**: `/api/v1/health/detailed/` - Full system status
- **Frontend**: `/` - Should render without errors

## Domain Configuration

### Custom Domains

Configured domains:
- `imos-staging-jiow3.ondigitalocean.app` (Primary)
- `proptech.cv` (Alias - pending DNS verification)
- `www.proptech.cv` (Alias)
- `demo.proptech.cv` (Alias)

### DNS Setup

Point your domain to DigitalOcean:
```
CNAME proptech.cv -> imos-staging-jiow3.ondigitalocean.app
```

Or use A records to the provided IPs.

## Support

- **Documentation**: `/api/docs/` (Swagger UI)
- **API Schema**: `/api/schema/`
- **Admin**: `/django-admin/`
