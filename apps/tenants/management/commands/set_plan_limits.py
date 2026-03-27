"""
Management command: set_plan_limits

Applies the PLAN_LIMITS defaults from settings to all (or filtered) tenant
TenantSettings rows.

Usage:
    # Update all starter tenants to PLAN_LIMITS['starter']
    python manage.py set_plan_limits --plan=starter

    # Update every tenant to their current plan's limits
    python manage.py set_plan_limits

    # Dry run — show what would change without saving
    python manage.py set_plan_limits --dry-run
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Apply PLAN_LIMITS from settings to TenantSettings rows.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plan',
            type=str,
            choices=['starter', 'pro', 'enterprise'],
            default=None,
            help='Only update tenants on this plan (default: all plans).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Show changes without saving to the database.',
        )

    def handle(self, *args, **options):
        from apps.tenants.models import Client, TenantSettings

        plan_filter = options['plan']
        dry_run = options['dry_run']
        plan_limits = getattr(settings, 'PLAN_LIMITS', {})

        if not plan_limits:
            raise CommandError('PLAN_LIMITS not defined in settings.')

        qs = Client.objects.filter(is_active=True)
        if plan_filter:
            qs = qs.filter(plan=plan_filter)

        updated = 0
        for tenant in qs:
            limits = plan_limits.get(tenant.plan)
            if not limits:
                self.stdout.write(
                    self.style.WARNING(f'  skip {tenant.slug}: no limits for plan "{tenant.plan}"')
                )
                continue

            tenant_settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
            changed_fields = []

            for field, value in limits.items():
                current = getattr(tenant_settings, field, None)
                if current != value:
                    changed_fields.append(f'{field}: {current} → {value}')
                    if not dry_run:
                        setattr(tenant_settings, field, value)

            if changed_fields:
                action = 'WOULD UPDATE' if dry_run else 'UPDATED'
                self.stdout.write(
                    f'  [{action}] {tenant.slug} ({tenant.plan}): '
                    + ', '.join(changed_fields)
                )
                if not dry_run:
                    tenant_settings.save(update_fields=list(limits.keys()))
                updated += 1
            else:
                self.stdout.write(f'  [OK]      {tenant.slug} ({tenant.plan}): no changes')

        suffix = ' (dry run)' if dry_run else ''
        self.stdout.write(
            self.style.SUCCESS(f'\nDone{suffix}: {updated} tenant(s) {"would be " if dry_run else ""}updated.')
        )
