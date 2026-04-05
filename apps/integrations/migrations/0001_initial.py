# Generated manually for ImoOS WhatsApp Integration

import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0001_initial'),  # Adjust as needed
        ('construction', '0001_initial'),  # Adjust as needed
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Nome único do template', max_length=100)),
                ('template_type', models.CharField(choices=[('TASK_REMINDER', 'Lembrete de Tarefa'), ('PROGRESS_UPDATE', 'Atualização de Progresso'), ('CONTRACT_SIGNATURE', 'Assinatura Pendente'), ('OVERDUE_ALERT', 'Alerta de Atraso'), ('WELCOME', 'Mensagem de Boas-vindas'), ('DAILY_REPORT_REMINDER', 'Lembrete de Relatório Diário')], default='TASK_REMINDER', help_text='Tipo/categoria do template', max_length=30)),
                ('meta_template_id', models.CharField(blank=True, help_text='ID do template na Meta (WhatsApp Business API)', max_length=100)),
                ('language', models.CharField(choices=[('pt_PT', 'Português (Portugal)'), ('pt_BR', 'Português (Brasil)')], default='pt_PT', max_length=10)),
                ('content_pt', models.TextField(help_text='Conteúdo em português com placeholders {{variavel}}')),
                ('variables', models.JSONField(default=list, help_text='Lista de variáveis: ["{{nome}}", "{{tarefa}}", "{{data}}"]')),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='Utilizador que criou o template', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Template WhatsApp',
                'verbose_name_plural': 'Templates WhatsApp',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='WhatsAppMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('direction', models.CharField(choices=[('OUTBOUND', 'Enviada'), ('INBOUND', 'Recebida')], help_text='Direção da mensagem', max_length=10)),
                ('phone_number', models.CharField(help_text='Número de telefone no formato +2389991234', max_length=20)),
                ('message_body', models.TextField(help_text='Conteúdo da mensagem')),
                ('meta_message_id', models.CharField(blank=True, help_text='ID da mensagem na Meta (para tracking)', max_length=100)),
                ('status', models.CharField(choices=[('SENT', 'Enviada'), ('DELIVERED', 'Entregue'), ('READ', 'Lida'), ('FAILED', 'Falhou'), ('PENDING', 'Pendente')], default='PENDING', max_length=15)),
                ('sent_at', models.DateTimeField(auto_now_add=True, help_text='Quando a mensagem foi enviada')),
                ('delivered_at', models.DateTimeField(blank=True, help_text='Quando foi entregue no dispositivo', null=True)),
                ('read_at', models.DateTimeField(blank=True, help_text='Quando foi lida pelo destinatário', null=True)),
                ('inbound_response', models.CharField(blank=True, help_text='Resposta rápida: ✅, ❌, 1, 2, 3, etc.', max_length=50)),
                ('processed', models.BooleanField(default=False, help_text='Se a resposta inbound já foi processada')),
                ('processed_at', models.DateTimeField(blank=True, help_text='Quando a resposta foi processada', null=True)),
                ('error_message', models.TextField(blank=True, help_text='Mensagem de erro em caso de falha')),
                ('raw_webhook_data', models.JSONField(blank=True, default=dict, help_text='Dados brutos do webhook (para debugging)')),
                ('lead', models.ForeignKey(blank=True, help_text='Lead associado à mensagem', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='whatsapp_messages', to='crm.lead')),
                ('task', models.ForeignKey(blank=True, help_text='Tarefa de construção associada', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='whatsapp_messages', to='construction.constructiontask')),
                ('template', models.ForeignKey(blank=True, help_text='Template utilizado (se aplicável)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='integrations.whatsapptemplate')),
                ('user', models.ForeignKey(blank=True, help_text='Utilizador associado à mensagem', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='whatsapp_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Mensagem WhatsApp',
                'verbose_name_plural': 'Mensagens WhatsApp',
                'ordering': ['-sent_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('whatsapp_enabled', models.BooleanField(default=True, help_text='Receber notificações via WhatsApp')),
                ('email_enabled', models.BooleanField(default=True, help_text='Receber notificações via Email')),
                ('sms_enabled', models.BooleanField(default=False, help_text='Receber notificações via SMS (fallback)')),
                ('urgent_only_whatsapp', models.BooleanField(default=False, help_text='Só enviar WhatsApp para notificações urgentes')),
                ('quiet_hours_start', models.TimeField(blank=True, help_text='Início do período de silêncio (não enviar notificações)', null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, help_text='Fim do período de silêncio', null=True)),
                ('notify_task_assignment', models.BooleanField(default=True, help_text='Notificar quando atribuída nova tarefa')),
                ('notify_task_overdue', models.BooleanField(default=True, help_text='Notificar tarefas atrasadas')),
                ('notify_daily_reminder', models.BooleanField(default=True, help_text='Lembrete diário de tarefas (8h)')),
                ('user', models.OneToOneField(help_text='Utilizador associado às preferências', on_delete=django.db.models.deletion.CASCADE, related_name='notification_preference', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Preferência de Notificação',
                'verbose_name_plural': 'Preferências de Notificação',
            },
        ),
        migrations.AddIndex(
            model_name='whatsappmessage',
            index=models.Index(fields=['phone_number', '-sent_at'], name='whatsapp_msg_phone_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappmessage',
            index=models.Index(fields=['status', 'processed'], name='whatsapp_msg_status_proc_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappmessage',
            index=models.Index(fields=['user', '-sent_at'], name='whatsapp_msg_user_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappmessage',
            index=models.Index(fields=['task', '-sent_at'], name='whatsapp_msg_task_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='whatsapptemplate',
            unique_together={('name',)},
        ),
    ]
