"""
Initial migration for apps.payments.

Tenant-schema migration — runs via:
    python manage.py migrate_schemas

Dependencies:
- contracts app must be migrated first (PaymentPlan has FK to contracts.Contract,
  PaymentPlanItem has optional FK to contracts.Payment).
- AUTH_USER_MODEL (shared schema) — for simple_history.history_user FK.
"""
import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # contracts must be migrated first — PaymentPlan references contracts.Contract
        # and PaymentPlanItem optionally references contracts.Payment.
        ('contracts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # ------------------------------------------------------------------ #
        # PaymentPlan                                                          #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Criado em',
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    verbose_name='Actualizado em',
                )),
                ('plan_type', models.CharField(
                    choices=[
                        ('STANDARD', 'Padrão (10/80/10)'),
                        ('CUSTOM', 'Personalizado'),
                    ],
                    default='STANDARD',
                    max_length=10,
                    verbose_name='Tipo de plano',
                )),
                ('total_cve', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Valor total (CVE)',
                )),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('contract', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='payment_plan',
                    to='contracts.contract',
                    verbose_name='Contrato',
                )),
            ],
            options={
                'verbose_name': 'Plano de Pagamento',
                'verbose_name_plural': 'Planos de Pagamento',
                'ordering': ['-created_at'],
            },
        ),

        # ------------------------------------------------------------------ #
        # HistoricalPaymentPlan (django-simple-history)                        #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='HistoricalPaymentPlan',
            fields=[
                ('id', models.UUIDField(
                    db_index=True,
                    default=uuid.uuid4,
                    editable=False,
                )),
                ('created_at', models.DateTimeField(
                    blank=True,
                    editable=False,
                    verbose_name='Criado em',
                )),
                ('updated_at', models.DateTimeField(
                    blank=True,
                    editable=False,
                    verbose_name='Actualizado em',
                )),
                ('plan_type', models.CharField(
                    choices=[
                        ('STANDARD', 'Padrão (10/80/10)'),
                        ('CUSTOM', 'Personalizado'),
                    ],
                    default='STANDARD',
                    max_length=10,
                    verbose_name='Tipo de plano',
                )),
                ('total_cve', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Valor total (CVE)',
                )),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('contract_id', models.UUIDField(db_index=True)),
                # simple_history metadata
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
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
                'verbose_name': 'historical Plano de Pagamento',
                'verbose_name_plural': 'historical Planos de Pagamento',
                'ordering': ['-history_date', '-history_id'],
                'get_latest_by': ('history_date', 'history_id'),
            },
        ),

        # ------------------------------------------------------------------ #
        # PaymentPlanItem                                                       #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='PaymentPlanItem',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Criado em',
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    verbose_name='Actualizado em',
                )),
                ('item_type', models.CharField(
                    choices=[
                        ('DEPOSIT', 'Sinal'),
                        ('INSTALLMENT', 'Prestação'),
                        ('FINAL', 'Pagamento Final'),
                    ],
                    max_length=15,
                    verbose_name='Tipo',
                )),
                ('percentage', models.DecimalField(
                    decimal_places=4,
                    max_digits=7,
                    verbose_name='Percentagem (%)',
                )),
                ('amount_cve', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Valor (CVE)',
                )),
                ('due_date', models.DateField(verbose_name='Data prevista')),
                ('mbe_reference', models.CharField(
                    blank=True,
                    max_length=25,
                    verbose_name='Referência MBE',
                )),
                ('order', models.PositiveSmallIntegerField(
                    default=0,
                    verbose_name='Ordem',
                )),
                ('plan', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='payments.paymentplan',
                    verbose_name='Plano',
                )),
                ('payment', models.OneToOneField(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='plan_item',
                    to='contracts.payment',
                    verbose_name='Pagamento liquidado',
                )),
            ],
            options={
                'verbose_name': 'Item do Plano de Pagamento',
                'verbose_name_plural': 'Itens do Plano de Pagamento',
                'ordering': ['order', 'due_date'],
            },
        ),
        migrations.AddIndex(
            model_name='paymentplanitem',
            index=models.Index(
                fields=['plan', 'order'],
                name='planitem_plan_order_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='paymentplanitem',
            index=models.Index(
                fields=['due_date'],
                name='planitem_due_date_idx',
            ),
        ),

        # ------------------------------------------------------------------ #
        # HistoricalPaymentPlanItem (django-simple-history)                    #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='HistoricalPaymentPlanItem',
            fields=[
                ('id', models.UUIDField(
                    db_index=True,
                    default=uuid.uuid4,
                    editable=False,
                )),
                ('created_at', models.DateTimeField(
                    blank=True,
                    editable=False,
                    verbose_name='Criado em',
                )),
                ('updated_at', models.DateTimeField(
                    blank=True,
                    editable=False,
                    verbose_name='Actualizado em',
                )),
                ('item_type', models.CharField(
                    choices=[
                        ('DEPOSIT', 'Sinal'),
                        ('INSTALLMENT', 'Prestação'),
                        ('FINAL', 'Pagamento Final'),
                    ],
                    max_length=15,
                    verbose_name='Tipo',
                )),
                ('percentage', models.DecimalField(
                    decimal_places=4,
                    max_digits=7,
                    verbose_name='Percentagem (%)',
                )),
                ('amount_cve', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Valor (CVE)',
                )),
                ('due_date', models.DateField(verbose_name='Data prevista')),
                ('mbe_reference', models.CharField(
                    blank=True,
                    max_length=25,
                    verbose_name='Referência MBE',
                )),
                ('order', models.PositiveSmallIntegerField(
                    default=0,
                    verbose_name='Ordem',
                )),
                # simple_history shadow FKs
                ('plan_id', models.UUIDField(db_index=True)),
                ('payment_id', models.UUIDField(
                    blank=True,
                    db_index=True,
                    null=True,
                )),
                # simple_history metadata
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
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
                'verbose_name': 'historical Item do Plano de Pagamento',
                'verbose_name_plural': 'historical Itens do Plano de Pagamento',
                'ordering': ['-history_date', '-history_id'],
                'get_latest_by': ('history_date', 'history_id'),
            },
        ),
    ]
