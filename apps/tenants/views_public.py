"""
Public views for tenant self-service registration (Sprint 7 - Prompt 03).
These endpoints are unauthenticated and rate-limited.
"""
import re
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.core.throttling import PublicEndpointThrottle
from .models import TenantRegistration, Client


class SUBDOMAIN_REGEX:
    """RFC 1123 compliant subdomain validation."""
    PATTERN = re.compile(r'^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$')
    RESERVED = frozenset([
        'www', 'api', 'admin', 'mail', 'smtp', 'ftp', 'imos', 'app',
        'localhost', 'static', 'media', 'cdn', 'dev', 'staging', 'prod',
    ])


def validate_subdomain(value: str) -> None:
    """
    Validate subdomain format and availability.
    Raises ValidationError if invalid or already taken.
    """
    if not SUBDOMAIN_REGEX.PATTERN.match(value):
        raise ValidationError(
            'Subdomínio inválido. Use apenas letras minúsculas, números e hífens '
            '(3-30 caracteres, deve começar e terminar com letra/número).'
        )
    
    if value.lower() in SUBDOMAIN_REGEX.RESERVED:
        raise ValidationError('Este subdomínio está reservado.')
    
    # Check if schema already exists
    schema_name = value.replace('-', '_')
    if Client.objects.filter(schema_name=schema_name).exists():
        raise ValidationError('Este subdomínio já está em uso.')


class TenantRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for public tenant registration."""
    
    subdomain = serializers.CharField(
        max_length=63,
        min_length=3,
        help_text='Subdomínio para a sua empresa (ex: minha-empresa)'
    )
    
    class Meta:
        model = TenantRegistration
        fields = [
            'company_name', 'subdomain', 'plan',
            'contact_email', 'contact_name', 'contact_phone',
            'country',
        ]
    
    def validate_subdomain(self, value):
        try:
            validate_subdomain(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate_plan(self, value):
        # Ensure plan is one of the allowed choices
        valid_plans = [choice[0] for choice in TenantRegistration.PLAN_CHOICES]
        if value not in valid_plans:
            raise serializers.ValidationError(
                f'Plano inválido. Escolha entre: {", ".join(valid_plans)}'
            )
        return value
    
    def validate_country(self, value):
        valid_countries = ['CV', 'AO', 'SN']
        if value not in valid_countries:
            raise serializers.ValidationError(
                f'País inválido. Escolha entre: {", ".join(valid_countries)}'
            )
        return value


class TenantRegistrationCreateView(generics.CreateAPIView):
    """
    Public endpoint for tenant self-service registration.
    
    POST /api/v1/register/
    Body: {
        "company_name": "Empresa A Lda",
        "subdomain": "empresa-a",
        "plan": "starter",
        "contact_email": "admin@empresa-a.cv",
        "contact_name": "João Silva",
        "contact_phone": "+238991234567",
        "country": "CV"
    }
    
    Response: 201 Created with registration details
    """
    queryset = TenantRegistration.objects.none()
    serializer_class = TenantRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicEndpointThrottle]
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Create registration and queue verification email."""
        from .tasks import send_verification_email
        
        registration = serializer.save()
        
        # Queue verification email
        transaction.on_commit(
            lambda: send_verification_email.delay(registration_id=str(registration.id))
        )
        
        return registration


class TenantRegistrationVerifyView(APIView):
    """
    Public endpoint for email verification.
    
    GET /api/v1/register/verify/?token={uuid}
    
    Response:
    - 200: Token valid, provisioning started
    - 400: Token invalid or expired
    """
    permission_classes = [AllowAny]
    throttle_classes = [PublicEndpointThrottle]
    
    def get(self, request):
        from ..tasks import provision_tenant
        
        token = request.query_params.get('token')
        
        if not token:
            return Response(
                {'error': 'Token não fornecido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            registration = TenantRegistration.objects.get(verification_token=token)
        except TenantRegistration.DoesNotExist:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already verified
        if registration.status == TenantRegistration.STATUS_VERIFIED:
            return Response({
                'status': 'already_verified',
                'message': 'Email já verificado. A conta está a ser configurada.',
                'company_name': registration.company_name,
            })
        
        # Check if already active
        if registration.status == TenantRegistration.STATUS_ACTIVE:
            return Response({
                'status': 'already_active',
                'message': 'Conta já está activa. Faça login.',
                'company_name': registration.company_name,
            })
        
        # Check token expiry
        if registration.is_token_expired:
            registration.status = TenantRegistration.STATUS_REJECTED
            registration.error_message = 'Token expirado'
            registration.save(update_fields=['status', 'error_message'])
            
            return Response(
                {'error': 'Token expirado. Por favor, registe-se novamente.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark as verified and start provisioning
        registration.status = TenantRegistration.STATUS_VERIFIED
        registration.save(update_fields=['status'])
        
        # Queue provisioning task
        transaction.on_commit(
            lambda: provision_tenant.delay(registration_id=str(registration.id))
        )
        
        return Response({
            'status': 'verified',
            'message': 'Email verificado! A sua conta está a ser configurada.',
            'company_name': registration.company_name,
            'next_steps': 'Receberá um email com as credenciais em breve.',
        })


class TenantRegistrationStatusView(APIView):
    """
    Check registration status by token.
    
    GET /api/v1/register/status/?token={uuid}
    
    Used by frontend to poll for provisioning completion.
    """
    permission_classes = [AllowAny]
    throttle_classes = [PublicEndpointThrottle]
    
    def get(self, request):
        token = request.query_params.get('token')
        
        if not token:
            return Response(
                {'error': 'Token não fornecido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            registration = TenantRegistration.objects.select_related().get(
                verification_token=token
            )
        except TenantRegistration.DoesNotExist:
            return Response(
                {'error': 'Registo não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'status': registration.status,
            'status_display': registration.get_status_display(),
            'company_name': registration.company_name,
            'subdomain': registration.subdomain,
            'plan': registration.plan,
            'error_message': registration.error_message,
            'provisioned_at': registration.provisioned_at.isoformat() if registration.provisioned_at else None,
        })
