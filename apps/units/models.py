from django.db import models
from simple_history.models import HistoricalRecords
from apps.core.models import TenantAwareModel
from apps.projects.models import Floor

class Unit(TenantAwareModel):
    """
    Unidade (Apartamento, Lote, Loja) dentro de um Piso.
    """
    TYPE_APARTMENT = 'APARTMENT'
    TYPE_LAND = 'LAND'
    TYPE_COMMERCIAL = 'COMMERCIAL'
    TYPE_PARKING = 'PARKING'
    TYPE_CHOICES = [
        (TYPE_APARTMENT, 'Apartamento'),
        (TYPE_LAND, 'Lote/Terreno'),
        (TYPE_COMMERCIAL, 'Comercial/Loja'),
        (TYPE_PARKING, 'Estacionamento'),
    ]

    STATUS_AVAILABLE = 'AVAILABLE'
    STATUS_RESERVED = 'RESERVED'
    STATUS_SOLD = 'SOLD'
    STATUS_BLOCKED = 'BLOCKED'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Disponível'),
        (STATUS_RESERVED, 'Reservado'),
        (STATUS_SOLD, 'Vendido'),
        (STATUS_BLOCKED, 'Bloqueado'),
    ]

    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='units')
    number = models.CharField(max_length=20)  # e.g., "101", "A-12"
    typology = models.CharField(max_length=10, blank=True)  # T1, T2, T3
    unit_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_APARTMENT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    
    # Financials
    price = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='CVE')
    
    # Areas
    internal_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    external_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Metadata
    fraçao = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'
        unique_together = ['floor', 'number']
        ordering = ['number']

    def __str__(self):
        return f'{self.floor} — Unit {self.number}'
