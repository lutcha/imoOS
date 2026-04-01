"""
ensure_demo_tenant — ImoOS management command
Idempotent wrapper for create_pilot_tenant.
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand
from apps.tenants.models import Client


class Command(BaseCommand):
    help = "Ensure a demo/pilot tenant exists safely."

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Schema name')
        parser.add_argument('--name', required=True, help='Display name')
        parser.add_argument('--domain', required=True, help='Domain name')
        parser.add_argument('--plan', default='pro', help='Subscription plan')

    def handle(self, *args, **options):
        schema = options['schema']
        name = options['name']
        domain = options['domain']
        plan = options['plan']

        if Client.objects.filter(schema_name=schema).exists():
            self.stdout.write(f"Tenant '{schema}' exists. Skipping.")
            return

        self.stdout.write(f"Creating pilot tenant '{schema}'...")
        
        call_command(
            'create_pilot_tenant',
            schema=schema,
            name=name,
            domain=domain,
            plan=plan,
            with_demo_data=True
        )
        self.stdout.write(self.style.SUCCESS(f"Created tenant '{schema}'."))
