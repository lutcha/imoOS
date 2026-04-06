# Generated manually for ImoOS Workflows App

import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── WorkflowDefinition ──────────────────────────────────────────────
        migrations.CreateModel(
            name='WorkflowDefinition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('workflow_type', models.CharField(
                    choices=[
                        ('SALES', 'Venda (Lead → Contrato)'),
                        ('PROJECT_INIT', 'Inicialização de Projeto'),
                        ('PAYMENT_MILESTONE', 'Milestone de Pagamento'),
                        ('NOTIFICATION', 'Notificação'),
                        ('CUSTOM', 'Customizado'),
                    ],
                    default='CUSTOM',
                    max_length=20,
                    verbose_name='Tipo',
                )),
                ('trigger_event', models.CharField(
                    choices=[
                        ('LEAD_CONVERTED', 'Lead Convertido'),
                        ('RESERVATION_CREATED', 'Reserva Criada'),
                        ('CONTRACT_SIGNED', 'Contrato Assinado'),
                        ('TASK_COMPLETED', 'Task Concluída'),
                        ('PAYMENT_DUE', 'Pagamento em Atraso'),
                        ('MANUAL', 'Manual'),
                    ],
                    max_length=30,
                    verbose_name='Evento de Trigger',
                )),
                ('steps_definition', models.JSONField(default=list, verbose_name='Definição dos Passos')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('auto_execute', models.BooleanField(default=True, verbose_name='Execução Automática')),
                ('notify_on_complete', models.BooleanField(default=True, verbose_name='Notificar ao Concluir')),
                ('notify_on_error', models.BooleanField(default=True, verbose_name='Notificar em Erro')),
            ],
            options={
                'verbose_name': 'Definição de Workflow',
                'verbose_name_plural': 'Definições de Workflow',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalWorkflowDefinition',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('workflow_type', models.CharField(
                    choices=[
                        ('SALES', 'Venda (Lead → Contrato)'),
                        ('PROJECT_INIT', 'Inicialização de Projeto'),
                        ('PAYMENT_MILESTONE', 'Milestone de Pagamento'),
                        ('NOTIFICATION', 'Notificação'),
                        ('CUSTOM', 'Customizado'),
                    ],
                    default='CUSTOM',
                    max_length=20,
                    verbose_name='Tipo',
                )),
                ('trigger_event', models.CharField(
                    choices=[
                        ('LEAD_CONVERTED', 'Lead Convertido'),
                        ('RESERVATION_CREATED', 'Reserva Criada'),
                        ('CONTRACT_SIGNED', 'Contrato Assinado'),
                        ('TASK_COMPLETED', 'Task Concluída'),
                        ('PAYMENT_DUE', 'Pagamento em Atraso'),
                        ('MANUAL', 'Manual'),
                    ],
                    max_length=30,
                    verbose_name='Evento de Trigger',
                )),
                ('steps_definition', models.JSONField(default=list, verbose_name='Definição dos Passos')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('auto_execute', models.BooleanField(default=True, verbose_name='Execução Automática')),
                ('notify_on_complete', models.BooleanField(default=True, verbose_name='Notificar ao Concluir')),
                ('notify_on_error', models.BooleanField(default=True, verbose_name='Notificar em Erro')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.TextField(null=True)),
                ('history_type', models.CharField(
                    choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                    max_length=1,
                )),
                ('history_user', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'historical Definição de Workflow',
                'verbose_name_plural': 'historical Definições de Workflow',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),

        # ── WorkflowTemplate ────────────────────────────────────────────────
        migrations.CreateModel(
            name='WorkflowTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('workflow_type', models.CharField(
                    choices=[
                        ('SALES', 'Venda (Lead → Contrato)'),
                        ('PROJECT_INIT', 'Inicialização de Projeto'),
                        ('PAYMENT_MILESTONE', 'Milestone de Pagamento'),
                        ('NOTIFICATION', 'Notificação'),
                        ('CUSTOM', 'Customizado'),
                    ],
                    max_length=20,
                    verbose_name='Tipo',
                )),
                ('trigger_event', models.CharField(
                    choices=[
                        ('LEAD_CONVERTED', 'Lead Convertido'),
                        ('RESERVATION_CREATED', 'Reserva Criada'),
                        ('CONTRACT_SIGNED', 'Contrato Assinado'),
                        ('TASK_COMPLETED', 'Task Concluída'),
                        ('PAYMENT_DUE', 'Pagamento em Atraso'),
                        ('MANUAL', 'Manual'),
                    ],
                    max_length=30,
                    verbose_name='Evento de Trigger',
                )),
                ('steps_definition', models.JSONField(default=list, verbose_name='Definição dos Passos')),
                ('is_system', models.BooleanField(default=False, verbose_name='Sistema')),
            ],
            options={
                'verbose_name': 'Template de Workflow',
                'verbose_name_plural': 'Templates de Workflow',
                'ordering': ['name'],
            },
        ),

        # ── WorkflowInstance ────────────────────────────────────────────────
        migrations.CreateModel(
            name='WorkflowInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workflow', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='instances',
                    to='workflows.workflowdefinition',
                    verbose_name='Workflow',
                )),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('RUNNING', 'Em Execução'),
                        ('COMPLETED', 'Concluído'),
                        ('FAILED', 'Falhou'),
                        ('CANCELLED', 'Cancelado'),
                        ('RETRYING', 'A Re-executar'),
                    ],
                    default='PENDING',
                    max_length=15,
                    verbose_name='Estado',
                )),
                ('context', models.JSONField(default=dict, verbose_name='Contexto')),
                ('trigger_model', models.CharField(blank=True, max_length=50, verbose_name='Modelo de Origem')),
                ('trigger_object_id', models.CharField(blank=True, max_length=36, verbose_name='ID do Objeto de Origem')),
                ('current_step', models.PositiveIntegerField(default=0, verbose_name='Passo Actual')),
                ('total_steps', models.PositiveIntegerField(default=0, verbose_name='Total de Passos')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Iniciado em')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Concluído em')),
                ('error_message', models.TextField(blank=True, verbose_name='Mensagem de Erro')),
                ('error_step', models.PositiveIntegerField(blank=True, null=True, verbose_name='Passo com Erro')),
                ('retry_count', models.PositiveIntegerField(default=0, verbose_name='Tentativas')),
                ('max_retries', models.PositiveIntegerField(default=3, verbose_name='Máx. Tentativas')),
            ],
            options={
                'verbose_name': 'Instância de Workflow',
                'verbose_name_plural': 'Instâncias de Workflow',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='workflowinstance',
            index=models.Index(fields=['status', '-created_at'], name='wflow_inst_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='workflowinstance',
            index=models.Index(fields=['trigger_model', 'trigger_object_id'], name='wflow_inst_trigger_idx'),
        ),
        migrations.CreateModel(
            name='HistoricalWorkflowInstance',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('RUNNING', 'Em Execução'),
                        ('COMPLETED', 'Concluído'),
                        ('FAILED', 'Falhou'),
                        ('CANCELLED', 'Cancelado'),
                        ('RETRYING', 'A Re-executar'),
                    ],
                    default='PENDING',
                    max_length=15,
                    verbose_name='Estado',
                )),
                ('context', models.JSONField(default=dict, verbose_name='Contexto')),
                ('trigger_model', models.CharField(blank=True, max_length=50, verbose_name='Modelo de Origem')),
                ('trigger_object_id', models.CharField(blank=True, max_length=36, verbose_name='ID do Objeto de Origem')),
                ('current_step', models.PositiveIntegerField(default=0, verbose_name='Passo Actual')),
                ('total_steps', models.PositiveIntegerField(default=0, verbose_name='Total de Passos')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Iniciado em')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Concluído em')),
                ('error_message', models.TextField(blank=True, verbose_name='Mensagem de Erro')),
                ('error_step', models.PositiveIntegerField(blank=True, null=True, verbose_name='Passo com Erro')),
                ('retry_count', models.PositiveIntegerField(default=0, verbose_name='Tentativas')),
                ('max_retries', models.PositiveIntegerField(default=3, verbose_name='Máx. Tentativas')),
                ('workflow', models.ForeignKey(
                    blank=True,
                    db_constraint=False,
                    null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='workflows.workflowdefinition',
                    verbose_name='Workflow',
                )),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.TextField(null=True)),
                ('history_type', models.CharField(
                    choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                    max_length=1,
                )),
                ('history_user', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'historical Instância de Workflow',
                'verbose_name_plural': 'historical Instâncias de Workflow',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),

        # ── WorkflowStep ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='WorkflowStep',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('instance', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='steps',
                    to='workflows.workflowinstance',
                    verbose_name='Instância',
                )),
                ('order', models.PositiveIntegerField(verbose_name='Ordem')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('action_type', models.CharField(
                    choices=[
                        ('CREATE_MODEL', 'Criar Modelo'),
                        ('UPDATE_MODEL', 'Actualizar Modelo'),
                        ('SEND_NOTIFICATION', 'Enviar Notificação'),
                        ('SEND_WHATSAPP', 'Enviar WhatsApp'),
                        ('SEND_EMAIL', 'Enviar Email'),
                        ('GENERATE_DOCUMENT', 'Gerar Documento'),
                        ('WEBHOOK', 'Webhook Externo'),
                        ('CUSTOM', 'Acção Customizada'),
                    ],
                    max_length=20,
                    verbose_name='Tipo de Acção',
                )),
                ('action_config', models.JSONField(default=dict, verbose_name='Configuração')),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('RUNNING', 'Em Execução'),
                        ('COMPLETED', 'Concluído'),
                        ('FAILED', 'Falhou'),
                        ('SKIPPED', 'Ignorado'),
                    ],
                    default='PENDING',
                    max_length=15,
                    verbose_name='Estado',
                )),
                ('result_data', models.JSONField(blank=True, default=dict, verbose_name='Dados do Resultado')),
                ('error_message', models.TextField(blank=True, verbose_name='Erro')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Iniciado em')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Concluído em')),
            ],
            options={
                'verbose_name': 'Passo de Workflow',
                'verbose_name_plural': 'Passos de Workflow',
                'ordering': ['instance', 'order'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='workflowstep',
            unique_together={('instance', 'order')},
        ),
        migrations.CreateModel(
            name='HistoricalWorkflowStep',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('order', models.PositiveIntegerField(verbose_name='Ordem')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('action_type', models.CharField(
                    choices=[
                        ('CREATE_MODEL', 'Criar Modelo'),
                        ('UPDATE_MODEL', 'Actualizar Modelo'),
                        ('SEND_NOTIFICATION', 'Enviar Notificação'),
                        ('SEND_WHATSAPP', 'Enviar WhatsApp'),
                        ('SEND_EMAIL', 'Enviar Email'),
                        ('GENERATE_DOCUMENT', 'Gerar Documento'),
                        ('WEBHOOK', 'Webhook Externo'),
                        ('CUSTOM', 'Acção Customizada'),
                    ],
                    max_length=20,
                    verbose_name='Tipo de Acção',
                )),
                ('action_config', models.JSONField(default=dict, verbose_name='Configuração')),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('RUNNING', 'Em Execução'),
                        ('COMPLETED', 'Concluído'),
                        ('FAILED', 'Falhou'),
                        ('SKIPPED', 'Ignorado'),
                    ],
                    default='PENDING',
                    max_length=15,
                    verbose_name='Estado',
                )),
                ('result_data', models.JSONField(blank=True, default=dict, verbose_name='Dados do Resultado')),
                ('error_message', models.TextField(blank=True, verbose_name='Erro')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Iniciado em')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Concluído em')),
                ('instance', models.ForeignKey(
                    blank=True,
                    db_constraint=False,
                    null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='workflows.workflowinstance',
                    verbose_name='Instância',
                )),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.TextField(null=True)),
                ('history_type', models.CharField(
                    choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                    max_length=1,
                )),
                ('history_user', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'historical Passo de Workflow',
                'verbose_name_plural': 'historical Passos de Workflow',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),

        # ── WorkflowLog ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name='WorkflowLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('instance', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='logs',
                    to='workflows.workflowinstance',
                    verbose_name='Instância',
                )),
                ('step', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='logs',
                    to='workflows.workflowstep',
                    verbose_name='Passo',
                )),
                ('level', models.CharField(
                    choices=[
                        ('DEBUG', 'Debug'),
                        ('INFO', 'Info'),
                        ('WARNING', 'Aviso'),
                        ('ERROR', 'Erro'),
                    ],
                    default='INFO',
                    max_length=10,
                    verbose_name='Nível',
                )),
                ('message', models.TextField(verbose_name='Mensagem')),
                ('details', models.JSONField(blank=True, default=dict, verbose_name='Detalhes')),
            ],
            options={
                'verbose_name': 'Log de Workflow',
                'verbose_name_plural': 'Logs de Workflow',
                'ordering': ['-created_at'],
            },
        ),
    ]
