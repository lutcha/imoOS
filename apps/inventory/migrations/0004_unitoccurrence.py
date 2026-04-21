# Generated manually — adds UnitOccurrence model (Bloco 5 / Maintenance feature).
import uuid

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_unit_inventory_unit_status_idx_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UnitOccurrence",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "occurrence_type",
                    models.CharField(
                        choices=[
                            ("DEFECT", "Defeito/Avaria"),
                            ("IMPROVEMENT", "Melhoria"),
                            ("PREVENTIVE", "Manutenção Preventiva"),
                            ("CLEANUP", "Limpeza/Finalização"),
                        ],
                        default="DEFECT",
                        max_length=20,
                    ),
                ),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("OPEN", "Aberto"),
                            ("IN_PROGRESS", "Em Resolução"),
                            ("RESOLVED", "Resolvido"),
                        ],
                        default="OPEN",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("LOW", "Baixa"),
                            ("MEDIUM", "Média"),
                            ("HIGH", "Alta"),
                        ],
                        default="MEDIUM",
                        max_length=10,
                    ),
                ),
                (
                    "resolved_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_occurrences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reported_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reported_occurrences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="occurrences",
                        to="inventory.unit",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ocorrência de Unidade",
                "verbose_name_plural": "Ocorrências de Unidade",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="unitoccurrence",
            index=models.Index(
                fields=["status", "priority"],
                name="inventory_occ_status_priority_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="unitoccurrence",
            index=models.Index(
                fields=["unit", "status"],
                name="inventory_occ_unit_status_idx",
            ),
        ),
        # HistoricalUnitOccurrence (django-simple-history)
        migrations.CreateModel(
            name="HistoricalUnitOccurrence",
            fields=[
                (
                    "id",
                    models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
                ),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                (
                    "occurrence_type",
                    models.CharField(
                        choices=[
                            ("DEFECT", "Defeito/Avaria"),
                            ("IMPROVEMENT", "Melhoria"),
                            ("PREVENTIVE", "Manutenção Preventiva"),
                            ("CLEANUP", "Limpeza/Finalização"),
                        ],
                        default="DEFECT",
                        max_length=20,
                    ),
                ),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("OPEN", "Aberto"),
                            ("IN_PROGRESS", "Em Resolução"),
                            ("RESOLVED", "Resolvido"),
                        ],
                        default="OPEN",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("LOW", "Baixa"),
                            ("MEDIUM", "Média"),
                            ("HIGH", "Alta"),
                        ],
                        default="MEDIUM",
                        max_length=10,
                    ),
                ),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reported_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.unit",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Ocorrência de Unidade",
                "verbose_name_plural": "historical Ocorrências de Unidade",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
