"""
Create tenant using public schema (workaround for managed PostgreSQL).
Usage: python manage.py create_tenant_public --schema=demo --name="Demo" --domain=demo.proptech.cv
"""
from django.core.management.base import BaseCommand
from django.db import connection
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Create tenant using public schema (for managed PostgreSQL)'

    def add_arguments(self, parser):
        parser.add_argument('--schema', type=str, required=True, help='Schema name (identifier)')
        parser.add_argument('--name', type=str, required=True, help='Tenant display name')
        parser.add_argument('--domain', type=str, required=True, help='Domain name')
        parser.add_argument('--plan', type=str, default='pro', help='Subscription plan')

    def handle(self, *args, **options):
        schema_name = options['schema']
        tenant_name = options['name']
        domain_name = options['domain']
        plan = options['plan']

        # Check if tenant already exists
        if Tenant.objects.filter(schema_name=schema_name).exists():
            self.stdout.write(self.style.WARNING(f"Tenant '{schema_name}' already exists"))
            tenant = Tenant.objects.get(schema_name=schema_name)
            self.ensure_domain(tenant, domain_name)
            return

        # Create tenant without creating schema (use public schema workaround)
        self.stdout.write(f"Creating tenant '{tenant_name}'...")
        
        try:
            # Create tenant - force using public schema
            tenant = Tenant(
                schema_name='public',  # Use public schema
                name=tenant_name,
                plan=plan,
                is_active=True
            )
            # Save without calling save() which creates schema
            Tenant.objects.bulk_create([tenant])
            tenant = Tenant.objects.get(name=tenant_name)
            
            # Update schema_name to the identifier
            Tenant.objects.filter(pk=tenant.pk).update(schema_name=schema_name)
            tenant.refresh_from_db()
            
            self.stdout.write(self.style.SUCCESS(f"Tenant '{tenant_name}' created!"))
            self.stdout.write(f"  Schema: {schema_name} (using public)")
            
            # Create domain
            self.ensure_domain(tenant, domain_name)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            self.stdout.write(self.style.NOTICE("\nWorkaround: Create tenant manually:"))
            self.stdout.write(f"  INSERT INTO tenants_tenant (schema_name, name, plan, is_active, created_at) VALUES ('{schema_name}', '{tenant_name}', '{plan}', true, NOW());")
            self.stdout.write(f"  INSERT INTO tenants_domain (domain, tenant_id, is_primary) VALUES ('{domain_name}', (SELECT id FROM tenants_tenant WHERE schema_name='{schema_name}'), true);")

    def ensure_domain(self, tenant, domain_name):
        """Ensure domain exists for tenant"""
        if not Domain.objects.filter(domain=domain_name).exists():
            Domain.objects.create(
                tenant=tenant,
                domain=domain_name,
                is_primary=True
            )
            self.stdout.write(self.style.SUCCESS(f"Domain '{domain_name}' added"))
        else:
            self.stdout.write(f"Domain '{domain_name}' already exists")
