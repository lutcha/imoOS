---
name: schema-migrations
description: Manage Django migrations for multi-tenant schemas — shared vs tenant scope, safe rollout, and rollback procedures. Use when creating or running migrations.
argument-hint: [migration-type] [app-name]
allowed-tools: Read, Write, Bash
---

# Multi-Tenant Migration Patterns — ImoOS

## Migration Types

### Shared Schema (public) — auth/tenant infrastructure
```bash
python manage.py makemigrations tenants users
python manage.py migrate_schemas --shared
```

### Tenant Schema (all tenants) — business models
```bash
python manage.py makemigrations projects inventory crm
python manage.py migrate_schemas
```

### Single Tenant (testing/debug)
```bash
python manage.py migrate_schemas --schema=empresa_a
```

## Safe Migration Checklist
Before running on production:
- [ ] Backup all tenant schemas: `make backup-all-schemas`
- [ ] Test migration on staging with representative data
- [ ] Verify rollback SQL exists (for destructive operations)
- [ ] Run during low-traffic window (before 08:00 CV time)
- [ ] Have `migrate_schemas --schema=ROLLBACK` ready

## Additive-Only Rule
For zero-downtime deploys, prefer additive migrations:
```python
# OK: Adding nullable field
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='unit',
            name='bim_guid',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]

# RISKY: Renaming/dropping — requires coordinated deploy
# Always add new field first, migrate data, then remove old field in next release
```

## Batched Rollout for Large Tenant Count
```python
# apps/core/management/commands/rollout_migration.py
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from apps.tenants.models import Client
import time

class Command(BaseCommand):
    help = "Roll out migration to tenants in batches to avoid DB overload"

    def add_arguments(self, parser):
        parser.add_argument('app_label')
        parser.add_argument('migration_name')
        parser.add_argument('--batch-size', type=int, default=10)
        parser.add_argument('--delay', type=int, default=30)

    def handle(self, *args, **options):
        tenants = Client.objects.filter(is_active=True).order_by('id')
        for i, tenant in enumerate(tenants):
            with schema_context(tenant.schema_name):
                from django.core.management import call_command
                call_command('migrate', options['app_label'], options['migration_name'])
                self.stdout.write(f'[{i+1}/{len(tenants)}] Migrated {tenant.schema_name}')
            if (i + 1) % options['batch_size'] == 0:
                time.sleep(options['delay'])
```
