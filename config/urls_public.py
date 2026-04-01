"""
Public schema URL configuration (PUBLIC_SCHEMA_URLCONF).
Served on the platform domain (e.g. imos.cv) — no tenant context.

Routes here must be either:
  - Unauthenticated public endpoints (lead capture, health)
  - Staff-only platform admin endpoints (tenant management)
"""
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from apps.core.views import health_check
from apps.crm.views_public import LeadCaptureView
from apps.contracts.views_public import SignatureView
from apps.tenants.views import TenantViewSet
from apps.tenants.views_public import (
    TenantRegistrationCreateView,
    TenantRegistrationVerifyView,
    TenantRegistrationStatusView,
)
from apps.marketplace.views_public import ImoCvPlatformWebhookView
from django_prometheus import exports

# Staff-only platform admin — manage all tenants
_admin_router = DefaultRouter()
_admin_router.register(r'admin/tenants', TenantViewSet, basename='tenant')

urlpatterns = [
    # Redirect root to /app (Frontend)
    path('', RedirectView.as_view(url='/app', permanent=False)),

    # Health check — must be first, hit by DO App Platform on the public domain
    path('api/v1/health/', health_check, name='health-check'),

    # Public unauthenticated
    path('api/v1/crm/lead-capture/', LeadCaptureView.as_view(), name='lead-capture-public'),
    path('api/v1/sign/<uuid:token>/', SignatureView.as_view(), name='contract-sign'),
    # imo.cv platform webhook — resolves tenant from imocv_listing_id
    path('api/v1/marketplace/webhook/imocv/', ImoCvPlatformWebhookView.as_view(), name='imocv-webhook-platform'),

    # Tenant Registration (Sprint 7 - Prompt 03)
    path('api/v1/register/', TenantRegistrationCreateView.as_view(), name='tenant-register'),
    path('api/v1/register/verify/', TenantRegistrationVerifyView.as_view(), name='tenant-register-verify'),
    path('api/v1/register/status/', TenantRegistrationStatusView.as_view(), name='tenant-register-status'),

    # Auth (allowed on platform domain)
    path('api/v1/users/', include('apps.users.urls')),

    # Dashboard (sometimes reversed during auth/member checks)
    path('api/v1/dashboard/', include('apps.core.dashboard_urls')),

    # Platform admin (is_staff required by TenantViewSet)
    path('api/v1/', include(_admin_router.urls)),

    # Prometheus metrics (Sprint 7)
    path('metrics/', exports.ExportToDjangoView, name='prometheus-metrics'),
]

from django.conf import settings
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
