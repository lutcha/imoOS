"""
Budget models — Tenant schema.

Base de preços local para Cabo Verde, com suporte a:
- Preços diferenciados por ilha
- Crowdsourcing de preços com gamificação
- Orçamentos simplificados estilo Excel
"""
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import TenantAwareModel


class LocalPriceItem(TenantAwareModel):
    """
    Preço unitário de materiais/mão-de-obra em Cabo Verde.
    
    Cada item tem preços específicos por ilha, refletindo as diferenças
    reais de custo entre Santiago, São Vicente, Sal, etc.
    """
    
    # Categorias de itens
    CATEGORY_MATERIALS = 'MATERIALS'
    CATEGORY_LABOR = 'LABOR'
    CATEGORY_EQUIPMENT = 'EQUIPMENT'
    CATEGORY_SERVICES = 'SERVICES'
    
    CATEGORIES = [
        (CATEGORY_MATERIALS, 'Materiais de Construção'),
        (CATEGORY_LABOR, 'Mão-de-Obra'),
        (CATEGORY_EQUIPMENT, 'Equipamentos'),
        (CATEGORY_SERVICES, 'Serviços'),
    ]
    
    # Unidades de medida
    UNIT_UN = 'UN'
    UNIT_M2 = 'M2'
    UNIT_M3 = 'M3'
    UNIT_KG = 'KG'
    UNIT_HR = 'HR'
    UNIT_DAY = 'DAY'
    UNIT_SACO = 'SACO'
    UNIT_L = 'L'
    UNIT_ML = 'ML'
    UNIT_KIT = 'KIT'
    
    UNITS = [
        (UNIT_UN, 'Unidade'),
        (UNIT_M2, 'Metro Quadrado'),
        (UNIT_M3, 'Metro Cúbico'),
        (UNIT_KG, 'Quilograma'),
        (UNIT_HR, 'Hora'),
        (UNIT_DAY, 'Dia'),
        (UNIT_SACO, 'Saco'),
        (UNIT_L, 'Litro'),
        (UNIT_ML, 'Metro Linear'),
        (UNIT_KIT, 'Kit'),
    ]
    
    # Ilhas de Cabo Verde
    ISLAND_CHOICES = [
        ('SANTIAGO', 'Santiago'),
        ('SAO_VICENTE', 'São Vicente'),
        ('SAL', 'Sal'),
        ('BOA_VISTA', 'Boa Vista'),
        ('SANTO_ANTAO', 'Santo Antão'),
        ('SAO_NICOLAU', 'São Nicolau'),
        ('FOGO', 'Fogo'),
        ('BRAVA', 'Brava'),
        ('MAIO', 'Maio'),
    ]
    
    category = models.CharField(
        max_length=20, 
        choices=CATEGORIES,
        verbose_name='Categoria'
    )
    code = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name='Código',
        help_text='Ex: IMOS-001, CV-045'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nome',
        help_text='Ex: Cimento CP350 50kg'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    unit = models.CharField(
        max_length=10, 
        choices=UNITS,
        verbose_name='Unidade'
    )
    
    # Preços por ilha (diferenças significativas!)
    price_santiago = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name='Preço Santiago (CVE)',
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    price_sao_vicente = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Preço São Vicente (CVE)'
    )
    price_sal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Preço Sal (CVE)'
    )
    price_boa_vista = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Preço Boa Vista (CVE)'
    )
    price_santo_antao = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Preço Santo Antão (CVE)'
    )
    price_sao_nicolau = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Preço São Nicolau (CVE)'
    )
    price_fogo = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Preço Fogo (CVE)'
    )
    price_brava = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Preço Brava (CVE)'
    )
    price_maio = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Preço Maio (CVE)'
    )
    
    # Metadados
    source = models.CharField(
        max_length=100,
        verbose_name='Fonte',
        help_text='Ex: Cimpor CV, Loja Praia, Crowdsourced'
    )
    last_updated = models.DateField(
        auto_now=True,
        verbose_name='Última Actualização'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Verificado',
        help_text='Verificado por administrador'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_price_items',
        verbose_name='Verificado por'
    )
    
    # Para relacionar com BIM (futuro)
    ifc_class = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name='Classe IFC',
        help_text='Ex: IfcWall, IfcSlab, IfcDoor'
    )
    
    class Meta:
        app_label = 'budget'
        verbose_name = 'Item de Preço'
        verbose_name_plural = 'Items de Preço'
        ordering = ['category', 'code']
        indexes = [
            models.Index(fields=['category', 'is_verified']),
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['category', 'name']),
        ]
    
    def __str__(self) -> str:
        return f'{self.code} - {self.name}'
    
    def get_price_for_island(self, island_code: str) -> Decimal:
        """
        Retornar preço para ilha específica.
        
        Args:
            island_code: Código da ilha (ex: 'SANTIAGO', 'SAL')
            
        Returns:
            Preço em CVE (fallback para Santiago se não definido)
        """
        price_map = {
            'SANTIAGO': self.price_santiago,
            'SAO_VICENTE': self.price_sao_vicente or self.price_santiago,
            'SAL': self.price_sal or self.price_santiago,
            'BOA_VISTA': self.price_boa_vista or self.price_santiago,
            'SANTO_ANTAO': self.price_santo_antao or self.price_santiago,
            'SAO_NICOLAU': self.price_sao_nicolau or self.price_santiago,
            'FOGO': self.price_fogo or self.price_santiago,
            'BRAVA': self.price_brava or self.price_santiago,
            'MAIO': self.price_maio or self.price_santiago,
        }
        return price_map.get(island_code, self.price_santiago)
    
    def get_all_island_prices(self) -> dict:
        """Retornar dicionário com preços de todas as ilhas."""
        return {
            'SANTIAGO': self.price_santiago,
            'SAO_VICENTE': self.price_sao_vicente,
            'SAL': self.price_sal,
            'BOA_VISTA': self.price_boa_vista,
            'SANTO_ANTAO': self.price_santo_antao,
            'SAO_NICOLAU': self.price_sao_nicolau,
            'FOGO': self.price_fogo,
            'BRAVA': self.price_brava,
            'MAIO': self.price_maio,
        }


