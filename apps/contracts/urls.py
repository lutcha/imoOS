from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractViewSet, PaymentViewSet, ContractTemplateViewSet, PaymentPatternViewSet

router = DefaultRouter()
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'templates', ContractTemplateViewSet, basename='template')
router.register(r'patterns', PaymentPatternViewSet, basename='pattern')

urlpatterns = [path('', include(router.urls))]
