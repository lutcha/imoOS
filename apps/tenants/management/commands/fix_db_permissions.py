"""
fix_db_permissions — Management command to fix PostgreSQL permissions

DigitalOcean Managed PostgreSQL requires explicit permissions for the database
user to CREATE SCHEMA. This command grants the necessary permissions.

Run this ONCE after initial database setup:
    python manage.py fix_db_permissions
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL permissions for schema creation (DigitalOcean Managed DB)'

    def handle(self, *args, **options):
        self.stdout.write('Checking database permissions...')

        with connection.cursor() as cursor:
            # Get current database user
            cursor.execute("SELECT current_user;")
            current_user = cursor.fetchone()[0]
            self.stdout.write(f'  Current user: {current_user}')

            # Get current database
            cursor.execute("SELECT current_database();")
            current_db = cursor.fetchone()[0]
            self.stdout.write(f'  Current database: {current_db}')

            # Check if user has CREATE privilege on database
            cursor.execute("""
                SELECT has_database_privilege(%s, %s, 'CREATE');
            """, [current_user, current_db])
            has_create = cursor.fetchone()[0]
            self.stdout.write(f'  Has CREATE privilege: {has_create}')

            if has_create:
                self.stdout.write(self.style.SUCCESS(
                    '✅ User already has CREATE privilege. No changes needed.'
                ))
                return

            # Grant CREATE privilege on database to current user
            self.stdout.write(f'Granting CREATE privilege to {current_user}...')
            cursor.execute(f'GRANT CREATE ON DATABASE "{current_db}" TO "{current_user}";')

            # Verify
            cursor.execute("""
                SELECT has_database_privilege(%s, %s, 'CREATE');
            """, [current_user, current_db])
            has_create = cursor.fetchone()[0]

            if has_create:
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Successfully granted CREATE privilege to {current_user}'
                ))
            else:
                raise CommandError(
                    f'Failed to grant CREATE privilege. '
                    f'You may need to run this as a superuser:\n'
                    f'  GRANT CREATE ON DATABASE "{current_db}" TO "{current_user}";'
                )
