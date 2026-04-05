"""
Budget serializers - ImoOS
Serializers para preços, orçamentos e gamificação.
"""
from rest_framework import serializers
from django.db import transaction

from .models import (
    PriceCategory, PriceItem, CrowdsourcedPrice,
    Budget, BudgetItem, UserPoints, PointsLog
)


class PriceCategorySerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceCategory
        fields = ['id', 'name', 'code', 'icon', 'is_active', 'item_count']
    
    def get_item_count(self, obj):
        return obj.items.filter(is_active=True).count()


class PriceItemSerializer(serializers.ModelSerializer):
    category_detail = PriceCategorySerializer(source='category', read_only=True)
    current_price = serializers.SerializerMethodField()
    island_prices = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceItem
        fields = [
            'id', 'category', 'category_detail', 'name', 'description', 'unit',
            'price_santiago', 'price_sao_vicente', 'price_sal', 'price_boa_vista',
            'price_santo_antao', 'price_sao_nicolau', 'price_maio', 'price_fogo', 
            'price_brava',
            'default_markup_pct', 'current_price', 'island_prices',
            'is_active', 'is_verified', 'source', 'last_updated',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_updated']
    
    def get_current_price(self, obj):
        """Retorna preço para ilha do contexto ou Santiago"""
        request = self.context.get('request')
        island = 'SANTIAGO'
        if request:
            island = request.query_params.get('island', 'SANTIAGO')
        return obj.get_price_for_island(island)
    
    def get_island_prices(self, obj):
        """Retorna dict com preços por ilha"""
        return {
            'SANTIAGO': obj.price_santiago,
            'SAO_VICENTE': obj.price_sao_vicente,
            'SAL': obj.price_sal,
            'BOA_VISTA': obj.price_boa_vista,
            'SANTO_ANTAO': obj.price_santo_antao,
            'SAO_NICOLAU': obj.price_sao_nicolau,
            'MAIO': obj.price_maio,
            'FOGO': obj.price_fogo,
            'BRAVA': obj.price_brava,
        }


class PriceItemListSerializer(serializers.ModelSerializer):
    """Serializer light para listagens"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    current_price = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceItem
        fields = [
            'id', 'name', 'unit', 'category_name', 'category_icon',
            'current_price', 'is_verified', 'source'
        ]
    
    def get_current_price(self, obj):
        request = self.context.get('request')
        island = 'SANTIAGO'
        if request:
            island = request.query_params.get('island', 'SANTIAGO')
        return obj.get_price_for_island(island)


class CrowdsourcedPriceSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.CharField(source='reported_by.email', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.email', read_only=True)
    island_display = serializers.CharField(source='get_island_display', read_only=True)
    reporter_role_display = serializers.CharField(source='get_reporter_role_display', read_only=True)
    category_detail = PriceCategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = CrowdsourcedPrice
        fields = [
            'id', 'item_name', 'category', 'category_detail',
            'price_cve', 'island', 'island_display', 'location_detail',
            'reported_by', 'reported_by_name', 'reporter_role', 'reporter_role_display',
            'supplier_name', 'date_reported', 'points_earned',
            'status', 'reviewed_by', 'reviewed_by_name', 'reviewed_at', 'review_notes',
            'linked_item', 'created_at'
        ]
        read_only_fields = [
            'id', 'points_earned', 'status', 'reviewed_by', 
            'reviewed_at', 'review_notes', 'linked_item', 'created_at'
        ]


class CrowdsourcedPriceCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de preço crowdsourced"""
    
    class Meta:
        model = CrowdsourcedPrice
        fields = [
            'item_name', 'category', 'price_cve', 'island',
            'location_detail', 'reporter_role', 'supplier_name'
        ]
    
    def create(self, validated_data):
        validated_data['reported_by'] = self.context['request'].user
        return super().create(validated_data)


class BudgetItemSerializer(serializers.ModelSerializer):
    price_item_detail = PriceItemListSerializer(source='price_item', read_only=True)
    category_code = serializers.CharField(source='get_category_code', read_only=True)
    
    class Meta:
        model = BudgetItem
        fields = [
            'id', 'budget', 'price_item', 'price_item_detail',
            'custom_name', 'custom_unit', 'custom_unit_price',
            'quantity', 'unit_price', 'total', 'order', 'notes',
            'category_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Valida que ou price_item ou custom_name está definido"""
        price_item = data.get('price_item')
        custom_name = data.get('custom_name')
        
        if not price_item and not custom_name:
            raise serializers.ValidationError(
                "Deve especificar um item da base de preços ou um nome customizado."
            )
        
        if not price_item:
            custom_unit_price = data.get('custom_unit_price')
            if not custom_unit_price:
                raise serializers.ValidationError(
                    "Para itens customizados, deve especificar o preço unitário."
                )
        
        return data


class BudgetItemCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de item de orçamento"""
    
    class Meta:
        model = BudgetItem
        fields = [
            'price_item', 'custom_name', 'custom_unit', 'custom_unit_price',
            'quantity', 'notes', 'order'
        ]
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantidade deve ser maior que zero.")
        return value


class BudgetListSerializer(serializers.ModelSerializer):
    """Serializer light para listagem de orçamentos"""
    island_display = serializers.CharField(source='get_island_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'description', 'project', 'island', 'island_display',
            'status', 'status_display', 'total', 'subtotal', 'contingency',
            'item_count', 'created_by_name', 'created_at', 'updated_at'
        ]
    
    def get_item_count(self, obj):
        return obj.items.count()


class BudgetDetailSerializer(serializers.ModelSerializer):
    """Serializer completo com itens"""
    island_display = serializers.CharField(source='get_island_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = BudgetItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'description', 'project', 'island', 'island_display',
            'contingency_pct', 'status', 'status_display',
            'total_materials', 'total_labor', 'total_equipment', 'total_services',
            'subtotal', 'contingency', 'total',
            'items', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_materials', 'total_labor', 'total_equipment', 'total_services',
            'subtotal', 'contingency', 'total'
        ]


class BudgetCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de orçamento"""
    
    class Meta:
        model = Budget
        fields = ['name', 'description', 'project', 'island', 'contingency_pct']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class UserPointsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserPoints
        fields = ['user', 'user_name', 'total_points', 'prices_reported', 'prices_verified', 'badges']


class PointsLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsLog
        fields = ['points', 'reason', 'created_at']


class LeaderboardEntrySerializer(serializers.Serializer):
    """Serializer para leaderboard"""
    rank = serializers.IntegerField()
    user_name = serializers.CharField()
    total_points = serializers.IntegerField()
    prices_reported = serializers.IntegerField()
    badges = serializers.ListField()


class BudgetExportSerializer(serializers.Serializer):
    """Serializer para exportação"""
    format = serializers.ChoiceField(choices=['pdf', 'excel'])
    include_notes = serializers.BooleanField(default=True)
