"""
Budget models - ImoOS
Base de preços local para Cabo Verde com suporte a crowdsourcing e gamificação.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel


class PriceCategory(TenantAwareModel):
    """Categorias: Materiais, Mão-de-obra, Equipamentos, Serviços"""
    
    name = models.CharField(max_length=100)  # "Materiais de Construção"
    code = models.CharField(max_length=10, unique=True)  # "MAT"
    icon = models.CharField(max_length=50, default='🔨')  # Emoji para UI
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoria de Preço'
        verbose_name_plural = 'Categorias de Preços'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class PriceItem(TenantAwareModel):
    """Item com preços por ilha"""
    
    ISLANDS = [
        ('SANTIAGO', 'Santiago'),
        ('SAO_VICENTE', 'São Vicente'),
        ('SAL', 'Sal'),
        ('BOA_VISTA', 'Boa Vista'),
        ('SANTO_ANTAO', 'Santo Antão'),
        ('SAO_NICOLAU', 'São Nicolau'),
        ('MAIO', 'Maio'),
        ('FOGO', 'Fogo'),
        ('BRAVA', 'Brava'),
    ]
    
    category = models.ForeignKey(
        PriceCategory, 
        on_delete=models.PROTECT, 
        related_name='items'
    )
    name = models.CharField(max_length=200)  # "Cimento CP350 50kg"
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20)  # "saco", "m2", "m3", "hora", "dia"
    
    # Preços por ilha (variação significativa!)
    price_santiago = models.DecimalField(max_digits=12, decimal_places=2)
    price_sao_vicente = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_sal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_boa_vista = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_santo_antao = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_sao_nicolau = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_maio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_fogo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_brava = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Se preço não definido para ilha, usar santiago + markup estimado
    default_markup_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'))
    
    # Metadados
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # Verificado por admin
    source = models.CharField(max_length=100, default='Admin')  # "Fornecedor X", "Crowdsourced"
    last_updated = models.DateField(auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Item de Preço'
        verbose_name_plural = 'Itens de Preços'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['name']),  # Para search
            models.Index(fields=['is_active', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.unit})"
    
    def get_price_for_island(self, island_code: str) -> Decimal:
        """Retorna preço para ilha específica ou calcula fallback"""
        island_map = {
            'SANTIAGO': self.price_santiago,
            'SAO_VICENTE': self.price_sao_vicente,
            'SAL': self.price_sal,
            'BOA_VISTA': self.price_boa_vista,
            'SANTO_ANTAO': self.price_santo_antao,
            'SAO_NICOLAU': self.price_sao_nicolau,
            'MAIO': self.price_maio,
            'FOGO': self.price_fogo,
            'BRAVA': self.price_brava,
        }
        
        price = island_map.get(island_code)
        if price:
            return price
        
        # Fallback: Santiago + markup
        return self.price_santiago * (1 + self.default_markup_pct / 100)
    
    def get_islands_with_prices(self):
        """Retorna lista de ilhas que têm preço definido"""
        islands = []
        island_fields = {
            'SANTIAGO': self.price_santiago,
            'SAO_VICENTE': self.price_sao_vicente,
            'SAL': self.price_sal,
            'BOA_VISTA': self.price_boa_vista,
            'SANTO_ANTAO': self.price_santo_antao,
            'SAO_NICOLAU': self.price_sao_nicolau,
            'MAIO': self.price_maio,
            'FOGO': self.price_fogo,
            'BRAVA': self.price_brava,
        }
        for code, price in island_fields.items():
            if price:
                islands.append(code)
        return islands


class CrowdsourcedPrice(TenantAwareModel):
    """Preços reportados pelos utilizadores"""
    
    REPORTED_BY_CHOICES = [
        ('VENDOR', 'Fornecedor'),
        ('CONTRACTOR', 'Empreiteiro'),
        ('ENGINEER', 'Engenheiro'),
        ('FIELD_STAFF', 'Equipa de Campo'),
        ('OTHER', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Rejeitado'),
    ]
    
    item_name = models.CharField(max_length=200)
    category = models.ForeignKey(
        PriceCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    price_cve = models.DecimalField(max_digits=12, decimal_places=2)
    island = models.CharField(max_length=20, choices=PriceItem.ISLANDS)
    location_detail = models.CharField(max_length=100, blank=True)  # "Praia, Achada Grande"
    
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_prices'
    )
    reporter_role = models.CharField(max_length=20, choices=REPORTED_BY_CHOICES)
    supplier_name = models.CharField(max_length=100, blank=True)  # Opcional
    date_reported = models.DateField(auto_now_add=True)
    
    # Gamificação
    points_earned = models.IntegerField(default=10)
    
    # Moderação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_prices'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Se aprovado, link ao PriceItem oficial
    linked_item = models.ForeignKey(
        PriceItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crowdsourced_entries'
    )
    
    class Meta:
        verbose_name = 'Preço Crowdsourced'
        verbose_name_plural = 'Preços Crowdsourced'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'island']),
            models.Index(fields=['reported_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.item_name} - {self.island} - {self.status}"


class Budget(TenantAwareModel):
    """Orçamento de projeto/obras"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Rascunho'),
        ('APPROVED', 'Aprovado'),
        ('BASELINE', 'Baseline'),  # Congelado para comparação
        ('ARCHIVED', 'Arquivado'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='budgets',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)  # "Orçamento Preliminar Palmira"
    description = models.TextField(blank=True)
    
    # Configuração
    island = models.CharField(max_length=20, choices=PriceItem.ISLANDS, default='SANTIAGO')
    contingency_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Totais (calculados)
    total_materials = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_labor = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_equipment = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_services = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    contingency = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_budgets'
    )
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['island', 'status']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_island_display()})"
    
    def recalculate_totals(self):
        """Recalcula totais baseado nos itens"""
        items = self.items.all()
        
        self.subtotal = sum(item.total for item in items)
        self.contingency = self.subtotal * (self.contingency_pct / 100)
        self.total = self.subtotal + self.contingency
        
        # Por categoria
        self.total_materials = Decimal('0.00')
        self.total_labor = Decimal('0.00')
        self.total_equipment = Decimal('0.00')
        self.total_services = Decimal('0.00')
        
        for item in items:
            category_code = item.get_category_code()
            if category_code == 'MAT':
                self.total_materials += item.total
            elif category_code == 'LABOR':
                self.total_labor += item.total
            elif category_code == 'EQUIP':
                self.total_equipment += item.total
            elif category_code == 'SERV':
                self.total_services += item.total
        
        self.save(update_fields=[
            'total_materials', 'total_labor', 'total_equipment',
            'total_services', 'subtotal', 'contingency', 'total'
        ])


