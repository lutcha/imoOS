---
name: management-commands
description: Create tenant-aware Django management commands for ImoOS with --schema flag. Auto-load when writing admin/maintenance scripts.
argument-hint: [command-name] [tenant-scope]
allowed-tools: Read, Write
---

# Tenant-Aware Management Commands — ImoOS

## Template: Iterate All Active Tenants
```python
# apps/core/management/commands/sync_all_listings.py
from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from apps.tenants.models import Client

class Command(BaseCommand):
    help = 'Sync all active unit listings to imo.cv for all tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Run for a single tenant schema (for testing/debug)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview actions without making changes',
        )

    def handle(self, *args, **options):
        schema = options.get('schema')
        if schema:
            tenants = Client.objects.filter(schema_name=schema, is_active=True)
        else:
            tenants = Client.objects.filter(is_active=True)

        for tenant in tenants:
            self.stdout.write(f'Processing {tenant.schema_name}...')
            with tenant_context(tenant):
                self._process_tenant(tenant, options['dry_run'])

    def _process_tenant(self, tenant, dry_run):
        from apps.inventory.models import Unit
        units = Unit.objects.filter(status='AVAILABLE', is_deleted=False)
        self.stdout.write(f'  Found {units.count()} units to sync')
        if not dry_run:
            # ... do actual work
            pass
```

## Template: Create Tenant
```python
# apps/tenants/management/commands/create_tenant.py
class Command(BaseCommand):
    help = 'Create a new tenant with schema, domain, and initial settings'

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True)
        parser.add_argument('--name', required=True)
        parser.add_argument('--domain', required=True)
        parser.add_argument('--plan', default='starter')

    def handle(self, *args, **options):
        tenant = Client.objects.create(
            schema_name=options['schema'],
            name=options['name'],
            slug=options['schema'].replace('_', '-'),
            plan=options['plan'],
        )
        Domain.objects.create(domain=options['domain'], tenant=tenant, is_primary=True)
        self.stdout.write(self.style.SUCCESS(f"Created tenant: {tenant.schema_name}"))
```

## Key Rules
- Always add `--schema` flag for targeted single-tenant runs
- Add `--dry-run` for destructive or data-changing commands
- Log progress per tenant — don't silence errors
- Test management commands in isolation tests suite