class SimpleBudget(TenantAwareModel):
    """
    Orçamento simplificado (Excel-like) para projectos.
    
    Permite criar orçamentos detalhados com itens de múltiplas categorias,
    com cálculo automático de totais e margem de contingência.
    """
    
    # Status
    STATUS_DRAFT = 'DRAFT'
    STATUS_APPROVED = 'APPROVED'
    STATUS_BASELINE = 'BASELINE'
    STATUS_ARCHIVED = 'ARCHIVED'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Rascunho'),
        (STATUS_APPROVED, 'Aprovado'),
        (STATUS_BASELINE, 'Baseline'),
        (STATUS_ARCHIVED, 'Arquivado'),
    ]
    
    ISLAND_CHOICES = LocalPriceItem.ISLAND_CHOICES
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Projecto'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nome',
        help_text='Ex: Orçamento Preliminar'
    )
    version = models.CharField(
        max_length=10, 
        default='1.0',
        verbose_name='Versão'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    
    # Configuração
    island = models.CharField(
        max_length=20,
        choices=ISLAND_CHOICES,
        default='SANTIAGO',
        verbose_name='Ilha',
        help_text='Para aplicar preços correctos'
    )
    currency = models.CharField(
        max_length=3, 
        default='CVE',
        verbose_name='Moeda'
    )
    contingency_pct = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.0,
        verbose_name='Contingência (%)',
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='Estado'
    )
    
    # Totais (denormalizados para performance)
    total_materials = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total Materiais'
    )
    total_labor = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total Mão-de-Obra'
    )
    total_equipment = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total Equipamentos'
    )
    total_services = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total Serviços'
    )
    subtotal = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    total_contingency = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total Contingência'
    )
    grand_total = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total Geral'
    )
    
    # Metadados
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_budgets',
        verbose_name='Criado por'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_budgets',
        verbose_name='Aprovado por'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Actualizado em'
    )
    approved_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Aprovado em'
    )
    
    class Meta:
        app_label = 'budget'
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['created_by', '-created_at']),
        ]
        unique_together = ['project', 'name', 'version']
    
    def __str__(self) -> str:
        return f'{self.name} (v{self.version}) - {self.project.name}'
    
    def recalculate_totals(self) -> None:
        """Recalcular totais baseado nos itens."""
        items = self.items.all()
        
        self.total_materials = sum(
            i.total for i in items 
            if i.category == LocalPriceItem.CATEGORY_MATERIALS
        )
        self.total_labor = sum(
            i.total for i in items 
            if i.category == LocalPriceItem.CATEGORY_LABOR
        )
        self.total_equipment = sum(
            i.total for i in items 
            if i.category == LocalPriceItem.CATEGORY_EQUIPMENT
        )
        self.total_services = sum(
            i.total for i in items 
            if i.category == LocalPriceItem.CATEGORY_SERVICES
        )
        
        self.subtotal = (
            self.total_materials + 
            self.total_labor + 
            self.total_equipment + 
            self.total_services
        )
        self.total_contingency = (self.subtotal * self.contingency_pct) / 100
        self.grand_total = self.subtotal + self.total_contingency
        
        self.save(update_fields=[
            'total_materials', 'total_labor', 'total_equipment',
            'total_services', 'subtotal', 'total_contingency',
            'grand_total', 'updated_at'
        ])
    
    def approve(self, user) -> None:
        """Aprovar o orçamento."""
        self.status = self.STATUS_APPROVED
        self.approved_by = user
        self.approved_at = models.DateTimeField().auto_now
        self.save(update_fields=['status', 'approved_by', 'approved_at'])
    
    def get_item_count(self) -> int:
        """Retornar número de itens no orçamento."""
        return self.items.count()


