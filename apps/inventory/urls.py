from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnitViewSet, UnitTypeViewSet

router = DefaultRouter()
router.register(r'units', UnitViewSet)
router.register(r'unit-types', UnitTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
