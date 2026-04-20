from rest_framework import serializers
from .models import Unit, UnitType, UnitPricing, UnitOccurrence


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


class UnitOccurrenceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    occurrence_type_display = serializers.CharField(source='get_occurrence_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    reporter_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    assignee_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = UnitOccurrence
        fields = [
            'id', 'unit', 'occurrence_type', 'occurrence_type_display',
            'description', 'status', 'status_display',
            'priority', 'priority_display', 'reported_by', 'reporter_name',
            'assigned_to', 'assignee_name', 'resolved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at']


class UnitSerializer(serializers.ModelSerializer):
    pricing = UnitPricingSerializer(read_only=True)
    unit_type_detail = UnitTypeSerializer(source='unit_type', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recent_occurrences = UnitOccurrenceSerializer(source='occurrences', many=True, read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id', 'floor', 'unit_type', 'unit_type_detail', 'code', 'description',
            'status', 'status_display', 'area_bruta', 'area_util',
            'orientation', 'floor_number', 'bim_guid',
            'pricing', 'recent_occurrences', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
