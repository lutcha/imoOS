"""
ensure_demo_users — Idempotently create demo tenant users.

Runs inside the `demo_promotora` schema (or any schema passed via --tenant).
Safe to run multiple times: uses get_or_create, never resets existing passwords.

Added to the migrate job in app.yaml so every deploy has the demo credentials
available without needing a manual console command.

Credentials created:
  admin@demo.cv       / Demo2026!   (admin, is_staff=True)
  gerente@demo.cv     / Demo2026!   (gestor)
  vendas@demo.cv      / Demo2026!   (vendedor)
  obra@demo.cv        / Demo2026!   (engenheiro)
  cliente1@demo.cv    / Demo2026!   (gestor)
  cliente2@demo.cv    / Demo2026!   (gestor)
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


DEMO_USERS = [
    {
        'email': 'admin@demo.cv',
        'first_name': 'Carlos',
        'last_name': 'Fonseca',
        'role': 'admin',
        'is_staff': True,
    },
    {
        'email': 'gerente@demo.cv',
        'first_name': 'Maria',
        'last_name': 'Silva',
        'role': 'gestor',
    },
    {
        'email': 'vendas@demo.cv',
        'first_name': 'João',
        'last_name': 'Santos',
        'role': 'vendedor',
    },
    {
        'email': 'obra@demo.cv',
        'first_name': 'Pedro',
        'last_name': 'Lima',
        'role': 'engenheiro',
    },
    {
        'email': 'cliente1@demo.cv',
        'first_name': 'Ana',
        'last_name': 'Oliveira',
        'role': 'gestor',
    },
    {
        'email': 'cliente2@demo.cv',
        'first_name': 'Miguel',
        'last_name': 'Ramos',
        'role': 'gestor',
    },
]

DEFAULT_PASSWORD = 'Demo2026!'


class Command(BaseCommand):
    help = 'Idempotently create demo users in the specified tenant schema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default='demo_promotora',
            help='Schema name of the tenant (default: demo_promotora)',
        )

    def handle(self, *args, **options):
        from apps.tenants.models import Client
        from apps.users.models import User

        schema = options['tenant']

        try:
            tenant = Client.objects.get(schema_name=schema)
        except Client.DoesNotExist:
            raise CommandError(
                f"Tenant '{schema}' does not exist. "
                "Run ensure_demo_tenant first."
            )

        connection.set_tenant(tenant)
        self.stdout.write(f"Creating demo users in schema '{schema}'…")

        created_count = 0
        for data in DEMO_USERS:
            email = data['email']
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'is_staff': data.get('is_staff', False),
                    'is_active': True,
                },
            )
            if created:
                user.set_password(DEFAULT_PASSWORD)
                user.save(update_fields=['password'])
                created_count += 1
                self.stdout.write(f"  ✓ Created {email}")
            else:
                self.stdout.write(f"  — {email} already exists")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Done — {created_count} user(s) created, "
                f"{len(DEMO_USERS) - created_count} already existed."
            )
        )
        self.stdout.write("\nCredentials:")
        for d in DEMO_USERS:
            self.stdout.write(f"  {d['email']} / {DEFAULT_PASSWORD}")
