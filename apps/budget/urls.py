"""
Budget URLs — URLs para o app budget.

Base path: /api/v1/budget/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.budget.views import (
    LocalPriceItemViewSet, SimpleBudgetViewSet,
    BudgetItemViewSet, CrowdsourcedPriceViewSet,
    UserPriceScoreViewSet, ConstructionExpenseViewSet,
    ConstructionAdvanceViewSet
)

router = DefaultRouter()
router.register(r'price-items', LocalPriceItemViewSet, basename='price-item')
router.register(r'budgets', SimpleBudgetViewSet, basename='budget')
router.register(r'budget-items', BudgetItemViewSet, basename='budget-item')
router.register(r'crowdsourced', CrowdsourcedPriceViewSet, basename='crowdsourced-price')
router.register(r'scores', UserPriceScoreViewSet, basename='user-score')
router.register(r'expenses', ConstructionExpenseViewSet, basename='construction-expense')
router.register(r'advances', ConstructionAdvanceViewSet, basename='construction-advance')

urlpatterns = [
    path('', include(router.urls)),
]
