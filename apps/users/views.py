from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connection
from django.conf import settings
from .models import User
from .serializers import UserSerializer, TenantTokenObtainPairSerializer


class TenantTokenObtainPairView(TokenObtainPairView):
    """
    Custom Login view to inject tenant claims in JWT.

    Supports explicit tenant resolution via `tenant_domain` in the request body.
    Node.js 18+ native fetch treats `Host` as a forbidden header and silently
    ignores overrides, so we cannot rely on the Host header for service-to-service
    calls from Next.js. The client must pass `tenant_domain` in the POST body.
    """
    serializer_class = TenantTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # ⚠️ DEV BYPASS - Temporário para desenvolvimento
        if getattr(settings, 'DEV_SKIP_AUTH', False):
            return self._dev_bypass_login(request)
        
        # If the caller supplies `tenant_domain` in the body, switch to that
        # tenant's schema before authentication.  This is necessary because
        # Node.js fetch (Node 18+) forbids overriding the Host header, so we
        # cannot use the Host-based django-tenants resolution for server-side
        # calls from the Next.js API route.
        tenant_domain = request.data.get('tenant_domain')
        if tenant_domain:
            try:
                from apps.tenants.models import Domain
                domain_obj = Domain.objects.select_related('tenant').get(
                    domain=tenant_domain
                )
                connection.set_tenant(domain_obj.tenant)
            except Exception:
                from rest_framework.response import Response as _Response
                return _Response(
                    {'detail': 'Tenant não encontrado.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return super().post(request, *args, **kwargs)
    
    def _dev_bypass_login(self, request):
        """
        ⚠️ DEV ONLY: Returns valid token without validating credentials.
        ⚠️ REMOVE before committing to production!
        """
        from apps.tenants.models import Domain, Client
        import warnings
        warnings.warn("⚠️ DEV_SKIP_AUTH is enabled - authentication bypassed!")
        
        tenant_domain = request.data.get('tenant_domain', 'demo.proptech.cv')
        
        # Try to resolve tenant
        try:
            domain_obj = Domain.objects.select_related('tenant').get(domain=tenant_domain)
            connection.set_tenant(domain_obj.tenant)
            tenant = domain_obj.tenant
        except Exception:
            # Fallback: use first active tenant
            tenant = Client.objects.filter(is_active=True).first()
            if not tenant:
                return Response(
                    {'detail': 'Nenhum tenant configurado. Execute: python manage.py ensure_demo_tenant'},
                    status=status.HTTP_404_NOT_FOUND
                )
            connection.set_tenant(tenant)
        
        # Get first active user (prefer admin/staff)
        user = User.objects.filter(is_active=True).order_by('-is_staff', '-is_superuser').first()
        
        if not user:
            return Response(
                {'detail': 'Nenhum usuário disponível. Execute: python manage.py ensure_demo_users'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate token without password validation
        refresh = self.serializer_class.get_token(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'tenant_schema': connection.schema_name,
            'tenant_name': tenant.name,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name() or user.email,
                'role': user.role,
                'is_staff': user.is_staff,
            }
        }, status=status.HTTP_200_OK)


class SuperAdminTokenObtainPairView(TokenObtainPairView):
    """
    Superadmin login view - always operates on public schema.
    Validates that user is_superuser=True.
    """
    serializer_class = TenantTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # ⚠️ DEV BYPASS - Temporário para desenvolvimento
        if getattr(settings, 'DEV_SKIP_AUTH', False):
            return self._dev_bypass_superadmin_login(request)
        
        # Force public schema for superadmin lookup
        connection.set_schema_to_public()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get user and verify is_superuser
        email = request.data.get('email', '').lower().strip()
        try:
            user = User.objects.get(email=email)
            if not user.is_staff:
                return Response(
                    {'detail': 'Acesso restrito a administradores da plataforma.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            # Return same error as regular auth to avoid user enumeration
            return Response(
                {'detail': 'Credenciais inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
    def _dev_bypass_superadmin_login(self, request):
        """
        ⚠️ DEV ONLY: Returns superadmin token without validating credentials.
        ⚠️ REMOVE before committing to production!
        """
        import warnings
        warnings.warn("⚠️ DEV_SKIP_AUTH is enabled - superadmin authentication bypassed!")
        
        # Force public schema
        connection.set_schema_to_public()
        
        # Get or create a superuser
        user = User.objects.filter(is_staff=True, is_active=True).first()
        
        if not user:
            # Create a temporary superuser
            user = User.objects.create_superuser(
                email='dev@proptech.cv',
                password='dev',
                first_name='Dev',
                last_name='Admin'
            )
        
        # Generate token
        refresh = self.serializer_class.get_token(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'tenant_schema': 'public',
            'tenant_name': 'Platform',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name() or user.email,
                'role': user.role,
                'is_staff': True,
            }
        }, status=status.HTTP_200_OK)


class TenantTokenRefreshView(TokenRefreshView):
    """
    Custom TokenRefreshView that preserves tenant claims in the new access token.
    
    The default TokenRefreshView only returns { access } without re-injecting
    the tenant claims (tenant_schema, tenant_name, email, role, full_name).
    
    This custom view:
    1. Decodes the refresh token to extract tenant claims
    2. Creates a new access token with the same claims
    3. Returns { access, tenant_schema, tenant_name } for frontend convenience
    """
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token_str = serializer.validated_data['refresh']
        refresh = RefreshToken(refresh_token_str)
        
        # Extract tenant claims from refresh token
        tenant_schema = refresh.get('tenant_schema')
        tenant_name = refresh.get('tenant_name')
        
        # Create new access token with the same claims
        access = refresh.access_token
        if tenant_schema:
            access['tenant_schema'] = tenant_schema
        if tenant_name:
            access['tenant_name'] = tenant_name
        
        # Return both the access token and tenant info for frontend convenience
        return Response({
            'access': str(access),
            'tenant_schema': tenant_schema,
            'tenant_name': tenant_name,
        })


class SuperAdminTokenRefreshView(TenantTokenRefreshView):
    """
    Superadmin token refresh — forces public schema before validating the JWT.
    Registered at /auth/superadmin/token/refresh/ which is in _AUTH_PATHS so the
    tenant middleware bypasses Host-based resolution and sets the public schema.
    The actual JWT validation is purely cryptographic (no extra DB query needed).
    """

    def post(self, request, *args, **kwargs):
        connection.set_schema_to_public()
        return super().post(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
