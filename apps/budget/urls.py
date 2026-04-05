"""
Budget URLs - ImoOS
URLs para preços, orçamentos e gamificação.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.PriceCategoryViewSet)
router.register(r'prices', views.PriceItemViewSet)
router.register(r'crowdsource', views.CrowdsourcedPriceViewSet, basename='crowdsource')
router.register(r'budgets', views.BudgetViewSet)
router.register(r'points', views.UserPointsViewSet, basename='points')

# Nested router para itens de orçamento
budget_items_urls = [
    path('', views.BudgetItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='budgetitem-list'),
    path('<uuid:pk>/', views.BudgetItemViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='budgetitem-detail'),
    path('bulk-create/', views.BudgetItemViewSet.as_view({'post': 'bulk_create'}), name='budgetitem-bulk-create'),
]

urlpatterns = [
    path('', include(router.urls)),
    
    # Budget Items (nested under budgets)
    path('budgets/<uuid:budget_pk>/items/', include(budget_items_urls)),
    
    # Gamification
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('my-points/', views.my_points, name='my-points'),
    
    # Legacy API endpoints (para compatibilidade)
    path('prices/search/', views.PriceItemViewSet.as_view({'get': 'search'}), name='price-search'),
]
