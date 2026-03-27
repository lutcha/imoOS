from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [path('', include(router.urls))]
