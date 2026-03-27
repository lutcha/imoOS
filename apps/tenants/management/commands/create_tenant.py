"""
Management command: create_tenant

Creates a new ImoOS tenant end-to-end:
  1. Client (PostgreSQL schema + auto migration via django-tenants)
  2. Primary Domain
  3. TenantSettings (plan defaults)
  4. Optional: admin User inside the tenant schema

Usage:
    python manage.py create_tenant \\
        --schema=empresa_a \\
        --name="Empresa A Lda" \\
        --domain=empresa-a.imos.cv \\
        --plan=pro \\
        --admin-email=admin@empresa-a.cv \\
        --admin-password=<secret>
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a new ImoOS tenant (Client + Domain + TenantSettings + optional admin user)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema', required=True, dest='schema_name',
            help='PostgreSQL schema name (lowercase, underscores only)',
        )
        parser.add_argument(
            '--name', required=True,
            help='Display name of the company (e.g. "Empresa A Lda")',
        )
        parser.add_argument(
            '--domain', required=True,
            help='Primary domain (e.g. empresa-a.imos.cv)',
        )
        parser.add_argument(
            '--slug', default=None,
            help='URL/S3 slug (defaults to schema_name with underscores → hyphens)',
        )
        parser.add_argument(
            '--plan', default='starter',
            choices=['starter', 'pro', 'enterprise'],
            help='Subscription plan (default: starter)',
        )
        parser.add_argument(
            '--country', default='CV',
            help='ISO 3166-1 alpha-2 country code (default: CV)',
        )
        parser.add_argument(
            '--currency', default='CVE',
            help='Currency code (default: CVE)',
        )
        parser.add_argument(
            '--admin-email', default=None, dest='admin_email',
            help='(Optional) Create an admin user with this email inside the tenant schema',
        )
        parser.add_argument(
            '--admin-password', default=None, dest='admin_password',
            help='Password for the admin user (required when --admin-email is set)',
        )

    def handle(self, *args, **options):
        from apps.tenants.models import Client, Domain, TenantSettings

        schema_name = options['schema_name']
        name = options['name']
        domain_name = options['domain']
        slug = options['slug'] or schema_name.replace('_', '-')
        plan = options['plan']
        country = options['country']
        currency = options['currency']
        admin_email = options['admin_email']
        admin_password = options['admin_password']

        # ------------------------------------------------------------------
        # Pre-flight validation
        # ------------------------------------------------------------------
        import re
        if not re.match(r'^[a-z][a-z0-9_]*$', schema_name):
            raise CommandError(
                'schema_name must be lowercase letters/digits/underscores, '
                'starting with a letter.'
            )
        if Client.objects.filter(schema_name=schema_name).exists():
            raise CommandError(f"Tenant with schema '{schema_name}' already exists.")
        if Client.objects.filter(slug=slug).exists():
            raise CommandError(f"Slug '{slug}' already in use.")
        if Domain.objects.filter(domain=domain_name).exists():
            raise CommandError(f"Domain '{domain_name}' is already registered.")
        if admin_email and not admin_password:
            raise CommandError('--admin-password is required when --admin-email is set.')

        # ------------------------------------------------------------------
        # Create Client — django-tenants auto_create_schema=True
        # runs migrate_schemas for this tenant when save() completes.
        # ------------------------------------------------------------------
        self.stdout.write(f"Creating tenant '{name}' …")
        self.stdout.write(f"  schema : {schema_name}")
        self.stdout.write(f"  domain : {domain_name}")
        self.stdout.write(f"  plan   : {plan}")

        try:
            client = Client(
                schema_name=schema_name,
                name=name,
                slug=slug,
                plan=plan,
                country=country,
                currency=currency,
                is_active=True,
            )
            client.save()   # triggers schema creation + migration
        except Exception as exc:
            raise CommandError(f'Failed to create tenant: {exc}') from exc

        self.stdout.write(self.style.SUCCESS(
            f"  Schema '{schema_name}' created and migrations applied."
        ))

        # ------------------------------------------------------------------
        # Primary domain
        # ------------------------------------------------------------------
        Domain.objects.create(domain=domain_name, tenant=client, is_primary=True)
        self.stdout.write(f"  Domain '{domain_name}' registered.")

        # ------------------------------------------------------------------
        # TenantSettings — plan defaults
        # ------------------------------------------------------------------
        plan_limits = {
            'starter':    {'max_projects': 3,  'max_units': 150, 'max_users': 10},
            'pro':        {'max_projects': 20, 'max_units': 1000, 'max_users': 50},
            'enterprise': {'max_projects': 0,  'max_units': 0,   'max_users': 0},
        }
        limits = plan_limits[plan]
        TenantSettings.objects.create(
            tenant=client,
            max_projects=limits['max_projects'],
            max_units=limits['max_units'],
            max_users=limits['max_users'],
        )
        self.stdout.write(
            f"  TenantSettings created "
            f"(max_projects={limits['max_projects']}, "
            f"max_units={limits['max_units']}, "
            f"max_users={limits['max_users']})."
        )

        # ------------------------------------------------------------------
        # Optional admin user + TenantMembership (created inside tenant schema)
        # ------------------------------------------------------------------
        if admin_email:
            from django_tenants.utils import tenant_context
            from django.contrib.auth import get_user_model
            from apps.memberships.models import TenantMembership
            User = get_user_model()
            with tenant_context(client):
                user = User.objects.create_user(
                    email=admin_email,
                    password=admin_password,
                    # User.role kept for display/informational use only.
                    # Auth decisions use TenantMembership.role (per-schema).
                    role='admin',
                    is_staff=False,
                )
                TenantMembership.objects.create(
                    user=user,
                    role=TenantMembership.ROLE_ADMIN,
                    is_active=True,
                )
            self.stdout.write(
                f"  Admin user '{user.email}' created with TenantMembership(role=admin)."
            )

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Tenant ready.'))
        self.stdout.write(f"  ID        : {client.id}")
        self.stdout.write(f"  Name      : {client.name}")
        self.stdout.write(f"  Schema    : {client.schema_name}")
        self.stdout.write(f"  Domain    : {domain_name}")
        self.stdout.write(f"  Plan      : {plan}")
        self.stdout.write(f"  S3 prefix : {client.s3_prefix}")
