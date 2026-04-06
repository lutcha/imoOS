"""
Workflow models — Definição e execução de workflows de integração.

Um workflow é uma sequência de passos que são executados automaticamente
quando certos eventos ocorrem no sistema (triggers).
"""
import uuid
import logging
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel

logger = logging.getLogger(__name__)


class WorkflowDefinition(TenantAwareModel):
    """
    Definição de um workflow — template para criar instâncias.
    
    Exemplos:
    - 'sales_flow': Lead → Reserva → Contrato
    - 'project_init': Contrato → Projeto de Obra
    - 'payment_milestone': Task → Pagamento
    """
    
    # Tipos de workflow
    TYPE_SALES = 'SALES'  # Lead → Reserva → Contrato
    TYPE_PROJECT_INIT = 'PROJECT_INIT'  # Contrato → Obra
    TYPE_PAYMENT_MILESTONE = 'PAYMENT_MILESTONE'  # Task → Pagamento
    TYPE_NOTIFICATION = 'NOTIFICATION'  # Notificações diversas
    TYPE_CUSTOM = 'CUSTOM'  # Workflow customizado
    
    TYPE_CHOICES = [
        (TYPE_SALES, 'Venda (Lead → Contrato)'),
        (TYPE_PROJECT_INIT, 'Inicialização de Projeto'),
        (TYPE_PAYMENT_MILESTONE, 'Milestone de Pagamento'),
        (TYPE_NOTIFICATION, 'Notificação'),
        (TYPE_CUSTOM, 'Customizado'),
    ]
    
    # Triggers (eventos que iniciam o workflow)
    TRIGGER_LEAD_CONVERTED = 'LEAD_CONVERTED'
    TRIGGER_RESERVATION_CREATED = 'RESERVATION_CREATED'
    TRIGGER_CONTRACT_SIGNED = 'CONTRACT_SIGNED'
    TRIGGER_TASK_COMPLETED = 'TASK_COMPLETED'
    TRIGGER_PAYMENT_DUE = 'PAYMENT_DUE'
    TRIGGER_MANUAL = 'MANUAL'
    
    TRIGGER_CHOICES = [
        (TRIGGER_LEAD_CONVERTED, 'Lead Convertido'),
        (TRIGGER_RESERVATION_CREATED, 'Reserva Criada'),
        (TRIGGER_CONTRACT_SIGNED, 'Contrato Assinado'),
        (TRIGGER_TASK_COMPLETED, 'Task Concluída'),
        (TRIGGER_PAYMENT_DUE, 'Pagamento em Atraso'),
        (TRIGGER_MANUAL, 'Manual'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    workflow_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_CUSTOM,
        verbose_name='Tipo'
    )
    
    # Trigger configuration
    trigger_event = models.CharField(
        max_length=30,
        choices=TRIGGER_CHOICES,
        verbose_name='Evento de Trigger'
    )
    
    # Definição dos passos (JSON Schema)
    steps_definition = models.JSONField(
        default=list,
        verbose_name='Definição dos Passos',
        help_text='Lista de passos com configuração'
    )
    
    # Configurações
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    auto_execute = models.BooleanField(
        default=True,
        verbose_name='Execução Automática',
        help_text='Executar automaticamente quando o trigger ocorrer'
    )
    
    # Notificações
    notify_on_complete = models.BooleanField(
        default=True,
        verbose_name='Notificar ao Concluir'
    )
    notify_on_error = models.BooleanField(
        default=True,
        verbose_name='Notificar em Erro'
    )
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Definição de Workflow'
        verbose_name_plural = 'Definições de Workflow'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} ({self.get_workflow_type_display()})'


class WorkflowInstance(TenantAwareModel):
    """
    Instância de um workflow em execução.
    
    Cada vez que um workflow é iniciado, uma instância é criada
    para rastrear o estado da execução.
    """
    
    STATUS_PENDING = 'PENDING'
    STATUS_RUNNING = 'RUNNING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_RETRYING = 'RETRYING'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_RUNNING, 'Em Execução'),
        (STATUS_COMPLETED, 'Concluído'),
        (STATUS_FAILED, 'Falhou'),
        (STATUS_CANCELLED, 'Cancelado'),
        (STATUS_RETRYING, 'A Re-executar'),
    ]
    
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name='Workflow'
    )
    
    # Estado da execução
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado'
    )
    
    # Contexto do workflow (dados compartilhados entre passos)
    context = models.JSONField(
        default=dict,
        verbose_name='Contexto',
        help_text='Dados passados entre os passos do workflow'
    )
    
    # Referência ao objeto que iniciou o workflow
    trigger_model = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Modelo de Origem'
    )
    trigger_object_id = models.CharField(
        max_length=36,
        blank=True,
        verbose_name='ID do Objeto de Origem'
    )
    
    # Progresso
    current_step = models.PositiveIntegerField(default=0, verbose_name='Passo Actual')
    total_steps = models.PositiveIntegerField(default=0, verbose_name='Total de Passos')
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Iniciado em')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Concluído em')
    
    # Erro (se falhou)
    error_message = models.TextField(blank=True, verbose_name='Mensagem de Erro')
    error_step = models.PositiveIntegerField(null=True, blank=True, verbose_name='Passo com Erro')
    
    # Retry
    retry_count = models.PositiveIntegerField(default=0, verbose_name='Tentativas')
    max_retries = models.PositiveIntegerField(default=3, verbose_name='Máx. Tentativas')
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Instância de Workflow'
        verbose_name_plural = 'Instâncias de Workflow'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['trigger_model', 'trigger_object_id']),
        ]
    
    def __str__(self):
        return f'{self.workflow.name} - {self.get_status_display()}'
    
    @property
    def progress_percent(self):
        if self.total_steps == 0:
            return 0
        return int((self.current_step / self.total_steps) * 100)


