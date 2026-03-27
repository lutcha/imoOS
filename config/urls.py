from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.core.views import health_check, DetailedHealthCheckView
from apps.tenants.views_public import (
    TenantRegistrationCreateView,
    TenantRegistrationVerifyView,
    TenantRegistrationStatusView,
)

# Django Admin URL — configurable via environment variable
DJANGO_SUPERADMIN_URL = getattr(settings, 'DJANGO_SUPERADMIN_URL', 'django-admin/')

urlpatterns = [
    path(DJANGO_SUPERADMIN_URL, admin.site.urls),
    path('api/v1/health/', health_check, name='health-check'),
    path('api/v1/health/detailed/', DetailedHealthCheckView.as_view(), name='health-detailed'),
    
    # Tenant Registration (Sprint 7 - Prompt 03) - Public endpoints
    path('api/v1/register/', TenantRegistrationCreateView.as_view(), name='tenant-register'),
    path('api/v1/register/verify/', TenantRegistrationVerifyView.as_view(), name='tenant-register-verify'),
    path('api/v1/register/status/', TenantRegistrationStatusView.as_view(), name='tenant-register-status'),
    
    # API V1
    path('api/v1/', include('apps.tenants.urls')),
    path('api/v1/', include('apps.memberships.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/crm/', include('apps.crm.urls')),
    path('api/v1/contracts/', include('apps.contracts.urls')),
    path('api/v1/construction/', include('apps.construction.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/marketplace/', include('apps.marketplace.urls')),
    path('api/v1/investors/', include('apps.investors.urls')),
    path('api/v1/dashboard/', include('apps.core.dashboard_urls')),
    
    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

from django.conf import settings
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
