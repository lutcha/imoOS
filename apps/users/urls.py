from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TenantTokenObtainPairView, TenantTokenRefreshView

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('auth/token/', TenantTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TenantTokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
