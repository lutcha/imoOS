"""
Create tenant using raw SQL (workaround for managed PostgreSQL without CREATE SCHEMA).
Usage: python manage.py create_tenant_sql --schema=demo --name="Demo" --domain=demo.proptech.cv
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create tenant using raw SQL (for managed PostgreSQL without CREATE SCHEMA permission)'

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

        with connection.cursor() as cursor:
            # Check if tenant exists
            cursor.execute(
                "SELECT id FROM tenants_tenant WHERE schema_name = %s",
                [schema_name]
            )
            if cursor.fetchone():
                self.stdout.write(self.style.WARNING(f"Tenant '{schema_name}' already exists"))
                # Ensure domain
                cursor.execute(
                    """INSERT INTO tenants_domain (domain, is_primary, tenant_id) 
                       SELECT %s, true, id FROM tenants_tenant WHERE schema_name = %s
                       ON CONFLICT DO NOTHING""",
                    [domain_name, schema_name]
                )
                return

            # Insert tenant (using public schema as placeholder)
            cursor.execute(
                """INSERT INTO tenants_tenant (schema_name, name, plan, is_active, created_on)
                   VALUES (%s, %s, %s, true, NOW())
                   RETURNING id""",
                [schema_name, tenant_name, plan]
            )
            tenant_id = cursor.fetchone()[0]
            
            # Insert domain
            cursor.execute(
                """INSERT INTO tenants_domain (domain, is_primary, tenant_id)
                   VALUES (%s, true, %s)""",
                [domain_name, tenant_id]
            )

        self.stdout.write(self.style.SUCCESS(f"✅ Tenant '{tenant_name}' created successfully!"))
        self.stdout.write(f"  ID: {tenant_id}")
        self.stdout.write(f"  Schema: {schema_name}")
        self.stdout.write(f"  Domain: {domain_name}")
        self.stdout.write(f"  Plan: {plan}")
        self.stdout.write(self.style.NOTICE("\n⚠️  IMPORTANT: Run migrations manually for this tenant:"))
        self.stdout.write(f"  python manage.py migrate_schemas --tenant={schema_name}")
