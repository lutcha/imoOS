from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyReportViewSet, ConstructionPhotoViewSet

router = DefaultRouter()
router.register(r'daily-reports', DailyReportViewSet, basename='daily-report')
router.register(r'photos', ConstructionPhotoViewSet, basename='construction-photo')

urlpatterns = [
    path('', include(router.urls)),
]
