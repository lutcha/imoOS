from rest_framework import serializers
from .models import Unit

class UnitSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='floor.building.project.name', read_only=True)
    building_name = serializers.CharField(source='floor.building.name', read_only=True)
    floor_number = serializers.CharField(source='floor.number', read_only=True)

    class Meta:
        model = Unit
        fields = (
            'id', 'floor', 'number', 'typology', 'unit_type', 'status', 
            'price', 'currency', 'internal_area', 'external_area', 
            'total_area', 'fraçao', 'description',
            'project_name', 'building_name', 'floor_number',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
