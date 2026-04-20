"""
Budget Serializers — Serializadores DRF para o app budget.
"""
from rest_framework import serializers

from apps.budget.models import (
    LocalPriceItem, SimpleBudget, BudgetItem,
    CrowdsourcedPrice, UserPriceScore,
    ConstructionExpense, ConstructionAdvance
)


class LocalPriceItemSerializer(serializers.ModelSerializer):
    """Serializer para itens da base de preços."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    island_prices = serializers.SerializerMethodField()
    
    class Meta:
        model = LocalPriceItem
        fields = [
            'id', 'code', 'name', 'description', 'category', 'category_display',
            'unit', 'unit_display', 'island_prices', 'source', 'is_verified',
            'last_updated', 'ifc_class', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_island_prices(self, obj):
        """Retornar preços por ilha como dicionário."""
        return {
            'santiago': float(obj.price_santiago) if obj.price_santiago else None,
            'sao_vicente': float(obj.price_sao_vicente) if obj.price_sao_vicente else None,
            'sal': float(obj.price_sal) if obj.price_sal else None,
            'boa_vista': float(obj.price_boa_vista) if obj.price_boa_vista else None,
            'santo_antao': float(obj.price_santo_antao) if obj.price_santo_antao else None,
            'sao_nicolau': float(obj.price_sao_nicolau) if obj.price_sao_nicolau else None,
            'fogo': float(obj.price_fogo) if obj.price_fogo else None,
            'brava': float(obj.price_brava) if obj.price_brava else None,
            'maio': float(obj.price_maio) if obj.price_maio else None,
        }


class LocalPriceItemListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de preços."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    current_price = serializers.SerializerMethodField()
    
    class Meta:
        model = LocalPriceItem
        fields = ['id', 'code', 'name', 'category', 'category_display', 'unit', 'current_price', 'is_verified']
    
    def get_current_price(self, obj):
        """Retornar preço para ilha padrão (Santiago)."""
        return float(obj.price_santiago)


class BudgetItemSerializer(serializers.ModelSerializer):
    """Serializer para items de orçamento."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    price_source_display = serializers.CharField(source='get_price_source_display', read_only=True)
    price_item_details = LocalPriceItemListSerializer(source='price_item', read_only=True)
    
    class Meta:
        model = BudgetItem
        fields = [
            'id', 'line_number', 'category', 'category_display',
            'description', 'quantity', 'unit', 'unit_display',
            'unit_price', 'total', 'price_item', 'price_item_details',
            'price_source', 'price_source_display', 'notes'
        ]
        read_only_fields = ['id', 'total']
    
    def create(self, validated_data):
        """Criar item e recalcular totais do orçamento."""
        item = super().create(validated_data)
        item.budget.recalculate_totals()
        return item
    
    def update(self, instance, validated_data):
        """Actualizar item e recalcular totais do orçamento."""
        item = super().update(instance, validated_data)
        item.budget.recalculate_totals()
        return item


class SimpleBudgetSerializer(serializers.ModelSerializer):
    """Serializer para orçamentos."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    island_display = serializers.CharField(source='get_island_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = SimpleBudget
        fields = [
            'id', 'project', 'project_name', 'name', 'version', 'description',
            'island', 'island_display', 'currency', 'contingency_pct',
            'status', 'status_display', 'item_count',
            'total_materials', 'total_labor', 'total_equipment', 'total_services',
            'subtotal', 'total_contingency', 'grand_total',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by',
            'total_materials', 'total_labor', 'total_equipment', 'total_services',
            'subtotal', 'total_contingency', 'grand_total'
        ]
    
    def create(self, validated_data):
        """Definir utilizador actual como criador."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SimpleBudgetDetailSerializer(SimpleBudgetSerializer):
    """Serializer detalhado para orçamentos (com items)."""
    
    items = BudgetItemSerializer(many=True, read_only=True)
    
    class Meta(SimpleBudgetSerializer.Meta):
        fields = SimpleBudgetSerializer.Meta.fields + ['items']


