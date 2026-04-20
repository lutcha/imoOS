from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connection
from .models import User
from .serializers import UserSerializer, TenantTokenObtainPairSerializer


class TenantTokenObtainPairView(TokenObtainPairView):
    """Login tenant. Recebe tenant_domain no body para resolver o schema."""
    serializer_class = TenantTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        tenant_domain = request.data.get('tenant_domain')
        if tenant_domain:
            try:
                from apps.tenants.models import Domain
                domain_obj = Domain.objects.select_related('tenant').get(domain=tenant_domain)
                connection.set_tenant(domain_obj.tenant)
            except Exception:
                return Response({'detail': 'Tenant não encontrado.'}, status=400)
        return super().post(request, *args, **kwargs)


class SuperAdminTokenObtainPairView(TokenObtainPairView):
    """Login superadmin. Sempre em schema público. Requer is_staff=True."""
    serializer_class = TenantTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        connection.set_schema_to_public()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email', '').lower().strip()
        try:
            user = User.objects.get(email=email)
            if not user.is_staff:
                return Response({'detail': 'Acesso restrito a staff.'}, status=403)
        except User.DoesNotExist:
            return Response({'detail': 'Credenciais inválidas.'}, status=401)
        return Response(serializer.validated_data, status=200)


class TenantTokenRefreshView(TokenRefreshView):
    """Refresh tenant session. Preserva claims tenant_schema no novo access token."""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = RefreshToken(serializer.validated_data['refresh'])
        tenant_schema = refresh.get('tenant_schema')
        tenant_name = refresh.get('tenant_name')
        access = refresh.access_token
        if tenant_schema:
            access['tenant_schema'] = tenant_schema
        if tenant_name:
            access['tenant_name'] = tenant_name
        return Response({'access': str(access), 'tenant_schema': tenant_schema, 'tenant_name': tenant_name})


class SuperAdminTokenRefreshView(TenantTokenRefreshView):
    """Refresh superadmin session. Força public schema."""

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
