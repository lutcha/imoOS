# Generated manually — re-creates DailyReport, ConstructionPhoto,
# ConstructionProgress, and ConstructionProject after migration 0004 deleted
# them.  The models were rewritten by Antigravity agent (Bloco 5) with a
# cleaner schema; this migration materialises that schema in the DB.
import uuid

import django.core.validators
import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0004_remove_constructionphoto_created_by_and_more"),
        ("contracts", "0005_contracttemplate_paymentpattern_and_more"),
        ("inventory", "0003_unit_inventory_unit_status_idx_and_more"),
        ("projects", "0004_projectdocument_historicalprojectdocument"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------
        # DailyReport
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="DailyReport",
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
                    "date",
                    models.DateField(db_index=True, verbose_name="Data"),
                ),
                (
                    "summary",
                    models.TextField(
                        help_text="Descrição das actividades realizadas no dia.",
                        verbose_name="Resumo",
                    ),
                ),
                (
                    "progress_pct",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="Avanço (%)",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Rascunho"),
                            ("SUBMITTED", "Submetido"),
                            ("APPROVED", "Aprovado"),
                        ],
                        db_index=True,
                        default="DRAFT",
                        max_length=15,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "weather",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        verbose_name="Condições meteorológicas",
                    ),
                ),
                (
                    "workers_count",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name="Número de trabalhadores",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="daily_reports",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Autor",
                    ),
                ),
                (
                    "building",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="daily_reports",
                        to="projects.building",
                        verbose_name="Edifício",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="daily_reports",
                        to="projects.project",
                        verbose_name="Projecto",
                    ),
                ),
            ],
            options={
                "verbose_name": "Diário de Obra",
                "verbose_name_plural": "Diários de Obra",
                "ordering": ["-date"],
                "unique_together": {("project", "building", "date")},
            },
        ),
        migrations.AddIndex(
            model_name="dailyreport",
            index=models.Index(
                fields=["project", "-date"],
                name="constr_rpt_proj_date_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="dailyreport",
            index=models.Index(
                fields=["status", "-date"],
                name="constr_rpt_status_date_idx",
            ),
        ),
        # ------------------------------------------------------------------
        # HistoricalDailyReport (django-simple-history)
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="HistoricalDailyReport",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                    ),
                ),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("date", models.DateField(db_index=True, verbose_name="Data")),
                ("summary", models.TextField(verbose_name="Resumo")),
                (
                    "progress_pct",
                    models.PositiveSmallIntegerField(verbose_name="Avanço (%)"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Rascunho"),
                            ("SUBMITTED", "Submetido"),
                            ("APPROVED", "Aprovado"),
                        ],
                        db_index=True,
                        default="DRAFT",
                        max_length=15,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "weather",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        verbose_name="Condições meteorológicas",
                    ),
                ),
                (
                    "workers_count",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name="Número de trabalhadores",
                    ),
                ),
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
                    "author",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Autor",
                    ),
                ),
                (
                    "building",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="projects.building",
                        verbose_name="Edifício",
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
                    "project",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="projects.project",
                        verbose_name="Projecto",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Diário de Obra",
                "verbose_name_plural": "historical Diários de Obra",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        # ------------------------------------------------------------------
        # ConstructionPhoto
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="ConstructionPhoto",
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
                    "s3_key",
                    models.CharField(max_length=500, verbose_name="Chave S3"),
                ),
                (
                    "thumbnail_s3_key",
                    models.CharField(
                        blank=True,
                        max_length=500,
                        verbose_name="Chave S3 (miniatura)",
                    ),
                ),
                (
                    "caption",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Legenda",
                    ),
                ),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                        verbose_name="Latitude",
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                        verbose_name="Longitude",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Carregado por",
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="photos",
                        to="construction.dailyreport",
                        verbose_name="Relatório",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fotografia de Obra",
                "verbose_name_plural": "Fotografias de Obra",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="constructionphoto",
            index=models.Index(
                fields=["report", "-created_at"],
                name="construction_photo_report_idx",
            ),
        ),
        # ------------------------------------------------------------------
        # ConstructionProgress
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="ConstructionProgress",
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
                    "progress_pct",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="Avanço geral (%)",
                    ),
                ),
                ("last_updated", models.DateTimeField(auto_now=True, verbose_name="Última actualização")),
                (
                    "building",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress",
                        to="projects.building",
                        verbose_name="Edifício",
                    ),
                ),
                (
                    "last_report",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="construction.dailyreport",
                        verbose_name="Último relatório aprovado",
                    ),
                ),
            ],
            options={
                "verbose_name": "Progresso de Construção",
                "verbose_name_plural": "Progressos de Construção",
            },
        ),
        # ------------------------------------------------------------------
        # ConstructionProject
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="ConstructionProject",
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
                    "name",
                    models.CharField(max_length=200, verbose_name="Nome"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Descrição"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PLANNING", "Em Planeamento"),
                            ("IN_PROGRESS", "Em Execução"),
                            ("ON_HOLD", "Suspenso"),
                            ("COMPLETED", "Concluído"),
                        ],
                        default="PLANNING",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "start_planned",
                    models.DateField(verbose_name="Início Planeado"),
                ),
                (
                    "end_planned",
                    models.DateField(
                        blank=True, null=True, verbose_name="Fim Planeado"
                    ),
                ),
                (
                    "start_actual",
                    models.DateField(
                        blank=True, null=True, verbose_name="Início Real"
                    ),
                ),
                (
                    "end_actual",
                    models.DateField(
                        blank=True, null=True, verbose_name="Fim Real"
                    ),
                ),
                (
                    "bim_model_s3_key",
                    models.CharField(
                        blank=True,
                        max_length=500,
                        verbose_name="S3 Key do Modelo BIM",
                    ),
                ),
                (
                    "building",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="construction_projects",
                        to="projects.building",
                        verbose_name="Edifício",
                    ),
                ),
                (
                    "contract",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="construction_project",
                        to="contracts.contract",
                        verbose_name="Contrato",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_construction_projects",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Criado por",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="construction_projects",
                        to="projects.project",
                        verbose_name="Projecto Imobiliário",
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="construction_project",
                        to="inventory.unit",
                        verbose_name="Unidade",
                    ),
                ),
            ],
            options={
                "verbose_name": "Projeto de Obra",
                "verbose_name_plural": "Projetos de Obra",
                "ordering": ["-created_at"],
            },
        ),
        # ------------------------------------------------------------------
        # HistoricalConstructionProject (django-simple-history)
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="HistoricalConstructionProject",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                    ),
                ),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("name", models.CharField(max_length=200, verbose_name="Nome")),
                ("description", models.TextField(blank=True, verbose_name="Descrição")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PLANNING", "Em Planeamento"),
                            ("IN_PROGRESS", "Em Execução"),
                            ("ON_HOLD", "Suspenso"),
                            ("COMPLETED", "Concluído"),
                        ],
                        default="PLANNING",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                ("start_planned", models.DateField(verbose_name="Início Planeado")),
                ("end_planned", models.DateField(blank=True, null=True, verbose_name="Fim Planeado")),
                ("start_actual", models.DateField(blank=True, null=True, verbose_name="Início Real")),
                ("end_actual", models.DateField(blank=True, null=True, verbose_name="Fim Real")),
                ("bim_model_s3_key", models.CharField(blank=True, max_length=500, verbose_name="S3 Key do Modelo BIM")),
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
                    "building",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="projects.building",
                        verbose_name="Edifício",
                    ),
                ),
                (
                    "contract",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="contracts.contract",
                        verbose_name="Contrato",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Criado por",
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
                    "project",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="projects.project",
                        verbose_name="Projecto Imobiliário",
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
                        verbose_name="Unidade",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Projeto de Obra",
                "verbose_name_plural": "historical Projetos de Obra",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
