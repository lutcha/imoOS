from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnitViewSet, UnitTypeViewSet, UnitOccurrenceViewSet

router = DefaultRouter()
router.register(r'units', UnitViewSet)
router.register(r'unit-types', UnitTypeViewSet)
router.register(r'unit-occurrences', UnitOccurrenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
