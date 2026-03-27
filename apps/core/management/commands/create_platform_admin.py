"""
Management command to create a platform super-admin user.
This user has is_staff=True and can access:
- Django Admin (/django-admin/)
- Super Admin Dashboard (/superadmin/)
- All tenant management endpoints

Usage:
    python manage.py create_platform_admin
    
Or with environment variables:
    PLATFORM_ADMIN_EMAIL=admin@imos.cv
    PLATFORM_ADMIN_PASSWORD=YourSecurePassword123
    python manage.py create_platform_admin
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create a platform super-admin user with is_staff=True"

    def handle(self, *args, **options):
        import os
        
        email = os.environ.get("PLATFORM_ADMIN_EMAIL", "superadmin@imos.cv")
        password = os.environ.get("PLATFORM_ADMIN_PASSWORD", None)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_staff:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Super-admin user '{email}' already exists and has staff privileges."
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        f"  Email: {email}\n"
                        f"  Staff: {user.is_staff}\n"
                        f"  Superuser: {user.is_superuser}\n"
                        f"  Role: {user.role}"
                    )
                )
                return
            else:
                # Upgrade existing user to staff
                user.is_staff = True
                user.is_superuser = True
                user.role = "admin"
                user.save(update_fields=["is_staff", "is_superuser", "role"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Upgraded existing user '{email}' to super-admin."
                    )
                )
                return
        
        # Get password interactively if not provided
        if not password:
            import getpass
            password = getpass.getpass("Password: ")
            password2 = getpass.getpass("Password (again): ")
            
            if password != password2:
                raise CommandError("Passwords do not match.")
            
            if len(password) < 8:
                raise CommandError("Password must be at least 8 characters.")
        
        # Create the super-admin user
        user = User.objects.create_user(
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
            role="admin",
            first_name="Platform",
            last_name="Admin",
        )
        
        self.stdout.write(self.style.SUCCESS("\n✓ Platform super-admin created successfully!\n"))
        self.stdout.write(
            self.style.SUCCESS(
                f"  Email:    {email}\n"
                f"  Staff:    {user.is_staff}\n"
                f"  Superuser: {user.is_superuser}\n"
                f"  Role:     {user.role}\n"
            )
        )
        
        self.stdout.write(self.style.WARNING(
            "\n⚠ IMPORTANT: Save this password securely!\n"
            "This user has access to:\n"
            "  - Django Admin: /django-admin/\n"
            "  - Super Admin Dashboard: /superadmin/\n"
            "  - All tenant management endpoints\n"
        ))
        
        self.stdout.write(self.style.SUCCESS(
            "Next steps:\n"
            "  1. Login at /django-admin/ with these credentials\n"
            "  2. Create your first tenant via Django Admin or API\n"
            "  3. Access /superadmin/ for platform management\n"
        ))
