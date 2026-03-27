"""
Initial migration for apps.contracts.

Tenant-schema migration — runs via:
    python manage.py migrate_schemas

Dependencies:
- AUTH_USER_MODEL (shared schema, always present before tenant migrations run)
- crm and inventory apps are referenced via string FK labels; their migrations
  are NOT listed here because they also have no 0001_initial on disk yet.
  Django resolves cross-app FKs lazily through the ORM — the tables must
  simply exist in the tenant schema before any FK inserts are attempted.
  Add explicit deps (e.g. ('crm', '0001_initial')) once those migrations exist.
"""
import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # Shared-schema migration for AUTH_USER_MODEL (apps.users) runs first
        # via migrate_schemas --shared, so this swappable dep is safe.
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # Contract                                                             #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='Contract',
            fields=[
                # --- TenantAwareModel / BaseModel fields ---
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
                # --- Contract-specific fields ---
                ('status', models.CharField(
                    choices=[
                        ('DRAFT', 'Rascunho'),
                        ('ACTIVE', 'Activo'),
                        ('COMPLETED', 'Concluído'),
                        ('CANCELLED', 'Cancelado'),
                    ],
                    db_index=True,
                    default='DRAFT',
                    max_length=15,
                    verbose_name='Estado',
                )),
                ('contract_number', models.CharField(
                    help_text='Ex: ImoOS-2026-0001',
                    max_length=50,
                    unique=True,
                    verbose_name='Número do contrato',
                )),
                ('total_price_cve', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Valor total (CVE)',
                )),
                ('signed_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Data de assinatura',
                )),
                ('pdf_s3_key', models.CharField(
                    blank=True,
                    max_length=500,
                    verbose_name='S3 key do PDF',
                )),
                ('notes', models.TextField(
                    blank=True,
                    verbose_name='Notas internas',
                )),
                # --- FK fields ---
                ('reservation', models.OneToOneField(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='contract',
                    to='crm.unitreservation',
                    verbose_name='Reserva de origem',
                )),
                ('unit', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='contracts',
                    to='inventory.unit',
                    verbose_name='Unidade',
                )),
                ('lead', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='contracts',
                    to='crm.lead',
                    verbose_name='Lead / Comprador',
                )),
                ('vendor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='contracts_as_vendor',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Vendedor responsável',
                )),
            ],
            options={
                'verbose_name': 'Contrato',
                'verbose_name_plural': 'Contratos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='contract',
            index=models.Index(
                fields=['status', '-created_at'],
                name='contract_status_created_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='contract',
            index=models.Index(
                fields=['unit', 'status'],
                name='contract_unit_status_idx',
            ),
        ),
        migrations.AddConstraint(
            model_name='contract',
            constraint=models.UniqueConstraint(
                condition=models.Q(status='ACTIVE'),
                fields=['reservation'],
                name='unique_active_contract_per_reservation',
            ),
        ),

        # ------------------------------------------------------------------ #
        # HistoricalContract (django-simple-history)                           #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='HistoricalContract',
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
                ('status', models.CharField(
                    choices=[
                        ('DRAFT', 'Rascunho'),
                        ('ACTIVE', 'Activo'),
                        ('COMPLETED', 'Concluído'),
                        ('CANCELLED', 'Cancelado'),
                    ],
                    db_index=True,
                    default='DRAFT',
                    max_length=15,
                    verbose_name='Estado',
                )),
                ('contract_number', models.CharField(
                    db_index=True,
                    help_text='Ex: ImoOS-2026-0001',
                    max_length=50,
                    verbose_name='Número do contrato',
                )),
                ('total_price_cve', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Valor total (CVE)',
                )),
                ('signed_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Data de assinatura',
                )),
                ('pdf_s3_key', models.CharField(
                    blank=True,
                    max_length=500,
                    verbose_name='S3 key do PDF',
                )),
                ('notes', models.TextField(
                    blank=True,
                    verbose_name='Notas internas',
                )),
                # simple_history shadow FK columns (integer, not UUID FK objects)
                ('reservation_id', models.UUIDField(
                    blank=True,
                    db_index=True,
                    null=True,
                )),
                ('unit_id', models.UUIDField(
                    db_index=True,
                )),
                ('lead_id', models.UUIDField(
                    db_index=True,
                )),
                ('vendor_id', models.UUIDField(
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
                'verbose_name': 'historical Contrato',
                'verbose_name_plural': 'historical Contratos',
                'ordering': ['-history_date', '-history_id'],
                'get_latest_by': ('history_date', 'history_id'),
            },
        ),

        # ------------------------------------------------------------------ #
        # Payment                                                               #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='Payment',
            fields=[
                # --- TenantAwareModel / BaseModel fields ---
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
                # --- Payment-specific fields ---
                ('payment_type', models.CharField(
                    choices=[
                        ('DEPOSIT', 'Sinal'),
                        ('INSTALLMENT', 'Prestação'),
                        ('FINAL', 'Pagamento Final'),
                    ],
                    max_length=15,
                    verbose_name='Tipo',
                )),
                ('amount_cve', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Valor (CVE)',
                )),
                ('due_date', models.DateField(verbose_name='Data de vencimento')),
                ('paid_date', models.DateField(
                    blank=True,
                    null=True,
                    verbose_name='Data de pagamento',
                )),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('PAID', 'Pago'),
                        ('OVERDUE', 'Em Atraso'),
                    ],
                    db_index=True,
                    default='PENDING',
                    max_length=10,
                    verbose_name='Estado',
                )),
                ('reference', models.CharField(
                    blank=True,
                    help_text='Referência MBE ou transferência bancária',
                    max_length=100,
                    verbose_name='Referência de pagamento',
                )),
                # --- FK ---
                ('contract', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='payments',
                    to='contracts.contract',
                    verbose_name='Contrato',
                )),
            ],
            options={
                'verbose_name': 'Pagamento',
                'verbose_name_plural': 'Pagamentos',
                'ordering': ['due_date'],
            },
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(
                fields=['status', 'due_date'],
                name='payment_status_due_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(
                fields=['contract', 'status'],
                name='payment_contract_status_idx',
            ),
        ),

        # ------------------------------------------------------------------ #
        # HistoricalPayment (django-simple-history)                            #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='HistoricalPayment',
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
                ('payment_type', models.CharField(
                    choices=[
                        ('DEPOSIT', 'Sinal'),
                        ('INSTALLMENT', 'Prestação'),
                        ('FINAL', 'Pagamento Final'),
                    ],
                    max_length=15,
                    verbose_name='Tipo',
                )),
                ('amount_cve', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Valor (CVE)',
                )),
                ('due_date', models.DateField(verbose_name='Data de vencimento')),
                ('paid_date', models.DateField(
                    blank=True,
                    null=True,
                    verbose_name='Data de pagamento',
                )),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('PAID', 'Pago'),
                        ('OVERDUE', 'Em Atraso'),
                    ],
                    db_index=True,
                    default='PENDING',
                    max_length=10,
                    verbose_name='Estado',
                )),
                ('reference', models.CharField(
                    blank=True,
                    help_text='Referência MBE ou transferência bancária',
                    max_length=100,
                    verbose_name='Referência de pagamento',
                )),
                # simple_history shadow FK column
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
                'verbose_name': 'historical Pagamento',
                'verbose_name_plural': 'historical Pagamentos',
                'ordering': ['-history_date', '-history_id'],
                'get_latest_by': ('history_date', 'history_id'),
            },
        ),
    ]
