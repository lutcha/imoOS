from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, InteractionViewSet
from .views_public import LeadCaptureView


router = DefaultRouter()
router.register(r'leads', LeadViewSet)
router.register(r'interactions', InteractionViewSet)

urlpatterns = [
    path('lead-capture/', LeadCaptureView.as_view(), name='lead-capture'),
    path('', include(router.urls)),
]

