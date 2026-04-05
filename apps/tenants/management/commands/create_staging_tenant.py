"""
Management command to create staging tenant.
Usage: python manage.py create_staging_tenant
"""
from django.core.management.base import BaseCommand
from django.db import connection
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Create staging tenant for the DO App Platform domain'

    def handle(self, *args, **options):
        schema_name = 'staging'
        tenant_name = 'Staging Promotora'
        domain_name = 'imos-staging-jiow3.ondigitalocean.app'

        # Check if tenant already exists
        if Tenant.objects.filter(schema_name=schema_name).exists():
            self.stdout.write(self.style.WARNING(f'Tenant {schema_name} already exists'))
            # Ensure domain exists
            tenant = Tenant.objects.get(schema_name=schema_name)
            if not Domain.objects.filter(domain=domain_name).exists():
                Domain.objects.create(
                    tenant=tenant,
                    domain=domain_name,
                    is_primary=True
                )
                self.stdout.write(self.style.SUCCESS(f'Domain {domain_name} added to tenant'))
            return

        # Create tenant
        tenant = Tenant(
            schema_name=schema_name,
            name=tenant_name,
            plan='pro',
            is_active=True
        )
        tenant.save()

        # Create domain
        Domain.objects.create(
            tenant=tenant,
            domain=domain_name,
            is_primary=True
        )

        self.stdout.write(self.style.SUCCESS(f'Staging tenant created successfully!'))
        self.stdout.write(f'Schema: {schema_name}')
        self.stdout.write(f'Domain: {domain_name}')