class CrowdsourcedPriceSerializer(serializers.ModelSerializer):
    """Serializer para preços crowdsourced."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    island_display = serializers.CharField(source='get_island_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.email', read_only=True)
    
    class Meta:
        model = CrowdsourcedPrice
        fields = [
            'id', 'item_name', 'category', 'category_display',
            'price_cve', 'unit', 'unit_display', 'location', 'island', 'island_display',
            'supplier', 'date_observed', 'status', 'status_display',
            'reported_by', 'reported_by_name', 'points_earned',
            'receipt_photo', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'verified_by', 'verified_at', 
            'points_earned', 'created_at'
        ]
    
    def create(self, validated_data):
        """Definir utilizador actual como reportador."""
        validated_data['reported_by'] = self.context['request'].user
        return super().create(validated_data)


class CrowdsourcedPriceVerifySerializer(serializers.Serializer):
    """Serializer para verificação de preços crowdsourced."""
    
    action = serializers.ChoiceField(choices=['verify', 'reject'])
    points = serializers.IntegerField(default=10, min_value=0, max_value=100)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    link_to_official = serializers.UUIDField(required=False, allow_null=True)


class UserPriceScoreSerializer(serializers.ModelSerializer):
    """Serializer para pontuação de utilizadores."""
    
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    user_name = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserPriceScore
        fields = [
            'id', 'user', 'user_name', 'total_points', 
            'prices_reported', 'prices_verified', 'rank', 'rank_display'
        ]
        read_only_fields = ['id', 'user', 'total_points', 'prices_reported', 'prices_verified', 'rank']


class PriceSuggestionRequestSerializer(serializers.Serializer):
    """Serializer para pedido de sugestão de preço."""
    
    item_name = serializers.CharField(required=True, max_length=200)
    island = serializers.ChoiceField(
        choices=LocalPriceItem.ISLAND_CHOICES,
        default='SANTIAGO'
    )
    category = serializers.ChoiceField(choices=LocalPriceItem.CATEGORIES)
    unit = serializers.ChoiceField(choices=LocalPriceItem.UNITS, required=False)


class PriceAnomalyCheckSerializer(serializers.Serializer):
    """Serializer para verificação de anomalia de preço."""
    
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    item_name = serializers.CharField(required=True, max_length=200)
    island = serializers.ChoiceField(choices=LocalPriceItem.ISLAND_CHOICES)
    category = serializers.ChoiceField(choices=LocalPriceItem.CATEGORIES)


class BudgetCreateFromTemplateSerializer(serializers.Serializer):
    """Serializer para criar orçamento a partir de template."""
    
    TEMPLATE_CHOICES = [
        ('residential_t2', 'Apartamento T2'),
        ('residential_t3', 'Apartamento T3'),
        ('commercial_small', 'Comercial Pequeno'),
    ]
    
    template_type = serializers.ChoiceField(choices=TEMPLATE_CHOICES)
    project_id = serializers.UUIDField()
    island = serializers.ChoiceField(
        choices=LocalPriceItem.ISLAND_CHOICES,
        default='SANTIAGO'
    )
    name = serializers.CharField(required=False, max_length=200, allow_blank=True)


class BudgetCompareSerializer(serializers.Serializer):
    """Serializer para comparação de versões."""
    
    version_a = serializers.CharField(max_length=10)
    version_b = serializers.CharField(max_length=10)


class ExcelImportSerializer(serializers.Serializer):
    """Serializer para importação de Excel."""
    
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validar extensão do ficheiro."""
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError('Ficheiro deve ser Excel (.xlsx ou .xls)')
        return value


class ConstructionExpenseSerializer(serializers.ModelSerializer):
    """Serializer para despesas de construção."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_name = serializers.CharField(source='task.name', read_only=True, default=None)
    amount_eur = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = ConstructionExpense
        fields = [
            'id', 'project', 'project_name', 'task', 'task_name',
            'description', 'category', 'category_display',
            'amount_cve', 'amount_eur', 'payment_date', 'supplier',
            'invoice_number', 'receipt_photo', 'status', 'status_display',
            'notes', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'amount_eur']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ConstructionAdvanceSerializer(serializers.ModelSerializer):
    """Serializer para adiantamentos a empreiteiros."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    amount_eur = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = ConstructionAdvance
        fields = [
            'id', 'project', 'project_name', 'description',
            'amount_cve', 'amount_eur', 'payment_date', 'recipient',
            'is_settled', 'settled_at', 'status', 'status_display',
            'notes', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'amount_eur', 'settled_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
