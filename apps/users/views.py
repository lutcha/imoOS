from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, TenantTokenObtainPairSerializer


class TenantTokenObtainPairView(TokenObtainPairView):
    """
    Custom Login view to inject tenant claims in JWT.
    """
    serializer_class = TenantTokenObtainPairSerializer


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
