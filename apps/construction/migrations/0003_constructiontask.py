# Generated manually for ConstructionTask model

import uuid
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('construction', '0002_alter_constructionphoto_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConstructionTask',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, verbose_name='Nome da Tarefa')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('status', models.CharField(choices=[('PENDING', 'Pendente'), ('IN_PROGRESS', 'Em Progresso'), ('COMPLETED', 'Concluída'), ('CANCELLED', 'Cancelada')], db_index=True, default='PENDING', max_length=20, verbose_name='Estado')),
                ('priority', models.CharField(choices=[('LOW', 'Baixa'), ('MEDIUM', 'Média'), ('HIGH', 'Alta'), ('URGENT', 'Urgente')], default='MEDIUM', max_length=20, verbose_name='Prioridade')),
                ('due_date', models.DateField(db_index=True, verbose_name='Data Limite')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Iniciada em')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Concluída em')),
                ('progress_pct', models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Progresso (%)')),
                ('notification_sent', models.BooleanField(default=False, help_text='Notificação de atribuição enviada')),
                ('reminder_sent', models.BooleanField(default=False, help_text='Lembrete enviado')),
                ('overdue_notification_sent', models.BooleanField(default=False, help_text='Notificação de atraso enviada')),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_construction_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Atribuído por')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_construction_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Atribuído a')),
                ('building', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='construction_tasks', to='projects.building', verbose_name='Edifício')),
                ('daily_report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='construction.dailyreport', verbose_name='Relatório Diário')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='construction_tasks', to='projects.project', verbose_name='Projecto')),
            ],
            options={
                'verbose_name': 'Tarefa de Construção',
                'verbose_name_plural': 'Tarefas de Construção',
                'ordering': ['-due_date', 'priority', 'created_at'],
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddIndex(
            model_name='constructiontask',
            index=models.Index(fields=['status', 'due_date'], name='constr_task_status_due_idx'),
        ),
        migrations.AddIndex(
            model_name='constructiontask',
            index=models.Index(fields=['assigned_to', 'status'], name='constr_task_assignee_idx'),
        ),
        migrations.AddIndex(
            model_name='constructiontask',
            index=models.Index(fields=['project', 'status'], name='constr_task_project_idx'),
        ),
    ]