class BudgetItem(TenantAwareModel):
    """Item de orçamento"""
    
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='items'
    )
    price_item = models.ForeignKey(
        PriceItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_entries'
    )
    
    # Se item custom (não na base)
    custom_name = models.CharField(max_length=200, blank=True)
    custom_unit = models.CharField(max_length=20, blank=True)
    custom_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    
    # Ordem para display
    order = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)  # "Preço negociado com fornecedor X"
    
    class Meta:
        verbose_name = 'Item de Orçamento'
        verbose_name_plural = 'Itens de Orçamento'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['budget', 'order']),
        ]
    
    def __str__(self):
        name = self.custom_name or (self.price_item.name if self.price_item else 'Item')
        return f"{name} - {self.quantity} x {self.unit_price}"
    
    def get_category_code(self):
        """Retorna código da categoria para cálculo de totais"""
        if self.price_item and self.price_item.category:
            return self.price_item.category.code
        return None
    
    def save(self, *args, **kwargs):
        # Auto-calcular preço
        if self.price_item:
            self.unit_price = self.price_item.get_price_for_island(self.budget.island)
            if not self.custom_name:
                self.custom_name = self.price_item.name
            if not self.custom_unit:
                self.custom_unit = self.price_item.unit
        elif self.custom_unit_price:
            self.unit_price = self.custom_unit_price
        
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.budget.recalculate_totals()


class UserPoints(TenantAwareModel):
    """Pontos acumulados por utilizador"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='points'
    )
    total_points = models.IntegerField(default=0)
    prices_reported = models.IntegerField(default=0)
    prices_verified = models.IntegerField(default=0)
    
    # Badges
    badges = models.JSONField(default=list)  # ["first_price", "10_prices", "verified_reporter"]
    
    class Meta:
        verbose_name = 'Pontos do Utilizador'
        verbose_name_plural = 'Pontos dos Utilizadores'
    
    def __str__(self):
        return f"{self.user.email} - {self.total_points} pontos"
    
    def add_points(self, points: int, reason: str):
        self.total_points += points
        self.save(update_fields=['total_points'])
        # Criar log
        PointsLog.objects.create(
            user=self.user,
            points=points,
            reason=reason
        )
    
    def add_badge(self, badge_code: str):
        """Adiciona um badge se ainda não existe"""
        if badge_code not in self.badges:
            self.badges.append(badge_code)
            self.save(update_fields=['badges'])
    
    def increment_prices_reported(self):
        self.prices_reported += 1
        self.save(update_fields=['prices_reported'])
        
        # Verificar badges
        if self.prices_reported == 1:
            self.add_badge('first_price')
            self.add_points(5, "Primeiro preço reportado!")
        elif self.prices_reported == 10:
            self.add_badge('10_prices')
            self.add_points(20, "10 preços reportados!")
        elif self.prices_reported == 50:
            self.add_badge('50_prices')
            self.add_points(50, "50 preços reportados!")
    
    def increment_prices_verified(self):
        self.prices_verified += 1
        self.save(update_fields=['prices_verified'])
        
        if self.prices_verified == 1:
            self.add_badge('verified_reporter')


class PointsLog(TenantAwareModel):
    """Log de pontos ganhos"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='points_log'
    )
    points = models.IntegerField()
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Pontos'
        verbose_name_plural = 'Logs de Pontos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} +{self.points} - {self.reason}"
