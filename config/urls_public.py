"""
Public schema URL configuration (PUBLIC_SCHEMA_URLCONF).
Only the lead-capture endpoint is intentionally exposed here.
All other paths return 404.
"""
from django.urls import path
from apps.crm.views_public import LeadCaptureView

urlpatterns = [
    path('api/v1/crm/lead-capture/', LeadCaptureView.as_view(), name='lead-capture-public'),
]
