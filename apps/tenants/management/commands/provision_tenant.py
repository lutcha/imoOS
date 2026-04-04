"""
provision_tenant — ImoOS management command

Idempotent tenant provisioning. Safe to run multiple times.
Handles three scenarios:
  1. Fresh: schema doesn't exist → full creation (Client + schema + Domain + Settings)
  2. Orphan schema: schema exists in PG but no Client row → sync records only
  3. Already exists: Client + schema both present → ensure Domain + Settings

Usage:
  python manage.py provision_tenant \\
    --schema demo_promotora \\
    --name "Demo Promotora" \\
    --domain demo.proptech.cv \\
    --plan pro \\
    --contact-email admin@demo.proptech.cv
"""
import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

logger = logging.getLogger(__name__)

PLAN_LIMITS = {
    'starter':    {'max_projects': 3,    'max_units': 150,   'max_users': 10},
    'pro':        {'max_projects': 20,   'max_units': 1000,  'max_users': 50},
    'enterprise': {'max_projects': 9999, 'max_units': 99999, 'max_users': 9999},
}


def _schema_exists(schema_name: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
            [schema_name],
        )
        return cursor.fetchone() is not None


class Command(BaseCommand):
    help = 'Idempotent tenant provisioning — safe to run multiple times'

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True,
                            help='PostgreSQL schema name (lowercase, underscores, 3-50 chars)')
        parser.add_argument('--name', required=True,
                            help='Company display name')
        parser.add_argument('--domain', required=True,
                            help='Primary domain (e.g. empresa.proptech.cv)')
        parser.add_argument('--plan', default='starter',
                            choices=['starter', 'pro', 'enterprise'])
        parser.add_argument('--contact-email', default='',
                            help='Admin contact email (optional)')
        parser.add_argument('--country', default='CV',
                            help='ISO 3166-1 alpha-2 country code')

    def handle(self, *args, **options):
        from apps.tenants.models import Client, Domain, TenantSettings

        schema = options['schema']
        name = options['name']
        domain_name = options['domain']
        plan = options['plan']
        country = options['country']
        slug = schema.replace('_', '-')

        logger.info('provision_tenant start', extra={
            'schema': schema, 'name': name, 'domain': domain_name, 'plan': plan,
        })
        self.stdout.write(f"provision_tenant: schema={schema} name={name} domain={domain_name} plan={plan}")

        # ------------------------------------------------------------------
        # Scenario 3: Client already exists → ensure Domain + Settings
        # ------------------------------------------------------------------
        try:
            client = Client.objects.get(schema_name=schema)
            self.stdout.write(f"  Client '{schema}' already exists — ensuring Domain + Settings.")
            self._ensure_domain(client, domain_name)
            self._ensure_settings(client, plan)
            self.stdout.write(self.style.SUCCESS(f"  ✓ already_exists — {schema}"))
            return 'already_exists'
        except Client.DoesNotExist:
            pass

        schema_in_pg = _schema_exists(schema)

        # ------------------------------------------------------------------
        # Scenario 2: Orphan schema (schema in PG, no Client row)
        # ------------------------------------------------------------------
        if schema_in_pg:
            self.stdout.write(f"  Schema '{schema}' exists in PG but no Client row — syncing records.")
            logger.warning('provision_tenant: orphan schema found, syncing records', extra={'schema': schema})

            # Create Client WITHOUT triggering auto_create_schema
            original_flag = Client.auto_create_schema
            Client.auto_create_schema = False
            try:
                with transaction.atomic():
                    client = Client.objects.create(
                        schema_name=schema,
                        name=name,
                        slug=slug,
                        plan=plan,
                        country=country,
                        currency='CVE' if country == 'CV' else 'EUR',
                        is_active=True,
                    )
            finally:
                Client.auto_create_schema = original_flag

            self.stdout.write(f"  Client row created (schema already existed in PG).")
            self._run_migrations(schema)
            self._ensure_domain(client, domain_name)
            self._ensure_settings(client, plan)
            self.stdout.write(self.style.SUCCESS(f"  ✓ synced — {schema}"))
            return 'synced'

        # ------------------------------------------------------------------
        # Scenario 1: Fresh creation
        # ------------------------------------------------------------------
        self.stdout.write(f"  Fresh creation: schema + Client + Domain + Settings.")
        try:
            with transaction.atomic():
                client = Client(
                    schema_name=schema,
                    name=name,
                    slug=slug,
                    plan=plan,
                    country=country,
                    currency='CVE' if country == 'CV' else 'EUR',
                    is_active=True,
                )
                client.save()  # triggers CREATE SCHEMA + migrate_schemas
        except Exception as exc:
            raise CommandError(f'Schema creation failed: {exc}') from exc

        self.stdout.write(f"  Schema '{schema}' created and migrated.")
        self._ensure_domain(client, domain_name)
        self._ensure_settings(client, plan)
        self.stdout.write(self.style.SUCCESS(f"  ✓ created — {schema}"))
        return 'created'

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ensure_domain(self, client, domain_name: str) -> None:
        from apps.tenants.models import Domain
        obj, created = Domain.objects.get_or_create(
            domain=domain_name,
            defaults={'tenant': client, 'is_primary': True},
        )
        if not created and obj.tenant_id != client.pk:
            self.stderr.write(
                f"  WARNING: domain '{domain_name}' already points to a different tenant."
            )
        else:
            self.stdout.write(f"  Domain '{domain_name}' {'created' if created else 'already registered'}.")

    def _ensure_settings(self, client, plan: str) -> None:
        from apps.tenants.models import TenantSettings
        limits = PLAN_LIMITS[plan]
        _, created = TenantSettings.objects.get_or_create(
            tenant=client,
            defaults=limits,
        )
        if created:
            self.stdout.write(f"  TenantSettings created (plan={plan}).")
        else:
            self.stdout.write(f"  TenantSettings already exist.")

    def _run_migrations(self, schema: str) -> None:
        from django.core.management import call_command
        self.stdout.write(f"  Running migrate_schemas for '{schema}'…")
        call_command('migrate_schemas', schema=schema, verbosity=0)
        self.stdout.write(f"  Migrations applied.")
