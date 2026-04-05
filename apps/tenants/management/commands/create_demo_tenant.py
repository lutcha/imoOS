"""
Management command to create demo tenant for testing.
Usage: python manage.py create_demo_tenant
"""
from django.core.management.base import BaseCommand
from django.db import connection
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Create demo tenant for testing'

    def handle(self, *args, **options):
        schema_name = 'demo_promotora'
        tenant_name = 'Demo Promotora'
        domain_name = 'demo.proptech.cv'

        # Check if tenant already exists
        if Tenant.objects.filter(schema_name=schema_name).exists():
            self.stdout.write(self.style.WARNING(f'Tenant {schema_name} already exists'))
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

        self.stdout.write(self.style.SUCCESS(f'Tenant {tenant_name} created successfully!'))
        self.stdout.write(f'Schema: {schema_name}')
        self.stdout.write(f'Domain: {domain_name}')
