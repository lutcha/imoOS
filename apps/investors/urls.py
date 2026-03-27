from rest_framework.routers import DefaultRouter
from .views import InvestorPortalViewSet

router = DefaultRouter()
router.register(r'portal', InvestorPortalViewSet, basename='investor-portal')

urlpatterns = router.urls
