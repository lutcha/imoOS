from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    TenantTokenObtainPairView,
    TenantTokenRefreshView,
    SuperAdminTokenObtainPairView,
    SuperAdminTokenRefreshView,
)

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    # Tenant auth endpoints
    path('auth/token/', TenantTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TenantTokenRefreshView.as_view(), name='token_refresh'),
    
    # Superadmin auth endpoints (always on public schema, bypassed by middleware)
    path('auth/superadmin/token/', SuperAdminTokenObtainPairView.as_view(), name='superadmin_token_obtain'),
    path('auth/superadmin/token/refresh/', SuperAdminTokenRefreshView.as_view(), name='superadmin_token_refresh'),
    
    path('', include(router.urls)),
]
