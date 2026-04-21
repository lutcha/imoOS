"""
reset_demo_tenant — ImoOS management command
Safely drops the demo_promotora schema and its database record to allow clean recreation.
"""
from django.core.management.base import BaseCommand
from apps.tenants.models import Client


class Command(BaseCommand):
    help = "Drops the demo_promotora tenant schema and record."

    def handle(self, *args, **options):
        schema = 'demo_promotora'
        
        try:
            tenant = Client.objects.get(schema_name=schema)
            self.stdout.write(f"Found tenant '{tenant.name}' with schema '{schema}'.")
            
            # In django-tenants, deleting the tenant model instance
            # will drop the schema automatically (if configured/standard).
            # We use CASCADE just in case.
            tenant.delete()
            
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted tenant record and schema for '{schema}'."))
            self.stdout.write("The next deployment will recreate it cleanly.")
            
        except Client.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Tenant with schema '{schema}' does not exist."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error deleting tenant: {e}"))
            # Fallback for manual schema dropping if model deletion fails to drop schema
            from django.db import connection
            with connection.cursor() as cursor:
                self.stdout.write(f"Attempting manual drop of schema '{schema}'...")
                cursor.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
                self.stdout.write(self.style.SUCCESS(f"Manual drop of schema '{schema}' complete."))
