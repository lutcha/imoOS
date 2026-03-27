"""
Inventory module — Tenant schema.
Units (Frações) are the core commercial asset of ImoOS.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from apps.projects.models import Floor

User = get_user_model()


class UnitType(models.Model):
    """Tipologia: T1, T2, T3, Loja, Estacionamento, etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)  # 'T2', 'Loja', 'Garagem'
    code = models.CharField(max_length=10)  # 'T2', 'L', 'G'
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Unit(models.Model):
    """
    Unidade de venda (Fração, Loja, Estacionamento).
    This is the core commercial entity — every sale starts here.
    """
    STATUS_AVAILABLE = 'AVAILABLE'
    STATUS_RESERVED = 'RESERVED'
    STATUS_CONTRACT = 'CONTRACT'
    STATUS_SOLD = 'SOLD'
    STATUS_MAINTENANCE = 'MAINTENANCE'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Disponível'),
        (STATUS_RESERVED, 'Reservado'),
        (STATUS_CONTRACT, 'Contrato Assinado'),
        (STATUS_SOLD, 'Vendido'),
        (STATUS_MAINTENANCE, 'Manutenção'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='units')
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    code = models.CharField(max_length=30, help_text='Ex: BLK-A-P3-DT2')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    # Physical characteristics
    area_bruta = models.DecimalField(max_digits=8, decimal_places=2, help_text='m² brutos')
    area_util = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text='m² úteis')
    orientation = models.CharField(max_length=20, blank=True, help_text='Norte, Sul, Mar, etc.')
    floor_number = models.IntegerField(default=0)

    # BIM integration (Phase 2)
    bim_guid = models.CharField(max_length=100, blank=True, help_text='IFC element GUID')

    # Soft delete
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Audit history — REQUIRED: tracks every status and price change
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'
        unique_together = ['floor', 'code']
        ordering = ['code']
        indexes = [
            models.Index(fields=['status'],            name='inventory_unit_status_idx'),
            models.Index(fields=['status', 'is_deleted'], name='inventory_unit_status_del_idx'),
        ]

    def __str__(self):
        return f'{self.code} ({self.get_status_display()})'

    @property
    def project(self):
        return self.floor.building.project


class UnitPricing(models.Model):
    """
    Current pricing for a Unit.
    Separate model to track price history via simple_history.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.OneToOneField(Unit, on_delete=models.CASCADE, related_name='pricing')
    price_cve = models.DecimalField(max_digits=12, decimal_places=2, help_text='Preço em CVE')
    price_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Preço em EUR')
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    DISCOUNT_NONE = 'NONE'
    DISCOUNT_PERCENT = 'PERCENT'
    DISCOUNT_FIXED = 'FIXED'
    DISCOUNT_CHOICES = [
        (DISCOUNT_NONE, 'Sem Desconto'),
        (DISCOUNT_PERCENT, 'Percentagem'),
        (DISCOUNT_FIXED, 'Valor Fixo'),
    ]
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_CHOICES, default=DISCOUNT_NONE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    @property
    def final_price_cve(self):
        if self.discount_type == self.DISCOUNT_PERCENT:
            return self.price_cve * (1 - self.discount_value / 100)
        elif self.discount_type == self.DISCOUNT_FIXED:
            return self.price_cve - self.discount_value
        return self.price_cve
