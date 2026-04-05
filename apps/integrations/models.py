"""
Models for WhatsApp Business API integration.
All models inherit from TenantAwareModel for multi-tenant isolation.
"""
from django.db import models
from django.conf import settings

from apps.core.models import TenantAwareModel


class WhatsAppTemplate(TenantAwareModel):
    """
    Templates aprovados pela Meta para envio via WhatsApp Business API.
    Cada tenant pode ter seus próprios templates customizados.
    """
    TEMPLATE_TYPES = [
        ('TASK_REMINDER', 'Lembrete de Tarefa'),
        ('PROGRESS_UPDATE', 'Atualização de Progresso'),
        ('CONTRACT_SIGNATURE', 'Assinatura Pendente'),
        ('OVERDUE_ALERT', 'Alerta de Atraso'),
        ('WELCOME', 'Mensagem de Boas-vindas'),
        ('DAILY_REPORT_REMINDER', 'Lembrete de Relatório Diário'),
    ]

    LANGUAGE_CHOICES = [
        ('pt_PT', 'Português (Portugal)'),
        ('pt_BR', 'Português (Brasil)'),
    ]

    name = models.CharField(max_length=100, help_text='Nome único do template')
    template_type = models.CharField(
        max_length=30,
        choices=TEMPLATE_TYPES,
        default='TASK_REMINDER',
        help_text='Tipo/categoria do template'
    )
    meta_template_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID do template na Meta (WhatsApp Business API)'
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='pt_PT'
    )
    content_pt = models.TextField(
        help_text='Conteúdo em português com placeholders {{variavel}}'
    )
    variables = models.JSONField(
        default=list,
        help_text='Lista de variáveis: ["{{nome}}", "{{tarefa}}", "{{data}}"]'
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        help_text='Utilizador que criou o template'
    )

    class Meta:
        app_label = 'integrations'
        verbose_name = 'Template WhatsApp'
        verbose_name_plural = 'Templates WhatsApp'
        unique_together = [('name',)]  # Único por tenant/schema
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_template_type_display()})'


class WhatsAppMessage(TenantAwareModel):
    """
    Log de todas as mensagens WhatsApp enviadas e recebidas.
    Mantém histórico completo para auditoria (LGPD/Lei 133/V/2019).
    """
    DIRECTION_OUTBOUND = 'OUTBOUND'
    DIRECTION_INBOUND = 'INBOUND'
    DIRECTION_CHOICES = [
        (DIRECTION_OUTBOUND, 'Enviada'),
        (DIRECTION_INBOUND, 'Recebida'),
    ]

    STATUS_SENT = 'SENT'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_READ = 'READ'
    STATUS_FAILED = 'FAILED'
    STATUS_PENDING = 'PENDING'
    STATUS_CHOICES = [
        (STATUS_SENT, 'Enviada'),
        (STATUS_DELIVERED, 'Entregue'),
        (STATUS_READ, 'Lida'),
        (STATUS_FAILED, 'Falhou'),
        (STATUS_PENDING, 'Pendente'),
    ]

    # Relacionamentos com models existentes (nullable para não quebrar)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='whatsapp_messages',
        help_text='Utilizador associado à mensagem'
    )
    lead = models.ForeignKey(
        'crm.Lead',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='whatsapp_messages',
        help_text='Lead associado à mensagem'
    )
    task = models.ForeignKey(
        'construction.ConstructionTask',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='whatsapp_messages',
        help_text='Tarefa de construção associada'
    )
    template = models.ForeignKey(
        WhatsAppTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='messages',
        help_text='Template utilizado (se aplicável)'
    )

    # Dados da mensagem
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        help_text='Direção da mensagem'
    )
    phone_number = models.CharField(
        max_length=20,
        help_text='Número de telefone no formato +2389991234'
    )
    message_body = models.TextField(
        help_text='Conteúdo da mensagem'
    )
    meta_message_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID da mensagem na Meta (para tracking)'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    # Timestamps de entrega
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Quando a mensagem foi enviada'
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Quando foi entregue no dispositivo'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Quando foi lida pelo destinatário'
    )

    # Para mensagens recebidas (inbound)
    inbound_response = models.CharField(
        max_length=50,
        blank=True,
        help_text='Resposta rápida: ✅, ❌, 1, 2, 3, etc.'
    )
    processed = models.BooleanField(
        default=False,
        help_text='Se a resposta inbound já foi processada'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Quando a resposta foi processada'
    )

    # Metadados adicionais
    error_message = models.TextField(
        blank=True,
        help_text='Mensagem de erro em caso de falha'
    )
    raw_webhook_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Dados brutos do webhook (para debugging)'
    )

    class Meta:
        app_label = 'integrations'
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['phone_number', '-sent_at'], name='whatsapp_msg_phone_idx'),
            models.Index(fields=['status', 'processed'], name='whatsapp_msg_status_proc_idx'),
            models.Index(fields=['user', '-sent_at'], name='whatsapp_msg_user_idx'),
            models.Index(fields=['task', '-sent_at'], name='whatsapp_msg_task_idx'),
        ]

    def __str__(self):
        direction_label = '→' if self.direction == self.DIRECTION_OUTBOUND else '←'
        return f'{direction_label} {self.phone_number} ({self.status})'

    def mark_delivered(self):
        """Marcar mensagem como entregue."""
        from django.utils import timezone
        self.status = self.STATUS_DELIVERED
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])

    def mark_read(self):
        """Marcar mensagem como lida."""
        from django.utils import timezone
        self.status = self.STATUS_READ
        self.read_at = timezone.now()
        if not self.delivered_at:
            self.delivered_at = self.read_at
        self.save(update_fields=['status', 'read_at', 'delivered_at'])

    def mark_failed(self, error_message=''):
        """Marcar mensagem como falhada."""
        self.status = self.STATUS_FAILED
        self.error_message = error_message[:500]  # Limitar tamanho
        self.save(update_fields=['status', 'error_message'])

    def mark_processed(self):
        """Marcar resposta inbound como processada."""
        from django.utils import timezone
        self.processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['processed', 'processed_at'])


