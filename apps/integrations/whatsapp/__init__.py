"""
WhatsApp Integration Module for ImoOS

Provides bidirectional communication via WhatsApp Business API.
- Proactive notifications for tasks, deadlines, contracts
- Inbound message processing with command parsing
- Fallback to SMS if WhatsApp fails

Usage:
    from apps.integrations.whatsapp.services import WhatsAppService
    
    # Send notification
    WhatsAppService.send_task_reminder(task_id, phone_number)
    
    # Process inbound webhook (called from views)
    WhatsAppService.process_inbound_message(data)
"""

default_app_config = 'apps.integrations.whatsapp.apps.WhatsAppConfig'
