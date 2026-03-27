import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # swappable_dependency handles the cross-schema User FK correctly:
        # shared-app migrations (--shared) run before tenant migrations,
        # so User is always present in the public schema when this runs.
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantMembership',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                )),
                ('user', models.ForeignKey(
                    db_index=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='memberships',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('role', models.CharField(
                    choices=[
                        ('admin', 'Administrador'),
                        ('gestor', 'Gestor de Projecto'),
                        ('vendedor', 'Vendedor'),
                        ('engenheiro', 'Engenheiro de Obra'),
                        ('investidor', 'Investidor'),
                    ],
                    max_length=20,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Membro do Tenant',
                'verbose_name_plural': 'Membros do Tenant',
            },
        ),
        migrations.AddConstraint(
            model_name='tenantmembership',
            constraint=models.UniqueConstraint(
                fields=['user'],
                name='unique_user_per_tenant_schema',
            ),
        ),
    ]
