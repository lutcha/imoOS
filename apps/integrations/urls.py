"""
URLs para WhatsApp Business API integration.
"""
from django.urls import path

from apps.integrations import views

urlpatterns = [
    # Webhook para receber mensagens (público, verificado por token)
    path('webhook/', views.whatsapp_webhook, name='whatsapp-webhook'),
    
    # API endpoints (autenticados)
    path('send-test/', views.send_test_message, name='send-test'),
    path('send-task/', views.send_task_notification, name='send-task-notification'),
    path('send-menu/', views.send_interactive_menu, name='send-interactive-menu'),
    path('preferences/', views.notification_preferences, name='notification-preferences'),
    path('history/', views.message_history, name='message-history'),
    path('templates/', views.WhatsAppTemplateListView.as_view(), name='template-list'),
]
