"""
Management command to create platform superadmin (public schema).
Usage: python manage.py create_platform_superadmin --email=admin@proptech.cv --password=ImoOS2026
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create platform superadmin user in public schema (for superadmin access)'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@proptech.cv', help='Superadmin email')
        parser.add_argument('--password', type=str, default='ImoOS2026', help='Superadmin password')
        parser.add_argument('--first-name', type=str, default='Platform', help='First name')
        parser.add_argument('--last-name', type=str, default='Admin', help='Last name')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        # Switch to public schema
        connection.set_schema_to_public()

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # Ensure it's a superuser and staff
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.WARNING(f'User {email} promoted to superuser'))
            else:
                self.stdout.write(self.style.WARNING(f'Superuser {email} already exists'))
            
            # Reset password if provided
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Password updated for {email}'))
            return

        # Create superuser
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Ensure is_staff is True (create_superuser should do this, but double-check)
        user.is_staff = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f'✅ Platform superadmin created successfully!'))
        self.stdout.write(f'   Email: {email}')
        self.stdout.write(f'   Password: {password}')
        self.stdout.write(f'   Schema: public')
        self.stdout.write(self.style.NOTICE(f'\nUse these credentials to login at /superadmin/login'))
