from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantSettingsView, S3PresignedUploadView, UsageView, PlanEventsView, SuperAdminTenantViewSet

# TenantViewSet (admin CRUD) lives in config/urls_public.py — staff-only,
# served from the platform domain, not from tenant subdomains.

# Super-admin router — Sprint 7
superadmin_router = DefaultRouter()
superadmin_router.register(r'tenants', SuperAdminTenantViewSet, basename='superadmin-tenant')

urlpatterns = [
    # Super-admin endpoints (Sprint 7)
    path('superadmin/', include(superadmin_router.urls)),
    
    # Current tenant's branding & integration settings
    path('tenant/settings/', TenantSettingsView.as_view(), name='tenant-settings'),
    # S3 presigned upload URL (tenant-scoped key prefix)
    path('tenant/s3-upload/', S3PresignedUploadView.as_view(), name='tenant-s3-upload'),
    # Plan consumption / usage
    path('tenant/usage/', UsageView.as_view(), name='tenant-usage'),
    # Plan event history
    path('tenant/plan-events/', PlanEventsView.as_view(), name='tenant-plan-events'),
]