class NotificationPreference(TenantAwareModel):
    """
    Preferências de notificação por utilizador.
    Permite controlar canais de comunicação (WhatsApp, Email, etc).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        help_text='Utilizador associado às preferências'
    )

    # Canais de comunicação
    whatsapp_enabled = models.BooleanField(
        default=True,
        help_text='Receber notificações via WhatsApp'
    )
    email_enabled = models.BooleanField(
        default=True,
        help_text='Receber notificações via Email'
    )
    sms_enabled = models.BooleanField(
        default=False,
        help_text='Receber notificações via SMS (fallback)'
    )

    # Configurações de urgência
    urgent_only_whatsapp = models.BooleanField(
        default=False,
        help_text='Só enviar WhatsApp para notificações urgentes'
    )
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text='Início do período de silêncio (não enviar notificações)'
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text='Fim do período de silêncio'
    )

    # Tipos de notificação específicos
    notify_task_assignment = models.BooleanField(
        default=True,
        help_text='Notificar quando atribuída nova tarefa'
    )
    notify_task_overdue = models.BooleanField(
        default=True,
        help_text='Notificar tarefas atrasadas'
    )
    notify_daily_reminder = models.BooleanField(
        default=True,
        help_text='Lembrete diário de tarefas (8h)'
    )

    # Metadados
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'integrations'
        verbose_name = 'Preferência de Notificação'
        verbose_name_plural = 'Preferências de Notificação'

    def __str__(self):
        return f'Preferências de {self.user.email}'

    def is_quiet_hours(self):
        """Verificar se está em período de silêncio."""
        from django.utils import timezone
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        now = timezone.localtime().time()
        if self.quiet_hours_start <= self.quiet_hours_end:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:  # Crosses midnight
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end

    def should_notify_whatsapp(self, is_urgent=False):
        """Determinar se deve enviar notificação WhatsApp."""
        if not self.whatsapp_enabled:
            return False
        if self.is_quiet_hours() and not is_urgent:
            return False
        if self.urgent_only_whatsapp and not is_urgent:
            return False
        return True
