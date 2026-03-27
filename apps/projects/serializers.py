from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Project, Building, Floor

class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = '__all__'

class BuildingSerializer(serializers.ModelSerializer):
    floors = FloorSerializer(many=True, read_only=True)

    class Meta:
        model = Building
        fields = '__all__'

class ProjectSerializer(GeoFeatureModelSerializer):
    buildings = BuildingSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        geo_field = 'location'
        fields = (
            'id', 'name', 'slug', 'status', 'description',
            'address', 'city', 'island',
            'start_date', 'expected_completion', 'actual_completion',
            'created_at', 'updated_at', 'buildings',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
