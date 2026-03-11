from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer, TenantTokenObtainPairSerializer

class TenantTokenObtainPairView(TokenObtainPairView):
    """
    Custom Login view to inject tenant claims in JWT.
    """
    serializer_class = TenantTokenObtainPairSerializer

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
