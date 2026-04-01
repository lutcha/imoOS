"""
Management command: ensure_public_tenant

Creates the public tenant and registers platform domains if they don't
already exist.  Safe to run multiple times (idempotent).

Called from the pre-deploy migrate job on DO App Platform so the
ImoOSTenantMiddleware can resolve the platform domain to the public
schema and serve the /api/v1/health/ endpoint.

Usage:
    python manage.py ensure_public_tenant --domain proptech.cv
    python manage.py ensure_public_tenant --domain my-app.ondigitalocean.app
"""

import os

from django.core.management.base import BaseCommand

from apps.tenants.models import Client, Domain


class Command(BaseCommand):
    help = "Ensure the public tenant and platform domain records exist."

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            type=str,
            default="",
            help="Primary platform domain to register (e.g. proptech.cv). "
            "Falls back to TENANT_BASE_DOMAIN env var.",
        )

    def handle(self, *args, **options):
        domain_name = options["domain"] or os.environ.get("TENANT_BASE_DOMAIN", "")

        # 1. Ensure public Client exists
        public_tenant, created = Client.objects.get_or_create(
            schema_name="public",
            defaults={
                "name": "ImoOS Platform",
                "slug": "platform",
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created public tenant."))
        else:
            self.stdout.write("Public tenant already exists.")

        # 2. Register the platform domain
        if domain_name:
            domain_obj, created = Domain.objects.get_or_create(
                domain=domain_name,
                defaults={"tenant": public_tenant, "is_primary": True},
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Registered domain: {domain_name}")
                )
            else:
                self.stdout.write(f"Domain already registered: {domain_name}")

        # 3. Always ensure the ondigitalocean.app wildcard entry exists for
        #    the DO health-check probe (it hits the default ingress domain).
        #    We register the literal APP_DOMAIN if provided by DO runtime.
        app_domain = os.environ.get("APP_DOMAIN", "")
        if app_domain and app_domain != domain_name:
            domain_obj, created = Domain.objects.get_or_create(
                domain=app_domain,
                defaults={"tenant": public_tenant, "is_primary": False},
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Registered DO app domain: {app_domain}")
                )
            else:
                self.stdout.write(f"DO app domain already registered: {app_domain}")

        self.stdout.write(self.style.SUCCESS("ensure_public_tenant complete."))
