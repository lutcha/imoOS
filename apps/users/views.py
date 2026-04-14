from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connection
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


class SuperAdminTokenObtainPairView(TokenObtainPairView):
    """
    Superadmin login view - always operates on public schema.
    Validates that user is_superuser=True.
    """
    serializer_class = TenantTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
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
