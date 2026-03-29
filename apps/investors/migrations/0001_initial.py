import django.db.models.deletion
import simple_history.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestorProfile',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                )),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='investor_profile',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('preferred_language', models.CharField(
                    choices=[
                        ('pt-pt', 'Português'),
                        ('en', 'English'),
                        ('fr', 'Français'),
                    ],
                    default='pt-pt',
                    max_length=5,
                )),
                ('notes', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Perfil de Investidor',
                'verbose_name_plural': 'Perfis de Investidores',
            },
        ),
        migrations.CreateModel(
            name='HistoricalInvestorProfile',
            fields=[
                ('id', models.UUIDField(
                    db_index=True,
                    default=uuid.uuid4,
                    editable=False,
                )),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('preferred_language', models.CharField(
                    choices=[
                        ('pt-pt', 'Português'),
                        ('en', 'English'),
                        ('fr', 'Français'),
                    ],
                    default='pt-pt',
                    max_length=5,
                )),
                ('notes', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
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
                ('user', models.ForeignKey(
                    blank=True,
                    db_constraint=False,
                    null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'historical Perfil de Investidor',
                'verbose_name_plural': 'historical Perfis de Investidores',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
