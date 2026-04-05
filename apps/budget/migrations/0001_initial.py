# Generated manually for ImoOS Budget App

import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CrowdsourcedPrice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('item_name', models.CharField(max_length=200, verbose_name='Nome do Item')),
                ('category', models.CharField(choices=[('MATERIALS', 'Materiais de Construção'), ('LABOR', 'Mão-de-Obra'), ('EQUIPMENT', 'Equipamentos'), ('SERVICES', 'Serviços')], max_length=20, verbose_name='Categoria')),
                ('price_cve', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Preço (CVE)')),
                ('unit', models.CharField(choices=[('UN', 'Unidade'), ('M2', 'Metro Quadrado'), ('M3', 'Metro Cúbico'), ('KG', 'Quilograma'), ('HR', 'Hora'), ('DAY', 'Dia'), ('SACO', 'Saco'), ('L', 'Litro'), ('ML', 'Metro Linear'), ('KIT', 'Kit')], max_length=10, verbose_name='Unidade')),
                ('location', models.CharField(max_length=100, verbose_name='Localização')),
                ('island', models.CharField(choices=[('SANTIAGO', 'Santiago'), ('SAO_VICENTE', 'São Vicente'), ('SAL', 'Sal'), ('BOA_VISTA', 'Boa Vista'), ('SANTO_ANTAO', 'Santo Antão'), ('SAO_NICOLAU', 'São Nicolau'), ('FOGO', 'Fogo'), ('BRAVA', 'Brava'), ('MAIO', 'Maio')], max_length=20, verbose_name='Ilha')),
                ('supplier', models.CharField(blank=True, max_length=100, verbose_name='Fornecedor')),
                ('date_observed', models.DateField(verbose_name='Data Observada')),
                ('status', models.CharField(choices=[('PENDING', 'Pendente'), ('VERIFIED', 'Verificado'), ('REJECTED', 'Rejeitado')], default='PENDING', max_length=20, verbose_name='Estado')),
                ('verified_at', models.DateTimeField(blank=True, null=True, verbose_name='Verificado em')),
                ('rejection_reason', models.TextField(blank=True, verbose_name='Motivo da Rejeição')),
                ('points_earned', models.IntegerField(default=0, verbose_name='Pontos Ganhos')),
                ('receipt_photo', models.URLField(blank=True, verbose_name='Foto do Recibo/Preço')),
            ],
            options={
                'verbose_name': 'Preço Crowdsourced',
                'verbose_name_plural': 'Preços Crowdsourced',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LocalPriceItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.CharField(choices=[('MATERIALS', 'Materiais de Construção'), ('LABOR', 'Mão-de-Obra'), ('EQUIPMENT', 'Equipamentos'), ('SERVICES', 'Serviços')], max_length=20, verbose_name='Categoria')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('unit', models.CharField(choices=[('UN', 'Unidade'), ('M2', 'Metro Quadrado'), ('M3', 'Metro Cúbico'), ('KG', 'Quilograma'), ('HR', 'Hora'), ('DAY', 'Dia'), ('SACO', 'Saco'), ('L', 'Litro'), ('ML', 'Metro Linear'), ('KIT', 'Kit')], max_length=10, verbose_name='Unidade')),
                ('price_santiago', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Preço Santiago (CVE)')),
                ('price_sao_vicente', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço São Vicente (CVE)')),
                ('price_sal', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço Sal (CVE)')),
                ('price_boa_vista', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço Boa Vista (CVE)')),
                ('price_santo_antao', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço Santo Antão (CVE)')),
                ('price_sao_nicolau', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço São Nicolau (CVE)')),
                ('price_fogo', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço Fogo (CVE)')),
                ('price_brava', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço Brava (CVE)')),
                ('price_maio', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço Maio (CVE)')),
                ('source', models.CharField(max_length=100, verbose_name='Fonte')),
                ('last_updated', models.DateField(auto_now=True, verbose_name='Última Actualização')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Verificado')),
                ('ifc_class', models.CharField(blank=True, max_length=50, verbose_name='Classe IFC')),
            ],
            options={
                'verbose_name': 'Item de Preço',
                'verbose_name_plural': 'Items de Preço',
                'ordering': ['category', 'code'],
            },
        ),
        migrations.CreateModel(
            name='SimpleBudget',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('version', models.CharField(default='1.0', max_length=10, verbose_name='Versão')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('island', models.CharField(choices=[('SANTIAGO', 'Santiago'), ('SAO_VICENTE', 'São Vicente'), ('SAL', 'Sal'), ('BOA_VISTA', 'Boa Vista'), ('SANTO_ANTAO', 'Santo Antão'), ('SAO_NICOLAU', 'São Nicolau'), ('FOGO', 'Fogo'), ('BRAVA', 'Brava'), ('MAIO', 'Maio')], default='SANTIAGO', max_length=20, verbose_name='Ilha')),
                ('currency', models.CharField(default='CVE', max_length=3, verbose_name='Moeda')),
                ('contingency_pct', models.DecimalField(decimal_places=2, default=10.0, max_digits=5, verbose_name='Contingência (%)')),
                ('status', models.CharField(choices=[('DRAFT', 'Rascunho'), ('APPROVED', 'Aprovado'), ('BASELINE', 'Baseline'), ('ARCHIVED', 'Arquivado')], default='DRAFT', max_length=20, verbose_name='Estado')),
                ('total_materials', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total Materiais')),
                ('total_labor', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total Mão-de-Obra')),
                ('total_equipment', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total Equipamentos')),
                ('total_services', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total Serviços')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Subtotal')),
                ('total_contingency', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total Contingência')),
                ('grand_total', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total Geral')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='Aprovado em')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_budgets', to=settings.AUTH_USER_MODEL, verbose_name='Aprovado por')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_budgets', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='projects.project', verbose_name='Projecto')),
            ],
            options={
                'verbose_name': 'Orçamento',
                'verbose_name_plural': 'Orçamentos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserPriceScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('total_points', models.IntegerField(default=0, verbose_name='Total de Pontos')),
                ('prices_reported', models.IntegerField(default=0, verbose_name='Preços Reportados')),
                ('prices_verified', models.IntegerField(default=0, verbose_name='Preços Verificados')),
                ('rank', models.CharField(choices=[('Novato', 'Novato'), ('Contribuidor', 'Contribuidor'), ('Especialista', 'Especialista'), ('Guru', 'Guru'), ('Lenda', 'Lenda')], default='Novato', max_length=20, verbose_name='Rank')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='price_score', to=settings.AUTH_USER_MODEL, verbose_name='Utilizador')),
            ],
            options={
                'verbose_name': 'Pontuação de Preços',
                'verbose_name_plural': 'Pontuações de Preços',
                'ordering': ['-total_points'],
            },
        ),
        migrations.CreateModel(
            name='BudgetItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('line_number', models.PositiveIntegerField(verbose_name='Nº Linha')),
                ('category', models.CharField(choices=[('MATERIALS', 'Materiais de Construção'), ('LABOR', 'Mão-de-Obra'), ('EQUIPMENT', 'Equipamentos'), ('SERVICES', 'Serviços')], max_length=20, verbose_name='Categoria')),
                ('description', models.CharField(max_length=255, verbose_name='Descrição')),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=12, verbose_name='Quantidade')),
                ('unit', models.CharField(choices=[('UN', 'Unidade'), ('M2', 'Metro Quadrado'), ('M3', 'Metro Cúbico'), ('KG', 'Quilograma'), ('HR', 'Hora'), ('DAY', 'Dia'), ('SACO', 'Saco'), ('L', 'Litro'), ('ML', 'Metro Linear'), ('KIT', 'Kit')], max_length=10, verbose_name='Unidade')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Preço Unitário')),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total')),
                ('price_source', models.CharField(choices=[('MANUAL', 'Manual'), ('DATABASE', 'Base de Dados'), ('CROWDSOURCED', 'Crowdsourced'), ('TEMPLATE', 'Template')], default='MANUAL', max_length=20, verbose_name='Origem do Preço')),
                ('notes', models.TextField(blank=True, verbose_name='Observações')),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='budget.simplebudget', verbose_name='Orçamento')),
                ('price_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='budget_items', to='budget.localpriceitem', verbose_name='Item da Base de Preços')),
            ],
            options={
                'verbose_name': 'Item de Orçamento',
                'verbose_name_plural': 'Items de Orçamento',
                'ordering': ['line_number'],
            },
        ),
        migrations.AddField(
            model_name='localpriceitem',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_price_items', to=settings.AUTH_USER_MODEL, verbose_name='Verificado por'),
        ),
        migrations.AddField(
            model_name='crowdsourcedprice',
            name='linked_price_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='crowdsourced_entries', to='budget.localpriceitem', verbose_name='Item Oficial Vinculado'),
        ),
        migrations.AddField(
            model_name='crowdsourcedprice',
            name='reported_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported_prices', to=settings.AUTH_USER_MODEL, verbose_name='Reportado por'),
        ),
        migrations.AddField(
            model_name='crowdsourcedprice',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_crowd_prices', to=settings.AUTH_USER_MODEL, verbose_name='Verificado por'),
        ),
        migrations.AddIndex(
            model_name='localpriceitem',
            index=models.Index(fields=['category', 'is_verified'], name='budget_loca_categor_5c9f68_idx'),
        ),
        migrations.AddIndex(
            model_name='localpriceitem',
            index=models.Index(fields=['name'], name='budget_loca_name_5a2c68_idx'),
        ),
        migrations.AddIndex(
            model_name='localpriceitem',
            index=models.Index(fields=['code'], name='budget_loca_code_6b9f12_idx'),
        ),
        migrations.AddIndex(
            model_name='localpriceitem',
            index=models.Index(fields=['category', 'name'], name='budget_loca_categor_e3b2a1_idx'),
        ),
        migrations.AddIndex(
            model_name='simplebudget',
            index=models.Index(fields=['project', 'status'], name='budget_simp_project_8a9c21_idx'),
        ),
        migrations.AddIndex(
            model_name='simplebudget',
            index=models.Index(fields=['created_by', '-created_at'], name='budget_simp_created_3b4f56_idx'),
        ),
        migrations.AddIndex(
            model_name='budgetitem',
            index=models.Index(fields=['budget', 'category'], name='budget_budg_budget__9c8a21_idx'),
        ),
        migrations.AddIndex(
            model_name='budgetitem',
            index=models.Index(fields=['budget', 'line_number'], name='budget_budg_budget__2d1e45_idx'),
        ),
        migrations.AddIndex(
            model_name='crowdsourcedprice',
            index=models.Index(fields=['status', 'island'], name='budget_crow_status_7f8e92_idx'),
        ),
        migrations.AddIndex(
            model_name='crowdsourcedprice',
            index=models.Index(fields=['category', 'status'], name='budget_crow_categor_1a2b34_idx'),
        ),
        migrations.AddIndex(
            model_name='crowdsourcedprice',
            index=models.Index(fields=['reported_by', '-created_at'], name='budget_crow_reporte_5c6d78_idx'),
        ),
        migrations.AddIndex(
            model_name='crowdsourcedprice',
            index=models.Index(fields=['item_name'], name='budget_crow_item_na_9e0f12_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='simplebudget',
            unique_together={('project', 'name', 'version')},
        ),
        migrations.AlterUniqueTogether(
            name='budgetitem',
            unique_together={('budget', 'line_number')},
        ),
    ]
