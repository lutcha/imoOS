from rest_framework import serializers
from .models import Unit, UnitType, UnitPricing


class UnitTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitType
        fields = ['id', 'name', 'code', 'bedrooms', 'bathrooms']


class UnitPricingSerializer(serializers.ModelSerializer):
    final_price_cve = serializers.ReadOnlyField()

    class Meta:
        model = UnitPricing
        fields = [
            'id', 'price_cve', 'price_eur', 'price_per_sqm',
            'discount_type', 'discount_value', 'final_price_cve', 'updated_at',
        ]


class UnitSerializer(serializers.ModelSerializer):
    pricing = UnitPricingSerializer(read_only=True)
    unit_type_detail = UnitTypeSerializer(source='unit_type', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id', 'floor', 'unit_type', 'unit_type_detail', 'code', 'description',
            'status', 'status_display', 'area_bruta', 'area_util',
            'orientation', 'floor_number', 'bim_guid',
            'pricing', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
