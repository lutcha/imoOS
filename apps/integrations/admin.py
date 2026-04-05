"""
Admin configuration for WhatsApp Business API integration.
"""
from django.contrib import admin

from apps.integrations.models import WhatsAppMessage, WhatsAppTemplate, NotificationPreference


@admin.register(WhatsAppTemplate)
class WhatsAppTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'language', 'is_active', 'created_at']
    list_filter = ['template_type', 'language', 'is_active']
    search_fields = ['name', 'content_pt']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Conteúdo', {
            'fields': ('content_pt', 'variables', 'language')
        }),
        ('Meta API', {
            'fields': ('meta_template_id',),
            'description': 'ID do template registrado na Meta'
        }),
        ('Metadados', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'direction', 'phone_number', 'status', 
        'user', 'sent_at', 'delivered_at', 'processed'
    ]
    list_filter = ['direction', 'status', 'sent_at', 'processed']
    search_fields = ['phone_number', 'message_body', 'meta_message_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('direction', 'status', 'phone_number')
        }),
        ('Conteúdo', {
            'fields': ('message_body', 'inbound_response')
        }),
        ('Relacionamentos', {
            'fields': ('user', 'lead', 'task', 'template')
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'delivered_at', 'read_at', 'processed_at')
        }),
        ('Meta/Tracking', {
            'fields': ('meta_message_id', 'error_message', 'processed'),
            'classes': ('collapse',)
        }),
        ('Debug', {
            'fields': ('raw_webhook_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Otimizar queryset com select_related."""
        return super().get_queryset(request).select_related('user', 'lead', 'task', 'template')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'whatsapp_enabled', 'email_enabled', 
        'urgent_only_whatsapp', 'updated_at'
    ]
    list_filter = ['whatsapp_enabled', 'email_enabled', 'urgent_only_whatsapp']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Canais de Notificação', {
            'fields': ('whatsapp_enabled', 'email_enabled', 'sms_enabled')
        }),
        ('Configurações de Urgência', {
            'fields': ('urgent_only_whatsapp', 'quiet_hours_start', 'quiet_hours_end')
        }),
        ('Tipos de Notificação', {
            'fields': (
                'notify_task_assignment', 
                'notify_task_overdue', 
                'notify_daily_reminder'
            )
        }),
    )
