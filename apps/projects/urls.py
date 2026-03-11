from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, BuildingViewSet, FloorViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'floors', FloorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
