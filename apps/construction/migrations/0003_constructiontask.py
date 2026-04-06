# Generated manually for ImoOS Construction App — Squad A5/C2
# Covers: ConstructionPhase, ConstructionTask (real fields), TaskPhoto,
#         TaskProgressLog, TaskDependency, CPMSnapshot, EVMSnapshot,
#         ConstructionProject and their Historical counterparts.

import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('construction', '0002_alter_constructionphoto_created_at_and_more'),
        ('projects', '0001_initial'),
        ('contracts', '0001_initial'),
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # ── ConstructionPhase ──────────────────────────────────────────────
        migrations.CreateModel(
            name='ConstructionPhase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='phases',
                    to='projects.project',
                    verbose_name='Projecto',
                )),
                ('building', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='phases',
                    to='projects.building',
                    verbose_name='Edifício',
                )),
                ('phase_type', models.CharField(
                    choices=[
                        ('FOUNDATION', 'Fundação'),
                        ('STRUCTURE', 'Estrutura'),
                        ('MASONRY', 'Alvenaria'),
                        ('MEP', 'Instalações Hidro/Elétrica'),
                        ('FINISHES', 'Acabamentos'),
                        ('DELIVERY', 'Entrega'),
                    ],
                    max_length=20,
                    verbose_name='Tipo de Fase',
                )),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('start_planned', models.DateField(verbose_name='Início Planeado')),
                ('end_planned', models.DateField(verbose_name='Fim Planeado')),
                ('start_actual', models.DateField(blank=True, null=True, verbose_name='Início Real')),
                ('end_actual', models.DateField(blank=True, null=True, verbose_name='Fim Real')),
                ('status', models.CharField(
                    choices=[
                        ('NOT_STARTED', 'Não Iniciado'),
                        ('IN_PROGRESS', 'Em Execução'),
                        ('COMPLETED', 'Concluído'),
                        ('BLOCKED', 'Bloqueado'),
                    ],
                    db_index=True,
                    default='NOT_STARTED',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('progress_percent', models.DecimalField(
                    decimal_places=2, default=0, max_digits=5, verbose_name='Progresso (%)',
                )),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_phases',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Fase da Obra',
                'verbose_name_plural': 'Fases da Obra',
                'ordering': ['project', 'order'],
            },
        ),
        migrations.AddIndex(
            model_name='constructionphase',
            index=models.Index(fields=['project', 'status'], name='constr_phase_project_status_idx'),
        ),
        migrations.AddIndex(
            model_name='constructionphase',
            index=models.Index(fields=['project', 'order'], name='constr_phase_project_order_idx'),
        ),
        migrations.CreateModel(
            name='HistoricalConstructionPhase',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('phase_type', models.CharField(
                    choices=[
                        ('FOUNDATION', 'Fundação'),
                        ('STRUCTURE', 'Estrutura'),
                        ('MASONRY', 'Alvenaria'),
                        ('MEP', 'Instalações Hidro/Elétrica'),
                        ('FINISHES', 'Acabamentos'),
                        ('DELIVERY', 'Entrega'),
                    ],
                    max_length=20,
                    verbose_name='Tipo de Fase',
                )),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('start_planned', models.DateField(verbose_name='Início Planeado')),
                ('end_planned', models.DateField(verbose_name='Fim Planeado')),
                ('start_actual', models.DateField(blank=True, null=True, verbose_name='Início Real')),
                ('end_actual', models.DateField(blank=True, null=True, verbose_name='Fim Real')),
                ('status', models.CharField(
                    choices=[
                        ('NOT_STARTED', 'Não Iniciado'),
                        ('IN_PROGRESS', 'Em Execução'),
                        ('COMPLETED', 'Concluído'),
                        ('BLOCKED', 'Bloqueado'),
                    ],
                    default='NOT_STARTED',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('progress_percent', models.DecimalField(
                    decimal_places=2, default=0, max_digits=5, verbose_name='Progresso (%)',
                )),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('project', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='projects.project',
                    verbose_name='Projecto',
                )),
                ('building', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='projects.building',
                    verbose_name='Edifício',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
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
                'verbose_name': 'historical Fase da Obra',
                'verbose_name_plural': 'historical Fases da Obra',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),

        # ── ConstructionTask ───────────────────────────────────────────────
        migrations.CreateModel(
            name='ConstructionTask',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phase', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tasks',
                    to='construction.constructionphase',
                    verbose_name='Fase',
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tasks',
                    to='projects.project',
                    verbose_name='Projecto',
                )),
                ('building', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='tasks',
                    to='projects.building',
                    verbose_name='Edifício',
                )),
                ('assigned_to', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assigned_tasks',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Atribuído a',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_tasks',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('wbs_code', models.CharField(
                    max_length=20,
                    verbose_name='Código WBS',
                    help_text='Ex: 1.1, 1.2, 2.1...',
                )),
                ('name', models.CharField(max_length=200, verbose_name='Nome da Tarefa')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('IN_PROGRESS', 'Em Andamento'),
                        ('COMPLETED', 'Concluído'),
                        ('BLOCKED', 'Bloqueada'),
                    ],
                    db_index=True,
                    default='PENDING',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('priority', models.CharField(
                    choices=[
                        ('LOW', 'Baixa'),
                        ('MEDIUM', 'Média'),
                        ('HIGH', 'Alta'),
                        ('URGENT', 'Urgente'),
                    ],
                    default='MEDIUM',
                    max_length=20,
                    verbose_name='Prioridade',
                )),
                ('due_date', models.DateField(db_index=True, verbose_name='Data Limite')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Iniciada em')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Concluída em')),
                ('progress_percent', models.DecimalField(
                    decimal_places=2, default=0, max_digits=5, verbose_name='Progresso (%)',
                )),
                ('estimated_cost', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Custo Estimado (CVE)',
                )),
                ('actual_cost', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Custo Real (CVE)',
                )),
                ('advanced_mode', models.CharField(
                    choices=[('OFF', 'Desligado'), ('ON', 'Ligado')],
                    default='OFF',
                    max_length=10,
                    verbose_name='Modo Avançado',
                )),
                ('duration_days', models.PositiveIntegerField(default=1, verbose_name='Duração (dias)')),
                ('bim_element_ids', models.JSONField(blank=True, default=list, verbose_name='IDs BIM (IFC)')),
                ('reminder_sent', models.BooleanField(default=False, help_text='Lembrete enviado')),
                ('overdue_notified', models.BooleanField(default=False, help_text='Notificação de atraso enviada')),
            ],
            options={
                'verbose_name': 'Tarefa de Construção',
                'verbose_name_plural': 'Tarefas de Construção',
                'ordering': ['phase', 'wbs_code', 'due_date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='constructiontask',
            unique_together={('project', 'wbs_code')},
        ),
        migrations.AddIndex(
            model_name='constructiontask',
            index=models.Index(fields=['project', 'status'], name='constr_task_project_status_idx'),
        ),
        migrations.AddIndex(
            model_name='constructiontask',
            index=models.Index(fields=['assigned_to', 'status'], name='constr_task_assignee_status_idx'),
        ),
        migrations.AddIndex(
            model_name='constructiontask',
            index=models.Index(fields=['due_date'], name='constr_task_due_date_idx'),
        ),
        migrations.AddIndex(
            model_name='constructiontask',
            index=models.Index(fields=['phase', 'wbs_code'], name='constr_task_phase_wbs_idx'),
        ),
        migrations.AddIndex(
            model_name='constructiontask',
            index=models.Index(fields=['advanced_mode'], name='constr_task_adv_mode_idx'),
        ),
        migrations.CreateModel(
            name='HistoricalConstructionTask',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('wbs_code', models.CharField(max_length=20, verbose_name='Código WBS')),
                ('name', models.CharField(max_length=200, verbose_name='Nome da Tarefa')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('IN_PROGRESS', 'Em Andamento'),
                        ('COMPLETED', 'Concluído'),
                        ('BLOCKED', 'Bloqueada'),
                    ],
                    default='PENDING',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('priority', models.CharField(
                    choices=[
                        ('LOW', 'Baixa'),
                        ('MEDIUM', 'Média'),
                        ('HIGH', 'Alta'),
                        ('URGENT', 'Urgente'),
                    ],
                    default='MEDIUM',
                    max_length=20,
                    verbose_name='Prioridade',
                )),
                ('due_date', models.DateField(verbose_name='Data Limite')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Iniciada em')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Concluída em')),
                ('progress_percent', models.DecimalField(
                    decimal_places=2, default=0, max_digits=5, verbose_name='Progresso (%)',
                )),
                ('estimated_cost', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Custo Estimado (CVE)',
                )),
                ('actual_cost', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Custo Real (CVE)',
                )),
                ('advanced_mode', models.CharField(
                    choices=[('OFF', 'Desligado'), ('ON', 'Ligado')],
                    default='OFF',
                    max_length=10,
                    verbose_name='Modo Avançado',
                )),
                ('duration_days', models.PositiveIntegerField(default=1, verbose_name='Duração (dias)')),
                ('bim_element_ids', models.JSONField(blank=True, default=list, verbose_name='IDs BIM (IFC)')),
                ('reminder_sent', models.BooleanField(default=False)),
                ('overdue_notified', models.BooleanField(default=False)),
                ('phase', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='construction.constructionphase',
                    verbose_name='Fase',
                )),
                ('project', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='projects.project',
                    verbose_name='Projecto',
                )),
                ('building', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='projects.building',
                    verbose_name='Edifício',
                )),
                ('assigned_to', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Atribuído a',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
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
                'verbose_name': 'historical Tarefa de Construção',
                'verbose_name_plural': 'historical Tarefas de Construção',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),

        # ── TaskDependency ─────────────────────────────────────────────────
        migrations.CreateModel(
            name='TaskDependency',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('from_task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='successors',
                    to='construction.constructiontask',
                    verbose_name='Da Tarefa',
                )),
                ('to_task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='predecessors',
                    to='construction.constructiontask',
                    verbose_name='Para a Tarefa',
                )),
                ('dependency_type', models.CharField(
                    choices=[
                        ('FS', 'Finish-to-Start'),
                        ('SS', 'Start-to-Start'),
                        ('FF', 'Finish-to-Finish'),
                        ('SF', 'Start-to-Finish'),
                    ],
                    default='FS',
                    max_length=2,
                    verbose_name='Tipo de Dependência',
                )),
                ('lag_days', models.IntegerField(default=0, verbose_name='Lag (dias)')),
            ],
            options={
                'verbose_name': 'Dependência entre Tarefas',
                'verbose_name_plural': 'Dependências entre Tarefas',
            },
        ),
        migrations.AlterUniqueTogether(
            name='taskdependency',
            unique_together={('from_task', 'to_task')},
        ),
        migrations.AddIndex(
            model_name='taskdependency',
            index=models.Index(fields=['from_task'], name='constr_dep_from_task_idx'),
        ),
        migrations.AddIndex(
            model_name='taskdependency',
            index=models.Index(fields=['to_task'], name='constr_dep_to_task_idx'),
        ),

        # ── CPMSnapshot ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='CPMSnapshot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('task', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cpm_data',
                    to='construction.constructiontask',
                    verbose_name='Tarefa',
                )),
                ('early_start', models.DateField(blank=True, null=True, verbose_name='Early Start')),
                ('early_finish', models.DateField(blank=True, null=True, verbose_name='Early Finish')),
                ('late_start', models.DateField(blank=True, null=True, verbose_name='Late Start')),
                ('late_finish', models.DateField(blank=True, null=True, verbose_name='Late Finish')),
                ('total_float', models.IntegerField(default=0, verbose_name='Folga Total (dias)')),
                ('free_float', models.IntegerField(default=0, verbose_name='Folga Livre (dias)')),
                ('is_critical', models.BooleanField(default=False, verbose_name='No Caminho Crítico')),
                ('calculated_at', models.DateTimeField(auto_now=True, verbose_name='Calculado em')),
            ],
            options={
                'verbose_name': 'Snapshot CPM',
                'verbose_name_plural': 'Snapshots CPM',
                'ordering': ['-calculated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='cpmsnapshot',
            index=models.Index(fields=['task', 'is_critical'], name='constr_cpm_task_critical_idx'),
        ),
        migrations.AddIndex(
            model_name='cpmsnapshot',
            index=models.Index(fields=['calculated_at'], name='constr_cpm_calculated_idx'),
        ),

        # ── TaskPhoto ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name='TaskPhoto',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='photos',
                    to='construction.constructiontask',
                    verbose_name='Tarefa',
                )),
                ('uploaded_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='uploaded_task_photos',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Carregado por',
                )),
                ('image', models.ImageField(upload_to='construction/photos/%Y/%m/', verbose_name='Imagem')),
                ('thumbnail', models.ImageField(
                    blank=True, null=True,
                    upload_to='construction/photos/%Y/%m/thumbs/',
                    verbose_name='Miniatura',
                )),
                ('caption', models.CharField(blank=True, max_length=200, verbose_name='Legenda')),
                ('latitude', models.DecimalField(
                    blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Latitude',
                )),
                ('longitude', models.DecimalField(
                    blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Longitude',
                )),
                ('taken_at', models.DateTimeField(blank=True, null=True, verbose_name='Data da Foto (EXIF)')),
                ('progress_at_upload', models.DecimalField(
                    decimal_places=2, default=0, max_digits=5, verbose_name='Progresso no Momento',
                )),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Carregado em')),
            ],
            options={
                'verbose_name': 'Foto da Tarefa',
                'verbose_name_plural': 'Fotos das Tarefas',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='taskphoto',
            index=models.Index(fields=['task', '-uploaded_at'], name='constr_photo_task_idx'),
        ),
        migrations.AddIndex(
            model_name='taskphoto',
            index=models.Index(fields=['uploaded_by', '-uploaded_at'], name='constr_photo_uploader_idx'),
        ),

        # ── TaskProgressLog ────────────────────────────────────────────────
        migrations.CreateModel(
            name='TaskProgressLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress_logs',
                    to='construction.constructiontask',
                    verbose_name='Tarefa',
                )),
                ('updated_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress_updates',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('old_percent', models.DecimalField(
                    decimal_places=2, max_digits=5, verbose_name='Progresso Anterior',
                )),
                ('new_percent', models.DecimalField(
                    decimal_places=2, max_digits=5, verbose_name='Novo Progresso',
                )),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
            ],
            options={
                'verbose_name': 'Log de Progresso',
                'verbose_name_plural': 'Logs de Progresso',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='taskprogresslog',
            index=models.Index(fields=['task', '-created_at'], name='constr_proglog_task_idx'),
        ),

        # ── EVMSnapshot ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='EVMSnapshot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='evm_snapshots',
                    to='projects.project',
                    verbose_name='Projecto',
                )),
                ('date', models.DateField(verbose_name='Data')),
                ('bac', models.DecimalField(decimal_places=2, max_digits=14, verbose_name='BAC (Budget at Completion)')),
                ('pv', models.DecimalField(decimal_places=2, max_digits=14, verbose_name='PV (Planned Value)')),
                ('ev', models.DecimalField(decimal_places=2, max_digits=14, verbose_name='EV (Earned Value)')),
                ('ac', models.DecimalField(decimal_places=2, max_digits=14, verbose_name='AC (Actual Cost)')),
                ('spi', models.DecimalField(
                    decimal_places=2, default=Decimal('1.00'), max_digits=5,
                    verbose_name='SPI (Schedule Performance Index)',
                )),
                ('cpi', models.DecimalField(
                    decimal_places=2, default=Decimal('1.00'), max_digits=5,
                    verbose_name='CPI (Cost Performance Index)',
                )),
                ('sv', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=14,
                    verbose_name='SV (Schedule Variance)',
                )),
                ('cv', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=14,
                    verbose_name='CV (Cost Variance)',
                )),
                ('eac', models.DecimalField(decimal_places=2, max_digits=14, verbose_name='EAC (Estimate at Completion)')),
                ('etc', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=14,
                    verbose_name='ETC (Estimate to Complete)',
                )),
                ('vac', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=14,
                    verbose_name='VAC (Variance at Completion)',
                )),
                ('tcpi', models.DecimalField(
                    blank=True, decimal_places=2, max_digits=5, null=True,
                    verbose_name='TCPI (To-Complete Performance Index)',
                )),
                ('total_tasks', models.PositiveIntegerField(default=0, verbose_name='Total de Tarefas')),
                ('completed_tasks', models.PositiveIntegerField(default=0, verbose_name='Tarefas Concluídas')),
                ('in_progress_tasks', models.PositiveIntegerField(default=0, verbose_name='Tarefas em Andamento')),
            ],
            options={
                'verbose_name': 'Snapshot EVM',
                'verbose_name_plural': 'Snapshots EVM',
                'ordering': ['-date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='evmsnapshot',
            unique_together={('project', 'date')},
        ),
        migrations.AddIndex(
            model_name='evmsnapshot',
            index=models.Index(fields=['project', '-date'], name='constr_evm_project_date_idx'),
        ),
        migrations.AddIndex(
            model_name='evmsnapshot',
            index=models.Index(fields=['date'], name='constr_evm_date_idx'),
        ),

        # ── ConstructionProject ────────────────────────────────────────────
        migrations.CreateModel(
            name='ConstructionProject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contract', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='construction_project',
                    to='contracts.contract',
                    verbose_name='Contrato',
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='construction_projects',
                    to='projects.project',
                    verbose_name='Projecto Imobiliário',
                )),
                ('building', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='construction_projects',
                    to='projects.building',
                    verbose_name='Edifício',
                )),
                ('unit', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='construction_project',
                    to='inventory.unit',
                    verbose_name='Unidade',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_construction_projects',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Criado por',
                )),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('status', models.CharField(
                    choices=[
                        ('PLANNING', 'Em Planeamento'),
                        ('IN_PROGRESS', 'Em Execução'),
                        ('ON_HOLD', 'Suspenso'),
                        ('COMPLETED', 'Concluído'),
                    ],
                    default='PLANNING',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('start_planned', models.DateField(verbose_name='Início Planeado')),
                ('end_planned', models.DateField(blank=True, null=True, verbose_name='Fim Planeado')),
                ('start_actual', models.DateField(blank=True, null=True, verbose_name='Início Real')),
                ('end_actual', models.DateField(blank=True, null=True, verbose_name='Fim Real')),
                ('bim_model_s3_key', models.CharField(blank=True, max_length=500, verbose_name='S3 Key do Modelo BIM')),
            ],
            options={
                'verbose_name': 'Projeto de Obra',
                'verbose_name_plural': 'Projetos de Obra',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalConstructionProject',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('status', models.CharField(
                    choices=[
                        ('PLANNING', 'Em Planeamento'),
                        ('IN_PROGRESS', 'Em Execução'),
                        ('ON_HOLD', 'Suspenso'),
                        ('COMPLETED', 'Concluído'),
                    ],
                    default='PLANNING',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('start_planned', models.DateField(verbose_name='Início Planeado')),
                ('end_planned', models.DateField(blank=True, null=True, verbose_name='Fim Planeado')),
                ('start_actual', models.DateField(blank=True, null=True, verbose_name='Início Real')),
                ('end_actual', models.DateField(blank=True, null=True, verbose_name='Fim Real')),
                ('bim_model_s3_key', models.CharField(blank=True, max_length=500, verbose_name='S3 Key do Modelo BIM')),
                ('contract', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='contracts.contract',
                    verbose_name='Contrato',
                )),
                ('project', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='projects.project',
                    verbose_name='Projecto Imobiliário',
                )),
                ('building', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='projects.building',
                    verbose_name='Edifício',
                )),
                ('unit', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to='inventory.unit',
                    verbose_name='Unidade',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Criado por',
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
                'verbose_name': 'historical Projeto de Obra',
                'verbose_name_plural': 'historical Projetos de Obra',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
