"""
Celery tasks for tenant onboarding and provisioning (Sprint 7 - Prompt 03).
"""
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_verification_email(self, registration_id: str):
    """
    Send verification email to new tenant registrant.
    
    Args:
        registration_id: UUID of TenantRegistration instance
    
    Retries:
        3 times with 5-minute delay (exponential backoff)
    """
    from ..models import TenantRegistration
    
    try:
        registration = TenantRegistration.objects.get(id=registration_id)
    except TenantRegistration.DoesNotExist:
        logger.error(f'TenantRegistration {registration_id} not found')
        return
    
    # Build verification URL
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    verification_url = f'{frontend_url}/verify-email?token={registration.verification_token}'
    
    # Render email template
    context = {
        'company_name': registration.company_name,
        'contact_name': registration.contact_name,
        'subdomain': registration.subdomain,
        'plan': registration.get_plan_display(),
        'verification_url': verification_url,
        'logo_url': 'https://imos.cv/logo.png',  # TODO: Configure in settings
        'support_email': 'support@imos.cv',
    }
    
    html_message = render_to_string(
        'tenants/emails/verification_email.html',
        context
    )
    
    plain_message = f"""
Bem-vindo ao ImoOS, {registration.contact_name}!

Obrigado por registar a sua empresa {registration.company_name}.

Para activar a sua conta, clique no link abaixo:
{verification_url}

Este link expira em 48 horas.

Plano seleccionado: {registration.get_plan_display()}
Subdomínio: {registration.subdomain}.imos.cv

Se não criou esta conta, ignore este email.

--
Equipa ImoOS
support@imos.cv
"""
    
    try:
        send_mail(
            subject=f'Bem-vindo ao ImoOS, {registration.company_name}!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.contact_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Verification email sent to {registration.contact_email}')
        
    except Exception as exc:
        logger.warning(f'Failed to send verification email: {exc}')
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=1, default_retry_delay=60, time_limit=120)
def provision_tenant(self, registration_id: str):
    """
    Provision a new tenant after email verification.
    
    This task:
    1. Validates registration status
    2. Creates Client (django-tenants)
    3. Creates Domain
    4. Creates TenantSettings
    5. Creates admin user
    6. Creates TenantMembership
    7. Sends credentials email
    8. Updates registration status
    
    Args:
        registration_id: UUID of TenantRegistration instance
    
    Retries:
        1 time with 60-second delay (idempotent operation)
    
    Timeout:
        120 seconds
    """
    from ..models import TenantRegistration, Client, Domain, TenantSettings
    from apps.users.models import User
    from apps.memberships.models import TenantMembership
    from django_tenants.utils import schema_context
    import secrets
    
    try:
        registration = TenantRegistration.objects.get(id=registration_id)
    except TenantRegistration.DoesNotExist:
        logger.error(f'TenantRegistration {registration_id} not found')
        return
    
    # Validate status
    if registration.status != TenantRegistration.STATUS_VERIFIED:
        logger.warning(
            f'Registration {registration_id} has status {registration.status}, '
            f'expected VERIFIED'
        )
        return
    
    # Mark as provisioning
    registration.status = TenantRegistration.STATUS_PROVISIONING
    registration.save(update_fields=['status'])
    
    try:
        # Generate schema name
        schema_name = registration.schema_name
        
        # Check if tenant already exists (idempotency)
        if Client.objects.filter(schema_name=schema_name).exists():
            logger.warning(f'Tenant {schema_name} already exists')
            registration.status = TenantRegistration.STATUS_ACTIVE
            registration.provisioned_at = timezone.now()
            registration.save(update_fields=['status', 'provisioned_at'])
            return
        
        # Generate random password for admin user
        admin_password = secrets.token_urlsafe(16)
        
        # Create Client (django-tenants will create schema)
        tenant = Client.objects.create(
            schema_name=schema_name,
            name=registration.company_name,
            slug=registration.subdomain,
            plan=registration.plan,
            is_active=True,
            country=registration.country,
            currency='CVE' if registration.country == 'CV' else 'USD',
            timezone='Atlantic/Cape_Verde',
        )
        
        logger.info(f'Client created: {tenant.schema_name}')
        
        # Create Domain
        domain_name = f'{registration.subdomain}.{getattr(settings, "TENANT_BASE_DOMAIN", "imos.cv")}'
        Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=True,
        )
        
        logger.info(f'Domain created: {domain_name}')
        
        # Create TenantSettings
        TenantSettings.objects.create(
            tenant=tenant,
            max_projects=get_max_projects_for_plan(registration.plan),
            max_units=get_max_units_for_plan(registration.plan),
            max_users=get_max_users_for_plan(registration.plan),
        )
        
        logger.info(f'TenantSettings created for {tenant.schema_name}')
        
        # Create admin user in tenant schema
        with schema_context(tenant.schema_name):
            admin_user = User.objects.create_user(
                email=registration.contact_email,
                password=admin_password,
                is_staff=True,
                is_superuser=True,
                role='admin',
                first_name=registration.contact_name.split()[0] if registration.contact_name else 'Admin',
                last_name=' '.join(registration.contact_name.split()[1:]) if len(registration.contact_name.split()) > 1 else '',
            )
            
            # Create membership
            TenantMembership.objects.create(
                tenant=tenant,
                user=admin_user,
                role='admin',
            )
        
        logger.info(f'Admin user created for {tenant.schema_name}')
        
        # Send credentials email
        send_credentials_email.delay(
            registration_id=str(registration.id),
            password=admin_password,
            domain=domain_name,
        )
        
        # Update registration status
        registration.status = TenantRegistration.STATUS_ACTIVE
        registration.provisioned_at = timezone.now()
        registration.save(update_fields=['status', 'provisioned_at'])
        
        # Log plan event
        from ..models import PlanEvent
        PlanEvent.objects.create(
            tenant=tenant,
            event_type=PlanEvent.EVENT_TRIAL_STARTED,
            from_plan='',
            to_plan=registration.plan,
            metadata={'source': 'self_service_registration'},
        )
        
        logger.info(f'Tenant {schema_name} provisioned successfully')
        
    except Exception as exc:
        logger.error(f'Failed to provision tenant {registration_id}: {exc}', exc_info=True)
        
        # Update registration with error
        registration.status = TenantRegistration.STATUS_REJECTED
        registration.error_message = str(exc)
        registration.save(update_fields=['status', 'error_message'])
        
        # Retry if not a validation error
        if 'already exists' not in str(exc):
            raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def send_credentials_email(self, registration_id: str, password: str, domain: str):
    """
    Send credentials email to new tenant admin.
    
    Args:
        registration_id: UUID of TenantRegistration instance
        password: Plain text admin password
        domain: Tenant domain URL
    """
    from ..models import TenantRegistration
    
    try:
        registration = TenantRegistration.objects.get(id=registration_id)
    except TenantRegistration.DoesNotExist:
        logger.error(f'TenantRegistration {registration_id} not found')
        return
    
    login_url = f'https://{domain}/login'
    
    context = {
        'company_name': registration.company_name,
        'contact_name': registration.contact_name,
        'email': registration.contact_email,
        'password': password,
        'login_url': login_url,
        'domain': domain,
        'logo_url': 'https://imos.cv/logo.png',
        'support_email': 'support@imos.cv',
    }
    
    html_message = render_to_string(
        'tenants/emails/credentials_email.html',
        context
    )
    
    plain_message = f"""
Bem-vindo ao ImoOS, {registration.contact_name}!

A sua conta foi configurada com sucesso.

Credenciais de acesso:
Email: {registration.contact_email}
Password: {password}

URL de login: {login_url}

⚠ IMPORTANTE: Esta password é temporária. Altere-a após o primeiro login.

--
Equipa ImoOS
support@imos.cv
"""
    
    try:
        send_mail(
            subject=f'A sua conta ImoOS está pronta! - {registration.company_name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.contact_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Credentials email sent to {registration.contact_email}')
        
    except Exception as exc:
        logger.warning(f'Failed to send credentials email: {exc}')
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_registrations():
    """
    Delete expired PENDING_VERIFICATION registrations older than 7 days.
    Runs daily via Celery Beat.
    """
    from ..models import TenantRegistration
    from django.utils import timezone
    
    threshold = timezone.now() - timezone.timedelta(days=7)
    
    deleted, _ = TenantRegistration.objects.filter(
        status=TenantRegistration.STATUS_PENDING,
        created_at__lt=threshold,
    ).delete()
    
    logger.info(f'Cleaned up {deleted} expired tenant registrations')
    return deleted


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_max_projects_for_plan(plan: str) -> int:
    """Get max projects limit for plan."""
    limits = {
        'starter': 3,
        'pro': 15,
        'enterprise': 999,
    }
    return limits.get(plan, 3)


def get_max_units_for_plan(plan: str) -> int:
    """Get max units limit for plan."""
    limits = {
        'starter': 100,
        'pro': 1000,
        'enterprise': 9999,
    }
    return limits.get(plan, 100)


def get_max_users_for_plan(plan: str) -> int:
    """Get max users limit for plan."""
    limits = {
        'starter': 5,
        'pro': 50,
        'enterprise': 999,
    }
    return limits.get(plan, 5)
