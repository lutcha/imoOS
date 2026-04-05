"""
WhatsApp Integration Models

All models extend TenantAwareModel for multi-tenant isolation.
No existing models are modified - only new extension tables created.
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TenantAwareModel


class WhatsAppContact(TenantAwareModel):
    """
    Extends User/Lead with WhatsApp contact information.
    Maintains LGPD compliance with opt-in tracking.
    
    This model does NOT modify existing User/Lead models.
    It's a separate table linked via OneToOneField.
    """
    
    # Link to existing entities (optional - can be standalone for leads)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='whatsapp_contact',
        verbose_name='Utilizador',
    )
    lead = models.OneToOneField(
        'crm.Lead',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='whatsapp_contact',
        verbose_name='Lead',
    )
    
    # Phone number in E.164 format (+2389991234)
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Número WhatsApp',
        help_text='Formato internacional: +2389991234'
    )
    
    # Display name (from WhatsApp profile or manual entry)
    display_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nome de Exibição'
    )
    
    # LGPD Compliance - explicit opt-in required
    opted_in = models.BooleanField(
        default=False,
        verbose_name='Consentimento LGPD',
        help_text='Utilizador consentiu receber comunicações via WhatsApp'
    )
    opted_in_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data do Consentimento'
    )
    opted_in_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP do Consentimento'
    )
    
    # WhatsApp Business API specific
    wa_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='WhatsApp ID',
        help_text='ID único atribuído pelo WhatsApp Business API'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    blocked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Bloqueado Em',
        help_text='Quando o utilizador bloqueou ou reportou spam'
    )
    block_reason = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Motivo do Bloqueio'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_interaction_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Interacção'
    )
    
    class Meta:
        app_label = 'whatsapp'
        verbose_name = 'Contacto WhatsApp'
        verbose_name_plural = 'Contactos WhatsApp'
        unique_together = [('tenant', 'phone_number')]
        indexes = [
            models.Index(fields=['tenant', 'phone_number'], name='wa_contact_phone_idx'),
            models.Index(fields=['tenant', 'user'], name='wa_contact_user_idx'),
            models.Index(fields=['tenant', 'opted_in'], name='wa_contact_optin_idx'),
        ]
    
    def __str__(self):
        name = self.display_name or (self.user.get_full_name() if self.user else self.phone_number)
        return f'{name} ({self.phone_number})'
    
    def opt_in(self, ip_address=None):
        """Record explicit opt-in consent (LGPD compliance)."""
        self.opted_in = True
        self.opted_in_at = timezone.now()
        self.opted_in_ip = ip_address
        self.save(update_fields=['opted_in', 'opted_in_at', 'opted_in_ip'])
    
    def opt_out(self):
        """Record opt-out (user revocation of consent)."""
        self.opted_in = False
        self.opted_in_at = None
        self.opted_in_ip = None
        self.save(update_fields=['opted_in', 'opted_in_at', 'opted_in_ip'])
    
    def record_interaction(self):
        """Update last interaction timestamp."""
        self.last_interaction_at = timezone.now()
        self.save(update_fields=['last_interaction_at'])
    
    def block(self, reason=''):
        """Block this contact (user reported spam or blocked us)."""
        self.is_active = False
        self.blocked_at = timezone.now()
        self.block_reason = reason
        self.save(update_fields=['is_active', 'blocked_at', 'block_reason'])


class WhatsAppMessageLog(TenantAwareModel):
    """
    Complete audit trail of all WhatsApp messages.
    Required for LGPD/Lei 133/V/2019 compliance.
    """
    
    # Direction
    DIRECTION_OUTBOUND = 'OUTBOUND'
    DIRECTION_INBOUND = 'INBOUND'
    DIRECTION_CHOICES = [
        (DIRECTION_OUTBOUND, 'Enviada'),
        (DIRECTION_INBOUND, 'Recebida'),
    ]
    
    # Message types
    TYPE_TEXT = 'TEXT'
    TYPE_IMAGE = 'IMAGE'
    TYPE_AUDIO = 'AUDIO'
    TYPE_DOCUMENT = 'DOCUMENT'
    TYPE_LOCATION = 'LOCATION'
    TYPE_TEMPLATE = 'TEMPLATE'
    TYPE_CHOICES = [
        (TYPE_TEXT, 'Texto'),
        (TYPE_IMAGE, 'Imagem'),
        (TYPE_AUDIO, 'Áudio'),
        (TYPE_DOCUMENT, 'Documento'),
        (TYPE_LOCATION, 'Localização'),
        (TYPE_TEMPLATE, 'Template'),
    ]
    
    # Status tracking
    STATUS_PENDING = 'PENDING'
    STATUS_SENT = 'SENT'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_READ = 'READ'
    STATUS_FAILED = 'FAILED'
    STATUS_RECEIVED = 'RECEIVED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_SENT, 'Enviada'),
        (STATUS_DELIVERED, 'Entregue'),
        (STATUS_READ, 'Lida'),
        (STATUS_FAILED, 'Falhou'),
        (STATUS_RECEIVED, 'Recebida'),
    ]
    
    contact = models.ForeignKey(
        WhatsAppContact,
        on_delete=models.CASCADE,
        related_name='message_logs',
        verbose_name='Contacto'
    )
    
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        verbose_name='Direcção'
    )
    message_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Tipo de Mensagem'
    )
    
    # Content
    content = models.TextField(
        blank=True,
        verbose_name='Conteúdo',
        help_text='Texto da mensagem ou legenda da mídia'
    )
    media_url = models.URLField(
        blank=True,
        verbose_name='URL da Mídia',
        help_text='URL temporário para foto/áudio/documento'
    )
    media_mime_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tipo MIME'
    )
    media_s3_key = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Chave S3',
        help_text='Chave do arquivo armazenado no S3 (para fotos recebidas)'
    )
    
    # External IDs from provider (Twilio/Meta)
    external_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID Externo',
        help_text='ID da mensagem no provedor (Twilio SID ou Meta ID)'
    )
    external_status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Status Externo'
    )
    
    # Status timestamps
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Status'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Enviada Em'
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Entregue Em'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Lida Em'
    )
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Falhou Em'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensagem de Erro'
    )
    
    # Link to related objects (generic, non-invasive)
    # Using string references to avoid circular imports
    related_task_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name='ID da Tarefa Relacionada'
    )
    related_contract_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name='ID do Contrato Relacionado'
    )
    related_lead_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name='ID do Lead Relacionado'
    )
    
    # Additional context
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadados',
        help_text='Dados adicionais específicos do contexto'
    )
    
    # Provider info
    provider = models.CharField(
        max_length=20,
        default='twilio',
        verbose_name='Provedor',
        help_text='twilio, meta, etc.'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'whatsapp'
        verbose_name = 'Log de Mensagem'
        verbose_name_plural = 'Logs de Mensagens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'contact', '-created_at'], name='wa_msg_contact_date_idx'),
            models.Index(fields=['tenant', 'external_id'], name='wa_msg_external_idx'),
            models.Index(fields=['tenant', 'status'], name='wa_msg_status_idx'),
            models.Index(fields=['tenant', 'direction', '-created_at'], name='wa_msg_direction_date_idx'),
            models.Index(fields=['tenant', 'related_task_id'], name='wa_msg_task_idx'),
        ]
    
    def __str__(self):
        direction_icon = '➡️' if self.direction == self.DIRECTION_OUTBOUND else '⬅️'
        return f'{direction_icon} {self.contact.phone_number} - {self.get_message_type_display()} ({self.status})'
    
    def mark_sent(self, external_id=None):
        """Mark message as sent."""
        self.status = self.STATUS_SENT
        self.sent_at = timezone.now()
        if external_id:
            self.external_id = external_id
        self.save(update_fields=['status', 'sent_at', 'external_id'])
    
    def mark_delivered(self):
        """Mark message as delivered to device."""
        self.status = self.STATUS_DELIVERED
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])
    
    def mark_read(self):
        """Mark message as read by recipient."""
        self.status = self.STATUS_READ
        self.read_at = timezone.now()
        self.save(update_fields=['status', 'read_at'])
    
    def mark_failed(self, error_message=''):
        """Mark message as failed."""
        self.status = self.STATUS_FAILED
        self.failed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=['status', 'failed_at', 'error_message'])


class WhatsAppCommand(TenantAwareModel):
    """
    Maps inbound text commands to system actions.
    Supports multiple aliases for the same command.
    """
    
    # Command types
    ACTION_TASK_COMPLETE = 'TASK_COMPLETE'
    ACTION_TASK_PROGRESS = 'TASK_PROGRESS'
    ACTION_TASK_ISSUE = 'TASK_ISSUE'
    ACTION_HELP = 'HELP'
    ACTION_PHOTO_UPLOAD = 'PHOTO_UPLOAD'
    ACTION_STATUS_CHECK = 'STATUS_CHECK'
    ACTION_OPT_OUT = 'OPT_OUT'
    ACTION_MENU = 'MENU'
    
    ACTION_CHOICES = [
        (ACTION_TASK_COMPLETE, '✅ Concluir Tarefa'),
        (ACTION_TASK_PROGRESS, '⏳ Em Andamento'),
        (ACTION_TASK_ISSUE, '❌ Reportar Problema'),
        (ACTION_HELP, '❓ Ajuda'),
        (ACTION_PHOTO_UPLOAD, '📷 Upload de Foto'),
        (ACTION_STATUS_CHECK, '📊 Verificar Status'),
        (ACTION_OPT_OUT, '🚫 Cancelar Subscrição'),
        (ACTION_MENU, '📋 Menu Principal'),
    ]
    
    command_text = models.CharField(
        max_length=50,
        verbose_name='Texto do Comando',
        help_text='Ex: "✅", "concluir", "1", "done"'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Acção'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descrição'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    priority = models.PositiveSmallIntegerField(
        default=100,
        verbose_name='Prioridade',
        help_text='Menor = verificado primeiro'
    )
    requires_context = models.BooleanField(
        default=False,
        verbose_name='Requer Contexto',
        help_text='Se True, só funciona em conversas ativas'
    )
    
    class Meta:
        app_label = 'whatsapp'
        verbose_name = 'Comando WhatsApp'
        verbose_name_plural = 'Comandos WhatsApp'
        unique_together = [('tenant', 'command_text')]
        ordering = ['priority', 'command_text']
    
    def __str__(self):
        return f'{self.command_text} → {self.get_action_display()}'


class WhatsAppConversation(TenantAwareModel):
    """
    Tracks active conversation state for context-aware interactions.
    Enables multi-step flows like photo upload after task selection.
    """
    
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_EXPIRED = 'EXPIRED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Activa'),
        (STATUS_EXPIRED, 'Expirada'),
        (STATUS_COMPLETED, 'Completa'),
    ]
    
    CONTEXT_TASK = 'TASK'
    CONTEXT_CONTRACT = 'CONTRACT'
    CONTEXT_SUPPORT = 'SUPPORT'
    CONTEXT_GENERAL = 'GENERAL'
    CONTEXT_CHOICES = [
        (CONTEXT_TASK, 'Tarefa'),
        (CONTEXT_CONTRACT, 'Contrato'),
        (CONTEXT_SUPPORT, 'Suporte'),
        (CONTEXT_GENERAL, 'Geral'),
    ]
    
    contact = models.ForeignKey(
        WhatsAppContact,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name='Contacto'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Estado'
    )
    context_type = models.CharField(
        max_length=20,
        choices=CONTEXT_CHOICES,
        default=CONTEXT_GENERAL,
        verbose_name='Tipo de Contexto'
    )
    context_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name='ID do Contexto',
        help_text='ID do objeto relacionado (tarefa, contrato, etc.)'
    )
    
    # Conversation state
    last_message_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Mensagem'
    )
    expires_at = models.DateTimeField(
        verbose_name='Expira Em',
        help_text='Conversa expira após período de inactividade'
    )
    
    # State machine data
    state_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Dados de Estado',
        help_text='Dados temporários da conversa (ex: tarefa selecionada)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'whatsapp'
        verbose_name = 'Conversa WhatsApp'
        verbose_name_plural = 'Conversas WhatsApp'
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['tenant', 'contact', '-last_message_at'], name='wa_conv_contact_idx'),
            models.Index(fields=['tenant', 'status', 'expires_at'], name='wa_conv_status_exp_idx'),
        ]
    
    def __str__(self):
        return f'Conversa com {self.contact.phone_number} ({self.context_type})'
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Conversations expire after 24 hours of inactivity
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def extend_expiry(self, hours=24):
        """Extend conversation expiry."""
        self.expires_at = timezone.now() + timezone.timedelta(hours=hours)
        self.save(update_fields=['expires_at'])
    
    def complete(self):
        """Mark conversation as completed."""
        self.status = self.STATUS_COMPLETED
        self.save(update_fields=['status'])
    
    @property
    def is_expired(self):
        """Check if conversation has expired."""
        return timezone.now() > self.expires_at


class WhatsAppTemplate(TenantAwareModel):
    """
    Pre-approved message templates for proactive notifications.
    Templates must be approved by WhatsApp/Meta before use.
    """
    
    CATEGORY_UTILITY = 'UTILITY'
    CATEGORY_MARKETING = 'MARKETING'
    CATEGORY_AUTHENTICATION = 'AUTHENTICATION'
    CATEGORY_CHOICES = [
        (CATEGORY_UTILITY, 'Utilitário'),
        (CATEGORY_MARKETING, 'Marketing'),
        (CATEGORY_AUTHENTICATION, 'Autenticação'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome do Template'
    )
    code = models.CharField(
        max_length=100,
        verbose_name='Código',
        help_text='Código único do template (ex: pt_task_reminder)'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_UTILITY,
        verbose_name='Categoria'
    )
    language_code = models.CharField(
        max_length=10,
        default='pt_PT',
        verbose_name='Código de Idioma'
    )
    
    # Template content
    header_text = models.CharField(
        max_length=60,
        blank=True,
        verbose_name='Cabeçalho'
    )
    body_text = models.TextField(
        verbose_name='Corpo da Mensagem',
        help_text='Use {{1}}, {{2}} para variáveis'
    )
    footer_text = models.CharField(
        max_length=60,
        blank=True,
        verbose_name='Rodapé'
    )
    
    # Approval status
    is_approved = models.BooleanField(
        default=False,
        verbose_name='Aprovado'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Aprovado Em'
    )
    external_template_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID Externo do Template'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'whatsapp'
        verbose_name = 'Template WhatsApp'
        verbose_name_plural = 'Templates WhatsApp'
        unique_together = [('tenant', 'code')]
    
    def __str__(self):
        return f'{self.name} ({self.code})'


class WhatsAppFallbackLog(TenantAwareModel):
    """
    Tracks fallback attempts when WhatsApp fails.
    Used for SMS fallback and dashboard notifications.
    """
    
    FALLBACK_TYPE_SMS = 'SMS'
    FALLBACK_TYPE_EMAIL = 'EMAIL'
    FALLBACK_TYPE_DASHBOARD = 'DASHBOARD'
    FALLBACK_TYPE_CHOICES = [
        (FALLBACK_TYPE_SMS, 'SMS'),
        (FALLBACK_TYPE_EMAIL, 'Email'),
        (FALLBACK_TYPE_DASHBOARD, 'Dashboard'),
    ]
    
    STATUS_PENDING = 'PENDING'
    STATUS_SENT = 'SENT'
    STATUS_FAILED = 'FAILED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_SENT, 'Enviado'),
        (STATUS_FAILED, 'Falhou'),
    ]
    
    original_message = models.ForeignKey(
        WhatsAppMessageLog,
        on_delete=models.CASCADE,
        related_name='fallback_attempts',
        verbose_name='Mensagem Original'
    )
    fallback_type = models.CharField(
        max_length=20,
        choices=FALLBACK_TYPE_CHOICES,
        verbose_name='Tipo de Fallback'
    )
    recipient = models.CharField(
        max_length=100,
        verbose_name='Destinatário',
        help_text='Número de telefone, email, ou ID do utilizador'
    )
    content = models.TextField(
        verbose_name='Conteúdo'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Status'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Enviado Em'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Erro'
    )
    external_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID Externo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'whatsapp'
        verbose_name = 'Log de Fallback'
        verbose_name_plural = 'Logs de Fallback'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Fallback {self.fallback_type} para {self.recipient}'
    
    def mark_sent(self, external_id=None):
        """Mark fallback as sent."""
        self.status = self.STATUS_SENT
        self.sent_at = timezone.now()
        if external_id:
            self.external_id = external_id
        self.save(update_fields=['status', 'sent_at', 'external_id'])
    
    def mark_failed(self, error_message=''):
        """Mark fallback as failed."""
        self.status = self.STATUS_FAILED
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
