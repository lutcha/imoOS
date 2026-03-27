from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ImoCvWebhookView, MarketplaceListingViewSet

router = DefaultRouter()
router.register(r'listings', MarketplaceListingViewSet, basename='marketplace-listing')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/imocv/', ImoCvWebhookView.as_view(), name='imocv-webhook'),
]