class BudgetItem(TenantAwareModel):
    """
    Item de orçamento (linha da tabela).
    
    Cada item representa uma linha no orçamento com quantidade,
    preço unitário e total calculado automaticamente.
    """
    
    PRICE_SOURCE_MANUAL = 'MANUAL'
    PRICE_SOURCE_DATABASE = 'DATABASE'
    PRICE_SOURCE_CROWDSOURCED = 'CROWDSOURCED'
    PRICE_SOURCE_TEMPLATE = 'TEMPLATE'
    
    PRICE_SOURCE_CHOICES = [
        (PRICE_SOURCE_MANUAL, 'Manual'),
        (PRICE_SOURCE_DATABASE, 'Base de Dados'),
        (PRICE_SOURCE_CROWDSOURCED, 'Crowdsourced'),
        (PRICE_SOURCE_TEMPLATE, 'Template'),
    ]
    
    budget = models.ForeignKey(
        SimpleBudget,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Orçamento'
    )
    
    # Linha do orçamento
    line_number = models.PositiveIntegerField(
        verbose_name='Nº Linha'
    )
    category = models.CharField(
        max_length=20,
        choices=LocalPriceItem.CATEGORIES,
        verbose_name='Categoria'
    )
    description = models.CharField(
        max_length=255,
        verbose_name='Descrição'
    )
    
    # Quantidade e preço
    quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=3,
        verbose_name='Quantidade',
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    unit = models.CharField(
        max_length=10,
        choices=LocalPriceItem.UNITS,
        verbose_name='Unidade'
    )
    unit_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name='Preço Unitário',
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total = models.DecimalField(
        max_digits=14, 
        decimal_places=2,
        verbose_name='Total',
        default=Decimal('0.00')
    )
    
    # Link com base de preços (opcional)
    price_item = models.ForeignKey(
        LocalPriceItem,
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='budget_items',
        verbose_name='Item da Base de Preços'
    )
    
    # Origem do preço
    price_source = models.CharField(
        max_length=20,
        choices=PRICE_SOURCE_CHOICES,
        default=PRICE_SOURCE_MANUAL,
        verbose_name='Origem do Preço'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    
    class Meta:
        app_label = 'budget'
        verbose_name = 'Item de Orçamento'
        verbose_name_plural = 'Items de Orçamento'
        ordering = ['line_number']
        indexes = [
            models.Index(fields=['budget', 'category']),
            models.Index(fields=['budget', 'line_number']),
        ]
        unique_together = ['budget', 'line_number']
    
    def __str__(self) -> str:
        return f'{self.line_number}. {self.description}'
    
    def save(self, *args, **kwargs):
        """Calcular total automaticamente antes de salvar."""
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class CrowdsourcedPrice(TenantAwareModel):
    """
    Preços reportados pelos utilizadores (crowdsourcing).
    
    Sistema de gamificação onde utilizadores reportam preços observados
    no mercado e ganham pontos por contribuições verificadas.
    """
    
    STATUS_PENDING = 'PENDING'
    STATUS_VERIFIED = 'VERIFIED'
    STATUS_REJECTED = 'REJECTED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_VERIFIED, 'Verificado'),
        (STATUS_REJECTED, 'Rejeitado'),
    ]
    
    ISLAND_CHOICES = LocalPriceItem.ISLAND_CHOICES
    
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_prices',
        verbose_name='Reportado por'
    )
    item_name = models.CharField(
        max_length=200,
        verbose_name='Nome do Item'
    )
    category = models.CharField(
        max_length=20,
        choices=LocalPriceItem.CATEGORIES,
        verbose_name='Categoria'
    )
    price_cve = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name='Preço (CVE)',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit = models.CharField(
        max_length=10,
        choices=LocalPriceItem.UNITS,
        verbose_name='Unidade'
    )
    location = models.CharField(
        max_length=100,
        verbose_name='Localização',
        help_text='Ex: Praia, Achada Grande'
    )
    island = models.CharField(
        max_length=20,
        choices=ISLAND_CHOICES,
        verbose_name='Ilha'
    )
    supplier = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Fornecedor',
        help_text='Opcional'
    )
    date_observed = models.DateField(
        verbose_name='Data Observada',
        help_text='Quando viu o preço'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='verified_crowd_prices',
        verbose_name='Verificado por'
    )
    verified_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Verificado em'
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='Motivo da Rejeição'
    )
    
    # Gamificação
    points_earned = models.IntegerField(
        default=0,
        verbose_name='Pontos Ganhos'
    )
    
    # Link com item oficial (quando verificado e integrado)
    linked_price_item = models.ForeignKey(
        LocalPriceItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='crowdsourced_entries',
        verbose_name='Item Oficial Vinculado'
    )
    
    # Evidência (foto opcional)
    receipt_photo = models.URLField(
        blank=True,
        verbose_name='Foto do Recibo/Preço',
        help_text='URL da foto no S3'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'budget'
        verbose_name = 'Preço Crowdsourced'
        verbose_name_plural = 'Preços Crowdsourced'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'island']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['reported_by', '-created_at']),
            models.Index(fields=['item_name']),
        ]
    
    def __str__(self) -> str:
        return f'{self.item_name} - {self.price_cve} CVE ({self.get_island_display()})'
    
    def verify(self, user, points: int = 10) -> None:
        """Verificar o preço reportado."""
        self.status = self.STATUS_VERIFIED
        self.verified_by = user
        self.verified_at = models.DateTimeField().auto_now
        self.points_earned = points
        self.save(update_fields=['status', 'verified_by', 'verified_at', 'points_earned'])
        
        # Actualizar pontuação do utilizador
        user_score, _ = UserPriceScore.objects.get_or_create(user=self.reported_by)
        user_score.add_points(points)
    
    def reject(self, user, reason: str = '') -> None:
        """Rejeitar o preço reportado."""
        self.status = self.STATUS_REJECTED
        self.verified_by = user
        self.verified_at = models.DateTimeField().auto_now
        self.rejection_reason = reason
        self.save(update_fields=['status', 'verified_by', 'verified_at', 'rejection_reason'])