class WorkflowStep(TenantAwareModel):
    """
    Passo individual de um workflow.
    
    Cada passo representa uma ação específica a ser executada.
    """
    
    # Tipos de ação
    ACTION_CREATE_MODEL = 'CREATE_MODEL'
    ACTION_UPDATE_MODEL = 'UPDATE_MODEL'
    ACTION_SEND_NOTIFICATION = 'SEND_NOTIFICATION'
    ACTION_SEND_WHATSAPP = 'SEND_WHATSAPP'
    ACTION_SEND_EMAIL = 'SEND_EMAIL'
    ACTION_GENERATE_DOCUMENT = 'GENERATE_DOCUMENT'
    ACTION_WEBHOOK = 'WEBHOOK'
    ACTION_CUSTOM = 'CUSTOM'
    
    ACTION_CHOICES = [
        (ACTION_CREATE_MODEL, 'Criar Modelo'),
        (ACTION_UPDATE_MODEL, 'Actualizar Modelo'),
        (ACTION_SEND_NOTIFICATION, 'Enviar Notificação'),
        (ACTION_SEND_WHATSAPP, 'Enviar WhatsApp'),
        (ACTION_SEND_EMAIL, 'Enviar Email'),
        (ACTION_GENERATE_DOCUMENT, 'Gerar Documento'),
        (ACTION_WEBHOOK, 'Webhook Externo'),
        (ACTION_CUSTOM, 'Acção Customizada'),
    ]
    
    STATUS_PENDING = 'PENDING'
    STATUS_RUNNING = 'RUNNING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'
    STATUS_SKIPPED = 'SKIPPED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_RUNNING, 'Em Execução'),
        (STATUS_COMPLETED, 'Concluído'),
        (STATUS_FAILED, 'Falhou'),
        (STATUS_SKIPPED, 'Ignorado'),
    ]
    
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name='Instância'
    )
    
    # Ordem do passo
    order = models.PositiveIntegerField(verbose_name='Ordem')
    name = models.CharField(max_length=100, verbose_name='Nome')
    
    # Configuração da ação
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Tipo de Acção'
    )
    action_config = models.JSONField(
        default=dict,
        verbose_name='Configuração',
        help_text='Parâmetros específicos da ação'
    )
    
    # Estado
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado'
    )
    
    # Resultado
    result_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Dados do Resultado'
    )
    error_message = models.TextField(blank=True, verbose_name='Erro')
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Iniciado em')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Concluído em')
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Passo de Workflow'
        verbose_name_plural = 'Passos de Workflow'
        ordering = ['instance', 'order']
        unique_together = ['instance', 'order']
    
    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'


class WorkflowLog(TenantAwareModel):
    """
    Log detalhado de execução de workflows.
    
    Usado para debugging e auditoria.
    """
    
    LEVEL_DEBUG = 'DEBUG'
    LEVEL_INFO = 'INFO'
    LEVEL_WARNING = 'WARNING'
    LEVEL_ERROR = 'ERROR'
    
    LEVEL_CHOICES = [
        (LEVEL_DEBUG, 'Debug'),
        (LEVEL_INFO, 'Info'),
        (LEVEL_WARNING, 'Aviso'),
        (LEVEL_ERROR, 'Erro'),
    ]
    
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Instância'
    )
    step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True,
        verbose_name='Passo'
    )
    
    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        default=LEVEL_INFO,
        verbose_name='Nível'
    )
    message = models.TextField(verbose_name='Mensagem')
    details = models.JSONField(default=dict, blank=True, verbose_name='Detalhes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Workflow'
        verbose_name_plural = 'Logs de Workflow'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'[{self.level}] {self.message[:50]}'


class WorkflowTemplate(TenantAwareModel):
    """
    Templates predefinidos para workflows comuns.
    
    Usado para inicializar workflows padrão em novos tenants.
    """
    
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    workflow_type = models.CharField(
        max_length=20,
        choices=WorkflowDefinition.TYPE_CHOICES,
        verbose_name='Tipo'
    )
    trigger_event = models.CharField(
        max_length=30,
        choices=WorkflowDefinition.TRIGGER_CHOICES,
        verbose_name='Evento de Trigger'
    )
    steps_definition = models.JSONField(
        default=list,
        verbose_name='Definição dos Passos'
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name='Sistema',
        help_text='Template de sistema não pode ser alterado'
    )
    
    class Meta:
        verbose_name = 'Template de Workflow'
        verbose_name_plural = 'Templates de Workflow'
        ordering = ['name']
    
    def __str__(self):
        return self.name
