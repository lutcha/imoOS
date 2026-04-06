"""
Workflow URLs — Rotas da API para workflows.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.workflows import views

router = DefaultRouter()
router.register(r'definitions', views.WorkflowViewSet, basename='workflow-definition')
router.register(r'instances', views.WorkflowInstanceViewSet, basename='workflow-instance')
router.register(r'sales', views.SalesWorkflowViewSet, basename='sales-workflow')
router.register(r'project-init', views.ProjectInitWorkflowViewSet, basename='project-init-workflow')
router.register(r'payment-milestones', views.PaymentMilestoneWorkflowViewSet, basename='payment-milestone-workflow')
router.register(r'notifications', views.NotificationWorkflowViewSet, basename='notification-workflow')
router.register(r'dashboard', views.WorkflowDashboardViewSet, basename='workflow-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