class UserPriceScore(TenantAwareModel):
    """
    Pontuação de gamificação para utilizadores.
    
    Sistema de ranks baseado em contribuições verificadas.
    """
    
    RANK_NOVATO = 'Novato'
    RANK_CONTRIBUIDOR = 'Contribuidor'
    RANK_ESPECIALISTA = 'Especialista'
    RANK_GURU = 'Guru'
    RANK_LENDA = 'Lenda'
    
    RANK_CHOICES = [
        (RANK_NOVATO, 'Novato'),
        (RANK_CONTRIBUIDOR, 'Contribuidor'),
        (RANK_ESPECIALISTA, 'Especialista'),
        (RANK_GURU, 'Guru'),
        (RANK_LENDA, 'Lenda'),
    ]
    
    # Thresholds de pontos para cada rank
    RANK_THRESHOLDS = {
        RANK_NOVATO: 0,
        RANK_CONTRIBUIDOR: 50,
        RANK_ESPECIALISTA: 200,
        RANK_GURU: 500,
        RANK_LENDA: 1000,
    }
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='price_score',
        verbose_name='Utilizador'
    )
    total_points = models.IntegerField(
        default=0,
        verbose_name='Total de Pontos'
    )
    prices_reported = models.IntegerField(
        default=0,
        verbose_name='Preços Reportados'
    )
    prices_verified = models.IntegerField(
        default=0,
        verbose_name='Preços Verificados'
    )
    rank = models.CharField(
        max_length=20,
        choices=RANK_CHOICES,
        default=RANK_NOVATO,
        verbose_name='Rank'
    )
    
    class Meta:
        app_label = 'budget'
        verbose_name = 'Pontuação de Preços'
        verbose_name_plural = 'Pontuações de Preços'
        ordering = ['-total_points']
    
    def __str__(self) -> str:
        return f'{self.user.email} - {self.rank} ({self.total_points} pts)'
    
    def add_points(self, points: int) -> None:
        """Adicionar pontos e actualizar rank."""
        self.total_points += points
        self.prices_verified += 1
        self._update_rank()
        self.save(update_fields=['total_points', 'prices_verified', 'rank'])
    
    def increment_reported(self) -> None:
        """Incrementar contador de preços reportados."""
        self.prices_reported += 1
        self.save(update_fields=['prices_reported'])
    
    def _update_rank(self) -> None:
        """Actualizar rank baseado nos pontos totais."""
        points = self.total_points
        if points >= self.RANK_THRESHOLDS[self.RANK_LENDA]:
            self.rank = self.RANK_LENDA
        elif points >= self.RANK_THRESHOLDS[self.RANK_GURU]:
            self.rank = self.RANK_GURU
        elif points >= self.RANK_THRESHOLDS[self.RANK_ESPECIALISTA]:
            self.rank = self.RANK_ESPECIALISTA
        elif points >= self.RANK_THRESHOLDS[self.RANK_CONTRIBUIDOR]:
            self.rank = self.RANK_CONTRIBUIDOR
        else:
            self.rank = self.RANK_NOVATO
