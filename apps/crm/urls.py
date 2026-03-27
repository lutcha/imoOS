from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, InteractionViewSet, ReservationViewSet
from .views_public import LeadCaptureView, WhatsAppWebhookView


router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'interactions', InteractionViewSet, basename='interaction')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('lead-capture/', LeadCaptureView.as_view(), name='lead-capture'),
    path('whatsapp-webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
    path('', include(router.urls)),
]

