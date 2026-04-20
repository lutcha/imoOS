"""
Construction API URLs.

Endpoints disponíveis:
- /phases/ - Fases da obra
- /tasks/ - Tarefas (Simple + Advanced mode)
- /photos/ - Fotos das tasks
- /dependencies/ - Dependências entre tasks (Advanced)
- /cpm/ - CPM (Critical Path Method)
- /evm/ - EVM (Earned Value Management)
- /dashboard/ - Dashboard aggregado
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ConstructionPhaseViewSet,
    ConstructionTaskViewSet,
    TaskPhotoViewSet,
    TaskDependencyViewSet,
    CPMViewSet,
    EVMViewSet,
    ConstructionDashboardViewSet,
    DailyReportViewSet,
    ConstructionPhotoViewSet,
)

router = DefaultRouter()
router.register(r'phases', ConstructionPhaseViewSet, basename='construction-phase')
router.register(r'tasks', ConstructionTaskViewSet, basename='construction-task')
router.register(r'photos', TaskPhotoViewSet, basename='task-photo')
router.register(r'dependencies', TaskDependencyViewSet, basename='task-dependency')
router.register(r'cpm', CPMViewSet, basename='cpm')
router.register(r'evm', EVMViewSet, basename='evm')
router.register(r'dashboard', ConstructionDashboardViewSet, basename='construction-dashboard')
router.register(r'daily-reports', DailyReportViewSet, basename='daily-report')
router.register(r'construction-photos', ConstructionPhotoViewSet, basename='construction-photo')

urlpatterns = [
    path('', include(router.urls)),
]
