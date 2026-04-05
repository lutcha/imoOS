"""
Management command to create superuser in public schema.
Usage: python manage.py create_superuser_public
"""
from django.core.management.base import BaseCommand
from django.db import connection
from apps.users.models import User


class Command(BaseCommand):
    help = 'Create superuser in public schema'

    def add_arguments(self, parser):
        parser.add_argument('--email', default='admin@proptech.cv')
        parser.add_argument('--password', default='ImoOS2026')
        parser.add_argument('--first_name', default='Admin')
        parser.add_argument('--last_name', default='ImoOS')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        # Ensure we're in public schema
        connection.set_schema_to_public()

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} password reset successfully!'))
        else:
            # Create superuser
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} created successfully!'))

        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
